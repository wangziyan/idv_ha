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

from constant import SERVER_PORT
from idv_ha import idv_ha
from log import logger

class Remote(object):
    @classmethod
    def ready_to_sync(cls, addr, res_num):
        logger.info("remote exec ready_to_sync")
        result = 0
        try:
            socket = TSocket.TSocket(addr, SERVER_PORT)
            transport = TTransport.TBufferedTransport(socket)
            protocol = TBinaryProtocol.TBinaryProtocol(transport)
            client = idv_ha.Client(protocol)
            transport.open()
            result = client.ready_to_sync(res_num)
        except (TException, Exception) as e:
            result = 1
            logger.exception("client %s", e)
        finally:
            logger.info("client transpot close")
            transport.close()
            return result
