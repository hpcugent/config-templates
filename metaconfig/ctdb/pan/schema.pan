declaration template metaconfig/ctdb/schema;

include 'pan/types';


function is_ctdb_pub_address = {
    parts = split(' ', ARGV[0]);
    if(is_network_name(parts[0]) && match(parts[1], ("^(eth[0-9]+|p[0-9]+p[0-9]+|em[0-9]+)$"))) {
        return(true);
    } else {
        error(format("%s is not a valid ctdb public address!", ARGV[0]));
        return(false);
    };
};

type ctdb_public_address = string with is_ctdb_pub_address(SELF);
type ctdb_public_addresses = ctdb_public_address[];

type ctdb_nodes = type_ip[];

type ctdb_service = {
'waitforgpfs'               ? string
'ulimit'                    ? long(0..)
'ctdb_debuglevel'           ? long(0..)
'ctdb_manages_nfs'          ? boolean
'ctdb_manages_samba'        ? boolean
'ctdb_nfs_skip_share_check' ? boolean
'ctdb_public_addresses'     ? string
'ctdb_recovery_lock'        : string
'ctdb_syslog'               ? boolean
'nfs_hostname'              ? type_fqdn
'nfs_server_mode'           ? string
'ctdb_nodes'                ? string
};

