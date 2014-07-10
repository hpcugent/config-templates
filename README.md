# Config templates

We have here TT files that may generate configuration files for:

* [Apache](http://httpd.apache.org) in various circumstances
* [nginx](http://nginx.org)
* Many [Logstash](http://logstash.net) inputs, outputs and filters.
* [PerfSONAR](http://perfsonar.net)
* Some basic udev rules
* named
* ...

And a tiny Perl script that fills them from a JSON file, if it has the
correct structure.

# Ongoing work

We are in preparation of moving the legacy hpcugent files to a properly 
structured and tested repository, that at some day should be moved to 
the quattor project at https://github.com/quattor.

The new structure consists of the following files/directories
* the metaconfig directory hold all services, each with their TT files, 
pan schema and unittest data
* the scripts directory holds useful standalone scripts, in particular the 
`json2tt.pl` script
* test directory with the (Python) unittest code
* setup_packaging.py a distultils packaging file for the new code (and only the new code)
* NOTICE (file as per the Apache License)

Read the principles behind the structure of the metaconfig directory
* https://github.com/hpcugent/config-templates/issues/40
* https://github.com/hpcugent/config-templates/issues/41


# Requirements

For installation
* perl `Template::Toolkit` (TT) version 2.25 or later (use CPAN or for src rpms on el5, el6 and el7, contact @stdweird)
* perl `JSON::XS`
* perl quattor modules `CAF`, `LC`

For unit-testing/development
* recent pan-compiler (10.1 or later), with `panc` in `$PATH`
* python `vsc-base` (`easy_install vsc-base` (use `--user` on recent systems for local install), or ask @stdweird for rpms)
* a local checkout of `template-library-core` repository (https://github.com/quattor/template-library-core); default 
expects it in the same directory as the checkout of this repository, but it can be changed via the `--core` option of the 
unittest suite

# Running the tests

From the base of the repository, run 
```bash
python test/suite.py
```
to run all tests of all services.

## Unittest suite help 

```bash
python test/suite.py -h
```
(try --help for long option names)

```
Usage: suite.py [options]


  Usage: "python -m test.suite" or "python test/suite.py"

  @author: Stijn De Weirdt (Ghent University)

Options:
  -h            show short help message and exit
  -H            show full help message and exit

  Main options (configfile section MAIN):
    -C CORE     Path to clone of template-library-core repo (def /home/stdweird/.git/github.ugent/template-library-core)
    -j JSON2TT  Path to json2tt.pl script (def /home/stdweird/.git/github.ugent/config-templates/scripts/json2tt.pl)
    -s SERVICE  Select one service to test (when not specified, run all services)
    -t TESTS    Select specific test for given service (when not specified, run all tests) (type comma-separated list)

  Debug and logging options (configfile section MAIN):
    -d          Enable debug log mode (def False)

Boolean options support disable prefix to do the inverse of the action, e.g. option --someopt also supports --disable-someopt.

All long option names can be passed as environment variables. Variable name is SUITE_<LONGNAME> eg. --some-opt is same as setting SUITE_SOME_OPT in the environment.
```

## Suported flags

Queries the supproted flags via the `--showflags` option
```bash
python test/suite.py --showflags
```
gives
```
supported flags: I, M, caseinsensitive, metaconfigservice=, multiline, negate
    I: alias for "caseinsensitive"
    M: shorthand for "multiline"
    caseinsensitive: Perform case-insensitive matches
    metaconfigservice=: Look for module/contents in the expected metaconfig component path for the service
    multiline: Treat all regexps as multiline regexps
    negate: Negate all regexps (none of the regexps can match) (not applicable when COUNT is set for individual regexp)
```

# Development example

Start with forking the upstream repository https://github.com/hpcugent/config-templates, and clone your personal fork in your workspace. 
(replace `stdweird` with your own github username). Also add the `upstream` repository (using `https` protocol).

```bash
git clone git@github.com:stdweird/config-templates.git
cd config-templates
git remote add upstream https://github.com/hpcugent/config-templates
```

Check your environment by running the unittests. No tests should fail when the environment is setup properly. 
(Open an issue on github in case there is a problem you can't resolve.)

```bash
python test/suite.py
```

## Add new service

### Target

Our `example` service requires a text config file in `/etc/example/exampled.conf` and has following structure
```
name = {
    hosts = server1,server2
    port = 800
    master = FALSE
    description = "My example"
}
```

where following fields are mandatory:
* `hosts`: a comma separated list of hostnames
* `port`: an integer
* `master`: boolean with possible values `TRUE` or `FALSE` 
* `description`: a quoted string 

The service has also an optional fields `option`, also a quoted string.

Upon changes of the config file, the `exampled` service needs to be restarted.

This type of configuration is ideally suited for metaconfig and TT.

### Prepare

Pick a good and relevant name for the service (in this case we will add the non-existing `example` service), and create 
```bash
service=example
```

Make a new branch where you will work in and that you will use to create the pull-request (PR) when finished
```bash
git checkout -b example_service
```

Create the initial directory structure.
```bash
mkdir -p metaconfig/$service/tests/{profiles,regexps} $service/pan
```

Add some typical files (some of the files are not mandatory, 
but are simply best practice).

```bash
cd metaconfig/$service

echo -e "declaration template metaconfig/$service/schema;\n" > pan/schema.pan
echo -e "unique template metaconfig/$service/config;\n\ninclude 'metaconfig/$service/schema';" > pan/config.pan

echo -e "object template config;\n\ninclude 'metaconfig/$service/config';\n" > tests/profiles/config.pan
mkdir tests/regexps/config
echo -e 'Base test for config\n---\nmultiline\n---\n$wontmatch^\n' > tests/regexps/config/base
```

Commit this initial structure
```bash
git commit -a "initial structure for service $service"
```
## Create the schema

The schema needs to be created in the `pan` subdirectory of the service directory `metaconfig/$service`. The file should be called `schema.pan`.

```
declaration template metaconfig/example/schema;

include 'pan/types';

type example_service = {
    'hosts' :  type_hostname[]
    'port' : long(0..)
    'master' : boolean
    'description' : string
    'option' ? string
};

```

* `long`, `boolean` and `string` are pan builtin types (see the panbook for more info)
* `type_hostname` is a type that is available from the main `pan/types` template as part of the core template library.

## Create config template for metaconfig component (optional)

A reference config file can now also be created, with e.g. the type binding to the correct path and configuration of the
restart action and the TT module to load. The file `config.pan` should be created in the same `pan` directory as `schema.pan`.

```
unique template metaconfig/example/config;

include 'metaconfig/example/schema';

bind "/software/components/metaconfig/services/{/etc/example/exampled.conf}/contents" = example_service;

prefix "/software/components/metaconfig/services/{/etc/example/exampled.conf}";
"daemon" = "exampled";
"module" = "example/main";

```

This will expect the TT module with relative filename `example/main.tt`.

## Make TT file to match desired output

Create the `main.tt` file with content in the `metaconfig/$service` directory

```
name = {
[% FILTER indent -%]
hosts = [% hosts.join(',') %]
port = [% port %]
master = [% master ? "TRUE" : "FALSE %]
description = "[% description %]"
[%     IF option.defined -%]
option = "[% option %]"
[%     END -%]
[% END -%]
}
```

* `FILTER indent` creates the indentation
* TT is known for newline issues, so be careful if the config files are sensitive to this.

## Add unittests

Each unittest consists of 2 parts:
* an object template that will generate the profile
* one or more files that contain regular expressions that will be tested against the 
output produced by the TT module and the profile.

The object template is compiled and outputted in JSON format using the pan-compiler. 
Then the `json2tt.pl` script is used to generate the output from the JSON and the TT module.

The testsuite takes care of the actual compilation and generation of the output, and the 
running of the tests.

### Flags

### simple unittest

The easiest example is a single object template with a single regexp file.

#### profile

By default, the expected pan path is under `/metaconfig`.

Create the profile `tests/profiles/simple.pan` as follows:
```
object template simple;

"/metaconfig/module" = "example/main";
prefix "/metaconfig/contents";
"hosts" = list("server1", "server2");
"port" = 800;
"master" = false;
"description" = "My example";

```

* the schema is not validated in this `simple` template, but it can easily be done by adding 
```
include 'metaconfig/example/schema';
bind "/metaconfig/example/contents" = example_service;
```

But the preferred way is to create a proper `config.pan` file and use that as described below.

#### regular expression

Make a 3 block text file called `simple`, with `---` as block separator as follows

```
Simple test
---
---
name
hosts
port
master
description
```

This will search the output for the words `name`, `hosts`, `port`, `master` and `description`.

This is good for illustrating the principle, but is a lousy unittest. Check the `config` unittest below for proper testing.

The filename `simple` has to match the object template you want to test with (in this case the `simple.pan` template).

#### verify

You can verify this single unittest for the `example` service using
```bash
python test/suite.py --service example --tests simple
```

### config based unittest

It is better to use a full blown template as will be used in the actual profiles. The added 
advantage here is the `config.pan` and `schema.pan` are tested as well.

#### profile

The profile is similar to the simple one (it are the same values after all we want to set), but by targetting `metaconfig` usage,
a different prefix is used.

```
object template config;

include 'metaconfig/example/config';

prefix "/software/components/metaconfig/services/{/etc/example/exampled.conf}/contents";
"hosts" = list("server1", "server2");
"port" = 800;
"master" = false;
"description" = "My example";

```

The type binding and definition of the TT module are part of the `config.pan` template, and this usage is very 
close to actual usage in actual machine templates.

#### regular expressions

We will now make several regular expression tests, each in their own file and grouped in a directory called `config` (also matching the object profile name). The filenames in the directory are not relevant (but no addiditional directory structure is allowed).

We need to set the `metaconfig=` flag to point the test infrastructure which metaconfig-controlled file this is supposed to test. 
In principle only one of the templates should set it this path (and if multiple ones are set, they all have to be equal).

Lets start with a regexp test identical to the `simple` test above, called `too_simple`:

```
Too simple test
---
metaconfigservice=/etc/example/exampled.conf
---
name
hosts
port
master
description
```

A 2nd better test uses the `multiline` flag, where the regular expressions are all interpreted as multiline regular expressions 

```
Basic multiline test
---
metaconfigservice=/etc/example/exampled.conf
multiline
---
^name
^\s{4}hosts
^\s{4}port
^\s{4}master
^\s{4}description
= ### COUNT 5
```

This test also uses the special directive ` ### COUNT X` (mind the leading space; X is number, can be 0 or more), where this regular 
expression is expected to occur exactly X times (in this case, we expect 5 `=` characters).

A 3rd test checks if certain regular expression do not match using the `negate` flag.

```
Basic negate test
---
metaconfigservice=/etc/example/exampled.conf
multiline
negate
---
^hosts
^port
^master
^description
```

This tests that the expected fields can't start at the beginning of the line, 
whitespace must be inserted before. 
(The `FILTER indent` TT inserts 4 spaces, as tested with the `\s{4}` in the multiline regexp above.)

If one only needs to check that a single regular expression does not occur, one can also use ` ### COUNT 0`.

#### verify

You can verify this single unittest for the `example` service using
```bash
python test/suite.py --service example --tests config
```

or both via
```bash
python test/suite.py --service example --tests config,simple
```

or all unittests of the `example` service with

```bash
python test/suite.py --service example
```

## Result filestructure

## Usage with ncm-metaconfig

