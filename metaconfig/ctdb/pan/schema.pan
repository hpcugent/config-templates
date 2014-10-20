declaration template metaconfig/ctdb/schema;

include 'pan/types';


function is_interface_device = {
    foreach(ifc;attr;value('/system/network/interfaces')) {
        if (attr['device'] == ARGV[0]){
            return(true);
        };
    };
    return(false);
};

@{ Checks for a valid ctdb public address @}
function is_ctdb_pub_address = {
    parts = split(' ', ARGV[0]);
    if(is_network_name(parts[0])) {
        if (exists(format("/system/network/interfaces/", parts[1])) || is_interface_device(parts[1]) ) {
                return(true);
        } else {
            error(format("%s is not specified in /system/network", parts[1]));
            return(false);
        }
    } else {
        error(format("%s is not a valid ctdb public address!", ARGV[0]));
        return(false);
    };
};


type ctdb_public_address = string with is_ctdb_pub_address(SELF);
type ctdb_public_addresses = ctdb_public_address[];

type ctdb_nodes = type_ip[];

@{ type for configuring the ctdb config file @}
type ctdb_service = {
    'ctdb_debuglevel'           ? long(0..)
    'ctdb_manages_nfs'          ? boolean
    'ctdb_manages_samba'        ? boolean
    'ctdb_nfs_skip_share_check' ? boolean
    'ctdb_nodes'                ? string
    'ctdb_public_addresses'     ? string
    'ctdb_recovery_lock'        : string
    'ctdb_syslog'               ? boolean
    'nfs_hostname'              ? type_fqdn
    'nfs_server_mode'           ? string
    'prologue'                  ? string    
};

