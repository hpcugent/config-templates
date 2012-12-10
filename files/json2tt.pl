#!/usr/bin/perl
use strict;
use warnings;
use JSON::XS;
use Template;

##
## Instructions
## yum install perl-Template-Toolkit -y
## cut and paste the portion of the json profile and save to a file
## ./json2tt.pl /path/to/file/with/json/snippet path/to/template.tt

open(my $fh, "<", $ARGV[0]);
my $json = decode_json(join("", <$fh>));
close($fh);
my $tpl = Template->new(STRICT => $ARGV[2]);
$tpl->process($ARGV[1], $json) or die "WTF: ", $tpl->error();
