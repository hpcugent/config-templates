object template public_addresses;

include 'metaconfig/ctdb/public_addresses';

"/software/components/metaconfig/services/{/etc/ctdb/public_addresses}/contents/nodelist" = list(
    '172.24.14.195/16 eth0', '172.24.14.196/16 eth0', '172.24.14.197/16 eth0'
);
