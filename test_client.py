# -*- coding: utf-8 -*-
#
# Created on 2020年05月27日
#
# @author: wzy
#
import sys
sys.path.append('gen-py')

from threading import Thread
from time import sleep

from idv_ha import idv_ha
from idv_ha.ttypes import DiskInfo, NetInfo, DrbdInfo

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

def get_client():
    transport = TSocket.TSocket(host='localhost', port=9011)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = idv_ha.Client(protocol)
    return transport, client

def test_thrift_data():
    print("exec drbd_health_check")
    transport, client = get_client()
    transport.open()
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

def test_drbd_health_check():
    print("exec test_drbd_health_check")
    transport, client = get_client()
    transport.open()
    client.drbd_health_check()
    transport.close()

def test_multi_thread():
    '''
    通过多线程测试，没发现有什么问题
    '''
    count = 0
    while count < 50:
        thread = Thread(target=test_drbd_health_check)
        thread.start()
        count += 1

def main():
    # test_thrift_data()
    test_multi_thread()

if __name__ == '__main__':
    main()
