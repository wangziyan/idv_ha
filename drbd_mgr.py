# -*- coding: utf-8 -*-
#
# Created on 2020年06月09日
#
# @author: wzy
#
from common import singleton
from drbd_const import DrbdState, DrbdConnState, DrbdDiskState
from utility import enable_idv_ha, get_drbd_conf
from log import logger

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

@singleton
class DrbdManager(object):
    def __init__(self):
        self.drbd_list = []
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
            else:
                logger.warning("there is no drbd conf file")
            self.drbd_prepare_ready = True
            logger.info("drbd is prepared")
        else:
            logger.info("idv ha disabled, so drbd will not prepare")
