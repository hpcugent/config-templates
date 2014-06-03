object template simple-client;

"/metaconfig/module" = "client";

prefix "/metaconfig/contents";
"logging" = nlist();
"libdefaults/default_realm" = 'KDC_REALM';
"realms" = nlist(
    'KDC_REALM', nlist(
        "kdc", 'KDC_SERVER',
        "admin_server", 'KDC_SERVER'
        ));
"domain_realms" = nlist('DEFAULT_DOMAIN', 'KDC_REALM');
