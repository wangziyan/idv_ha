# -*- coding: utf-8 -*-
#
# Created on 2020年06月04日
#
# @author: wzy
#

from threading import Thread

from constant import HA_SETUP_RESULT
from drbd import DrbdTask
from drbd_mgr import DrbdManager
from disk_mgr import DiskManager
from log import logger
from utility import is_idv_ha_enabled

class ProcessHandler(object):
    def __init__(self):
        self.__drbd_task = DrbdTask()
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

    # TODO(wzy): 建立高可用
    def setup_idv_ha(self, net, drbd, is_master, is_force=False):
        logger.info("server recv setup_idv_ha")

        block_dev = drbd.block_dev
        res_num = drbd.res_num

        # 如果目录已经挂载需要先取消挂载，如果是主节点的话之后要再次挂载
        if not self.__disk_mgr.try_umount(block_dev):
            # 取消挂载失败，判断是因为哪种原因的失败，并返回结果
            return self.__disk_mgr.umount_failed_reason(block_dev)

        if is_idv_ha_enabled():
            # 已经开了IDV_HA,建立HA的请求属于添加新的存储池
            self.__drbd_mgr.init_drbd(net, drbd, is_master)
            return HA_SETUP_RESULT.SUCCESS

        # 判断是否存在drbd元数据
        if self.__drbd_mgr.is_drbd_meta_data_exist(res_num, block_dev):
            # 若存在, 更新drbd资源文件,恢复建立连接
            self.__drbd_mgr.update_and_recovery(net, drbd, is_master)
        else:
            # 否则就属于首次建立
            self.__drbd_mgr.init_drbd(net, drbd, is_master)

        # 启动ovp-idv、drbd等多个服务
        self.__drbd_mgr.start_multi_services()

        # 保存信息到配置文件
        self.__drbd_mgr.save_idv_ha_conf(net, drbd, is_master, True)

    # TODO(wzy): 是否准备好建立IDV_HA，条件是元数据创建成功，目录没有挂载
    def read_to_sync(self):
        pass

    # TODO(wzy): drbd的健康状态检测
    def drbd_health_check(self):
        logger.info("server recv drbd health check")
        return 0

    # TODO(wzy): 切换为主节点
    def switch_master(self):
        logger.info("server recv switch master")
        print("server recv switch master")
        self.__drbd_task.switch_master()

    # TODO(wzy): 切换为备节点
    def switch_backup(self):
        logger.info("server recv switch backup")
        print("server recv switch backup")
        self.__drbd_task.switch_backup()
