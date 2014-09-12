object template config;

include 'metaconfig/device-mapper/config';

prefix "/software/components/metaconfig/services/{/etc/multipath.conf}/contents/defaults";
'path_checker' = 'hp_sw';
'prio' = 'hp_sw';
'user_friendly_names' = true;
'path_grouping_policy' = 'group_by_prio';
'failback' = 'immediate';
'detect_prio' = true;
'path_selector' = list('round-robin', 0); 
'features' = list(1, list('queue_if_no_path'));

prefix "/software/components/metaconfig/services/{/etc/multipath.conf}/contents";
"multipaths/0/wwid" = "3600c0ff00012c51bacb68a4e01000000";
"multipaths/0/alias" = "p21as1ScrD";
"multipaths/1/wwid" = "3600c0ff00012c51b92b68a4e01000000";
"multipaths/1/alias" = "p21as1ScrM";
"multipaths/2/wwid" = "3600c0ff00012c51b9eb68a4e01000000";
"multipaths/2/alias" = "p21as1SofD";
"multipaths/3/wwid" = "3600c0ff00012c51baab68a4e01000000";
"multipaths/3/alias" = "p21as1SofM";
"multipaths/4/wwid" = "3600c0ff00012c51bb8b68a4e01000000";
"multipaths/4/alias" = "p21as2ScrD";
"multipaths/5/wwid" = "3600c0ff00012c51bc4b68a4e01000000";
"multipaths/5/alias" = "p21as3ScrD";
"multipaths/6/wwid" = "3600c0ff00012c51bd0b68a4e01000000";
"multipaths/6/alias" = "p21as4ScrD";
"multipaths/7/wwid" = "3600c0ff00012c329acb68a4e01000000";
"multipaths/7/alias" = "p21bs1ScrD";
"multipaths/8/wwid" = "3600c0ff00012c329b8b68a4e01000000";
"multipaths/8/alias" = "p21bs2ScrD";
"multipaths/9/wwid" = "3600c0ff00012c329c4b68a4e01000000";
"multipaths/9/alias" = "p21bs3ScrD";
"multipaths/10/wwid" = "3600c0ff00012c32992b68a4e01000000";
"multipaths/10/alias" = "p21bs3ScrM";
"multipaths/11/wwid" = "3600c0ff00012c3299eb68a4e01000000";
"multipaths/11/alias" = "p21bs3SofD";
"multipaths/12/wwid" = "3600c0ff00012c329aab68a4e01000000";
"multipaths/12/alias" = "p21bs3SofM";
"multipaths/13/wwid" = "3600c0ff00012c329d0b68a4e01000000";
"multipaths/13/alias" = "p21bs4ScrD";

