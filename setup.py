#!/usr/bin/env python
#-*- coding:utf-8 -*-

#
# Copyright 2011 malev.com.ar
#
# Author: Marcos Vanetta <marcosvanetta@gmail.com>
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of either or both of the following licenses:
#
# 1) the GNU Lesser General Public License version 3, as published by the
# Free Software Foundation; and/or
# 2) the GNU Lesser General Public License version 2.1, as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the applicable version of the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of both the GNU Lesser General Public
# License version 3 and version 2.1 along with this program.  If not, see
# <http://www.gnu.org/licenses/>
#

"""Build tar.gz for pomodoro-indicator.
Needed packages to run (using Debian/Ubuntu package names):
    python-appindicator  0.3.0-0ubuntu1
    python-gobject       2.28.3-1ubuntu1.1
    python-notify        0.1.1-2build4
    python-gtk2-dev      0.1.1-2build4
    python-pygame        1.9.1release-0ubuntu4

"""


import os
import sys
from distutils.command.install import install
from distutils.core import setup

PROJECTNAME = 'pomodoro-indicator'


class CustomInstall(install):
    """Custom installation class on package files.

    It copies all the files into the "PREFIX/share/PROJECTNAME" dir.
    """
    def run(self):
        """Run parent install, and then save the install dir in the script."""
        install.run(self)

        for script in self.distribution.scripts:
            script_path = os.path.join(self.install_scripts,
                                       os.path.basename(script))
            with open(script_path, 'rb') as fh:
                content = fh.read()
            content = content.replace('@ INSTALLED_BASE_DIR @',
                                      self._custom_data_dir)
            with open(script_path, 'wb') as fh:
                fh.write(content)

    def finalize_options(self):
        """Alter the installation path."""
        install.finalize_options(self)

        # the data path is under 'prefix'
        data_dir = os.path.join(self.prefix, "share",
                                self.distribution.get_name())

        # if we have 'root', put the building path also under it (used normally
        # by pbuilder)
        if self.root is None:
            build_dir = data_dir
        else:
            build_dir = os.path.join(self.root, data_dir[1:])

        # change the lib install directory so all package files go inside here
        self.install_lib = build_dir

        # save this custom data dir to later change the scripts
        self._custom_data_dir = data_dir


def main():
    SHARE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "share")
    data_files = []
    # don't trash the users system icons!!
    black_list = ['index.theme', 'index.theme~']

    for path, dirs, files in os.walk(SHARE_PATH):
        data_files.append(tuple((path.replace(SHARE_PATH, "share", 1),
            [os.path.join(path, file) for file in files if file not in
                black_list])))

    setup(
        name = PROJECTNAME,
        version = '0.0.4a',
        license = 'GPL-3',
        author = 'Sergio',
        author_email = 'd3ph.ru@gmail.com',
        description = 'Pomodoro technique app indicator.',
        long_description = 'Pomodoro technique app indicator',
        url = 'https://github.com/d3ph/pomodoro-indicator',

        packages = ["pomodoro"],
        package_data = {"pomodoro": ["images/*.png", "sounds/*.ogg", ]},
        data_files = data_files,
        scripts = [os.path.join("bin", "pomodoro-indicator")],

        cmdclass = {
            'install': CustomInstall
        }
    )

if __name__ == '__main__':
    sys.exit(main())
