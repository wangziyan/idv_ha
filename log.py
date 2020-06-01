# -*- coding: utf-8 -*-
#
# Created on 2020年05月28日
#
# @author: wzy
#

import os
import logging
import logging.handlers

from constant import AVDS_LOG_PATH, IDV_HA_LOG_PATH

LOG_LEVEL = "DEBUG"


def init_logger(name, level, f=None):
    LEVEL = getattr(logging, level.upper(), None)
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(LEVEL)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if f:
        fh = logging.handlers.RotatingFileHandler(f, maxBytes=1024*1024*50, backupCount=5)
        fh.setLevel(LEVEL)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    else:
        sh = logging.StreamHandler()
        sh.setLevel(LEVEL)
        sh.setFormatter(formatter)
        logger.addHandler(sh)
    return logger


def log_init():
    if not os.path.exists(AVDS_LOG_PATH):
        os.makedirs(AVDS_LOG_PATH)
    init_logger('idv_ha', LOG_LEVEL, IDV_HA_LOG_PATH)
    return logging.getLogger("idv_ha")


logger = log_init()
