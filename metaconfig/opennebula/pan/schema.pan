declaration template metaconfig/opennebula/schema;

type uuid = string with match(SELF,'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}');

type ip_ipv4 = string with match(SELF,'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})');

type opennebula_datastore = {
    "name" : string 
};

type opennebula_database = {
    "backend" : string 
    "server" : string
    "port" : long(0..)
    "user" : string
    "passwd" : string
    "db_name" : string
};

type opennebula_log = {
    "system" : string = 'file'
    "debug_level" : long = 3
} = nlist();

type opennebula_datastore_ceph = {
    include opennebula_datastore
    "bridge_list" : string[]
    "ceph_host" : string[]
    "ceph_secret" : uuid 
    "ceph_user" : string
    "datastore_capacity_check" : boolean = true
    "disk_type" : string = 'RBD'
    "ds_mad" : string = 'ceph'
    "pool_name" : string
    "tm_mad" : string = 'ceph'
    "type" : string = 'IMAGE_DS'
};



type opennebula_vnet = {
    "name" : string
    "type" : string  = 'FIXED'
    "bridge" : string
    "gateway" : ip_ipv4 
    "dns" : ip_ipv4
    "network_mask" : ip_ipv4
};


type opennebula_remoteconf_ceph = {
    "pool_name" : string
    "host" : string
    "ceph_user" ? string
    "staging_dir" ? string = '/var/tmp' with match(SELF,'[^/]+/?$')
    "rbd_format" ? long(2)
    "qemu_img_convert_args" ? string
};

type opennebula_oned = {
    "database" : opennebula_database
    "default_device_prefix" ? string = 'hd'
    "onegate_endpoint" ? string
    "monitoring_interval" : long = 60
    "monitoring_threads" : long = 50
    "scripts_remote_dir" : string = '/var/tmp/one'
    "log" : opennebula_log
    "port" : long = 2633
    "vnc_base_port" : long = 5900
    "network_size" : long = 254
    "mac_prefix" : string = '02:00'
    "datastore_capacity_check" : boolean = true
    "default_image_type" : string = 'OS'
    "default_cdrom_device_prefix" : string = 'hd'
    "session_expiration_time" : long = 900
    "default_umask" : long = 177
    "vm_restricted_attr" : string = 'CONTEXT/FILES'
#    "vm_restricted_attr" : string = 'NIC/MAC'
#    "vm_restricted_attr" : string = 'NIC/VLAN_ID'
#    "vm_restricted_attr" : string = 'NIC/BRIDGE'
    "image_restricted_attr" : string = 'SOURCE'
    "inherit_datastore_attr" : string = 'CEPH_HOST'
#    "inherit_datastore_attr" : string = 'CEPH_SECRET'
#    "inherit_datastore_attr" : string = 'CEPH_USER'
#    "inherit_datastore_attr" : string = 'RBD_FORMAT'
#    "inherit_datastore_attr" : string = 'GLUSTER_HOST'
#    "inherit_datastore_attr" : string = 'GLUSTER_VOLUME'
#    "inherit_vnet_attr" : string = 'VLAN_TAGGED_ID'
};
