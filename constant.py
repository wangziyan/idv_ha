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

# IDV HA日志配置
AVDS_LOG_PATH = "/thinputer/log/"
IDV_HA_LOG_NAME = "idv_ha.log"
IDV_HA_LOG_PATH = AVDS_LOG_PATH + IDV_HA_LOG_NAME

# 存储池文件
STORAGE_CONF = "/etc/ovp/storage.cfg"
# 两端磁盘大小差异不能超过10G
DISK_SIZE_LIMIT = 10

class HA_PREPARE_RESULT(object):
    SUCCESS = 0                 # 可以建立
    CLUSTER_ESTABLISHED = 1     # 已经加入了集群
    IDV_HA_ESTABLISHED = 2      # 已经与其他节点建立了IDV_HA
    STORAGE_NAME_DIFF = 3       # 存储池名称不同(包含没有对应名称的以及没有的)
    DISK_TYPE_NOT_LVM = 4       # 没有建立lvm
    DISK_CACHE_ENABLED = 5      # 已经开启了磁盘缓存
    DISK_SIZE_NOT_SAME = 6      # 磁盘大小不一致
    DISK_CONTENT_NOT_SUP = 7    # 存储池内容有不支持的项

class HA_SETUP_RESULT(object):
    SUCCESS = 0              # 建立成功
    VM_STARTED = 1           # 有开启的虚拟机
    IDV_TEMPLATE_OPENED = 2  # 有IDV镜像已经打开了
    FS_EXIST = 3             # 仍有数据，需要清空
    THRIFT_ERROR = 4         # Thrift请求出现问题
    ERROR_5 = 5
    UNKNOWN = 10             # 未知
