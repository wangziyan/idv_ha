# -*- coding: utf-8 -*-
#
# Created on 2020年05月27日
#
# @author: wzy
#

import os
import sys
import signal
from threading import Thread
from time import sleep
from subprocess import call as sub_call
sys.path.append('gen-py')

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from idv_ha import idv_ha

from constant import SERVER_PORT
from tools import get_system_uptime, shell_cmd
from utility import is_idv_ha_enabled, is_master_node
from ha_handler import ProcessHandler
from log import logger

def start_service():
    uptime = get_system_uptime()
    # 如果不是主节点，keepalived启动时间推迟
    if not is_master_node() and uptime < 120:
        sleep(120)
    sleep(5)

    logger.info("start service keepalived......")
    cmd = "systemctl start keepalived"
    ret = shell_cmd(cmd)
    if ret != 0:
        logger.error("start service keepalived failed")

class HAServer(object):
    def __init__(self, host="0.0.0.0", port=SERVER_PORT):
        self.host = host
        self.port = port

    def _handle_signal(self, signum, frame):
        print("exit by ctrl c")
        os._exit(0)

    def start(self):
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

        handler = ProcessHandler()
        processor = idv_ha.Processor(handler)
        transport = TSocket.TServerSocket(self.host, self.port)
        tfactory = TTransport.TBufferedTransportFactory()
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()

        logger.info("server host: %s start listen port: %d" % (self.host, self.port))
        server = TServer.TThreadPoolServer(processor, transport, tfactory, pfactory)
        server.setNumThreads(15)

        try:
            # TODO(wzy): 开机的时候如果没有启用idv ha，就不会启动服务，如果后面需要开启idv ha 需要重新启动服务?
            if is_idv_ha_enabled():
                logger.info("server idv ha is enable")
                services = Thread(target=start_service)
                services.setDaemon(True)
                services.start()
            else:
                logger.info("server idv ha is disabled")
            server.serve()
        except Exception as e:
            logger.error("server error: %s" % e.message)
            logger.error("stop drbd and keepalived service")
            sub_call("systemctl stop drbd", close_fds=True, shell=True)
            sub_call("systemctl stop keepalived", close_fds=True, shell=True)
            os._exit(e.code)

def main():
    idv_ha_server = HAServer()
    idv_ha_server.start()

if __name__ == '__main__':
    main()
