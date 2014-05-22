#!/usr/bin/perl
# LICENSE HEADER HERE

=pod

=head1 NAME

json2tt tool to convert json in to text using Template-Toolkit

=head1 OPTIONS

=over 4

=item --help
Shows the actual options.

=cut

BEGIN {
    # use perl libs in /usr/lib/perl
    push(@INC, '/usr/lib/perl');

}

package json2tt;

use CAF::Application;
use CAF::Reporter;

our @ISA= qw(CAF::Application CAF::Reporter);

#
# Public Methods/Functions for CAF
#
sub app_options {

    push(my @array,

        { NAME    => 'json=s',
          HELP    => 'path to file with the JSON input data (can be gzip compressed if it has extension .gz)',
          DEFAULT => undef },

        { NAME    => 'template=s',
          HELP    => 'path to the (base) template (precedence over metaconfigservice and unittest)',
          DEFAULT => undef },

        { NAME    => 'relative=s',
          HELP    => 'relative path in json file to use as content (no leading /; is applied after metaconfigservices or unittest)',
          DEFAULT => undef,  
        },

        { NAME    => 'metaconfigservice=s',
          HELP    => 'Get the relevant data from the quattor metaconfig service (i.e. use the module value as template, and use the contents as json data)',
          DEFAULT => undef },
            
        { NAME    => 'unittest',
          HELP    => 'Get the relevant data from the /metaconfig path (i.e. use the module value as template, and use the contents as json data)',
          DEFAULT => undef },

        { NAME    => 'includepath=s',
          HELP    => 'path to the use to include tt file from (:-separated list of paths)',
          DEFAULT => undef },
        
        { NAME    => "strict",
          HELP    => "don't ignore the use of undefined variables",
          DEFAULT => 0 },

        { NAME    => "dumpjson",
          HELP    => "dump the json, no templating",
          DEFAULT => 0 },

        );

    return(\@array);

}

sub _initialize {

    my $self = shift;

    #
    # define application specific data.
    #

    # external version number
    $self->{'VERSION'} = '1.0.0';

    # show setup text
    $self->{'USAGE'} = "Usage: json2tt [options]\n";

    #
    # log file policies
    #

    # append to logfile, do not truncate
    $self->{'LOG_APPEND'} = 1;

    # add time stamp before every entry in log
    $self->{'LOG_TSTAMP'} = 1;

    #
    # start initialization of CAF::Application
    #
    unless ($self->SUPER::_initialize(@_)) {
        return(undef);
    }

    # start using log file (could be done later on instead)
    $self->set_report_logfile($self->{'LOG'});

    return(SUCCESS);

}


package main;

use strict;
use warnings;
use JSON::XS;
use Template 2.25;
use Data::Dumper;

use strict;
use vars qw($this_app %SIG);

# fix umask
umask (022);

# unbuffer STDOUT & STDERR
autoflush STDOUT 1;
autoflush STDERR 1;

#
# initialize the main class.
#
unless ($this_app = json2tt->new($0, @ARGV)) {
    throw_error('json2tt: cannot start application');
}

sub escape($) {
    my $str = shift;
    $str =~ s/([^a-zA-Z0-9])/sprintf("_%lx", ord($1))/eg;
    # special case: 1st character cannot be a digit
    $str =~ s/^([0-9])/sprintf("_%lx", ord($1))/e;
    return($str);
}


# read in JSON as specified by the --json option
sub read_json() {
    if (! $this_app->option("json")) {
        $this_app->error("Missing json file (--json option)");
        exit(1);
    }

    my $fn = $this_app->option("json");
    my $fh;
    if ($fn =~ /\.gz$/) {
        open($fh, "gunzip -c $fn |");
    } else {
        open($fh, '<',$fn);
    }
    my $json = decode_json(join("", <$fh>));
    close($fh);
    
    return $json;
}

my $template_opts = {};

$this_app->debug(3,"Set STRICT template option to ", $this_app->option('strict'));
$template_opts->{STRICT} = $this_app->option('strict');

if ($this_app->option("includepath")) {
    $this_app->debug(3,"Set INCLUDE_PATH template option to ", $this_app->option('includepath'));
    $template_opts->{INCLUDE_PATH} = $this_app->option("includepath") 
}

my $json = read_json();
my $tt; 

# get the template and new json content from the json file
my $ut=$this_app->option("unittest");
my $mcs = $this_app->option("metaconfigservice");
if ($ut && $mcs) {
    $this_app->error("Use one of unittest or metaconfigservice option");
    exit(3);
} elsif ($ut || $mcs) {
    my $reljson;
    if ($ut) {
        $this_app->verbose("unittest defined.");
        $reljson = $json->{metaconfig};
    } elsif ($mcs) {
        $this_app->verbose("metaconfigservice $mcs defined.");
        $reljson = $json->{software}->{components}->{metaconfig}->{services}->{escape($mcs)};
    }

    if ($reljson->{module}) {
        my $ttname = $reljson->{module};
        $tt="$ttname.tt";
    } else {
        $this_app->error("No module defined for metaconfigservice %s",$this_app->option("metaconfigservice"));
    };
    # redefine the json contents
    $json=$reljson->{contents};
}

# process relative path.
my $relpath = $this_app->option("relative");
if ($relpath) {
    $this_app->verbose("Relative path $relpath");
    # rel path, starting from root of tree
    my @paths = split('/', $relpath);
    foreach my $path (@paths) {
        $json = $json->{$path};
    }
}

if ($this_app->option("dumpjson")) {
    $this_app->debug(4,"Dumping json, no templating");
    print Dumper($json), "\n";
    exit(0);
}

# template option as last, takes precedence
if ($this_app->option("template")) {
    $tt = $this_app->option("template");
    $this_app->verbose("Use template $tt");
}

if ($tt) {
    $this_app->debug(3,"tt file $tt opts ", Dumper($template_opts));
    my $tpl = Template->new($template_opts);
    if($tpl->process($tt, $json)) {
        $this_app->verbose("Succesful template processing.")
    } else {
        $this_app->error("Template processing failed : ", $tpl->error());
        exit(2);
    }
} else {
    $this_app->error("No template defined.");
    exit(5);
}
