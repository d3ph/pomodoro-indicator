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

"""
Configuration file
"""

import os
from ConfigParser import SafeConfigParser

CONFIG_FILE = ".pomodoro-indicator.config"


class Configuration(object):
    """
    Handles the configuration file or the defaults
    """
    def __init__(self):
        self.base_dir = os.path.realpath(__file__)
        self.config_file = os.path.join(os.path.expanduser("~"), CONFIG_FILE)
        self.parser = SafeConfigParser()
        self.parser.read(self.config_file)
        self.options_keys = {
            'continue_working_after_rest': 'bool',
            'can_pause': 'bool',
            'max_work_time': 'int',
            'max_rest_time': 'int',
            'break_sound': 'string',
            'ring_sound': 'string',
            'ticking_sound': 'string' #path
        }
        self.default_options = {
            'continue_working_after_rest': True,
            "can_pause": True,
            "max_work_time": 1500,
            "max_rest_time": 300,
            "break_sound": os.path.join(self.base_directory(), "sounds/break.ogg"),
            "ring_sound": os.path.join(self.base_directory(), "sounds/ring.ogg"),
            "ticking_sound": os.path.join(self.base_directory(), "sounds/ticking.ogg")
        }
        self.current_options = self.default_options
        if os.path.exists(self.config_file):
            self.load_config()

    def load_config(self):
        for option, t in self.options_keys.items():
            self.current_options[option] = self.load_option(option, t)

    def load_option(self, option, t):
        if self.parser.has_option('pomodoro', option):
            if t == 'bool':
                return self.parser.getboolean('pomodoro', option)
            if t == 'int':
                return self.parser.getint('pomodoro', option)
            return self.parser.get('pomodoro', option)
        else:
            return self.default_options[option]

    def __getitem__(self, key):
        print self.current_options
        return self.current_options[key]

    def base_directory(self):
        """Returns the base directory"""
        return os.path.dirname(os.path.realpath(__file__))

    def icon_directory(self):
        """Returns the location of the icons"""
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), "images")

if __name__ == "__main__":
    print __doc__
