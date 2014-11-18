unique template metaconfig/elasticsearch/config;

include 'metaconfig/elasticsearch/schema';

bind "/software/components/metaconfig/services/{/etc/elasticsearch/elasticsearch.yml}/contents" = type_elasticsearch;

prefix "/software/components/metaconfig/services/{/etc/elasticsearch/elasticsearch.yml}";
"daemon/0" = "elasticsearch";
"owner" = "root";
"group" = "root";
"mode" = 0644;
"module" = "yaml";

