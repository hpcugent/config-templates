template metaconfig/kerberos/krb5_conf;

include 'metaconfig/kerberos/schema';

bind "/software/components/metaconfig/services/{/etc/krb5.conf}/contents" = krb5_conf_file;
