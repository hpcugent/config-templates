declaration template metaconfig/opennebula/schema;

type uuid = string with match(SELF,'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}');

type ip_ipv4 = string with match(SELF,'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})');

type directory = string with match(SELF,'[^/]+/?$');

type opennebula_datastore = {
    "name" : string 
};

type opennebula_db = {
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

type opennebula_federation = {
    "mode" : string = 'STANDALONE'
    "zone_id" : long = 0
    "master_oned" : string = ''
} = nlist();

type opennebula_im_mad_collectd = {
    "executable" : string = 'collectd'
    "arguments" : string =  '-p 4124 -f 5 -t 50 -i 20'
} = nlist();

type opennebula_im_mad_kvm = {
    "executable" : string = 'one_im_ssh'
    "arguments" : string =  '-r 3 -t 15 kvm'
} = nlist();

type opennebula_im_mad_xen = {
    "executable" : string = 'one_im_ssh'
    "arguments" : string =  '-r 3 -t 15 xen4'
} = nlist();

type opennebula_im_mad = {
    "collectd" : opennebula_im_mad_collectd
    "kvm" : opennebula_im_mad_kvm
    "xen" : opennebula_im_mad_xen
} = nlist();

type opennebula_vm_mad_kvm = {
    #"name" : string = 'kvm'
    "executable" : string = 'one_vmm_exec'
    "arguments" : string = '-t 15 -r 0 kvm'
    "default" : string = 'vmm_exec/vmm_exec_kvm.conf'
    #"type" : string = 'kvm'
} = nlist();

type opennebula_vm_mad_xen = {
    #"name" : string = 'xen'
    "executable" : string = 'one_vmm_exec'
    "arguments" : string = '-t 15 -r 0 xen4'
    "default" : string = 'vmm_exec/vmm_exec_xen4.conf'
    #"type" : string = 'xen'       
} = nlist();

type opennebula_vm_mad = {
    "kvm" : opennebula_vm_mad_kvm
    "xen" : opennebula_vm_mad_xen
} = nlist();

type opennebula_tm_mad = {
    "executable" : string = 'one_tm'
    "arguments" : string = '-t 15 -d dummy,lvm,shared,fs_lvm,qcow2,ssh,vmfs,ceph'
} = nlist();

type opennebula_datastore_mad = {
    "executable" : string = 'one_datastore'
    "arguments" : string  = '-t 15 -d dummy,fs,vmfs,lvm,ceph'
} = nlist();

type opennebula_hm_mad = {
    "executable" : string = 'one_hm'
} = nlist();

type opennebula_auth_mad = {
    "executable" : string = 'one_auth_mad'
    "authn" : string = 'ssh,x509,ldap,server_cipher,server_x509'
} = nlist();

type opennebula_tm_mad_conf = {
    "name" : string = "dummy"
    "ln_target" : string = "NONE"
    "clone_target" : string = "SYSTEM"
    "shared" : boolean = true
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
    "staging_dir" ? directory = '/var/tmp'
    "rbd_format" ? long(2)
    "qemu_img_convert_args" ? string
};

type opennebula_oned = {
    "db" : opennebula_db
    "default_device_prefix" ? string = 'hd'
    "onegate_endpoint" ? string
    "monitoring_interval" : long = 60
    "monitoring_threads" : long = 50
    "scripts_remote_dir" : directory = '/var/tmp/one'
    "log" : opennebula_log
    "federation" : opennebula_federation
    "port" : long = 2633
    "vnc_base_port" : long = 5900
    "network_size" : long = 254
    "mac_prefix" : string = '02:00'
    "datastore_capacity_check" : boolean = true
    "default_image_type" : string = 'OS'
    "default_cdrom_device_prefix" : string = 'hd'
    "session_expiration_time" : long = 900
    "default_umask" : long = 177
    "im_mad" : opennebula_im_mad
    "vm_mad" : opennebula_vm_mad
#    "vm_mad_kvm" : opennebula_vm_mad_kvm
#    "vm_mad_xen" : opennebula_vm_mad_xen
    "tm_mad" : opennebula_tm_mad
    "datastore_mad" : opennebula_datastore_mad
    "hm_mad" : opennebula_hm_mad
    "auth_mad" : opennebula_auth_mad
    "tm_mad_conf" : opennebula_tm_mad_conf[] = list(nlist(), nlist("name", "somethingelse"))
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
