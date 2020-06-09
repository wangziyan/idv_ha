# -*- coding: utf-8 -*-
#
# Created on 2020年06月04日
#
# @author: wzy
#
import subprocess
from functools import wraps
from log import logger

def get_system_uptime():
    uptime = 0
    try:
        with open("/proc/uptime", "r") as file:
            res = file.readline().strip()
            uptime = float(res.split(" ")[0])
    except IOError as ex:
        logger.exception(ex)
    return uptime

def shell_cmd(cmd, need_out=False):
    returncode = 1
    try:
        if need_out:
            returncode = subprocess.check_output(cmd, close_fds=True, shell=True)
        else:
            returncode = subprocess.check_call(cmd, close_fds=True, shell=True)
    except subprocess.CalledProcessError as e:
        logger.exception(e.message)
    finally:
        return returncode

def check_net(interface):
    cmd = "ethtool %s|grep 'Link detected:'|awk -F ':' '{print $2}'" % interface
    ret = shell_cmd(cmd, need_out=True).strip().lower()
    return True if ret == "yes" else False

def log_enter_exit(func):
    @wraps(func)
    def log_content(*args, **kargs):
        logger.info("enter function(%s)" % (func.__name__))
        result = func(*args, **kargs)
        logger.info("exit function(%s) status(%s)" % (func.__name__, result))
        return result
    return log_content
