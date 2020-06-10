# -*- coding: utf-8 -*-
#
# Created on 2020年06月04日
#
# @author: wzy
#
import subprocess
import tempfile
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

def shell_command(cmd, need_out=False):
    returncode = 1
    output = ""
    try:
        if need_out:
            returncode = subprocess.check_output(cmd, close_fds=True, shell=True, stderr=subprocess.STDOUT)
        else:
            returncode = subprocess.check_call(cmd, close_fds=True, shell=True)
    except subprocess.CalledProcessError as e:
        output = e.output
        logger.exception("shell exec failed cmd:%s output:%s" % (e.cmd, output))
    finally:
        if need_out:
            return returncode, output
        else:
            return returncode

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
    link = shell_command(cmd, need_out=True)[1].strip().lower()
    return True if link == "yes" else False

def log_enter_exit(func):
    @wraps(func)
    def log_content(*args, **kargs):
        logger.info("enter function(%s)" % (func.__name__))
        result = func(*args, **kargs)
        logger.info("exit function(%s) status(%s)" % (func.__name__, result))
        return result
    return log_content
