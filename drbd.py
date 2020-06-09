# -*- coding: utf-8 -*-
#
# Created on 2020年05月28日
#
# @author: wzy
#
from Queue import Queue
from threading import Thread

from common import singleton
from utility import get_keepalived_conf
from log import logger

@singleton
class Drbd(object):
    def __init__(self):
        self.__queue = Queue()
        self.__task_run = False
        self.read_keepalived()
        self.start()

    def __run(self):
        """
        we only exec the latest work
        """
        while True:
            work = None
            while True:
                work = self.__queue.get()
                if self.__queue.empty():
                    break
                self.__queue.task_done()
                logger.info("multi task drop " + work.__name__)
            self.__task_run = True
            work()
            self.__task_run = False
            self.__queue.task_done()

    def __switch_master(self):
        print("enter __switch_master")
        print("do nothing")

    def __switch_backup(self):
        print("enter __switch_backup")
        print("do nothing")

    def __switch_fault(self):
        print("enter __switch_fault")
        print("do nothing")

    def switch_master(self):
        self.__queue.put(self.__switch_master)

    def switch_backup(self):
        self.__queue.put(self.__switch_backup)

    def switch_falut(self):
        self.__queue.put(self.__switch_fault)

    def start(self):
        try:
            thread = Thread(target=self.__run)
            thread.setDaemon(True)
            thread.start()
        except Exception as e:
            logger.error(e.message)

    def read_keepalived(self):
        keepavlied_conf = get_keepalived_conf()
        if keepavlied_conf:
            self.__ka_state = keepavlied_conf.get("state")
            self.__router_id = keepavlied_conf.get("router_id")
            self.__virtual_ip = keepavlied_conf.get("virtual_ip")
            self.__interface = keepavlied_conf.get("interface")
        else:
            print("no keepalvied conf")

    def __check_ha_cluster_state(self):
        pass

    def _check_state_of_idv_ha(self):
        try:
            thread = Thread(target=self.__check_ha_cluster_state)
            thread.start()
        except Exception as e:
            logger.exception(e.message)
