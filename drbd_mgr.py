# -*- coding: utf-8 -*-
#
# Created on 2020年06月09日
#
# @author: wzy
#

import os
import re

from time import sleep
from threading import Thread
from collections import OrderedDict

from common import singleton
from constant import (DRBD_CONF,
                      STORAGE_CONF,
                      IDV_HA_CONF,
                      SUCCESS,
                      DRBD_SWITCH_PRIMARY_FAILED,
                      DRBD_SWITCH_SECONDARY_FAILED,
                      DRBD_REMOTE_ROLE_ERROR,
                      HA_REMOVE_RESULT,
                      DRBD_UMOUNT_FAILED)
from drbd_const import (DrbdState,
                        DrbdConnState,
                        DrbdDiskState,
                        DrbdRState,
                        DrbdRole,
                        SyncState,
                        ConnState,
                        UPDATE_INTERVERL)
from drbd_cmd import (drbd_base_resource_str,
                      get_drbd_role,
                      get_remote_role)
from log import logger
from tools import (shell_cmd,
                   get_disk_info_from_cfg,
                   get_block_size,
                   is_large_disk,
                   get_storage_name,
                   get_disk_size,
                   kill9_process_of_mount_dir)
from utility import (is_idv_ha_enabled,
                     get_drbd_conf,
                     get_idv_ha_conf,
                     is_master_node,
                     save_conf,
                     get_keepalived_conf,
                     disable_auto_mount,
                     enable_auto_mount)
from timer_task import TimerTask

