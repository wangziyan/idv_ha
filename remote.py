# -*- coding: utf-8 -*-
#
# Created on 2020年06月17日
#
# @author: wzy
#
import sys
sys.path.append('gen-py')

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.Thrift import TException

from constant import SERVER_PORT, THRIFT_ERROR
from idv_ha import Ha
from log import logger

class Remote(object):
    @classmethod
    def ready_to_sync(cls, addr, res_num):
        logger.info("remote exec ready_to_sync")
        result = None
        try:
            socket = TSocket.TSocket(addr, SERVER_PORT)
            transport = TTransport.TBufferedTransport(socket)
            protocol = TBinaryProtocol.TBinaryProtocol(transport)
            client = Ha.Client(protocol)
            transport.open()
            result = client.ready_to_sync(res_num)
            transport.close()
        except (TException, Exception) as e:
            logger.exception("remote client %s", e)
            result = THRIFT_ERROR

        return result

    @classmethod
    def remote_setup(cls, net, drbd, is_master, is_force):
        logger.info("exec remote setup")
        result = None
        try:
            socket = TSocket.TSocket(net.backup_ip, SERVER_PORT)
            socket.setTimeout(60000)
            transport = TTransport.TBufferedTransport(socket)
            protocol = TBinaryProtocol.TBinaryProtocol(transport)
            client = Ha.Client(protocol)
            transport.open()
            result = client.setup(net, drbd, is_master, is_force)
            transport.close()
        except (TException, Exception) as e:
            logger.exception("remote client %s", e)
            result = THRIFT_ERROR

        return result

    @classmethod
    def remote_remove(cls, addr, is_master):
        logger.info("exec remote remove")
        result = None
        try:
            socket = TSocket.TSocket(addr, SERVER_PORT)
            transport = TTransport.TBufferedTransport(socket)
            protocol = TBinaryProtocol.TBinaryProtocol(transport)
            client = Ha.Client(protocol)
            transport.open()
            result = client.remove(is_master)
            transport.close()
        except (TException, Exception) as e:
            logger.exception("remote client %s", e)
            result = THRIFT_ERROR

        return result
