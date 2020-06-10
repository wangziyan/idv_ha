# -*- coding: utf-8 -*-
#
# Created on 2020年06月04日
#
# @author: wzy
#
import os
import json

from constant import IDV_HA_CONF, IDV_HA_CONF_PATH, DRBD_CONF
from log import logger

def is_file_exist(filename):
    if os.path.exists(filename):
        return True
    else:
        if not os.path.exists(IDV_HA_CONF_PATH):
            os.makedirs(IDV_HA_CONF_PATH)
        logger.info("%s is not exist" % filename)
        return False

def enable_idv_ha():
    res = False
    if is_file_exist(IDV_HA_CONF):
        try:
            with open(IDV_HA_CONF, "r") as j_file:
                data = json.load(j_file)
                enabled = data.get("status").get("enable_ha", "false")
                if enabled == "true":
                    res = True
        except Exception as e:
            logger.error("server enable_idv_ha error: %s" % e)
    return res

def is_master_node():
    res = False
    if is_file_exist(IDV_HA_CONF):
        try:
            with open(IDV_HA_CONF, "r") as j_file:
                data = json.load(j_file)
                is_master = data.get("status").get("is_master", "false")
                if is_master == "true":
                    res = True
        except Exception as e:
            logger.error("server is_master_node error: %s" % e)
    else:
        logger.error("file %s is not exist" % IDV_HA_CONF)
    return res

def get_keepalived_conf():
    conf = {}
    if is_file_exist(IDV_HA_CONF):
        try:
            with open(IDV_HA_CONF, "r") as j_file:
                data = json.load(j_file)
                logger.info("enter")
                conf["state"] = data.get("keepalived").get("state", "")
                conf["router_id"] = data.get("keepalived").get("router_id", 10)
                conf["virtual_ip"] = data.get("keepalived").get("virtual_ip", "")
                conf["interface"] = data.get("keepalived").get("interface", "")
                logger.info("read keepalived conf state:%s router_id:%d virtual_ip:%s interface:%s",
                            conf["state"], conf["router_id"], conf["virtual_ip"], conf["interface"])
        except Exception as e:
            logger.error("server get_keepalived_conf error: %s" % e)
    else:
        conf = None
    return conf

def get_drbd_conf():
    conf = None
    if is_file_exist(DRBD_CONF):
        try:
            with open(DRBD_CONF, "r") as j_file:
                conf = json.load(j_file)
        except Exception as e:
            logger.error("server get_drbd_conf error:%s" % e)
    return conf

def save_conf(filename, data):
    if is_file_exist(filename):
        try:
            with open(filename, "w") as j_file:
                json.dump(data, j_file, indent=4)
        except Exception as e:
            logger.error("server save_conf error:%s" % e)
