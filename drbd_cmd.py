# -*- coding: utf-8 -*-
#
# Created on 2020年06月09日
#
# @author: wzy
#

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
