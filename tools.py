# -*- coding: utf-8 -*-
#
# Created on 2020年06月04日
#
# @author: wzy
#

import os
import subprocess
import tempfile
import time
from functools import wraps

from constant import STORAGE_CONF, DISK_SIZE_LIMIT
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
    logger.info("cmd is " + cmd)
    returncode = 0
    out = ""
    if need_out:
        try:
            out_temp = None
            out_temp = tempfile.SpooledTemporaryFile(bufsize=4096)
            fileno = out_temp.fileno()
            child = subprocess.Popen(cmd, shell=True, close_fds=True, stdout=fileno, stderr=fileno)
            child.wait()
            out_temp.seek(0)
            out = out_temp.read()
            returncode = child.returncode
        except Exception as e:
            logger.exception(e)
        finally:
            if out_temp:
                out_temp.close()
    else:
        child = subprocess.Popen(cmd, shell=True, close_fds=True,
                                 stdout=open("/dev/null", "w"), stderr=subprocess.STDOUT)
        child.wait()
        returncode = child.returncode

    try:
        if child.stdin:
            child.stdin.close()
        if child.stdout:
            child.stdout.close()
        if child.stderr:
            child.stderr.close()
        child.kill()
    except Exception as e:
        pass

    if need_out:
        return returncode, out.strip()
    else:
        return returncode

def check_net(interface):
    cmd = "ethtool %s|grep 'Link detected:'|awk -F ':' '{print $2}'" % interface
    link = shell_cmd(cmd, need_out=True)[1].strip().lower()

    return True if link == "yes" else False

def get_vip(interface):
    cmd = "ip addr show %s|grep 'scope global secondary %s'" % (interface, interface)
    ret, output = shell_cmd(cmd, need_out=True)

    if ret == 0:
        return output.split("inet")[1].strip().split(" ")[0].split("/")[0]
    else:
        return

def get_disk_info_from_cfg(disk_name, value):
    logger.debug("into get_disk_info_from_cfg get %s %s" % (disk_name, value))
    result = ''
    disk_find = 0
    fsize = 0
    if os.path.exists(STORAGE_CONF):
        fsize = os.path.getsize(STORAGE_CONF)
    if fsize <= 0:
        logger.error('the STORAGE_CONF size is 0')
        return result
    try:
        with open(STORAGE_CONF, 'r') as f:
            logger.debug("open STORAGE_CONF ok %s" % fsize)
            for line in f.readlines():
                curline = line.strip().split(' ')
                if curline[0] == 'dir:' and curline[1] == disk_name:
                    disk_find = 1
                if disk_find and curline[0] == value:
                    result = curline[1]
                    disk_find = 0
                    break
        logger.debug("json data disk_dir:%s " % result)
    except Exception as e:
        logger.error("get_disk_info_from_cfg error :%s " % str(e))

    return result

def get_disk_size(mount_dir):
    # 此方法有问题，如果没有挂载则无法获取正确的磁盘大小
    size = 0
    cmd = "df -Plh %s | tail -n 1" % mount_dir
    ret, output = shell_cmd(cmd, need_out=True)

    if ret != 0:
        logger.error("the dir: %s is not exist" % mount_dir)
    else:
        output = output.strip().split()
        size = int(output[1].strip("G"))

    return size

def get_block_size(block_dev):
    """
    获取分区或磁盘大小
    """
    cmd = "lsblk %s --output SIZE | grep -v SIZE" % block_dev
    _, output = shell_cmd(cmd, need_out=True)

    return output.strip()

def is_large_disk(disk_size):
    size = disk_size[:-1]
    unit = disk_size[-1:]

    if unit == "T" or (int(size) > 500 and unit == "G"):
        return True
    else:
        return False

def is_disk_type_same(disk_dir, disk_type):
    cmd = "df -Plh %s | tail -n 1" % disk_dir
    ret, output = shell_cmd(cmd, need_out=True)

    if ret != 0:
        logger.error("the dir: %s is not exist" % disk_dir)
    else:
        block_dev = output.strip().split()[0]
        cmd = "lsblk %s | tail -n 1" % block_dev
        _, output = shell_cmd(cmd, need_out=True)
        ttype = output.strip().split()[5]
        return True if ttype == disk_type else False

    return False

# TODO(wzy): 不准确
def is_cache_enabled(disk_dir):
    cmd = "df -Plh %s | tail -n 1" % disk_dir
    ret, output = shell_cmd(cmd, need_out=True)

    if ret != 0:
        logger.error("the dir: %s is not exist" % disk_dir)
    else:
        output = output = output.strip().split()
        return True if "cache" in output[0] else False

    return False

def is_disk_size_same(size1, size2):
    if abs(size1 - size2) > DISK_SIZE_LIMIT:
        return False

    return True

def is_content_supported(disk_name, remote_content):
    disk_content = get_disk_info_from_cfg(disk_name, "content")
    if disk_content == "":
        logger.error("can not get path from storage.cfg")
        return False
    else:
        contents = disk_content.strip().split(",")
        remote_content = remote_content.strip().split(",")
        if "idv" not in contents:
            return False
        else:
            if disk_name == "local":
                # local要保证内容是一致的
                contents.sort()
                remote_content.sort()
                return True if contents == remote_content else False
            if len(contents) > 1:
                # 其他只能是idv镜像
                return False
            return True

def log_enter_exit(func):
    @wraps(func)
    def log_content(*args, **kargs):
        logger.info("enter function(%s)" % (func.__name__))
        result = func(*args, **kargs)
        logger.info("exit function(%s) status(%s)" % (func.__name__, result))
        return result
    return log_content

def set_timer(interval, func_name=None):
    def _timer(func):
        @wraps(func)
        def __timer(*args, **kargs):
            begin_hour = time.localtime(time.time()).tm_min
            logger.info("func:%s(%s), is run" % (func.__name__, func_name))

            while True:
                func(*args, **kargs)

                # every hour print once
                current_hour = time.localtime(time.time()).tm_min

                if begin_hour != current_hour:
                    logger.info("func:%s(%s), is run" % (func.__name__, func_name))
                    begin_hour = current_hour

                time.sleep(interval)
        return __timer
    return _timer
