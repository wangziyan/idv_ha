// 磁盘信息
struct DiskInfo{
    1:string storage_name;  // 存储池名称
    2:string volume_name;   // 块设备名称
    3:i32 size;             // 磁盘大小
    4:string type;          // 磁盘类型(是否为lvm)
    5:string content;       // 磁盘内容的类型(ISO镜像,VDI模板,VDI镜像,IDV镜像,备份文件)
}

// 网络信息
struct NetInfo{
    1:string vip;   // 虚拟ip
    2:string rid;   // 虚拟路由id
    3:string m_ip;  // 主节点ip
    4:string b_ip;  // 备节点ip
}

// drbd信息
struct DrbdInfo{
    1:i32 res_num;  // 资源编号
    2:i32 port_num; // 端口号
    3:string node;  // 主机名
    4:string block; // 备份块设备名
}

// 节点信息
struct NodeInfo{
    1:string hostname;
}

service idv_ha{
    // 对端是否具备建立IDV_HA的条件
    map<string, i32> idv_ha_prepared(1:list<DiskInfo> disk)
    // 对端是否已经与其他节点建立了IDV_HA
    bool idv_ha_created_with_others(1:string ip1, 2:string ip2)

    // 建立idv高可用服务
    i32 setup_idv_ha(1:NetInfo net, 2:DrbdInfo drbd)
    // 修改idv高可用服务
    i32 amend_idv_ha(1:NetInfo net)
    // 删除idv高可用服务
    i32 remove_idv_ha()

    // 备节点汇报磁盘错误信息
    i32 report_disk_error_info(1:list<DiskInfo> disk)

    // drbd健康监测
    i32 drbd_health_check()
    // idv服务监测
    i32 idv_service_check()
    // 网络健康检测
    i32 net_health_check()

    // 切换为主节点
    void switch_master()
    // 切换为备节点
    void switch_backup()
    // 切换错误状态
    void switch_faults()
}
