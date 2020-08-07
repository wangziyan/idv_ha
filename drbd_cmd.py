# -*- coding: utf-8 -*-
#
# Created on 2020年06月09日
#
# @author: wzy
#

import re
from drbd_const import DrbdRole
from tools import shell_cmd

def drbd_base_resource_str():
    res_str = '''resource %s {
    device     /dev/drbd%s;
    disk       %s;
    meta-disk  internal;
    on %s {
        address   %s:%s;
    }
    on %s {
        address   %s:%s;
    }
}'''

    return res_str

def get_cstate():
    cstate = []
    ret, output = shell_cmd("drbdadm cstate all", need_out=True)

    if "\n" in output:
        cstate = output.split("\n")
    else:
        cstate = [output]

    return cstate

def get_dstate():
    dstate = []
    ret, output = shell_cmd("drbdadm dstate all", need_out=True)

    if "\n" in output:
        output = output.split("\n")

        for state in output:
            dstate.append(state.split("/")[0])
    else:
        dstate = [output]

    return dstate

def get_local_role():
    role = []
    ret, output = shell_cmd("drbdadm role all", need_out=True)

    if ret == 0:
        if "\n" in output:
            role = output.split("\n")
        else:
            role = [output]

    return role

def get_remote_role():
    role = []
    ret, output = shell_cmd("drbdsetup status all --verbose", need_out=True)

    if ret == 0:
        role = re.findall(r"role:(.+?) congested:", output)

    return role

def get_drbd_role():
    # Drbd所有资源的状态必须要保持一致
    role = get_local_role()
    role = list(set(role))

    if len(role) != 1:
        return DrbdRole.error

    if role[0] == DrbdRole.secondary:
        return DrbdRole.secondary

    if role[0] == DrbdRole.primary:
        return DrbdRole.primary

    return DrbdRole.error
