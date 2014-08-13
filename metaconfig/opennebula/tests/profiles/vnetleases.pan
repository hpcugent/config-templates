object template vnetleases;

include 'vm';

# copy for unittests
"/metaconfig/module" = "opennebula/vnetleases";
"/metaconfig/contents/system" = value("/system");
"/metaconfig/contents/hardware" = value("/hardware");
