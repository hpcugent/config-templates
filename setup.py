#!/usr/bin/env python
# -*- coding: latin-1 -*-
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
"""
Basic setup.py for building the config-templates-metaconfig

@author: Stijn De Weirdt (Ghent University)
"""

import sys
import os
from distutils.core import setup

BASE_DIR = "/usr/share/templates/quattor"


def gen_data_files(*ttdirs):
    "Copied from http://stackoverflow.com/questions/3596979/manifest-in-ignored-on-python-setup-py-install-no-data-files-installed"
    data = []

    for ttdir in ttdirs:
        for root, dirs, files in os.walk(ttdir):
            tts = [os.path.join(root, f) for f in files if f.endswith('.tt')]
            if tts:
                data.extend(tts)
    return data


def gen_tt_files_metaconfig():
    "Copied from http://stackoverflow.com/questions/3596979/manifest-in-ignored-on-python-setup-py-install-no-data-files-installed"
    data = []

    for root, dirs, files in os.walk('metaconfig'):
        tts = [os.path.join(root, f) for f in files if f.endswith('.tt')]
        if tts:
            data.append([os.path.join(BASE_DIR, root), tts])
    return data

setup(
    name="config-templates-metaconfig",
    version="2.0.9",
    description="Templates for services configured with ncm-metaconfig and Template::Toolkit",
    long_description="""Skeletons of configuration files for services that will be configured with ncm-metaconfig.""",
    license='Apache License 2.0',
    author="HPC UGent",
    author_email="hpc-admin@lists.ugent.be",
    data_files=gen_tt_files_metaconfig(),
    scripts=["scripts/json2tt.pl"],
    url="https://github.com/hpcugent/config-templates",
)
