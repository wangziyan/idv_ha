# -*- coding: utf-8 -*-
#
# Created on 2020年06月04日
#
# @author: wzy
#

from threading import Thread
from drbd import Drbd
from drbd_mgr import DrbdManager
from disk_mgr import DiskManager
from log import logger

class ProcessHandler(object):
    def __init__(self):
        self.__drbd = Drbd()
        self.__drbd_mgr = DrbdManager()
        self.__disk_mgr = DiskManager()

        t = Thread(target=self.prepare)
        t.start()

    def prepare(self):
        self.__drbd_mgr.prepare()

    def idv_ha_created_with_others(self, ip1, ip2):
        # 检测是否已与其他节点建立了HA
        logger.info("server recv idv_ha_created_with_others")
        return self.__drbd_mgr.have_drbd_with_others(ip1, ip2)

    def idv_ha_prepared(self, disks):
        # 检测是否具备开启idv ha的条件
        logger.info("server recv idv_ha_prepared")
        return self.__disk_mgr.is_disk_matched(disks)

    # TODO(wzy): drbd的健康状态检测
    def drbd_health_check(self):
        logger.info("server recv drbd health check")
        return 0

    # TODO(wzy): 切换为主节点
    def switch_master(self):
        logger.info("server recv switch master")
        print("server recv switch master")
        self.__drbd.switch_master()

    # TODO(wzy): 切换为备节点
    def switch_backup(self):
        logger.info("server recv switch backup")
        print("server recv switch backup")
        self.__drbd.switch_backup()
