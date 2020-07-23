# -*- coding: utf-8 -*-
#
# Created on 2020年06月04日
#
# @author: wzy
#

from threading import Thread
from time import sleep

from constant import HA_SETUP_RESULT, HA_REMOVE_RESULT
from drbd import DrbdTask
from drbd_mgr import DrbdManager
from disk_mgr import DiskManager
from log import logger
from remote import Remote
from tools import get_local_hostname

class ProcessHandler(object):
    def __init__(self):
        self.__drbd_task = DrbdTask()
        self.__drbd_mgr = DrbdManager()
        self.__disk_mgr = DiskManager()

        t = Thread(target=self.prepare)
        t.start()

    def prepare(self):
        self.__drbd_mgr.prepare()

    def created_with_others(self, ip1, ip2):
        # 检测是否已与其他节点建立了HA
        logger.info("server recv idv_ha_created_with_others")
        return self.__drbd_mgr.have_drbd_with_others(ip1, ip2)

    def prepared(self, disks):
        # 检测是否具备开启IDVHa的条件
        logger.info("server recv idv_ha_prepared")
        return self.__disk_mgr.is_well_prepared(disks)

    def setup(self, net, drbd, is_master, is_force=False):
        logger.info("server recv setup_idv_ha")
        result = None
        print("net vip is %s" % net.vip)
        print("net rid is %s" % net.rid)
        print("net master_ip is %s" % net.master_ip)
        print("net backup_ip is %s" % net.backup_ip)
        print("drbd res_num is %s" % drbd.res_num)
        print("drbd port_num is %s" % drbd.port_num)
        print("drbd primary_host is %s" % drbd.primary_host)
        print("drbd secondary_host is %s" % drbd.secondary_host)
        print("drbd block_dev is %s" % drbd.block_dev)

        if is_master:
            result = Remote.remote_setup(net, drbd, not is_master, is_force)

        if result:
            logger.info("setup result %d" % result)

        if is_master and result:
            return result + 10

        block_dev = drbd.block_dev
        res_num = drbd.res_num

        # 主节点判断是否存在元数据，备节点重新建立
        if self.__drbd_mgr.is_drbd_meta_data_exist(res_num, block_dev) and is_master:
            # 若存在,更新drbd资源文件,恢复建立连接
            result = self.__drbd_mgr.update_and_recovery(net, drbd, is_master)
            if result:
                # TODO(wzy)：失败的话需要重新恢复服务，挂载？
                return HA_SETUP_RESULT.INIT_ERROR
        else:
            # 否则就属于首次建立
            result = self.__drbd_mgr.init_drbd(net, drbd, is_master)
            if result:
                # TODO(wzy)：失败的话需要重新恢复服务，挂载？
                return HA_SETUP_RESULT.INIT_ERROR

        if not is_master:
            logger.info("remote server setup result is %d" % result)
            self.__drbd_mgr.start_multi_services()
            self.__drbd_mgr.save_idv_ha_conf(net, drbd, is_master, True)
            self.__drbd_mgr.take_over_mount(drbd)
            logger.info("remote server setup result is %d" % result)
            return result

        # 等待对端是否完成了同步准备工作，然后开始同步
        #for _ in range(3):
        #    if Remote.ready_to_sync(net.backup_ip, res_num):
        #        self.__drbd_mgr.force_primary_resource(res_num)
        #        result = HA_SETUP_RESULT.SUCCESS
        #        break
        #    sleep(3)

        self.__drbd_mgr.force_primary_resource(res_num)

        # 在子线程创建文件系统，完成后挂载目录
        if is_master:
            t = Thread(target=self.__drbd_mgr.mkfs_and_mount, args=(res_num,))
            t.setDaemon(True)
            t.start()

        # 启动ovp-idv、drbd等多个服务
        self.__drbd_mgr.start_multi_services()
        # 保存信息到配置文件
        self.__drbd_mgr.save_idv_ha_conf(net, drbd, is_master, True)
        # 接管AVD Server自动挂载，由IDV_HA完成挂载
        self.__drbd_mgr.take_over_mount(drbd)

        return result

    def modify(self, net):
        logger.info("server recv modify idv ha")

    def remove(self, is_master):
        logger.info("server recv remove idv ha")
        remote_result = None

        if is_master:
            drbd_lists = self.__drbd_mgr.get_drbd_list()
            for drbd in drbd_lists:
                if not self.__disk_mgr.try_umount(drbd.drbd_dev):
                    return HA_REMOVE_RESULT.UMOUNT_ERROR

        if is_master:
            remote_ip = self.__drbd_mgr.get_remote_ip()
            logger.info("remote ip is %s" % remote_ip)
            remote_result = Remote.remote_remove(remote_ip, not is_master)

        if is_master and remote_result:
            return remote_result

        return self.__drbd_mgr.remove(is_master)

    def ready_to_sync(self, res_num):
        return self.__drbd_mgr.is_ready_to_sync(res_num)

    def get_drbd_state(self):
        return self.__drbd_mgr.get_state()

    def get_ha_info(self, ip):
        logger.info("server get idv info from perl")
        print("server get idv info from perl")
        return self.__drbd_mgr.get_ha_info(ip)

    def get_hostname(self):
        logger.info("remote server get hostname")
        print("remote server get hostname")
        return get_local_hostname()

    # TODO(wzy): drbd的健康状态检测
    def drbd_health_check(self):
        logger.info("server recv drbd health check")
        return self.__drbd_task.health_check()

    # TODO(wzy): 切换为主节点
    def switch_master(self):
        # TODO(wzy): 备切换主的限制是什么？
        logger.info("server recv switch master")
        print("server recv switch master")
        self.__drbd_task.switch_master()

    # TODO(wzy): 切换为备节点
    def switch_backup(self):
        logger.info("server recv switch backup")
        print("server recv switch backup")
        self.__drbd_task.switch_backup()
        self.__drbd_mgr.switch_backup()

    # TODO(wzy): 切换为备节点
    def switch_faults(self):
        logger.info("server recv switch backup")
        print("server recv switch backup")
        self.__drbd_task.switch_faults()
