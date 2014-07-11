#!/usr/bin/python
#
# Distributed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
#
"""
Usage: "python -m test.suite" or "python test/suite.py"

@author: Stijn De Weirdt (Ghent University)
"""

# set sys.path to avoid explicit PYTHONPATH setting in default use mode
import os
import sys
_reldir = os.path.dirname(os.path.dirname(__file__))
_absdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not (_reldir in sys.path or _absdir in sys.path):
    sys.path.insert(0, _absdir)

import glob
import operator
import os
import re
import shutil
import tempfile
import unittest

from unittest import TestLoader

from test.testclass import RegexpTestCase, gen_test_func
from vsc.utils.generaloption import simple_option
from vsc.utils import fancylogger


log = None

TEST_CLASS_ATTRS = None

OBJECT_PROFILE_REGEX = re.compile(r'^object\s+template\s+(?P<prof>\S+)\s*;\s*$', re.M)

REGEXPS_SEPARATOR_REGEX = re.compile(r'^-{3}$', re.M)
REGEXPS_EXPECTED_BLOCKS = 3
REGEXPS_SUPPORTED_FLAGS = {
    'multiline': re.M,
    'M': re.M,

    'caseinsensitive': re.I,
    'I': re.I,
}

# parse each reguar expression line
# if count is not None, the regular expression has to match exactly this number
# (count can be 0 to negate a single regexp)
REGEXP_REGEXP = re.compile('^\s*(?P<regex>.*?)\s*(?:\s#{3}\sCOUNT\s(?P<count>\d+))?$')


# some help / documentation
# format is key : (help, is_prefix)
SUPPORTED_FLAGS = {
    'multiline': ('Treat all regexps as multiline regexps', False),
    'M': ('shorthand for "multiline"', False),
    'caseinsensitive': ('Perform case-insensitive matches', False),
    'I': ('alias for "caseinsensitive"', False),
    'metaconfigservice=': ('Look for module/contents in the expected metaconfig component path for the service', True),
    'negate': ('Negate all regexps (none of the regexps can match) (not applicable when COUNT is set for individual regexp)', False),
}


def valid_flag(flag):
    """Check if flag is a valid flag"""
    exact = [flag == k for k, v in SUPPORTED_FLAGS.items() if not v[0]]
    prefix = [flag.startswith(k) for k, v in SUPPORTED_FLAGS.items() if v[0]]
    # assuming python 2.6
    return any(exact + prefix)


def flag_help(supported=False):
    """Return some flag help. If supported, then return the list of supported flags"""
    flags = SUPPORTED_FLAGS.keys()
    flags.sort()
    supported_txt = "supported flags: %s" % ', '.join(flags)
    if supported:
        return supported_txt

    txt = "%s\n" % supported_txt
    for flag in flags:
        descr = SUPPORTED_FLAGS[flag][0]
        txt += "%s%s: %s\n" % (' ' * 4, flag, descr)
    return txt

def find_tt_files(path):
    """Return list of relative path to .tt files"""
    res_dir = []
    res_tt = []
    for root, dirs, files in os.walk(path):
        tts = [os.path.join(root, f) for f in files if f.endswith('.tt')]
        if tts:
            res_tt.extend(tts)
            res_dir.append(root)

    log.debug("Found %s tt files (%s)" % (len(res_tt), res_tt))
    log.debug("Found %s tt dirs (%s)" % (len(res_dir), res_dir))
    return res_tt


def check_pan(path):
    """Check the pan subdir. Return True if all is fine"""
    pandir = os.path.join(path, 'pan')
    if not (os.path.exists(pandir) and os.path.isdir(pandir)):
        log.error('No valid pan subdirectory in path %s' % path)
        return False
    schemafile = os.path.join(pandir, 'schema.pan')
    if not (os.path.exists(schemafile) and os.path.isfile(schemafile)):
        log.error('No valid schema found in path %s (expected %s)' % (path, schemafile))
        return False

    return True


def get_object_profiles(path):
    """Return list of pobject profiles names"""
    res = []
    for rel_fn in os.listdir(path):
        if not rel_fn.endswith('.pan'):
            log.error('Found file %s in profilesdir %s without .pan extension' % (rel_fn, path))
            continue
        fn = os.path.join(path, rel_fn)

        proftxt = open(fn).read()
        r = OBJECT_PROFILE_REGEX.search(proftxt)
        if not r:
            log.error('No object template line found in %s' % fn)
            continue
        prof = r.groupdict()['prof']
        if not rel_fn == "%s.pan" % prof:
            log.error("Profile name %s doesn't match filename %s" % (prof, rel_fn))
            continue
        res.append(prof)

    return res


