unique template metaconfig/ganesha/config_v2;

variable GANESHA_SERVICE ?= 'nfs-ganesha';
variable CTDB_MANAGES_GANESHA ?= false;

include 'metaconfig/ganesha/schema_v2';

bind "/software/components/metaconfig/services/{/etc/ganesha/ganesha.nfsd.conf}/contents" = ganesha_v2_config;

prefix "/software/components/metaconfig/services/{/etc/ganesha/ganesha.nfsd.conf}";
"daemon" = {if (CTDB_MANAGES_GANESHA) { null } else { list(GANESHA_SERVICE) }};
"module" = "ganesha/2.2/main";

