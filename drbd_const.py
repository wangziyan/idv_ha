# -*- coding: utf-8 -*-
#
# Created on 2020年06月04日
#
# @author: wzy
#
class DrbdState(object):
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
    d_unknown = "DUnknown"

class DrbdConnState(object):
    connected = "Connected"
    stand_alone = "StandAlone"
    connecting = "Connecting"
    unknown = "unknown"

class DrbdCopyState(object):
    off = "Off"
    established = "Established"
    sync_source = "SyncSource"
    sync_target = "SyncTarget"
