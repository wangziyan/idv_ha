# -*- coding: utf-8 -*-
#
# Created on 2020年05月27日
#
# @author: wzy
#
import sys
sys.path.append('gen-py')

from idv_ha import idv_ha
from idv_ha.ttypes import DiskInfo, NetInfo, DrbdInfo

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

def main():
    transport = TSocket.TSocket(host='192.168.1.244', port=9011)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)

    client = idv_ha.Client(protocol)

    transport.open()

    print("exec drbd_health_check")
    client.drbd_health_check()

    disks = []

    disk1 = DiskInfo()
    disk1.storage_name = 'local'
    disk1.volume_name = '/dev/vg/lv_local'
    disk1.size = 380
    disk1.type = 'lvm'

    disk2 = DiskInfo()
    disk2.storage_name = 'sdc'
    disk2.volume_name = '/dev/vg/lv_sdc'
    disk2.size = 1000
    disk2.type = 'lvm'

    disks.append(disk1)
    disks.append(disk2)

    print("exec idv_ha_prepared")
    res = client.idv_ha_prepared(disks)
    for key, value in res.items():
        print("key is %s, value is %d") % (key, value)

    transport.close()


if __name__ == '__main__':
    main()
