# -*- coding: utf-8 -*-
#
# Created on 2020年05月28日
#
# @author: wzy
#

from time import sleep
from Queue import Queue
from threading import Thread
from collections import OrderedDict

from common import singleton
from constant import (SUCCESS,
                      FAILED,
                      DRBD_INCONSISTENT,
                      DRBD_DISKLESS,
                      ROLE_ABNORMAL_MAX_TIMES,
                      KEEPALIVED_CONF,
                      IDV_HA_CONF,
                      NET_DISCONNECT,
                      NET_VRRP_NOT_MATCH,
                      HA_MODIFY_RESULT,
                      DRBD_SWITCH_PRIMARY_FAILED,
                      DRBD_SWITCH_SECONDARY_FAILED)
from drbd_const import (DrbdConnState,
                        DrbdDiskState,
                        DrbdRole)
from drbd_cmd import (get_cstate,
                      get_dstate,
                      get_local_role,
                      get_drbd_role)
from keepalived import get_keepalived_state, KeepalivedState
from tools import (shell_cmd,
                   check_net,
                   vrrp_is_matched,
                   vrid_is_used)
from utility import (get_keepalived_conf,
                     update_conf,
                     get_idv_ha_conf,
                     save_conf)
from log import logger

@singleton
class DrbdTask(object):
    def __init__(self):
        self.__queue = Queue()
        self.__task_run = False
        self.__role_abnormal_times = 0
        self.__ka_state = None
        self.__router_id = None
        self.__virtual_ip = None
        self.__interface = None
        self.__drbd_mgr = None
        self.__role_status = None

        self.read_keepalived()
        self.start()

    def __run(self):
        """
        多个切换任务到来时，只执行最后一个任务
        """
        while True:
            work = None
            while True:
                work = self.__queue.get()
                if self.__queue.empty():
                    break
                self.__queue.task_done()
                logger.info("multi task drop " + work.__name__)
            self.__task_run = True
            work()
            self.__task_run = False
            self.__queue.task_done()

    def __switch_master(self):
        logger.info("begin __switch_master")

        # drbd设备检测
        if DrbdDiskState.inconsistent in get_dstate():
            logger.error("drbd disk state inconsistent")
            return DRBD_INCONSISTENT

        if self.__drbd_mgr.switch_master():
            logger.error("drbd mgr switch master failed")
            self.__switch_failed(DrbdRole.primary)
            self.__role_status = DrbdRole.error()
            return DRBD_SWITCH_PRIMARY_FAILED

        if DrbdConnState.stand_alone in get_cstate():
            cmd = "drbdadm connect all"
            output = shell_cmd(cmd, need_out=True)[1]
            logger.info(output)

        self.__role_status = DrbdRole.primary
        logger.info("end __switch_master")

    def __switch_backup(self):
        logger.info("begin __switch_backup")

        if self.__drbd_mgr.switch_backup():
            logger.error("drbd mgr switch backup failed")
            self._switch_failed(DrbdRole.secondary)
            self.__role_status = DrbdRole.error
            return DRBD_SWITCH_SECONDARY_FAILED

        if DrbdConnState.stand_alone in get_cstate():
            cmd = "drbdadm connect all"
            output = shell_cmd(cmd, need_out=True)[1]
            logger.info(output)

        self.__role_status = DrbdRole.secondary
        logger.info("end __switch_backup")

    def __switch_fault(self):
        logger.info("begin __switch_fault")
        # 错误状态的时候切换成备份服务器
        try:
            self.switch_backup()
        except Exception as e:
            logger.exception(e)
            self._switch_failed(KeepalivedState.fault)

    def __switch_failed(self, func):
        self.__task_run = False

        if func != self.__switch_fault:
            times = 10
        else:
            times = 20

        for _ in range(times):
            sleep(6)

            if not self.__queue.empty() or self.__role_status != DrbdRole.error:
                logger.info("end __switch_failed")
                return

            func()

    def __conn_state_check(self):
        if DrbdConnState.stand_alone in get_cstate():
            self.connect()

    def __disk_state_check(self):
        dstate = get_dstate()

        if DrbdDiskState.inconsistent in dstate:
            logger.warn("drbd disk inconsistent")
            return DRBD_INCONSISTENT

        if DrbdDiskState.diskless in dstate:
            logger.warn("drbd disk diskless")
            return DRBD_DISKLESS

        return SUCCESS

    def __role_health_check(self):
        drbd_role = get_drbd_role()
        keepa_state = get_keepalived_state()

        if (drbd_role == DrbdRole.primary and keepa_state == KeepalivedState.master) or \
           (drbd_role == DrbdRole.secondary and keepa_state == KeepalivedState.backup):
            self.__role_abnormal_times = 0
        else:
            logger.warn("drbd role:%s keepalived state:%s" % (drbd_role, keepa_state))

            if self.__task_run or not self.__queue.empty():
                self.__role_abnormal_times = 0
            else:
                self.__role_abnormal_times += 1

                if self.__role_abnormal_times > ROLE_ABNORMAL_MAX_TIMES:
                    if keepa_state == KeepalivedState.master:
                        self.switch_master()
                    elif keepa_state == KeepalivedState.backup:
                        self.switch_backup()

    def __check_ha_cluster_state(self):
        pass

    def _check_state_of_idv_ha(self):
        try:
            thread = Thread(target=self.__check_ha_cluster_state)
            thread.start()
        except Exception as e:
            logger.exception(e.message)

    def __switch_master_failed(self):
        logger.info("enter __switch_master_failed")
        self.__switch_failed(self.__switch_master)

    def __switch_backup_failed(self):
        logger.info("enter __switch_backup_failed")
        self.__switch_failed(self.__switch_backup)

    def __switch_faults_failed(self):
        logger.info("enter __switch_faults_failed")
        self.__switch_failed(self.__switch_fault)

    def _switch_failed(self, status):
        if not self.__queue.empty():
            return

        if status == DrbdRole.primary:
            func = self.__switch_master_failed
        elif status == DrbdRole.secondary:
            func = self.__switch_backup_failed
        elif status == KeepalivedState.fault:
            func = self.__switch_faults_failed
        else:
            return

        logger.info("drbd task queue put method:%s", func.__name__)
        self.__queue.put(func)

    def set_drbd_mgr(self, mgr):
        self.__drbd_mgr = mgr

    def switch_master(self):
        self.__queue.put(self.__switch_master)

    def switch_backup(self):
        self.__queue.put(self.__switch_backup)

    def switch_faults(self):
        self.__queue.put(self.__switch_fault)

    def net_health_check(self):
        if not check_net(self.__interface):
            logger.error("net is disconnect")
            return NET_DISCONNECT

        if vrrp_is_matched(self.__router_id, self.__virtual_ip):
            return SUCCESS

        return NET_VRRP_NOT_MATCH

    def health_check(self):
        self.__conn_state_check()
        ret = self.__disk_state_check()

        if ret == SUCCESS or ret == DRBD_DISKLESS:
            self.__role_health_check()

        return ret

    def start(self):
        try:
            thread = Thread(target=self.__run)
            thread.setDaemon(True)
            thread.start()
        except Exception as e:
            logger.error(e.message)

    def read_keepalived(self):
        keepavlied_conf = get_keepalived_conf()

        if keepavlied_conf:
            self.__ka_state = keepavlied_conf.get("state")
            self.__router_id = keepavlied_conf.get("router_id")
            self.__virtual_ip = keepavlied_conf.get("virtual_ip")
            self.__interface = keepavlied_conf.get("interface")
        else:
            logger.warning("no keepalvied conf")

    def connect(self):
        role = get_local_role()

        if DrbdRole.secondary in role:
            # TODO(wzy): 是否需要增加一个舍弃本端修改重新连接对端的操作discard-my-data?
            cmd = "drbdadm connect all"
            shell_cmd(cmd)

    def modify(self, net):
        result = HA_MODIFY_RESULT.UNKNOWN

        if self.__ka_state != "FAULT":
            if net.rid != self.__router_id:
                # 如果局域网中已经有使用了的虚拟路由id则不允许重复使用
                if vrid_is_used(net.rid):
                    return HA_MODIFY_RESULT.VRID_USED

                self.__router_id = net.rid
                re_expr = r"virtual_router_id\s+\d{1,3}"
                begin = r"vrrp_instance\s+management\s+{"
                end = r"^}"
                replace_str = "virtual_router_id " + net.rid
                update_conf(KEEPALIVED_CONF, re_expr, replace_str, begin, end)

            if net.vip != self.__virtual_ip:
                self.__virtual_ip = net.ip
                re_expr = r"(?:\d{1,3}\.){3}\d{1,3}"
                begin = r"vrrp_instance\s+management\s+{"
                end = r"^}"
                update_conf(KEEPALIVED_CONF, re_expr, net.vip, begin, end)

            # 修改HA配置文件
            self.save_ha_conf(rid=net.rid, vip=net.vip)
            # 配置热重载
            cmd = "kill -HUP $(cat /var/run/keepalived.pid)"
            shell_cmd(cmd)
            result = HA_MODIFY_RESULT.SUCCESS
        else:
            logger.error("current state is %s not support modify config", self.__ka_state)
            result = HA_MODIFY_RESULT.INVALID_STATE

        return result

    def save_ha_conf(self, **cfg):
        ha_conf = get_idv_ha_conf()
        new_conf = OrderedDict()
        new_conf["keepalived"] = OrderedDict()
        new_conf["drbd"] = OrderedDict()
        new_conf["status"] = OrderedDict()
        new_conf["keepalived"] = ha_conf.get("keepalived")
        new_conf["drbd"] = ha_conf.get("drbd")
        new_conf["status"] = ha_conf.get("status")

        if cfg.get('rid', ''):
            new_conf["keepalived"]["router_id"] = cfg.get('rid', '')
        if cfg.get('vip', ''):
            new_conf["keepalived"]["virtual_ip"] = cfg.get('vip', '')

        save_conf(IDV_HA_CONF, new_conf)
        logger.info("save idv_ha conf finished")
