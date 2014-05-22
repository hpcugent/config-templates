#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
# Copyright 2014-2014 Ghent University
#
# This file is part of config-templates-metaconfig,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# http://github.com/hpcugent/config-templates-metaconfig
#
# config-templates-metaconfig is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# config-templates-metaconfig is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with VSC-tools. If not, see <http://www.gnu.org/licenses/>.
#
"""Basic setup.py for building the config-templates-metaconfig"""

import sys
import os
from distutils.core import setup

BASE_DIR = "/usr/share/templates/quattor/metaconfig"


def gen_data_files(*ttdirs):
    "Copied from http://stackoverflow.com/questions/3596979/manifest-in-ignored-on-python-setup-py-install-no-data-files-installed"
    data = []

    for ttdir in ttdirs:
        for root, dirs, files in os.walk(ttdir):
            tts = [os.path.join(root, f) for f in files if f.endswith('.tt')]
            if tts:
                data.extend(tts)

    return data


setup(
    name="config-templates-metaconfig",
    version="2.0.0",
    description="Templates for services configured with ncm-metaconfig and Template::Toolkit",
    long_description="""Skeletons of configuration files for services that will be configured with ncm-metaconfig.""",
    license="LGPL",
    author="HPC UGent",
    author_email="hpc-admin@lists.ugent.be",
    data_files=gen_data_files('metaconfig'),
    scripts=["scripts/json2tt.pl"],
    url="http://www.ugent.be/hpc",
)
