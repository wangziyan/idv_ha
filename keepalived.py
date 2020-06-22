# -*- coding: utf-8 -*-
#
# Created on 2020年06月22日
#
# @author: wzy
#

from tools import get_vip, check_net
from utility import get_keepalived_conf
class KeepalivedState(object):
    master = "MASTER"
    backup = "BACKUP"
    fault = "FAULT"

def get_keepalived_state():
    conf = get_keepalived_conf()

    if conf:
        virtual_ip = conf.get("virtual_ip")
        interface = conf.get("interface")
        ip = get_vip(interface)

        if not check_net(interface):
            return KeepalivedState.fault
        if ip == virtual_ip:
            return KeepalivedState.master
        else:
            return KeepalivedState.backup
    else:
        return KeepalivedState.fault