class Drbd(object):
    def __init__(self, resource_num, resource_conf=None):
        self.primary_addr = None
        self.primary_host = None
        self.secondary_addr = None
        self.secondary_host = None
        self.is_primary = None
        self.res_num = resource_num
        self.is_metadata_ready = None
        self.is_umount = True  # temporary useless
        self.fs_type = None
        self.storage = None

        self.role = DrbdRole.unknown
        self.cstate = DrbdConnState.unknown
        self.dstate = DrbdDiskState.unknown
        self.rstate = DrbdRState.unknown
        self.progress = "0"

        # 初始化有两种情况，开机读取配置文件以及新建立IDV_HA的DRBD对象
        # TODO(wzy): status 需要明确具体的含义是什么
        if resource_conf:
            self.back_device = resource_conf.get("drbd_back_device", "/dev/mapper/idvha-%s" % (self.res_num))
            self.drbd_dev = resource_conf.get("drbd_dev", "/dev/drbd%s" % (self.res_num))
            self.port = str(7789 + int(self.res_num))
            self.res_name = resource_conf.get("resource_name", "r%s" % (self.res_num))
            self.res_path = resource_conf.get("resource_path", "/etc/drbd.d/r%s.res" % (self.res_num))
            self.storage_dir = resource_conf.get("storage_dir", "")
            self.status = resource_conf.get("status", 0)
            self.storage = resource_conf.get("storage", get_storage_name(self.back_device))
        else:
            self.back_device = None
            self.drbd_dev = "/dev/drbd%s" % (self.res_num)
            self.port = str(7789 + int(self.res_num))
            self.res_name = "r%s" % (self.res_num)
            self.res_path = "/etc/drbd.d/r%s.res" % (self.res_num)
            self.storage_dir = None
            self.status = DrbdState.SUCCESS

        self.mount_cmd = self.init_cmd_shell()

    def init_cmd_shell(self):
        drbd_dev = self.drbd_dev
        mount_dir = self.storage_dir
        cmd = "mkdir -p %s && mount %s %s" % (mount_dir, drbd_dev, mount_dir)

        return cmd

    def update(self, net_info, drbd_info, is_primary):
        self.primary_addr = net_info.master_ip
        self.primary_host = drbd_info.primary_host
        self.secondary_addr = net_info.backup_ip
        self.secondary_host = drbd_info.secondary_host
        self.is_primary = is_primary
        self.port = str(drbd_info.port_num)
        self.back_device = drbd_info.block_dev
        self.storage_dir = get_disk_info_from_cfg(get_storage_name(self.back_device), "path")  # 从storage.cfg中获取挂载目录
        self.storage = get_storage_name(self.back_device)
        # 更新挂载目录
        self.mount_cmd = self.init_cmd_shell()
        # TODO(wzy):role是否更新，还是等待定时器自动获取
        self.role = DrbdRole.primary if is_primary else DrbdRole.secondary

    def back_device_exist(self):
        return True if os.path.exists(self.back_device) else False

    def up_resource(self):
        cmd = "drbdadm up %s" % self.res_name
        ret, output = shell_cmd(cmd, need_out=True)

        if ret != SUCCESS:
            self.status = DrbdState.UP_FAILED
            logger.error("up resource %s failed output:%s" % (self.res_name, output))
            return False

        return True

    def down_resource(self):
        cmd = "drbdadm down %s" % self.res_name
        ret, output = shell_cmd(cmd, need_out=True)

        if ret != SUCCESS:
            logger.error("down resource %s failed output:%s" % (self.res_name, output))
            return False

        return True

    def force_primary(self):
        cmd = "drbdadm primary %s --force" % self.res_name
        ret, output = shell_cmd(cmd, need_out=True)

        if ret != SUCCESS:
            logger.error("force primary error: %s" % output)

        logger.info("force_primary succcess")

        return ret == SUCCESS

    def get_cstate(self):
        cmd = "drbdadm cstate %s" % self.res_name
        _, output = shell_cmd(cmd, need_out=True)
        c_state = DrbdConnState.unknown

        try:
            c_state = output.strip()
        except Exception as e:
            logger.exception(e.message)

        return c_state

    def get_dstate(self):
        cmd = "drbdadm dstate %s" % self.res_name
        _, output = shell_cmd(cmd, need_out=True)
        d_state = DrbdDiskState.unknown

        try:
            d_state = output.split('\n')[0].split("/")[0]
        except Exception as e:
            logger.exception(e.message)

        return d_state

    def get_rstate(self):
        cmd = "drbdsetup status %s --verbose" % self.res_name
        _, output = shell_cmd(cmd, need_out=True)
        role = DrbdRState.unknown

        try:
            role = re.findall(r"replication:(.+?) ", output)[0]
        except Exception as e:
            logger.exception(e.message)

        return role

    def get_role(self):
        cmd = "drbdadm role %s" % self.res_name
        _, output = shell_cmd(cmd, need_out=True)
        ret = DrbdRole.unknown

        try:
            ret = output.strip()
        except Exception as e:
            logger.exception(e.message)

        return ret

    def get_sync_progress(self):
        cmd = "drbdsetup status %s --verbose" % self.res_name
        _, output = shell_cmd(cmd, need_out=True)
        progress = 0

        try:
            progress = re.findall(r"done:(.+?)\n", output)[0]
        except Exception as e:
            logger.exception(e.message)

        return progress

    def get_fs_type(self):
        cmd = "blkid %s" % self.drbd_dev
        _, output = shell_cmd(cmd, need_out=True)
        _type = None

        try:
            _type = re.search('TYPE="(.*?)"', output).group(1)
        except Exception as e:
            _type = None
            logger.error("get_fs_type error: %s" % e)

        return _type

    def get_current_state(self):
        if self.dstate == DrbdDiskState.up_to_date:
            return SyncState.FINISHED

        if self.rstate == DrbdRState.sync_source or self.rstate == DrbdRState.sync_target:
            return SyncState.SYNC

        return SyncState.WAITING

    def create_drbd_resource_file(self):
        try:
            res_conf = drbd_base_resource_str()

            res_conf = res_conf % (self.res_name,
                                   self.res_num,
                                   self.back_device,
                                   self.primary_host,
                                   self.primary_addr,
                                   self.port,
                                   self.secondary_host,
                                   self.secondary_addr,
                                   self.port)

            # write drbd conf to res file
            with open(self.res_path, "w") as drbd_config:
                drbd_config.write(res_conf)

        except Exception as e:
            logger.error("create drbd resource file error:%s" % e)

    def update_drbd_resource(self):
        # 删除然后再重新创建
        cmd = "rm -f %s" % self.res_path
        shell_cmd(cmd)
        self.create_drbd_resource_file()

    def create_drbd_meta_data(self):
        cmd = '''
drbdadm create-md %s << EOF
yes
yes
EOF
''' % (self.res_name)

        ret, output = shell_cmd(cmd, need_out=True)

        # TODO(wzy): 创建元数据前清除了文件系统，所以还会出现哪些创建失败的情况不清楚
        # res文件会有一些判断，不符合将会报错
        if ret != SUCCESS:
            self.status = DrbdState.INIT_FAILED
            logger.error("drbd create meta data failed: %s" % output)
        else:
            self.status = DrbdState.SUCCESS
            logger.info("drbd create meta data success")

        return self.status

    def update_drbd_info(self):
        self.cstate = self.get_cstate()
        self.dstate = self.get_dstate()
        self.rstate = self.get_rstate()
        self.role = self.get_role()

        # 如果是正在同步状态，更新进度
        if "Sync" in self.rstate:
            self.progress = self.get_sync_progress()

        self.fs_type = self.get_fs_type()

    def mount_dir(self):
        cmd = self.mount_cmd
        ret, output = shell_cmd(cmd, need_out=True)

        if ret != SUCCESS:
            self.status = DrbdState.MOUNT_FAILED
            logger.error("mount resource %s failed output:%s" % (self.res_name, output))
        else:
            self.status = DrbdState.SUCCESS
            logger.info("mount resource %s success" % self.res_name)

    def wipe_fs(self):
        cmd = "wipefs -a %s" % self.back_device
        shell_cmd(cmd)
        logger.info("wipe %s filesystem" % self.back_device)

    def make_fs(self, block_dev, drbd_dev):
        size = get_disk_size(block_dev)

        if size >= 500:
            cmd = "mkfs.ext4 -F -T largefile %s" % drbd_dev
        else:
            cmd = "mkfs.ext4 -F %s" % drbd_dev

        ret, output = shell_cmd(cmd, need_out=True)

        if ret != SUCCESS:
            logger.error("make filesystem failed: %s" % output)

