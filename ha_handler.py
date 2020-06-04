# -*- coding: utf-8 -*-
#
# Created on 2020年06月04日
#
# @author: wzy
#
from log import logger

class ProcessHandler(object):
    def __init__(self):
        pass

    def drbd_health_check(self):
        logger.info("server recv drbd health check")
        return 0

    def idv_ha_prepared(self, disks):
        logger.info("server recv idv ha prepared")
        result = {}

        for disc in disks:
            print("disk storage name is %s", disc.storage_name)
            print("disk volume name is %s", disc.volume_name)
            print("disk disk size is %d", disc.size)
            print("disk disk type is %s", disc.type)
            result[disc.storage_name] = True

        return result

    # TODO(wzy): 切换为主节点
    def switch_master(self):
        logger.info("server recv switch master")
        print("server recv switch master")
        return 0

    # TODO(wzy): 切换为备节点
    def switch_backup(self):
        logger.info("server recv switch backup")
        print("server recv switch backup")
        return 1
