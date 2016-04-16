from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys
import platform
import logging
# To use a consistent encoding
from codecs import open

logger = logging.getLogger(__name__)

here = os.path.abspath(os.path.dirname(__file__))


def get_testing_input_folder():
    data_folder = os.path.abspath(os.path.join(here, os.pardir, os.pardir, os.pardir, "data", "downloaded"))
    if not os.path.exists(data_folder):
        raise RuntimeError("The testing input folder does not exist: %s" % data_folder)
    return data_folder


def get_testing_input_subfolders():
    df = get_testing_input_folder()
    return [o for o in os.listdir(df) if os.path.isdir(os.path.join(df, o))]


def get_testing_output_folder():
    data_folder = os.path.abspath(os.path.join(here, os.pardir, os.pardir, os.pardir, "data", "created"))
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
        self._append_exists = False
        if mode == 'a':
            self._append_exists = os.path.exists(data_path)
        self._io = open(self.path, mode=mode, encoding=encoding)

    @property
    def append_exists(self):
        """Return if the file was existing before the appending operation"""
        return self._append_exists


def info_libs():
    from .. import __version__ as ss_version
    msg = "os: %s %s\n" % (os.name, "64" if is_64bit_os() else "32")
    msg += "python: %s %s-bit\n" % (platform.python_version(), "64" if is_64bit_python() else "32")
    msg += "hydroffice.soundspeed: %s\n" % ss_version

    vers = None
    try:
        from hydroffice.soundspeedmanager import __version__ as ssm_version
        vers = ssm_version
    except ImportError:
        vers = None
    msg += "hydroffice.soundspeedmanager: %s\n" % vers

    try:
        from hydroffice.soundspeedsettings import __version__ as sss_version
        vers = sss_version
    except ImportError:
        vers = None
    msg += "hydroffice.soundspeedsettings: %s\n" % vers

    try:
        from matplotlib import __version__ as mpl_version
        vers = mpl_version
    except ImportError:
        vers = None
    msg += "matplotlib: %s\n" % vers

    try:
        from PySide import __version__ as pyside_version
        vers = pyside_version
    except ImportError:
        vers = None
    msg += "pyside: %s\n" % vers

    try:
        from osgeo.gdal import __version__ as gdal_version
        vers = gdal_version
    except ImportError:
        vers = None
    msg += "gdal: %s\n" % vers

    try:
        from pyproj import __version__ as pyproj_version
        vers = pyproj_version
    except ImportError:
        vers = None
    msg += "pyproj: %s\n" % vers

    return msg


def is_64bit_os():
    """ Check if the current OS is at 64 bits """
    return platform.machine().endswith('64')


def is_64bit_python():
    """ Check if the current Python is at 64 bits """
    return platform.architecture()[0] == "64bit"


def is_windows(cls):
    """ Check if the current OS is Windows """
    return (sys.platform == 'win32') or (os.name is "nt")


def is_darwin(cls):
    """ Check if the current OS is Mac OS """
    return sys.platform == 'darwin'


def is_linux(cls):
    """ Check if the current OS is Linux """
    return sys.platform == 'linux'
