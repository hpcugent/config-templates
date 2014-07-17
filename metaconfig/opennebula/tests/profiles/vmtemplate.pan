object template vmtemplate;

include 'vm';

# copy for unittests
"/metaconfig/module" = "opennebula/vmtemplate";
"/metaconfig/contents/system" = value("/system");
"/metaconfig/contents/hardware" = value("/hardware");
