# -*- coding: utf-8 -*-
#
# Created on 2020年05月28日
#
# @author: wzy
#


def singleton(cls):
    instances = {}

    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getinstance
