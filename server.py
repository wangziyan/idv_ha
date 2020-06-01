# -*- coding: utf-8 -*-
#
# Created on 2020年05月27日
#
# @author: wzy
#
import os
import sys
import signal
sys.path.append('gen-py')
# sys.path.insert(0, glob.glob('../../lib/py/build/lib*')[0])

from idv_ha import idv_ha
from idv_ha.ttypes import DiskInfo, NetInfo, DrbdInfo

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from constant import SERVER_PORT
from log import logger


class ProcessHandler:
    def __init__(self):
        self.log = {}

    def drbd_health_check(self):
        print("server recv drbd health check")
        return 0

    def idv_ha_prepared(self, disks):
        print("server recv idv ha prepared")
        result = {}

        for disc in disks:
            print("disk storage name is %s", disc.storage_name)
            print("disk volume name is %s", disc.volume_name)
            print("disk disk size is %d", disc.size)
            print("disk disk type is %s", disc.type)
            result[disc.storage_name] = True

        return result


def handle_exit(signum, frame):
    print("exit by ctrl c")
    logger.info("exit by ctrl c")
    os._exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    handler = ProcessHandler()
    processor = idv_ha.Processor(handler)
    transport = TSocket.TServerSocket(host='0.0.0.0', port=SERVER_PORT)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    logger.info("server start listen port %d", SERVER_PORT)
    server = TServer.TThreadPoolServer(processor, transport, tfactory, pfactory)
    server.setNumThreads(15)
    server.serve()
