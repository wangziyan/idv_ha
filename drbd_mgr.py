# -*- coding: utf-8 -*-
#
# Created on 2020年06月09日
#
# @author: wzy
#
import os
from time import sleep
from common import singleton
from constant import DRBD_CONF
from drbd_const import DrbdState, DrbdConnState, DrbdDiskState
from log import logger
from tools import shell_cmd
from utility import enable_idv_ha, get_drbd_conf, is_master_node, save_conf

class Drbd(object):
    def __init__(self, resource_num, resource_conf):
        self.primary_addr = None
        self.secondary_addr = None
        self.is_primary = None
        self.res_num = resource_num

        self.role = None
        self.cstate = DrbdConnState.unknown
        self.dstate = DrbdDiskState.d_unknown
        self.progress = "0%"

        self.back_device = resource_conf.get("drbd_back_device", "/dev/mapper/vg_drbd-%s" % (self.res_num))
        self.drbd_dev = resource_conf.get("drbd_dev", "/dev/drbd%s" % (self.res_num))
        self.port = str(7789 + int(self.res_num))
        self.res_name = resource_conf.get("resource_name", "r%s" % (self.res_num))
        self.res_path = resource_conf.get("resource_path", "/etc/drbd.d/r%s.res" % (self.res_num))
        self.storage_dir = resource_conf.get("storage_dir", "")
        self.status = resource_conf.get("status", 0)

        self.mount_cmd = self.init_cmd_shell()

    def init_cmd_shell(self):
        drbd_dev = self.drbd_dev
        mount_dir = self.storage_dir
        cmd = "mkdir -p %s && mount %s %s" % (mount_dir, drbd_dev, mount_dir)

        return cmd

    def back_device_exist(self):
        return True if os.path.exists(self.back_device) else False

    def up_resource(self):
        cmd = "drbdadm up %s" % self.res_name
        ret, output = shell_cmd(cmd, need_out=True)

        if ret != 0:
            self.status = DrbdState.UP_FAILED
            logger.error("up resource %s failed output:%s" % (self.res_name, output))
            return False
        return True

    def down_resource(self):
        cmd = "drbdadm down %s" % self.res_name
        ret, output = shell_cmd(cmd, need_out=True)

        if ret != 0:
            logger.error("down resource %s failed output:%s" % (self.res_name, output))
            return False
        return True

    def get_dstate(self):
        cmd = "drbdadm dstate %s" % (self.res_name)
        _, output = shell_cmd(cmd, need_out=True)
        ret = DrbdDiskState.d_unknown
        try:
            ret = output.split('\n')[0].split("/")[0]
        except Exception as e:
            logger.exception(e.message)
        return ret

@singleton
class DrbdManager(object):
    def __init__(self):
        self.drbd_lists = []
        self.primary_addr = None
        self.secondary = None
        self.is_primary = None
        self.is_local = False
        self.role = None
        self.drbd_prepare_ready = False
        self.all_change_dir = []
        self.in_update_time = 0

    def prepare(self):
        if enable_idv_ha():
            logger.info("begin drbd preparation")
            drbd_conf = get_drbd_conf()

            if drbd_conf:
                for res_num, res_conf in drbd_conf.items():
                    drbd = Drbd(res_num, res_conf)
                    # 根据配置文件初始化原有的状态是否清空
                    # drbd.status = DrbdState.SUCCESS

                    if not drbd.back_device_exist():
                        logger.warning("no drbd device: %s" % drbd.back_device)
                        drbd.status = DrbdState.MOUNT_FAILED

                    self.drbd_lists.append(drbd)
            else:
                logger.warning("there is no drbd conf file")

            self.start_service()

            # TODO(wzy): 这里是否需要考虑脑裂的情况？完全依赖配置文件会不会有问题？会有问题的
            if is_master_node():  # master node mount dir
                self.primary_all_resources()
                self.mount_dir()

            self.save_drbd_conf()  # 是不是也是多余的操作
            self.drbd_prepare_ready = True
            logger.info("drbd is prepared")
        else:
            logger.info("idv ha disabled, so drbd will not prepare")

    def start_service(self):
        logger.info("start service drbd......")
        cmd = "systemctl start drbd"
        ret = shell_cmd(cmd)
        if ret != 0:
            logger.error("start service drbd failed")

    def mount_dir(self, add_drbd=None):
        drbd_lists = []
        if add_drbd:
            drbd_lists.append(add_drbd)
        else:
            drbd_lists = self.drbd_lists

        for drbd in drbd_lists:
            cmd = drbd.mount_cmd
            logger.info("drbd mount cmd:%s" % cmd)
            ret, output = shell_cmd(cmd, need_out=True)

            if ret != 0:
                drbd.status = DrbdState.MOUNT_FAILED
                logger.error("mount resource %s failed output:%s" % (drbd.res_name, output))
            else:
                drbd.status = DrbdState.SUCCESS
                logger.info("mount resource %s success" % drbd.res_name)

    def primary_all_resources(self):
        self.check_inactive_state()

        cmd = "drbdadm primary all"
        ret, output = shell_cmd(cmd, need_out=True)

        if ret != 0:
            logger.error(output)
            return False
        logger.info("primary_all_resources succcess")
        return ret == 0

    def check_inactive_state(self):
        count = 0
        in_negotiating = False

        while count < 5:  # TODO(wzy): 只检测了negotiating这种状态
            try:
                for drbd in self.drbd_lists:
                    dstate = drbd.get_dstate()
                    if DrbdDiskState.negotiating in dstate:
                        drbd.down_resource()
                        sleep(5)
                        drbd.up_resource()
                        logger.warning("drbd state in %s" % dstate)
                        in_negotiating = True

                if not in_negotiating:
                    return
            except:
                logger.error("check_inactive_state error")
            count += 1
            logger.error("drbd in negotiating state recheck")

    def save_drbd_conf(self):
        drbd_conf = {}

        for drbd in self.drbd_lists:
            res_num = drbd.res_num
            drbd_conf[res_num] = {}
            drbd_conf[res_num]["drbd_back_device"] = drbd.back_device
            drbd_conf[res_num]["drdb_dev"] = drbd.drbd_dev
            drbd_conf[res_num]["port"] = int(drbd.port)
            drbd_conf[res_num]["resource_name"] = drbd.res_name
            drbd_conf[res_num]["resource_path"] = drbd.res_path
            drbd_conf[res_num]["storage_dir"] = drbd.storage_dir
            drbd_conf[res_num]["status"] = drbd.status

        save_conf(DRBD_CONF, drbd_conf)
