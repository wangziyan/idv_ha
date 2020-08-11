# -*- coding: utf-8 -*-
#
# Created on 2020年05月28日
#
# @author: wzy
#

# IDV HA Server监听端口
SERVER_PORT = 9011
# Thrift 超时时间
THRIFT_TIMEOUT = 30000

# IDV HA相关配置文件
IDV_HA_CONF_PATH = "/etc/ovp/idv_ha/"
IDV_HA_CONF = IDV_HA_CONF_PATH + "idv_ha.conf"

# DRBD配置文件
DRBD_CONF = IDV_HA_CONF_PATH + "drbd.conf"

# Keepalived配置文件
KEEPALIVED_CONF = "/etc/keepalived/keepalived.conf"

# IDV HA日志配置
AVDS_LOG_PATH = "/thinputer/log/"
IDV_HA_LOG_NAME = "idv_ha.log"
IDV_HA_LOG_PATH = AVDS_LOG_PATH + IDV_HA_LOG_NAME

# 存储池配置文件
STORAGE_CONF = "/etc/ovp/storage.cfg"
# 存储池挂载目录文件
STORAGE_MOUNT = "/etc/ovp-config/storage-mount.cfg"

# 两端磁盘大小差异不能超过5G
DISK_SIZE_LIMIT = 5

class HA_PREPARE_RESULT(object):
    SUCCESS = 0                 # 可以建立
    CLUSTER_ESTABLISHED = 1     # 已经加入了集群
    IDV_HA_ESTABLISHED = 2      # 已经与其他节点建立了IDV_HA
    STORAGE_NAME_DIFF = 3       # 存储池名称不同(包含没有对应名称的以及没有的)
    DISK_TYPE_NOT_LVM = 4       # 没有建立lvm
    DISK_CACHE_ENABLED = 5      # 已经开启了磁盘缓存
    DISK_SIZE_NOT_SAME = 6      # 磁盘大小不一致
    DISK_CONTENT_NOT_SUP = 7    # 存储池内容有不支持的项
    DISK_BUSY = 8               # 磁盘被占用无法取消挂载

class HA_SETUP_RESULT(object):
    SUCCESS = 0               # 建立成功
    UMOUNT_ERROR = 1          # 取消挂载失败 useless
    INIT_ERROR = 2            # 初始化失败
    FS_EXIST = 3              # 仍有数据，需要清空
    REMOTE_UMOUNT_ERROR = 11  # 远端取消挂在失败
    REMOTE_INIT_ERROR = 12    # 远端初始化失败
    REMOTE_FS_EXIST = 13      # 远端仍有数据需要清空
    UNKNOWN = 100             # 未知

class HA_REMOVE_RESULT(object):
    SUCCESS = 0                 # 移除成功
    UMOUNT_ERROR = 1            # 取消挂载失败
    DOWN_RES_ERROR = 2          # 资源关闭失败
    REMOTE_DOWN_RES_ERROR = 12  # 远程资源关闭失败

####################################Drbd State####################################
SUCCESS = 0
FAILED = 1
THRIFT_ERROR = 1000
DRBD_INCONSISTENT = 1001
DRBD_DISKLESS = 1002

DRBD_SWITCH_PRIMARY_FAILED = 1100  # 提升为主失败
DRBD_SWITCH_SECONDARY_FAILED = 1101  # 降级为备失败
DRBD_REMOTE_ROLE_ERROR = 1102  # 远端角色错误

####################################Keepalived State####################################
NET_DISCONNECT = 1200  # 网络断开
NET_VRRP_NOT_MATCH = 1201  # 没有匹配的VRRP包
NET_VRRP_VRID_USED = 1202  # 虚拟路由id已经被使用

ROLE_ABNORMAL_MAX_TIMES = 3
