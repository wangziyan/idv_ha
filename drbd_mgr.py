# -*- coding: utf-8 -*-
#
# Created on 2020年06月09日
#
# @author: wzy
#
import os
from common import singleton
from drbd_const import DrbdState, DrbdConnState, DrbdDiskState
from log import logger
from tools import shell_cmd
from utility import enable_idv_ha, get_drbd_conf

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

    def back_device_exist(self):
        return True if os.path.exists(self.back_device) else False

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

                    # 开启Drbd服务
                    self.start_service()
            else:
                logger.warning("there is no drbd conf file")
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
