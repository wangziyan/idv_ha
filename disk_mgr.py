# -*- coding: utf-8 -*-
#
# Created on 2020年06月11日
#
# @author: wzy
#

from constant import HA_PREPARE_RESULT
from tools import (get_disk_info_from_cfg,
                   get_disk_size,
                   is_disk_size_same,
                   is_disk_type_same,
                   is_content_supported)
from utility import is_idv_ha_enabled

class DiskManager(object):
    def __init__(self):
        pass

    def is_disk_matched(self, disks):
        # 判断磁盘条件是否具备
        result = {}

        for disc in disks:
            print("disk storage name is %s", disc.storage_name)
            print("disk volume name is %s", disc.volume_name)
            print("disk size is %d", disc.size)
            print("disk type is %s", disc.type)
            print("disk content is %s", disc.content)

            mount_dir = get_disk_info_from_cfg(disc.storage_name, "path")

            if mount_dir == "":
                # 存储池名称不一致
                result[disc.storage_name] = HA_PREPARE_RESULT.STORAGE_NAME_DIFF
                continue

            if not is_disk_type_same(mount_dir, disc.type):
                # 磁盘的类型不一致（没有启用lvm）
                result[disc.storage_name] = HA_PREPARE_RESULT.DISK_TYPE_NOT_LVM
                continue

            # TODO(wzy): 检查磁盘缓存是否开启

            size = get_disk_size(mount_dir)

            if not is_disk_size_same(size, disc.size):
                # 磁盘大小不一致
                result[disc.storage_name] = HA_PREPARE_RESULT.DISK_SIZE_NOT_SAME
                continue

            if not is_content_supported(disc.storage_name, disc.content):
                # 存储池内容类型不支持,local也要进行这项检测
                result[disc.storage_name] = HA_PREPARE_RESULT.DISK_CONTENT_NOT_SUP
                continue

            result[disc.storage_name] = HA_PREPARE_RESULT.SUCCESS

        return result
