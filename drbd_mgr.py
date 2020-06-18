# -*- coding: utf-8 -*-
#
# Created on 2020年06月09日
#
# @author: wzy
#

import os
from collections import OrderedDict
from time import sleep
from common import singleton
from constant import DRBD_CONF, STORAGE_CONF, IDV_HA_CONF
from drbd_const import DrbdState, DrbdConnState, DrbdDiskState
from drbd_cmd import (drbd_base_resource_str)
from log import logger
from tools import shell_cmd, get_disk_info_from_cfg
from utility import (is_idv_ha_enabled,
                     get_drbd_conf,
                     get_idv_ha_conf,
                     is_master_node,
                     save_conf)

class Drbd(object):
    def __init__(self, resource_num, resource_conf=None):
        self.primary_addr = None
        self.primary_host = None
        self.secondary_addr = None
        self.secondary_host = None
        self.is_primary = None
        self.res_num = resource_num

        self.role = None
        self.cstate = DrbdConnState.unknown
        self.dstate = DrbdDiskState.d_unknown
        self.progress = "0%"

        # 初始化有两种情况，开机读取配置文件以及新建立IDV_HA的DRBD对象
        if not resource_conf:
            self.back_device = resource_conf.get("drbd_back_device", "/dev/mapper/vg_drbd-%s" % (self.res_num))
            self.drbd_dev = resource_conf.get("drbd_dev", "/dev/drbd%s" % (self.res_num))
            self.port = str(7789 + int(self.res_num))
            self.res_name = resource_conf.get("resource_name", "r%s" % (self.res_num))
            self.res_path = resource_conf.get("resource_path", "/etc/drbd.d/r%s.res" % (self.res_num))
            self.storage_dir = resource_conf.get("storage_dir", "")
            self.status = resource_conf.get("status", 0)
        else:
            self.back_device = "/dev/mapper/vg_drbd-%s" % (self.res_num)
            self.drbd_dev = "/dev/drbd%s" % (self.res_num)
            self.port = str(7789 + int(self.res_num))
            self.res_name = "r%s" % (self.res_num)
            self.res_path = "/etc/drbd.d/r%s.res" % (self.res_num)
            # TODO(wzy): 可能会出现异常无法获取？
            self.storage_dir = get_disk_info_from_cfg(STORAGE_CONF, "path")  # 从storage.cfg中获取挂载目录
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
        self.port = str(drbd_info.port)

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

    def force_primary(self):
        cmd = "drbdadm primary %s --force" % self.res_name
        ret, output = shell_cmd(cmd, need_out=True)

        if ret != 0:
            logger.error("force primary error: %s" % output)
        logger.info("force_primary succcess")

        return ret == 0

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
                ''' % (self.resource)

        ret, output = shell_cmd(cmd, need_out=True)

        if ret != 0:
            self.status = DrbdState.INIT_FAILED
            logger.error("drbd create meta data failed: %s" % output)
            # TODO(wzy): 创建元数据失败的情况要处理——擦除文件系统

    def wipe_fs(self, block_dev):
        cmd = "wipefs -a %s" % block_dev
        shell_cmd(cmd)
        logger.info("wipe %s filesystem" % block_dev)

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
        if is_idv_ha_enabled():
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
            logger.info("idv ha drbd is prepared")
        else:
            logger.info("idv ha disabled, so drbd will not prepare")

    def start_service(self):
        logger.info("start service drbd......")
        cmd = "systemctl start drbd"
        ret = shell_cmd(cmd)
        if ret != 0:
            logger.error("start service drbd failed")

    def start_multi_services(self):
        # 开启多种服务
        cmd = "systemctl start drbd ovp-idv"
        ret, output = shell_cmd(cmd, need_out=True)
        if ret != 0:
            logger.error("start services failed output: %s" % output)

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
        drbd_conf = OrderedDict()

        for drbd in self.drbd_lists:
            res_num = drbd.res_num
            drbd_conf[res_num] = OrderedDict()
            drbd_conf[res_num]["drbd_back_device"] = drbd.back_device
            drbd_conf[res_num]["drdb_dev"] = drbd.drbd_dev
            drbd_conf[res_num]["port"] = int(drbd.port)
            drbd_conf[res_num]["resource_name"] = drbd.res_name
            drbd_conf[res_num]["resource_path"] = drbd.res_path
            drbd_conf[res_num]["storage_dir"] = drbd.storage_dir
            drbd_conf[res_num]["status"] = drbd.status

        save_conf(DRBD_CONF, drbd_conf)

    def save_idv_ha_conf(self, net_info, drbd_info, is_primary, enabled):
        # 使用有序字典写入配置文件，便于阅读,is useful or useless
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
        else:
            # 没有配置文件创建一个配置文件
            new_conf["keepalived"]["state"] = "MASTER" if is_primary else "BACKUP"
            new_conf["keepalived"]["router_id"] = net_info.rid
            new_conf["keepalived"]["virtual_ip"] = net_info.vip
            new_conf["keepalived"]["interface"] = "vmbr0"  # TODO(wzy): 使用哪个网口如何确定
            new_conf["drbd"]["res_num"] = drbd_info.res_num
            new_conf["drbd"]["res_port"] = drbd_info.port_num
            new_conf["drbd"]["node1"] = drbd_info.primary_host
            new_conf["drbd"]["node2"] = drbd_info.secondary_host
            new_conf["status"]["enable_ha"] = "true" if enabled else "false"
            new_conf["status"]["is_master"] = "true" if is_primary else "false"

        save_conf(IDV_HA_CONF, new_conf)

    def have_drbd_with_others(self, ip1, ip2):
        # 判断是否已经与其他节点建立了IDV_HA
        if not is_idv_ha_enabled():
            return False

        for drbd in self.drbd_lists:
            if ip1 == drbd.primary_addr and ip2 == drbd.secondary_addr:
                return False

        return True

    def init_drbd(self, net_info, drbd_info, is_primary):
        # 创建DRBD对象
        drbd = Drbd(drbd_info.res_num)
        drbd.update(net_info, drbd_info, is_primary)
        # 创建drbd资源文件
        drbd.create_drbd_resource_file()
        # 创建drbd元数据
        drbd.create_drbd_meta_data()
        # 启用drbd资源
        drbd.up_resource()
        self.drbd_lists.append(drbd)
        # 把drbd信息写入配置文件
        self.save_drbd_conf()
        # DRBD的首次同步
        if is_primary:
            # TODO(wzy): 强制同步前需要询问备节点是否已准备好，主节点作为同步源,进行同步
            drbd.force_primary()
            pass

    def is_drbd_meta_data_exist(self, res_num, block_dev, version="v09", meta_type="internal"):
        result = False
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

    def update_and_recovery(self, net_info, drbd_info, is_primary):
        # 重新修改drbd配置文件,资源文件,然后再保存
        print("update resource conf")
        print("resource num:" + drbd_info.res_num)
        print("port num:" + drbd_info.port)
        print("node name:" + drbd_info.node)
        print("block dev:" + drbd_info.block)
        res_num = drbd_info.res_num

        # 读取drbd配置文件
        drbd_conf = get_drbd_conf()

        if drbd_conf:
            for num, res_conf in drbd_conf.items():
                if res_num == num:
                    logger.info("find drbd configuration we will update it")
                    drbd = Drbd(num, res_conf)
                    drbd.update(net_info, drbd_info, is_primary)
                    # 更新drbd资源文件
                    drbd.update_drbd_resource()
                    # 启用资源
                    drbd.up_resource()
                    self.drbd_lists.append(drbd)
                    break

        # 保存配置到drbd.conf
        self.save_drbd_conf()
