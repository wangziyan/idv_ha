# -*- coding: utf-8 -*-
#
# Created on 2020年06月19日
#
# @author: wzy
#

from threading import Thread

from tools import set_timer

class TimerTask(object):
    def __init__(self, func, time):
        self.func = func
        self.time = time

        self.thread = Thread(target=self.run_timed_task)
        self.thread.setDaemon(True)
        self.thread.start()

    def run_timed_task(self):
        @set_timer(self.time, self.func)
        def __run_timed_task():
            self.func()

        __run_timed_task()
