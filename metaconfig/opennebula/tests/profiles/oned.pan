object template oned;

"/metaconfig/module" = "opennebula/oned";

prefix "/metaconfig/contents";

"database" = nlist(
           "backend", "mysql",
           "server", "localhost",
           "port", 0,
           "user", "oneadmin",
           "passwd", "my-fancy-pass",
           "db_name", "opennebula",
);

"default_device_prefix" = "vd";
"onegate_endpoint" = "http://localhost:5030";

