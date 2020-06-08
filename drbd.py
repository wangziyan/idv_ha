# -*- coding: utf-8 -*-
#
# Created on 2020年05月28日
#
# @author: wzy
#
from Queue import Queue
from threading import Thread, Lock

from common import singleton
from log import logger

@singleton
class Drbd(object):
    def __init__(self):
        self.__queue = Queue()
        self.__lock = Lock()
        self.__task_run = False
        self.start()

    def __run(self):
        while True:
            work = None
            while True:
                work = self.__queue.get()
                if self.__queue.empty():
                    break
                self.__queue.task_done()
                logger.info("drop " + work.__name__)
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
        # with self.__lock:
        self.__queue.put(self.__switch_master)

    def switch_backup(self):
        # with self.__lock:
        self.__queue.put(self.__switch_backup)

    def switch_falut(self):
        # with self.__lock:
        self.__queue.put(self.__switch_fault)

    def start(self):
        try:
            thread = Thread(target=self.__run)
            thread.setDaemon(True)
            thread.start()
        except Exception as ex:
            logger.error(ex.message)
