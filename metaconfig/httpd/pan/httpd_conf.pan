unique template metaconfig/httpd/httpd_conf;

include 'metaconfig/httpd/schema';

bind "/software/components/metaconfig/services/{/etc/httpd/conf/httpd.conf}/contents" = httpd_global;

prefix "/software/components/metaconfig/services/{/etc/httpd/conf/httpd.conf}";
"module" = "httpd/httpd_conf";
"daemon/0" = "httpd";

variable HTTPD_OS_FLAVOUR ?= 'el6';

"/software/components/metaconfig/services/{/etc/httpd/conf/httpd.conf}/contents" = create(format('common/httpd/struct/httpd_conf_%s', HTTPD_OS_FLAVOUR));
