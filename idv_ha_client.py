# -*- coding: utf-8 -*-
#
# Created on 2020年06月01日
#
# @author: wzy
#

from argparse import ArgumentParser

def switch_master():
    print("exec switch master")

def switch_backup():
    print("exec switch backup")

parser = ArgumentParser(description="IDV High Availability Client")
subparsers = parser.add_subparsers(help="sub-command help")

parser_switch_master = subparsers.add_parser("switch_master", help="switch node into master")
parser_switch_master.set_defaults(func=switch_master)

parser_switch_backup = subparsers.add_parser("switch_backup", help="switch node into backup")
parser_switch_backup.set_defaults(func=switch_backup)

args = parser.parse_args()

if "check" not in args.func.__name__:
    print(args)

ret = args.func()

if ret:
    exit(ret)
else:
    exit(0)

