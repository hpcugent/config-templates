#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
# Copyright 2009-2012 Ghent University
#
# This file is part of VSC-tools,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# http://github.com/hpcugent/VSC-tools
#
# VSC-tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# VSC-tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with VSC-tools. If not, see <http://www.gnu.org/licenses/>.
#
"""Basic setup.py for building the hpcugent Icinga checks"""

import sys
import os
from distutils.core import setup
import glob

BASE_DIR = "/usr/share/templates/quattor/metaconfig"

def gen_data_files(*dirs):
    "Copied from http://stackoverflow.com/questions/3596979/manifest-in-ignored-on-python-setup-py-install-no-data-files-installed"
    data = []

    for src_dir in dirs:
        for root, dirs, files in os.walk(src_dir):
            d = root.split("/")
            dst = os.path.sep.join([BASE_DIR] + d[2:])
            data.append((dst, map(lambda f: os.path.sep.join([root, f]),
                                     files)))

    return data


setup(name="config-templates-metaconfig",
      version="1.37",
      description="Templates for services configured with ncm-metaconfig and Template::Toolkit",
      long_description="""Skeletons of configuration files for services that will be configured
with ncm-metaconfig.
""",
      license="LGPL",
      author="HPC UGent",
      author_email="hpc-admin@lists.ugent.be",
      data_files=gen_data_files("files/metaconfig"),
      scripts=["files/json2tt.pl"],
      url="http://www.ugent.be/hpc")
