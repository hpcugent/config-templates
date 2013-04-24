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
##
## support reading quattor json profiles directly and using the contents from metaconfig component
##   metaconfig path is 4th argumnet, use empty string as 3rd if needed
##  ./json2tt.pl /path/to/quattor/build/xml/node.domain.json.gz metaconfig/snmp/snmp.tt '' /etc/snmp/snmp.conf
##

sub escape($) {
    my $str = shift;
    $str =~ s/([^a-zA-Z0-9])/sprintf("_%lx", ord($1))/eg;
    # special case: 1st character cannot be a digit
    $str =~ s/^([0-9])/sprintf("_%lx", ord($1))/e;
    return($str);
}

my $fn = $ARGV[0];
my $fh;
if ($fn =~ /\.gz$/) {
    open($fh, "gunzip -c $fn |");
} else {
    open($fh, '<',$fn);
}
my $json = decode_json(join("", <$fh>));
close($fh);

if ( @ARGV >= 4 ) {
    $json = $json->{software}->{components}->{metaconfig}->{services}->{escape($ARGV[3])}->{contents};
};

my $tpl = Template->new(STRICT => $ARGV[2]);
$tpl->process($ARGV[1], $json) or die "WTF: ", $tpl->error();
