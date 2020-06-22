# -*- coding: utf-8 -*-
#
# Created on 2020年06月09日
#
# @author: wzy
#

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
