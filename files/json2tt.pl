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
##   4th argument, use empty string as 3rd if needed
##   absolute path: metaconfig filename path
##      ./json2tt.pl /path/to/quattor/build/xml/node.domain.json.gz metaconfig/snmp/snmp.tt '' /etc/snmp/snmp.conf
##   relative path: path in tree
##      ./json2tt.pl /path/to/quattor/build/xml/node.domain.json.gz authconfig.sssd.tt '' software/components/authconfig/method/sssd


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
    if ($ARGV[3] =~ m/^\//) {
        # abs path for file in metaconfig
        $json = $json->{software}->{components}->{metaconfig}->{services}->{escape($ARGV[3])}->{contents};
    } else {
        # rel path, starting from root of tree
        my @paths = split('/', $ARGV[3]);
        foreach my $path (@paths) {
            $json = $json->{$path};
        }
    }
};


my $tpl = Template->new(STRICT => $ARGV[2]);
$tpl->process($ARGV[1], $json) or die "WTF: ", $tpl->error();
