# -*- coding: utf-8 -*-
#
# Created on 2020年06月01日
#
# @author: wzy
#

import sys
sys.path.append('gen-py')

from argparse import ArgumentParser

from idv_ha import idv_ha
from idv_ha.ttypes import DiskInfo, NetInfo, DrbdInfo

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.Thrift import TException

from constant import SERVER_PORT, THRIFT_TIMEOUT
from log import logger

def get_client(host="localhost", port=SERVER_PORT, timeout=THRIFT_TIMEOUT):
    transport = TSocket.TSocket(host, port) 
    transport.setTimeout(timeout)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = idv_ha.Client(protocol)
    return client, transport

def switch_master():
    logger.info("client exec switch master")
    try:
        client, transport = get_client()
        transport.open()
        client.switch_master()
    except (TException, Exception) as e:
        logger.exception("client %s", e)
    finally:
        logger.info("client transpot close")
        transport.close()

def switch_backup():
    logger.info("client exec switch backup")
    try:
        client, transport = get_client()
        transport.open()
        client.switch_backup()
    except (TException, Exception) as e:
        logger.exception("client %s", e)
    finally:
        logger.info("client transpot close")
        transport.close()

def drbd_health_check():
    logger.info("client exec drbd health check")
    try:
        client, transport = get_client()
        transport.open()
        res = client.drbd_health_check()
    except (TException, Exception) as e:
        logger.exception("client %s", e)
    finally:
        logger.info("client transpot close")
        transport.close()
        return res

parser = ArgumentParser(description="IDV High Availability Client")
subparsers = parser.add_subparsers(help="sub-command help")

# 切换成主服务器
parser_switch_master = subparsers.add_parser("switch_master", help="switch node into master")
parser_switch_master.set_defaults(func=switch_master)

# 切换成备服务器
parser_switch_backup = subparsers.add_parser("switch_backup", help="switch node into backup")
parser_switch_backup.set_defaults(func=switch_backup)

# drbd健康检测
parser_drbd_health_check = subparsers.add_parser("drbd_health_check", help="check drbd health status")
parser_drbd_health_check.set_defaults(func=drbd_health_check)

args = parser.parse_args()

ret = args.func()

if ret:
    print("exit with code %d" % ret)
    exit(ret)
else:
    print("exit normal")
    exit(0)