def parse_regexp(fn):
    """Parse a single regexp"""
    # look for 2 separators, everything after the 2nd are regexpes
    blocks = REGEXPS_SEPARATOR_REGEX.split(open(fn).read())
    if not len(blocks) == REGEXPS_EXPECTED_BLOCKS:
        log.error('Found %s blocks, more/less then number of expected blocks %s' % (len(blocks), REGEXPS_EXPECTED_BLOCKS))
        return

    description = blocks[0].strip().replace("\n", " "*2)  # make single line
    flags = [x.strip() for x in blocks[1].strip().split("\n") if x.strip()]
    regexps_strs = [x.strip() for x in blocks[2].strip().split("\n") if x.strip()]

    extra_flags = {}

    # operator tuple: the operator, and message incase of failure of the test
    # test is assertTrue(op(regexp.search(output)))
    # message is put before the regexp pattern
    op = [operator.truth, '']
    re_flags = 0
    for flag in flags:
        # extra check
        if not valid_flag(flag):
            log.error('Unknown flag %s (%s). Ignoring' % (flag, flag_help(supported=True)))
            continue

        if flag.startswith('metaconfigservice='):
            extra_flags['mode'] = ('--' + flag).split('=')
        elif flag == 'negate':
            op = [operator.not_, 'negated ']
        elif flag in REGEXPS_SUPPORTED_FLAGS:
            re_flags |= REGEXPS_SUPPORTED_FLAGS[flag]

    regexps_compiled = []
    for line in regexps_strs:
        r_line = REGEXP_REGEXP.search(line)
        if not r_line:
            # how did we get here?
            log.error("Invalid regular expression line %s. Skipping." % line)
            continue

        regexps_str = r_line.groupdict()['regex']
        try:
            r = re.compile(regexps_str, re_flags)
            count = r_line.groupdict().get('count', None)
            if count is None:
                count = -1
            regexps_compiled.append([op, r, int(count)])
        except re.error, e:
            log.error("Failed to compile regexps_str %s with flags %s: %s. Skipping." % (regexps_str, re_flags, e))

    return description, regexps_compiled, extra_flags


def parse_regexps(fns):
    """Parse each regex, returns a list of tuples with description and list of compiled regexpes"""
    res = []
    for fn in fns:
        result = parse_regexp(fn)
        if result is None:
            log.error("Failed to parse regexp file %s. Skipping." % fn)
        else:
            res.append(result)
    return res


def get_regexps(path, profs):
    """Get the regular expressions for each profile as a dict."""
    res = {}
    for regexp_name in os.listdir(path):
        if regexp_name not in profs:
            log.error('Regexp file/dir %s found that has no profile. ignoring' % regexp_name)
            continue

        # regexp_name is now name of profile

        regexp_files = []
        abs_regexp = os.path.join(path, regexp_name)
        if os.path.isfile(abs_regexp):
            regexp_files.append(abs_regexp)
        elif os.path.isdir(abs_regexp):
            regexp_files.extend([os.path.join(abs_regexp, fn) for fn in os.listdir(abs_regexp)])
        else:
            log.error('unsupported regexp %s (should be file or directory)' % abs_regexp)
            continue

        res[regexp_name] = parse_regexps(regexp_files)

    return res


def make_regexps_unittests(service, profpath, templatepath, regexps_map):
    """Create the unittest class and test functions, run the test and return the result"""

    class_name = "%sRegexpTest" % service
    attrs = {
        'SERVICE': service,
        'PROFILEPATH': profpath,
        'TEMPLATEPATH': templatepath,
        'METACONFIGPATH': os.path.dirname(templatepath),
    }
    attrs.update(TEST_CLASS_ATTRS)

    # create test cases
    #     one testcase class per service
    #     one testfunction per profile
    #     one test per regexps
    for profile, regexps_tuples in sorted(regexps_map.items()):
        # a bit messy: make_result_extra_falgs are shared
        # so only need to set them in one regexp file
        # since they all cover the same profile
        make_result_extra_flags = {}
        for extra_flags in [x[2] for x in regexps_tuples]:
            make_result_extra_flags.update(extra_flags)
        if make_result_extra_flags:
            log.info('make_result_extra_flags for profile %s: %s' % (profile, make_result_extra_flags))
        attrs["test_%s" % profile] = gen_test_func(profile, [x[:2] for x in regexps_tuples], **make_result_extra_flags)

    # type is class factory
    testclass = type(class_name, (RegexpTestCase,), attrs)
    return TestLoader().loadTestsFromTestCase(testclass)


def make_tests(path, tests):
    """Make the tests for each profile"""
    testsdir = os.path.join(path, 'tests')
    if not (os.path.exists(testsdir) and os.path.isdir(testsdir)):
        log.error('No valid tests subdirectory in path %s' % path)
        return False

    profilesdir = os.path.join(testsdir, 'profiles')
    if not (os.path.exists(profilesdir) and os.path.isdir(profilesdir)):
        log.error('No valid profiles subdirectory in tests path %s' % testsdir)
        return False

    regexpsdir = os.path.join(testsdir, 'regexps')
    if not (os.path.exists(regexpsdir) and os.path.isdir(regexpsdir)):
        log.error('No valid regexps subdirectory in tests path %s' % testsdir)
        return False

    # get the object templates from the profiles dir
    profiles = get_object_profiles(profilesdir)

    if tests:
        # filter out the non-matching profiles from regexps map
        newprofiles = []
        for prof in profiles:
            if prof in tests:
                newprofiles.append(prof)
            else:
                log.debug('Skipping profile %s, not in tests %s' % (prof, tests))
        profiles = newprofiles

    # dict with profile as key and list of tuples with descritoin and list of compiled regexps
    regexps_map = get_regexps(regexpsdir, profiles)

    # is there a regexp for each profile?
    if not len(regexps_map) == len(profiles):
        log.error("Number of regexps_map entries %s is not equal to total number of profiles %s" % (len(regexps_map), len(profiles)))

    return make_regexps_unittests(os.path.basename(path), profilesdir, path, regexps_map)


