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
import glob
import os
import re
import shutil
import sys
import tempfile
import unittest

from unittest import TestLoader

from test.testclass import RegexpTestCase, gen_test_func
from vsc.utils import fancylogger

log = None
JSON2TT = None

OBJECT_PROFILE_REGEX = re.compile(r'^object\s+template\s+(?P<prof>\S+)\s*;\s*$', re.M)

REGEXPS_SEPARATOR_REGEX = re.compile(r'^-{3}$', re.M)
REGEXPS_EXPECTED_BLOCKS = 3
REGEXPS_SUPPORTED_FLAGS = {
    'multiline': re.M,
    'M': re.M,

    'caseinsensitive': re.I,
    'I': re.I,
}


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
        log.error('Found %s blocks, more then number of expected blocks %s' % (len(blocks), REGEXPS_EXPECTED_BLOCKS))

    description = blocks[0].strip().replace("\n", " "*2)  # make single line
    flags = [x.strip() for x in blocks[1].strip().split("\n") if x.strip()]
    regexps_strs = [x.strip() for x in blocks[2].strip().split("\n") if x.strip()]

    re_flags = 0
    for flag in flags:
        if not flag in REGEXPS_SUPPORTED_FLAGS:
            log.error('Unknown flag %s (supported: %s). Ignoring' % (flag, REGEXPS_SUPPORTED_FLAGS.keys()))
            continue
        re_flags |= REGEXPS_SUPPORTED_FLAGS[flag]

    regexps_compiled = []
    for regexps_str in regexps_strs:
        try:
            r = re.compile(regexps_str, re_flags)
        except Exception, e:
            log.error("Failed to compile regexps_str %s with flags %s: %s" % (regexps_str, re_flags, e))
        regexps_compiled.append(r)

    return description, regexps_compiled


def parse_regexps(fns):
    """Parse each regex, returns a list of tuples with description and list of compiled regexpes"""
    res = []
    for fn in fns:
        res.append(parse_regexp(fn))
    return res


def get_regexps(path, profs):
    """Get the regular expressions for each profile as a dict."""
    res = {}
    for regexp in os.listdir(path):
        if not regexp in profs:
            log.error('Regexp file/dir %s found that has no profile. ignoring' % regexp)
            continue

        # regexp is now name of profile

        regexp_files = []
        abs_regexp = os.path.join(path, regexp)
        if os.path.isfile(abs_regexp):
            regexp_files.append(abs_regexp)
        elif os.path.isdir(abs_regexp):
            regexp_files.extend([os.path.join(abs_regexp, fn) for fn in os.listdir(abs_regexp)])
        else:
            log.error('unsupported regexp %s (should be file or directory)' % abs_regexp)
            continue

        res[regexp] = parse_regexps(regexp_files)

    return res


def make_regexps_unittests(service, profpath, templatepath, regexps_map):
    """Create the unittest class and test functions, run the test and return the result"""

    class_name = "%sRegexpTest" % service
    attrs = {
        'SERVICE': service,
        'PROFILEPATH': profpath,
        'TEMPLATEPATH': templatepath,
        'JSON2TT': JSON2TT,
    }

    # create test cases
    #     one testcase class per service
    #     one testfunction per profile
    #     one test per regexps
    for profile, regexps_tuples in sorted(regexps_map.items()):
        attrs["test_%s" % profile] = gen_test_func(profile, regexps_tuples)

    # type is class factory
    testclass = type(class_name, (RegexpTestCase,), attrs)
    return TestLoader().loadTestsFromTestCase(testclass)


def make_tests(path):
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
    # dict with profile as key and list of tuples with descritoin and list of compiled regexps
    regexps_map = get_regexps(regexpsdir, profiles)
    # is there a regexp for each profile?
    if not len(regexps_map) == len(profiles):
        log.error("Number of regexps_map entries %s is not equal to number of profiles %s" % (len(regexps_map), len(profiles)))

    return make_regexps_unittests(os.path.basename(path), profilesdir, path, regexps_map)


def validate(path=None):
    """Validate the directory structure and return the test modules suite() results"""
    if path is None:
        testdir = os.path.dirname(__file__)
        basedir = os.path.dirname(testdir)
        path = os.path.join(basedir, 'metaconfig')

        # set it
        global JSON2TT
        JSON2TT = os.path.join(basedir, 'scripts', 'json2tt.pl')

    res = []
    for service in os.listdir(path):
        abs_service = os.path.join(path, service)
        if not os.path.isdir(abs_service):
            log.error('Found non-directory %s in path %s. Ignoring.' % (service, path))
            continue

        # any tt files?
        ttfiles = find_tt_files(abs_service)
        if not ttfiles:
            log.error('Found no tt files for service %s in path %s. Ignoring.' % (service, path))
            continue

        # is there a pan subdir with a schema.pan
        if not check_pan(abs_service):
            continue

        tests = make_tests(abs_service)
        res.append(tests)

    return tests

if __name__ == '__main__':
    # make sure temporary files can be created/used
    fd, fn = tempfile.mkstemp()
    os.close(fd)
    os.remove(fn)
    testdir = tempfile.mkdtemp()
    for test_fn in [fn, os.path.join(testdir, 'test')]:
        try:
            open(fn, 'w').write('test')
        except IOError, err:
            sys.stderr.write("ERROR: Can't write to temporary file %s, set $TMPDIR to a writeable directory (%s)" % (fn, err))
            sys.exit(1)
    os.remove(fn)
    shutil.rmtree(testdir)

    # initialize logger for all the unit tests
    fd, log_fn = tempfile.mkstemp(prefix='config-templates-metaconfig-tests-', suffix='.log')
    os.close(fd)
    os.remove(log_fn)
    fancylogger.logToFile(log_fn)
    log = fancylogger.getLogger()

    SUITE = unittest.TestSuite(validate())

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
