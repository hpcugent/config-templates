declaration template metaconfig/kerberos/schema;

type krb5_logging = {
    "default" : string = "FILE:/var/log/krb5libs.log"
    "kdc" : string = "FILE:/var/log/krb5kdc.log"
    "admin_server" : string = "FILE:/var/log/kadmind.log"
};

type krb5_realm = {
    "kdc" : string
    "admin_server" : string
};

type krb5_libdefaults = {
    "default_realm" : string
    "dns_lookup_realm" : boolean = false
    "dns_lookup_kdc" : boolean = false
    # The lifetimes are specified in seconds
    "ticket_lifetime" : long = 24*60*60
    "renew_lifetime" : long = 7*24*60
    "forwardable" : boolean = true
    "default_keytab_name" : string = "FILE:/etc/krb5.keytab"
};

type krb5_conf_file = {
    "logging" : krb5_logging
    "libdefaults" : krb5_libdefaults
    "realms" : krb5_realm{}
    "domain_realms" : type_fqdn{}
};

