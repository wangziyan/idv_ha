// 磁盘信息
struct DiskInfo{
    1:string storage_name;  // 存储池名称
    2:string volume_name;   // 块设备名称
    3:i32 size;             // 磁盘大小(单位是G)
    4:string type;          // 磁盘类型(是否为lvm)
    5:string content;       // 磁盘内容的类型(ISO镜像,VDI模板,VDI镜像,IDV镜像,备份文件)
}

// 网络信息
struct NetInfo{
    1:string vip;        // 虚拟ip
    2:string rid;        // 虚拟路由id
    3:string master_ip;  // 主节点ip
    4:string backup_ip;  // 备节点ip
}

// drbd信息
struct DrbdInfo{
    1:i32 res_num;                  // 资源编号 资源和端口号都是对应的,端口是不是多余的？
    2:i32 port_num;                 // 端口号
    3:string primary_host;          // 主节点主机名
    4:string secondary_host;        // 备节点主机名
    5:string block_dev;             // 底层块设备名
    6:optional bool is_external;    // 是否为外部元数据
    7:optional string metedata;     // 外部元数据
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
    i32 setup_idv_ha(1:NetInfo net, 2:DrbdInfo drbd, 3:bool is_master, 4:optional bool is_force)
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

###########################两个server之间使用的方法##################################
    // 主节点请求备节点是否准备好进行同步
    bool ready_to_sync(i32 res_num)
}
