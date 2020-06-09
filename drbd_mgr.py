# -*- coding: utf-8 -*-
#
# Created on 2020年06月09日
#
# @author: wzy
#
from common import singleton
# from tools import log_enter_exit
from utility import enable_idv_ha, get_drbd_conf
from log import logger

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
            print(drbd_conf)
            self.drbd_prepare_ready = True
            logger.info("drbd is prepared")
        else:
            logger.info("idv ha disable drbd will not prepare")
