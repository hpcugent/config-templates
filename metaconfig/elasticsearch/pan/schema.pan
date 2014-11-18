declaration template metaconfig/elasticsearch/schema;

type es_cluster = {
    "name" ? string
};

type es_node = {
    "master" ? boolean
    "name" ? string
    "rack" ? string
    "data" ? boolean
};

type es_index_search = {
    "showlog" ? string{}
};


type es_translog = {
    "flush_threshold_ops" : long = 5000
};

type es_index = {
    "number_of_shards" ? long(0..)
    "number_of_replicas" ? long(0..)
    "search" ? es_index_search
    "refresh" ? long(0..)
    "translog" ? es_translog
};

type es_recovery = {
    "max_size_per_sec" : long = 0
    "concurrent_streams" : long = 5
};

type es_memory = {
    "index_buffer_size" : string with match(SELF, '^\d+%+')
};

type es_indices = {
    "recovery" ? es_recovery
    "memory" ? es_memory
};

type es_gw = {
    "type" : string = "local"
    "fs" ? string
    "recover_after_nodes" ? long
    "recover_after_time" ? long
} with (SELF["type"] == "local" || (SELF["type"] == "fs" && exists(SELF["fs"])));

type es_network = {
    "host" ? type_hostname
    "bind_host" ? type_hostname
    "publish_host" ? type_hostname
};

type es_monitoring = {
    "enabled" : boolean = false
};

type es_thread_search = {
    "type" : string with match(SELF, "^(fixed|cached|blocking)$")
    "size" : long(0..)
    "min" ? long
    "queue_size" ? long(0..)
    "reject_policy" ? string with match(SELF, "^(caller|abort)$")
};

@{
Thread pool management.  See
http://www.elasticsearch.org/guide/reference/modules/threadpool/
@}
type es_threadpool = {
    "search" : es_thread_search
    "index" : es_thread_search
    "get" ? es_thread_search
    "bulk"  ? es_thread_search
    "warmer" ? es_thread_search
    "refresh" ? es_thread_search

};

type es_bootstrap = {
    "mlockall" ? boolean
};

type es_transport = {
    "host" ? type_hostname
};

type type_elasticsearch = {
    "node" ? es_node
    "index" ? es_index
    "gateway" ? es_gw
    "indices" ? es_indices
    "network" : es_network = nlist("host", "localhost")
    "monitor.jvm" : es_monitoring = nlist()
    "threadpool" ? es_threadpool
    "bootstrap" ? es_bootstrap
    "cluster" ? es_cluster
    "transport" ? es_transport
};

type es_sysconfig = {
    "ES_USER" : string = "elasticsearch"
    "ES_HOME" : string = "/usr/share/elasticsearch"

    "LOG_DIR" : string = "/var/log/elasticsearch"
    "DATA_DIR" : string = "/var/lib/elasticsearch"
    "WORK_DIR" : string = "/tmp/elasticsearch"
    "CONF_DIR" : string = "/etc/elasticsearch"
    "CONF_FILE" : string = "/etc/elasticsearch/elasticsearch.yml"

    "ES_INCLUDE" ? string 
    "ES_HEAP_SIZE" : string = "2g"
    "ES_HEAP_NEWSIZE" ? string 
    "ES_DIRECT_SIZE" ? string
    "ES_JAVA_OPTS" ? string
    "ES_CLASSPATH" ? string
    "MAX_OPEN_FILES" : long(1..) = 65535
    "MAX_LOCKED_MEMORY" ? string # eg unlimited

    "JAVA_HOME" ? string
};
