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
