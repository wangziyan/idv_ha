# idv_ha
ha implementation with drbd and keepalived

# Thrift
使用的版本为0.9.1
修改idv_ha.thrift后，需要重新生成对应的python及perl文件

thrift-0.9.1.exe --gen py idv_ha.thrift
thrift-0.9.1.exe --gen perl idv_ha.thrift

