# -*- coding: utf-8 -*-
#
# Created on 2020年06月04日
#
# @author: wzy
#

UPDATE_INTERVERL = 10

class DrbdState(object):
    """
    DRBD配置文件状态
    """
    SUCCESS = 0
    INIT_FAILED = 1
    FORMAT_FAILED = 2
    MOUNT_FAILED = 3
    UP_FAILED = 4
    INCONSISTENT = 5

class DrbdDiskState(object):
    up_to_date = "UpToDate"
    consistent = "Consistent"
    inconsistent = "Inconsistent"
    diskless = "Diskless"
    negotiating = "Negotiating"
    unknown = "DUnknown"

class DrbdConnState(object):
    connected = "Connected"
    stand_alone = "StandAlone"
    connecting = "Connecting"
    unknown = "unknown"

class DrbdRState(object):
    off = "Off"
    established = "Established"
    sync_source = "SyncSource"
    sync_target = "SyncTarget"
    unknown = "Unknown"

class DrbdRole(object):
    primary = "Primary"
    secondary = "Secondary"
    unknown = "Unknown"
    error = "Error"
    primary_no_secondary = "Primary/Unknown"
    secondary_no_primary = "Secondary/Unknown"

class SyncState(object):
    WAITING = -1    # 未开始
    SYNC = 1        # 正在同步
    FINISHED = 2    # 同步完成
    ALONE = 3       # 自己断开连接
    CONNECTING = 4  # 对方断开连接
