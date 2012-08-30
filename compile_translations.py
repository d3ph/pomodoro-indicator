#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import errno
from glob import glob
import shutil
import msgfmt

PROJECTNAME='pomodoro-indicator'


def list_message_files(suffix=".po"):
    """Return list of all found message files and their intallation paths"""
    _files = glob("po/*" + suffix)
    _list = []
    for _file in _files:
        # basename (without extension) is a locale name
        _locale = os.path.splitext(os.path.basename(_file))[0]
        _list.append((_file, os.path.join(
            'share', 'locale', _locale, "LC_MESSAGES", "%s.mo" % PROJECTNAME)))
    return _list


def pmkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise


def cleanup():
    _base_dir = os.path.abspath(os.path.dirname(__file__))
    _locale_dir = os.path.join(_base_dir, 'share', 'locale')
    
    print 'Cleaning dir ', _locale_dir
    shutil.rmtree(_locale_dir)


def build_message_files():
    """For each po/*.po, build .mo file in target locale directory"""
    for (_src, _dst) in list_message_files():
        _dst_dir = os.path.abspath(os.path.dirname(_dst))
        pmkdir(_dst_dir)
        _abs_file = os.path.abspath(_dst)
        print "Compiling %s -> %s" % (_src, _abs_file)
        msgfmt.make(_src, _abs_file)


if __name__ == '__main__':
    cleanup()
    build_message_files()
