from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys
import logging
# To use a consistent encoding
from codecs import open

logger = logging.getLogger(__name__)

here = os.path.abspath(os.path.dirname(__file__))


def get_testing_input_folder():
    data_folder = os.path.abspath(os.path.join(here, os.pardir, os.pardir, "data", "downloaded"))
    if not os.path.exists(data_folder):
        raise RuntimeError("The testing input folder does not exist: %s" % data_folder)
    return data_folder


def get_testing_input_subfolders():
    df = get_testing_input_folder()
    return [o for o in os.listdir(df) if os.path.isdir(os.path.join(df, o))]


def get_testing_output_folder():
    data_folder = os.path.abspath(os.path.join(here, os.pardir, os.pardir, "data", "created"))
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    return data_folder


def explore_folder(path):
    """Open the passed path using OS-native commands"""
    if not path:
        return

    import subprocess

    if sys.platform == 'darwin':
        subprocess.call(['open', '--', path])

    elif sys.platform == 'linux':
        subprocess.call(['xdg-open', path])

    elif (sys.platform == 'win32') or (os.name is "nt"):
        subprocess.call(['explorer', path])

    else:
        raise OSError("Unknown/unsupported OS")


class FileInfo(object):
    def __init__(self, data_path):
        self._path = os.path.abspath(data_path)
        self._basename = os.path.basename(self._path).split('.')[0]
        self._ext = os.path.basename(self._path).split('.')[-1]
        self._io = None

    @property
    def path(self):
        return self._path

    @property
    def basename(self):
        return self._basename

    @property
    def ext(self):
        return self._ext

    @property
    def io(self):
        return self._io

    @io.setter
    def io(self, value):
        self._io = value

    def __repr__(self):
        msg = "<%s:%s:%s>" % (self.__class__.__name__, self._basename, self._ext)

        return msg


class FileManager(FileInfo):
    def __init__(self, data_path, mode, encoding='utf-8'):
        """Open the passed file and store related info"""
        if (not os.path.exists(data_path)) and ((mode == 'r') or (mode == 'rb')):
            raise RuntimeError('the passed file does not exist: %s' % data_path)
        super(FileManager, self).__init__(data_path=data_path)
        self._io = open(self._path, mode=mode, encoding=encoding)
