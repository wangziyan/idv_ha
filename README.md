# ovp-idv-ha
ha implementation with drbd and keepalived

# Thrift
thrift使用的版本为0.9.1
修改idv_ha.thrift后，需要重新生成对应的python及perl文件，命令如下

thrift-0.9.1.exe --gen py idv_ha.thrift
thrift-0.9.1.exe --gen perl idv_ha.thrift

# keepalived
keepalived使用的版本为2.0.19
keepalived.conf是keepalived的配置文件，详细说明查看官网
https://www.keepalived.org/manpage.html

# DRBD
kmod-drbd使用的9.0.24版本
drbd-utils使用的9.13.1版本
说明文档：
https://www.linbit.com/drbd-user-guide/drbd-guide-9_0-cn/

# systemd配置文件
ovp-idv-ha.service

# rpm打包脚本
ovp-idv-ha.spec




