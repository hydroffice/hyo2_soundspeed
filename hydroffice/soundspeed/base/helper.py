from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys
import platform
import logging
# To use a consistent encoding
from codecs import open

logger = logging.getLogger(__name__)


class FileInfo(object):
    """A class that collects information on a passed file"""

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

    try:
        from hydroffice.soundspeedmanager import __version__ as ssm_version

    except ImportError:
        ssm_version = None

    vrs = ssm_version
    msg += "hydroffice.soundspeedmanager: %s\n" % vrs

    try:
        from hydroffice.soundspeedsettings import __version__ as sss_version

    except ImportError:
        sss_version = None

    vrs = sss_version
    msg += "hydroffice.soundspeedsettings: %s\n" % vrs

    try:
        from matplotlib import __version__ as mpl_version

    except ImportError:
        mpl_version = None

    vrs = mpl_version
    msg += "matplotlib: %s\n" % vrs

    try:
        from PySide import __version__ as pyside_version

    except ImportError:
        pyside_version = None

    vrs = pyside_version
    msg += "pyside: %s\n" % vrs

    try:
        from osgeo.gdal import __version__ as gdal_version

    except ImportError:
        gdal_version = None

    vrs = gdal_version
    msg += "gdal: %s\n" % vrs

    try:
        from pyproj import __version__ as pyproj_version

    except ImportError:
        pyproj_version = None

    vrs = pyproj_version
    msg += "pyproj: %s\n" % vrs

    try:
        from netCDF4 import __version__ as netcdf4_version

    except ImportError:
        netcdf4_version = None

    vrs = netcdf4_version
    msg += "netCDF4: %s" % vrs

    return msg


def is_64bit_os():
    """ Check if the current OS is at 64 bits """
    return platform.machine().endswith('64')


def is_64bit_python():
    """ Check if the current Python is at 64 bits """
    return platform.architecture()[0] == "64bit"


def is_windows():
    """ Check if the current OS is Windows """
    return (sys.platform == 'win32') or (os.name is "nt")


def is_darwin():
    """ Check if the current OS is Mac OS """
    return sys.platform == 'darwin'


def is_linux():
    """ Check if the current OS is Linux """
    return sys.platform in ['linux', 'linux2']


def explore_folder(path):
    """Open the passed path using OS-native commands"""
    if not os.path.exists(path):
        logger.warning('the passed path to open does not exist: %s' % path)
        return False

    import subprocess

    if is_darwin():
        subprocess.call(['open', '--', path])
        return True

    elif is_linux():
        subprocess.call(['xdg-open', path])
        return True

    elif is_windows():
        subprocess.call(['explorer', path])
        return True

    else:
        logger.warning("Unknown/unsupported OS")
        return False


def first_match(dct, val):
    if not isinstance(dct, dict):
        raise RuntimeError("invalid first input: it is %s instead of a dict" % type(dct))
    # print(dct, val)
    values = [key for key, value in dct.items() if value == val]
    if len(values) != 0:
        return values[0]
    else:
        raise RuntimeError("unknown value %s in dict: %s" % (val, dct))


def python_path():
    """ Return the python site-specific directory prefix (PyInstaller-aware) """

    # required by PyInstaller
    if hasattr(sys, '_MEIPASS'):

        if is_windows():
            import win32api
            # noinspection PyProtectedMember
            sys_prefix = win32api.GetLongPathName(sys._MEIPASS)
        else:
            # noinspection PyProtectedMember
            sys_prefix = sys._MEIPASS

        logger.debug("using _MEIPASS: %s" % sys_prefix)
        return sys_prefix

    # check if in a virtual environment
    if hasattr(sys, 'real_prefix'):
        return sys.real_prefix

    return sys.prefix


def is_pydro():
    try:
        # noinspection PyUnresolvedReferences
        import HSTB
        return True

    except Exception:

        try:
            # noinspection PyUnresolvedReferences
            import HSTP
            return True

        except Exception:
            return False
