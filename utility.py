# -*- coding: utf-8 -*-
#
# Created on 2020年06月04日
#
# @author: wzy
#

import os
import json
import shutil
import fileinput
import re

from constant import IDV_HA_CONF, IDV_HA_CONF_PATH, DRBD_CONF, STORAGE_MOUNT
from log import logger

def is_file_exist(filename):
    if os.path.exists(filename):
        return True
    else:
        if not os.path.exists(IDV_HA_CONF_PATH):
            os.makedirs(IDV_HA_CONF_PATH)
        logger.info("%s is not exist" % filename)
        return False

def is_idv_ha_enabled():
    res = False
    if is_file_exist(IDV_HA_CONF):
        try:
            with open(IDV_HA_CONF, "r") as j_file:
                data = json.load(j_file)
                enabled = data.get("status").get("enable_ha", "false")
                if enabled == "true":
                    res = True
        except Exception as e:
            logger.error("server is_idv_ha_enabled error: %s" % e)

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
                conf["ip1"] = data.get("keepalived").get("interface", "0.0.0.0")
                conf["ip2"] = data.get("keepalived").get("interface", "0.0.0.0")
                logger.info("read keepalived conf state:%s router_id:%s virtual_ip:%s interface:%s ip1:%s ip2:%s",
                            conf["state"], conf["router_id"], conf["virtual_ip"],
                            conf["interface"], conf["ip1"], conf["ip2"])
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

def get_idv_ha_conf():
    conf = None
    if is_file_exist(IDV_HA_CONF):
        try:
            with open(IDV_HA_CONF, "r") as j_file:
                conf = json.load(j_file)
        except Exception as e:
            logger.error("server get_idv_ha_conf error:%s" % e)

    return conf

def save_conf(filename, data):
    try:
        with open(filename, "w") as j_file:
            json.dump(data, j_file, indent=4)
    except Exception as e:
        logger.error("server save_conf error:%s" % e)

def disable_auto_mount(storage):
    """
    禁用AVD Server自动挂载目录
    """
    if is_file_exist(STORAGE_MOUNT):
        mount_dir = ""
        try:
            with open(STORAGE_MOUNT, "r") as f:
                for line in f:
                    if storage in line:
                        line = line.replace("mount", "#mount")
                    mount_dir += line

            with open(STORAGE_MOUNT, "w") as f:
                f.write(mount_dir)
        except Exception as e:
            logger.error("disable auto mount error:%s" % e)

def enable_auto_mount(storage):
    """
    启用AVD Server自动挂载目录
    """
    if is_file_exist(STORAGE_MOUNT):
        mount_dir = ""
        try:
            with open(STORAGE_MOUNT, "r") as f:
                for line in f:
                    if storage in line:
                        line = line.replace("#mount", "mount")
                    mount_dir += line

            with open(STORAGE_MOUNT, "w") as f:
                f.write(mount_dir)
        except Exception as e:
            logger.error("enable auto mount error:%s" % e)

def update_conf(cfg, re_exp, replace, begin="", end=""):
    """
    更新keepalvied的配置文件
    """
    if os.path.exists(cfg):
        file_bk = "%s.bk" % cfg
        shutil.copy(cfg, file_bk)
        modify_file(file_bk, re_exp, replace, begin, end)
        shutil.move(file_bk, cfg)
    else:
        logger.error("file:%s is not exist", cfg)

def modify_file(file_name, re_exp, replace, begin, end):
    text_begin = begin.strip()
    text_end = end.strip()

    for_replace = True

    if text_begin:
        for_replace = False

    try:
        for line in fileinput.input(file_name, inplace=1):
            if text_begin and re.search(text_begin, line):
                for_replace = True

            if text_end and re.search(text_end, line):
                for_replace = False

            if for_replace:
                line = re.sub(re_exp, replace, line)
            print line,
    except OSError as e:
        logger.exception(e)
    except [RuntimeError, ValueError, IndexError] as e:
        raise e
    finally:
        fileinput.close()