def validate(service=None, tests=None, path=None):
    """Validate the directory structure and return the test modules suite() results.
    @param service: only process the specified service, when None, process all services
    @param tests: only process the specified tests, when None, process all tests
    """
    res = []
    for srvc in os.listdir(path):
        if service and not srvc == service:
            log.debug('Skipping srvc %s (service %s set)' % (srvc, service))
            continue

        abs_srvc = os.path.join(path, srvc)
        if not os.path.isdir(abs_srvc):
            log.error('Found non-directory %s in path %s. Ignoring.' % (srvc, path))
            continue

        # any tt files?
        ttfiles = find_tt_files(abs_srvc)
        if not ttfiles:
            log.error('Found no tt files for service %s in path %s. Ignoring.' % (srvc, path))
            continue

        # is there a pan subdir with a schema.pan
        if not check_pan(abs_srvc):
            log.error('check_pan failed for %s. Skipping' % srvc)
            continue

        restests = make_tests(abs_srvc, tests)
        res.append(restests)

    return res

if __name__ == '__main__':
    # use absolute path
    testdir = os.path.dirname(os.path.abspath(__file__))
    basedir = os.path.dirname(testdir)
    path = os.path.join(basedir, 'metaconfig')

    # default: use json2tt.pl from this release
    json2tt = os.path.join(basedir, 'scripts', 'json2tt.pl')
    # default: assume a checkout of template-library-core in same workspace
    quattortemplatecorepath = os.path.join(os.path.dirname(basedir), 'template-library-core')

    opts = {
        "service" : ("Select one service to test (when not specified, run all services)", None, "store", None, 's'),
        "tests" : ("Select specific test for given service (when not specified, run all tests)", "strlist", "store", None, 't'),
        "json2tt": ("Path to json2tt.pl script", None, "store", json2tt, 'j'),
        "core" : ("Path to clone of template-library-core repo", None, "store", quattortemplatecorepath, 'C'),
        "showjson": ("Show the generated profile JSON", None, "store_true", None),
        "showtt": ("Show the generated TT output for each profile", None, "store_true", None),
        "showflags": ("Show the flags and description and exit", None, "store_true", None),
    }
    go = simple_option(opts)

    if go.options.showflags:
        print flag_help()
        sys.exit(0)

    TEST_CLASS_ATTRS = {
        'JSON2TT': go.options.json2tt,
        'TEMPLATE_LIBRARY_CORE': go.options.core,
        'SHOWJSON' : go.options.showjson,
        'SHOWTT' : go.options.showtt,
    }

    # no tests without service
    if go.options.tests and not go.options.service:
        go.log.error('Tests specified but no service.')
        sys.exit(1)

    # TODO test panc version. has to be 10.1 (panc has no --version?)

    # make sure temporary files can be created/used
    fd, fn = tempfile.mkstemp()
    os.close(fd)
    os.remove(fn)
    testdir = tempfile.mkdtemp()
    for test_fn in [fn, os.path.join(testdir, 'test')]:
        try:
            open(fn, 'w').write('test')
        except IOError, err:
            go.log.error("Can't write to temporary file %s, set $TMPDIR to a writeable directory (%s)" % (fn, err))
            sys.exit(1)
    os.remove(fn)
    shutil.rmtree(testdir)

    # initialize logger for all the unit tests
    fd, log_fn = tempfile.mkstemp(prefix='config-templates-metaconfig-tests-', suffix='.log')
    os.close(fd)
    os.remove(log_fn)
    fancylogger.logToFile(log_fn)
    log = fancylogger.getLogger()

    SUITE = unittest.TestSuite(validate(path=path, service=go.options.service, tests=go.options.tests))

    # uses XMLTestRunner if possible, so we can output an XML file that can be supplied to Jenkins
    xml_msg = ""
    try:
        import xmlrunner  # requires unittest-xml-reporting package
        xml_dir = 'test-reports'
        res = xmlrunner.XMLTestRunner(output=xml_dir, verbosity=1).run(SUITE)
        xml_msg = ", XML output of tests available in %s directory" % xml_dir
    except ImportError, err:
        sys.stderr.write("WARNING: xmlrunner module not available, falling back to using unittest...\n\n")
        res = unittest.TextTestRunner().run(SUITE)

    fancylogger.logToFile(log_fn, enable=False)

    if not res.wasSuccessful():
        sys.stderr.write("ERROR: Not all tests were successful.\n")
        print "Log available at %s" % log_fn, xml_msg
        sys.exit(2)
    else:
        for f in glob.glob('%s*' % log_fn):
            os.remove(f)
