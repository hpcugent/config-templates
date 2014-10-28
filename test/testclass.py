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
Custom TestCase 

@author: Stijn De Weirdt (Ghent University)
"""

import logging
import operator
import os
import shutil
import tempfile

from unittest import TestCase
from vsc.utils.run import run_asyncloop


def gen_test_func(profile, regexps_tuples, **make_result_extra_flags):
    """Test function generator"""
    def test_func(self):
        self.makeResult(profile, **make_result_extra_flags)

        # make this a test in case of failure for proper reporting
        # -> all other tests will fail anyway
        if not regexps_tuples:
            self.assertTrue(False, 'No regexp tests for %s' % (profile))
            return

        if self.pancout is not None:
            self.assertTrue(False, 'No json for %s (panc failed: %s)' % (profile, self.pancout))
            return

        if self.json2ttout is not None:
            self.assertTrue(False, 'No tt output for %s (json2tt failed: %s)' % (profile, self.json2ttout))
            return

        for descr, compiled_regexp_tuples in regexps_tuples:
            for idx, (op, compiled_regexp, count) in enumerate(compiled_regexp_tuples):
                if count < 0:
                    to_check = compiled_regexp.search(self.result)
                    extra_msg = ''
                else:
                    all_matches = compiled_regexp.findall(self.result)
                    count_matches = len(all_matches)
                    to_check = count_matches == count
                    extra_msg = " COUNT set: expected %s matches, all matches (%s): %s" % (count, count_matches, all_matches)

                    # The negate flag is ignored when count is set.
                    # Stating regexp foo must not appear exactly three times is overengineering this.
                    if not op == operator.truth:
                        extra_msg += ' (forcing operator.truth; thus ignoring flag (e.g. negate))'
                        op[0] = operator.truth

                versioninfo = ''
                if self.VERSION is not None:
                    versioninfo = " (version %s)" % self.VERSION
                msg = "%s%s regexp (%03d) %spattern %s%s\noutput:\n%s"
                tup = (descr, versioninfo, idx, op[1], compiled_regexp.pattern, extra_msg, self.result)
                self.assertTrue(op[0](to_check), msg % tup)

    return test_func


class RegexpTestCase(TestCase):
    """Dedicated testcase class for handling regular expressions for config-templates-metaconfig"""
    SERVICE = None  # name of service
    PROFILEPATH = None  # absolute path of profiles folder
    METACONFIGPATH = None  # absolute path to metaconfig subdir
    TEMPLATEPATH = None  # absolute path of templates folder
    VERSIOn = None  # version of service

    JSON2TT = None  # absolute path to the json2tt.pl tool
    TEMPLATE_LIBRARY_CORE = None  # abs path to template library core (mainly for pan/types etc)
    SHOWJSON = False  # print the generated JSON from profile compilation
    SHOWTT = False  # print the generated output from JSON2TT

    def setUp(self):
        """Set up testcase. This makes a copy of the templates under service/pan 
        (like the schema.pan) and puts them in the expected namespace 
        metaconfig/<service>/.
        No other copies are made, but this requires panc 10.1 to work.
        """
        self.servicepath = os.path.join(self.METACONFIGPATH, self.SERVICE)
        self.tmpdir = tempfile.mkdtemp()
        self.extradir = os.path.join(self.tmpdir, '_extra')
        # copy metaconfig/<service>/pan directory in self.extradir directory
        # (allows to include and test the schema) this creates the correct namespace
        # (templates in the pan directory are in metaconfig/<service>/ namespace)
        pandir = os.path.join(self.extradir, 'metaconfig', self.SERVICE)
        shutil.copytree(os.path.join(self.servicepath, 'pan'), pandir)

    def makeResult(self, profile, mode=None):
        """Compile the profile from SERVICE and run the template toolkit on it"""
        tmpdir = self.tmpdir
        self.pancout = None
        self.json2ttout = None

        includepaths = [self.PROFILEPATH, self.extradir, self.TEMPLATE_LIBRARY_CORE]

        cmd = [
            'panc',
            '--formats' , 'json',
            '--include-path', os.pathsep.join(includepaths),
            '--output-dir', tmpdir,
            os.path.join(self.PROFILEPATH, "%s.pan" % profile)
            ]
        ec, out = run_asyncloop(cmd)

        jsonfile = os.path.join(tmpdir, "%s.json" % profile)
        if not os.path.exists(jsonfile):
            logging.debug("No json file found for service %s and profile %s. cmd %s output %s" % (self.SERVICE, profile, cmd, out))
            self.pancout = out
            return

        if self.SHOWJSON:
            print "profile %s JSON:\n%s" % (profile, open(jsonfile).read())

        if mode is None:
            mode = ['--unittest']
        cmd = [
            'perl', self.JSON2TT,
            '--json', jsonfile,
            '--includepath', os.path.dirname(self.METACONFIGPATH)
            ] + mode
        ec, out = run_asyncloop(cmd)
        if ec > 0:
            logging.debug("json2tt exited with non-zero ec %s: %s" % (ec, out))
            self.json2ttout = out
            return

        self.result = out
        if self.SHOWTT:
            print "profile %s TT output:\n%s" % (profile, out)

    def tearDown(self):
        """Clean up after running testcase."""
        try:
            shutil.rmtree(self.tmpdir)
        except OSError, err:
            pass