@singleton
class DrbdManager(object):
    def __init__(self):
        self.drbd_lists = []
        self.primary_addr = None
        self.secondary_addr = None
        self.primary_host = None
        self.secondary_host = None
        self.is_primary = None
        self.is_local = False
        self.drbd_prepare_ready = False

        # temporary useless
        self.update_timer = TimerTask(self.update_drbd_task, UPDATE_INTERVERL)

    def prepare(self):
        if is_idv_ha_enabled():
            logger.info("begin drbd preparation")
            # 读取配置文件中主机名及ip
            ha_conf = get_idv_ha_conf()

            if ha_conf:
                logger.info("begin ha exist")
                self.primary_addr = ha_conf.get("keepalived")['ip1']
                self.secondary_addr = ha_conf.get("keepalived")['ip2']
                self.primary_host = ha_conf.get("drbd")['node1']
                self.secondary_host = ha_conf.get("drbd")['node2']
                logger.info("begin prepare ip1:%s ip2:%s node1:%s node2:%s" % (self.primary_addr, self.secondary_addr,
                            self.primary_host, self.secondary_host))

            drbd_conf = get_drbd_conf()

            if drbd_conf:
                for res_num, res_conf in drbd_conf.items():
                    drbd = Drbd(res_num, res_conf)
                    # 根据配置文件初始化原有的状态是否清空
                    drbd.status = DrbdState.SUCCESS
                    drbd.up_resource()

                    if not drbd.back_device_exist():
                        logger.warning("no drbd device: %s" % drbd.back_device)
                        drbd.status = DrbdState.MOUNT_FAILED

                    self.drbd_lists.append(drbd)
            else:
                logger.warning("there is no drbd conf file")

            self.start_service()

            # TODO(wzy): 这里是否需要考虑脑裂的情况？完全依赖配置文件会不会有问题？
            if is_master_node():  # master node mount dir
                self.primary_all_resources()
                self.mount_all_dir()

            self.save_drbd_conf()  # 是不是也是多余的操作
            self.drbd_prepare_ready = True
            logger.info("idv ha drbd is prepared")
        else:
            logger.info("idv ha disabled, so drbd will not prepare")

    def start_service(self):
        logger.info("start service drbd......")
        cmd = "systemctl start drbd"
        ret = shell_cmd(cmd)
        if ret != SUCCESS:
            logger.error("start service drbd failed")

    def start_multi_services(self):
        # 开启多种服务
        cmd = "systemctl start drbd keepalived ovp-idv smb"
        ret, output = shell_cmd(cmd, need_out=True)
        if ret != SUCCESS:
            logger.error("start services failed output: %s" % output)

    def start_other_service(self):
        cmd = "systemctl start ovp-idv smb"
        ret, output = shell_cmd(cmd, need_out=True)
        if ret != SUCCESS:
            logger.error("start other services failed output: %s" % output)

    def stop_drbd_service(self):
        cmd = "systemctl stop drbd keepalived"
        ret, output = shell_cmd(cmd, need_out=True)
        if ret != SUCCESS:
            logger.error("stop drbd keepalvied service failed output: %s" % output)

    def stop_other_service(self):
        cmd = "systemctl stop ovp-idv smb"
        ret, output = shell_cmd(cmd, need_out=True)
        if ret != SUCCESS:
            logger.error("stop other services failed output: %s" % output)

    def update_drbd_task(self):
        for drbd in self.drbd_lists:
            drbd.update_drbd_info()

    def mount_all_dir(self, add_drbd=None):
        drbd_lists = []
        if add_drbd:
            drbd_lists.append(add_drbd)
        else:
            drbd_lists = self.drbd_lists

        for drbd in drbd_lists:
            cmd = drbd.mount_cmd
            logger.info("drbd mount cmd:%s" % cmd)
            ret, output = shell_cmd(cmd, need_out=True)

            if ret != SUCCESS:
                drbd.status = DrbdState.MOUNT_FAILED
                logger.error("mount resource %s failed output:%s" % (drbd.res_name, output))
            else:
                drbd.status = DrbdState.SUCCESS
                logger.info("mount resource %s success" % drbd.res_name)

    def primary_all_resources(self):
        self.check_inactive_state()

        cmd = "drbdadm primary all"
        ret, output = shell_cmd(cmd, need_out=True)

        if ret != SUCCESS:
            logger.error(output)
            return False
        logger.info("primary_all_resources succcess")

        return ret == SUCCESS

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
        drbd_conf = OrderedDict()

        for drbd in self.drbd_lists:
            res_num = drbd.res_num
            drbd_conf[res_num] = OrderedDict()
            drbd_conf[res_num]["drbd_back_device"] = drbd.back_device
            drbd_conf[res_num]["drdb_dev"] = drbd.drbd_dev
            drbd_conf[res_num]["port"] = drbd.port
            drbd_conf[res_num]["resource_name"] = drbd.res_name
            drbd_conf[res_num]["resource_path"] = drbd.res_path
            drbd_conf[res_num]["storage_dir"] = drbd.storage_dir
            drbd_conf[res_num]["status"] = drbd.status
            drbd_conf[res_num]["storage"] = drbd.storage

        save_conf(DRBD_CONF, drbd_conf)

    def save_idv_ha_conf(self, net_info, drbd_info, is_primary, enabled):
        """
        enabled: True 表示开启高可用 False 表示关闭高可用
        """
        # 使用有序字典写入配置文件，便于阅读,is useful or useless
        logger.info("enter save conf %s" % IDV_HA_CONF)
        ha_conf = get_idv_ha_conf()
        new_conf = OrderedDict()
        new_conf["keepalived"] = OrderedDict()
        new_conf["drbd"] = OrderedDict()
        new_conf["status"] = OrderedDict()

        if ha_conf:
            new_conf["keepalived"] = ha_conf.get("keepalived")
            new_conf["drbd"] = ha_conf.get("drbd")
            new_conf["status"] = ha_conf.get("status")
            new_conf["status"]["enable_ha"] = "true" if enabled else "false"
            new_conf["status"]["is_master"] = "true" if is_primary else "false"

            if net_info:
                new_conf["keepalived"]["state"] = "MASTER" if is_primary else "BACKUP"
                new_conf["keepalived"]["router_id"] = net_info.rid
                new_conf["keepalived"]["virtual_ip"] = net_info.vip
                new_conf["keepalived"]["ip1"] = net_info.master_ip
                new_conf["keepalived"]["ip2"] = net_info.backup_ip

            if drbd_info:
                new_conf["drbd"]["res_num"] = drbd_info.res_num
                new_conf["drbd"]["res_port"] = drbd_info.port_num
                new_conf["drbd"]["node1"] = drbd_info.primary_host
                new_conf["drbd"]["node2"] = drbd_info.secondary_host
        else:
            # 没有配置文件创建一个配置文件
            new_conf["keepalived"]["state"] = "MASTER" if is_primary else "BACKUP"
            new_conf["keepalived"]["router_id"] = net_info.rid
            new_conf["keepalived"]["virtual_ip"] = net_info.vip
            new_conf["keepalived"]["interface"] = "vmbr0"  # TODO(wzy): 使用哪个网口如何确定
            new_conf["keepalived"]["ip1"] = "0.0.0.0"
            new_conf["keepalived"]["ip2"] = "0.0.0.0"
            new_conf["drbd"]["res_num"] = drbd_info.res_num
            new_conf["drbd"]["res_port"] = drbd_info.port_num
            new_conf["drbd"]["node1"] = drbd_info.primary_host
            new_conf["drbd"]["node2"] = drbd_info.secondary_host
            new_conf["status"]["enable_ha"] = "true" if enabled else "false"
            new_conf["status"]["is_master"] = "true" if is_primary else "false"

        save_conf(IDV_HA_CONF, new_conf)
        logger.info("save conf %s" % IDV_HA_CONF)

    def take_over_mount(self, drbd):
        logger.info("take over AVD Server auto mount")
        storage = get_storage_name(drbd.block_dev)
        disable_auto_mount(storage)

    def recover_auto_mount(self):
        for drbd in self.drbd_lists:
            enable_auto_mount(drbd.storage)

    def have_drbd_with_others(self, ip1, ip2):
        # 判断是否已经与其他节点建立了IDV_HA
        if not is_idv_ha_enabled():
            return False

        for drbd in self.drbd_lists:
            if ip1 == drbd.primary_addr and ip2 == drbd.secondary_addr:
                return False

        return True

    def init_drbd(self, net_info, drbd_info, is_primary):
        logger.info("server is master:%d init drbd" % is_primary)
        self.primary_addr = net_info.master_ip
        self.secondary_addr = net_info.backup_ip
        self.primary_host = drbd_info.primary_host
        self.secondary_host = drbd_info.secondary_host
        # 创建DRBD对象
        drbd = Drbd(drbd_info.res_num)
        drbd.update(net_info, drbd_info, is_primary)
        # 创建drbd资源文件
        drbd.create_drbd_resource_file()
        # 擦除文件系统
        drbd.wipe_fs()

        # 创建drbd元数据
        if drbd.create_drbd_meta_data():
            return drbd.status

        # 启用前先关闭资源
        drbd.down_resource()

        # 启用drbd资源
        if not drbd.up_resource():
            return drbd.status

        self.drbd_lists.append(drbd)
        # 把drbd信息写入配置文件
        self.save_drbd_conf()
        logger.info("server is master:%d init drbd success" % is_primary)
        logger.info("server is master:%d drbd status" % drbd.status)

        return drbd.status

    def update_mount(self, res_num):  # temporary useless
        for drbd in self.drbd_lists:
            if res_num == drbd.res_num:
                drbd.is_umount = True

    def is_drbd_meta_data_exist(self, res_num, block_dev, version="v09", meta_type="internal"):
        result = False
        res_num = "r" + str(res_num)
        cmd = "drbdmeta %s %s %s %s dstate" % (res_num, version, block_dev, meta_type)
        ret, output = shell_cmd(cmd, need_out=True)

        if ret == 1:
            for line in output.split("\n"):
                if line == "No valid meta data found":
                    result = False
                    logger.info("drbd meta data does not exist: %s" % output)
        elif ret == 0:
            result = True
            logger.info("drbd meta data exist: %s" % output)

        return result

    def is_ready_to_sync(self, res_num):
        for drbd in self.drbd_lists:
            if res_num == drbd.res_num:
                if drbd.is_metadata_ready and drbd.is_umount:
                    return True

        return False

    def update_and_recovery(self, net_info, drbd_info, is_primary):
        # 重新修改drbd配置文件,资源文件,然后再保存
        print("update resource conf")
        print("resource num:" + drbd_info.res_num)
        print("port num:" + drbd_info.port_num)
        print("node1 name:" + drbd_info.primary_host)
        print("node2 name:" + drbd_info.secondary_host)
        print("block dev:" + drbd_info.block_dev)
        self.primary_addr = net_info.master_ip
        self.secondary_addr = net_info.backup_ip
        self.primary_host = drbd_info.primary_host
        self.secondary_host = drbd_info.secondary_host
        res_num = drbd_info.res_num
        status = None

        # 读取drbd配置文件
        drbd_conf = get_drbd_conf()

        if drbd_conf:
            # TODO(wzy): 判断条件过于简单
            for num, res_conf in drbd_conf.items():
                if res_num == num:
                    logger.info("find drbd configuration we will update it")
                    drbd = Drbd(num, res_conf)
                    drbd.update(net_info, drbd_info, is_primary)
                    # 更新drbd资源文件
                    drbd.update_drbd_resource()
                    # 启用前先禁用
                    drbd.down_resource()
                    # 启用资源
                    drbd.up_resource()
                    status = drbd.status

                    # 非成功状态直接返回
                    if not status:
                        return status

                    self.drbd_lists.append(drbd)
                    break

        # 保存配置到drbd.conf
        self.save_drbd_conf()

        return status

    def force_primary_resource(self, res_num):
        for drbd in self.drbd_lists:
            if res_num == drbd.res_num:
                return drbd.force_primary()

    def mkfs_and_mount(self, res_num):
        logger.info("master server run mkfs thread")

        for drbd in self.drbd_lists:
            if res_num == drbd.res_num:
                # 开始同步后即创建文件系统,可能比较耗时，在子线程中执行
                t = Thread(target=drbd.make_fs, args=(drbd.back_device, drbd.drbd_dev))
                t.start()
                break

        mkfs_finish = False
        while True:
            # 文件系统创建结束后挂载目录
            for drbd in self.drbd_lists:
                if drbd.res_num == res_num:
                    if "ext4" == drbd.fs_type:
                        self.mount_dir()
                        mkfs_finish = True

            if mkfs_finish:
                break

            sleep(3)

    def umount_dir(self):
        cmd = "df -hx tmpfs"
        _, output = shell_cmd(cmd, need_out=True)
        dir_list = output.split('\n')

        for path in dir_list:
            if not re.search("^/dev/drbd", path):
                continue

            mount_dir = path.split()[5]

            if mount_dir:
                cmd = "umount -f %s" % mount_dir
                ret, output = shell_cmd(cmd, need_out=True)

                if ret != SUCCESS:
                    # 强制关闭占用目录的进程
                    kill9_process_of_mount_dir(mount_dir)
                    cmd = "umount -f %s" % mount_dir
                    ret, output = shell_cmd(cmd, need_out=True)

                    if ret != SUCCESS:
                        logger.error("umount %s failed", mount_dir)
                        return False

        return True

    def switch_master(self):
        if get_drbd_role() != DrbdRole.primary:
            for i in range(6):
                if DrbdRole.primary not in get_remote_role():
                    for _ in range(3):
                        self.primary_all_resources()
                        sleep(2)
                        if DrbdRole.primary == get_drbd_role():
                            break
                    break
                elif i == 5:
                    logger.error("remote role is Primary")
                    return DRBD_REMOTE_ROLE_ERROR
                sleep(2)

        if get_drbd_role() != DrbdRole.primary:
            logger.error("primary resource failed")
            return DRBD_SWITCH_PRIMARY_FAILED

        self.is_primary = True

        self.mount_all_dir()
        self.start_other_service()

        return SUCCESS

    def switch_backup(self):
        # 停止可能占用路径的服务
        self.stop_other_service()
        # 取消挂载
        if not self.umount_dir():
            return DRBD_UMOUNT_FAILED
        # drbd降级为secondary
        if get_drbd_role() == DrbdRole.secondary:
            for _ in range(3):
                output = shell_cmd("drbdadm secondary all", need_out=True)[1]
                logger.info(output)
                sleep(2)
                if get_drbd_role() == DrbdRole.secondary:
                    break

        if get_drbd_role() != DrbdRole.secondary:
            logger.error("drbd secondary resource failed")
            return DRBD_SWITCH_SECONDARY_FAILED

        return SUCCESS

    def check_state(self):
        state = 0

        for drbd in self.drbd_lists:
            if drbd.cstate == DrbdConnState.connected:
                state = ConnState.connected
            elif drbd.cstate == DrbdConnState.connecting:
                state = ConnState.connecting
            else:
                state = ConnState.stand_alone

        return state

    def get_ha_info(self, local_ip):
        keepavlied_conf = get_keepalived_conf()
        vip = keepavlied_conf.get("virtual_ip")
        rid = keepavlied_conf.get("router_id")
        status = self.check_state()
        local_is_primary = False
        res = []

        if not is_idv_ha_enabled():
            return res

        if local_ip == self.primary_addr:
            local_is_primary = True

        for _ in range(2):
            logger.info("begin range")
            node_info = {
                "servername": self.primary_host if local_is_primary else self.secondary_host,
                "serverip": self.primary_addr if local_is_primary else self.secondary_addr,
                "islocal": "1" if local_is_primary else "0",
                "virip": vip,
                "routeid": str(rid),
                "role": "Master" if local_is_primary else "Slave",
                "status": str(status)
            }
            local_is_primary = not local_is_primary
            res.append(node_info)

        return res

    def get_state(self):
        result = []
        state = {}

        for drbd in self.drbd_lists:
            state['status'] = drbd.get_current_state()
            state['rate'] = drbd.progress
            state['storage'] = drbd.storage
            result.append(state)

        return result

    def get_drbd_list(self):
        return self.drbd_lists

    def get_remote_ip(self):
        return self.secondary_addr

    def remove(self, is_master):
        for drbd in self.drbd_lists:
            if not drbd.down_resource():
                if is_master:
                    return HA_REMOVE_RESULT.DOWN_RES_ERROR
                else:
                    return HA_REMOVE_RESULT.REMOTE_DOWN_RES_ERROR
            drbd.drbd_dev = drbd.back_device
            drbd.mount_cmd = drbd.init_cmd_shell()

        self.save_idv_ha_conf(None, None, is_master, False)
        self.mount_all_dir()
        self.recover_auto_mount()
        self.start_multi_services()
        self.stop_drbd_service()
        del self.drbd_lists[:]

        return HA_REMOVE_RESULT.SUCCESS
