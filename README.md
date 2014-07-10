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
* NOTICE (file as per the Apache License

Read the principles behind the structure of the metaconfig directory
* https://github.com/hpcugent/config-templates/issues/40
* https://github.com/hpcugent/config-templates/issues/41


# Requirements

For installation
* perl `Template::Toolkit` version 2.25 or later (use CPAN or for src rpms on el5, el6 and el7, contact @stdweird)
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
PYTHONPATH=$PWD python $PWD/test/suite.py
```
to run all tests of all services.

## Unittest suite help 

```bash
PYTHONPATH=$PWD python $PWD/test/suite.py -h
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
PYTHONPATH=$PWD python $PWD/test/suite.py --showflags
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
(replace `stdweird` with your own github username)

```bash
git clone git@github.com:stdweird/config-templates.git
```

## Add new service

Pick a good and relevant name for the service (in this case we will add the non-existing `example` service), and create 
```bash
service=example
```

Make a new branch where you will work in and that you will use to create the pull-request (PR) when finished
```bash
cd config-templates
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
git commit -a "initial structure for servicce $service"
```


## Add unittests

### Flags

## Usage with ncm-metaconfig

