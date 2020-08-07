# -*- coding: utf-8 -*-
#
# Created on 2020年05月28日
#
# @author: wzy
#

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
                      IDV_HA_CONF)
from drbd_const import (DrbdConnState,
                        DrbdDiskState,
                        DrbdRole)
from drbd_cmd import (get_cstate,
                      get_dstate,
                      get_local_role,
                      get_drbd_role)
from keepalived import get_keepalived_state, KeepalivedState
from tools import shell_cmd
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
        self.read_keepalived()
        self.start()

    def __run(self):
        """
        we only exec the latest work
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
        logger.info("start switch master")
        print("enter __switch_master")
        print("do nothing")
        # drbd设备检测

    def __switch_backup(self):
        print("enter __switch_backup")
        print("do nothing")

    def __switch_fault(self):
        print("enter __switch_fault")
        print("do nothing")

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
            self.__role_abnormal_times += 1
            logger.warn("drbd role:%s keepalived state:%s" % (drbd_role, keepa_state))

            if self.__role_abnormal_times > ROLE_ABNORMAL_MAX_TIMES:
                if keepa_state == KeepalivedState.master:
                    self.switch_master()
                elif keepa_state == KeepalivedState.backup:
                    self.switch_backup()

    def switch_master(self):
        self.__queue.put(self.__switch_master)

    def switch_backup(self):
        self.__queue.put(self.__switch_backup)

    def switch_faults(self):
        self.__queue.put(self.__switch_fault)

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
        result = FAILED

        if self.__ka_state != "FAULT":
            if net.vip != self.__virtual_ip:
                self.__virtual_ip = net.ip
                re_expr = r"(?:\d{1,3}\.){3}\d{1,3}"
                begin = r"vrrp_instance\s+management\s+{"
                end = r"^}"
                update_conf(KEEPALIVED_CONF, re_expr, net.vip, begin, end)

            if net.rid != self.__router_id:
                self.__router_id = net.rid
                re_expr = r"virtual_router_id\s+\d{1,3}"
                begin = r"vrrp_instance\s+management\s+{"
                end = r"^}"
                replace_str = "virtual_router_id " + net.rid
                update_conf(KEEPALIVED_CONF, re_expr, replace_str, begin, end)

            # 修改HA配置文件
            self.save_ha_conf(rid=net.rid, vip=net.vip)
            # 配置热重载
            cmd = "kill -HUP $(cat /var/run/keepalived.pid)"
            shell_cmd(cmd)
            result = SUCCESS
        else:
            logger.error("current state is %s not support modify config", self.__ka_state)

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

    def __check_ha_cluster_state(self):
        pass

    def _check_state_of_idv_ha(self):
        try:
            thread = Thread(target=self.__check_ha_cluster_state)
            thread.start()
        except Exception as e:
            logger.exception(e.message)
