# Builds a single-folder EXE for distribution.
#
# To compile, execute the following within the source directory:
#
# python /path/to/pyinstaller.py SoundSpeedManager.spec
#
# The resulting .exe file is placed in the dist/SoundSpeedManager folder.
#
# It may require to manually copy DLLs and other files.
# Move _gdal.dll under a folder named 'osgeo'
# Copy the qt.conf and opengl32sw.dll, libEGL.dll, d3dcompiler_47.dll
#
# Uploading to BitBucket: curl -s -v -u giumas:password -X POST https://api.bitbucket.org/2.0/repositories/hydroffice/hyo_sound_speed_manager/downloads -F files=@SoundSpeedManager.2020.0.4.zip


from datetime import datetime
import sys
import os
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT, TOC
from PyInstaller.compat import is_darwin, is_win

from hyo2.ssm2 import __version__ as ssm_version

sys.setrecursionlimit(20000)

is_alpha = False
is_beta = False
if is_alpha:
    alphabeta = ".a%s" % datetime.now().strftime("%Y%m%d%H%M%S")
elif is_beta:
    alphabeta = ".b%s" % datetime.now().strftime("%Y%m%d%H%M%S")
else:
    alphabeta = str()


def collect_pkg_data(package, include_py_files=False, subdir=None):
    from PyInstaller.utils.hooks import get_package_paths, remove_prefix, PY_IGNORE_EXTENSIONS

    # Accept only strings as packages.
    if type(package) is not str:
        raise ValueError

    pkg_base, pkg_dir = get_package_paths(package)
    if subdir:
        pkg_dir = os.path.join(pkg_dir, subdir)
    # Walk through all file in the given package, looking for data files.
    data_toc = TOC()
    for dir_path, dir_names, files in os.walk(pkg_dir):
        for f in files:
            extension = os.path.splitext(f)[1]
            if include_py_files or (extension not in PY_IGNORE_EXTENSIONS):
                source_file = os.path.join(dir_path, f)
                dest_folder = remove_prefix(dir_path, os.path.dirname(pkg_base) + os.sep)
                dest_file = os.path.join(dest_folder, f)
                data_toc.append((dest_file, source_file, 'DATA'))

    return data_toc


def python_path() -> str:
    """ Return the python site-specific directory prefix (PyInstaller-aware) """

    # required by PyInstaller
    if hasattr(sys, '_MEIPASS'):

        if is_win():
            import win32api
            # noinspection PyProtectedMember
            sys_prefix = win32api.GetLongPathName(sys._MEIPASS)
        else:
            # noinspection PyProtectedMember
            sys_prefix = sys._MEIPASS

        print("using _MEIPASS: %s" % sys_prefix)
        return sys_prefix

    # check if in a virtual environment
    if hasattr(sys, 'real_prefix'):
        return sys.real_prefix

    return sys.prefix


def collect_folder_data(input_data_folder: str, relative_output_folder: str, recursively: bool = False):

    data_toc = TOC()
    if not os.path.exists(input_data_folder):
        print("issue with folder: %s" % input_data_folder)
        return data_toc

    for dir_path, dir_names, files in os.walk(input_data_folder):
        for f in files:
            source_file = os.path.join(dir_path, f)
            dest_file = os.path.normpath(
                os.path.join(relative_output_folder, os.path.relpath(dir_path, input_data_folder), f))
            data_toc.append((dest_file, source_file, 'DATA'))

        if not recursively:
            break

    return data_toc


share_folder = os.path.join(python_path(), "Library", "share")
output_folder = os.path.join("Library", "share")
pyproj_data = collect_folder_data(input_data_folder=share_folder, relative_output_folder=output_folder)
share_folder = os.path.join(python_path(), "share", "cartopy", "shapefiles", "natural_earth", "physical")
output_folder = os.path.join("cartopy", "data", "shapefiles", "natural_earth", "physical")
cartopy_data = collect_folder_data(input_data_folder=share_folder, relative_output_folder=output_folder,
                                   recursively=True)

abc_data = collect_pkg_data('hyo2.abc2')
ssm2_data = collect_pkg_data('hyo2.ssm2')
try:
    sdm_data = collect_pkg_data('hyo2.sdm3')
except Exception as e:
    print("skipping hyo2.surveydatamonitor: %s" % e)
    sdm_data = TOC()

icon_file = os.path.normpath(os.path.join(os.getcwd(), 'freeze', 'SoundSpeedManager.ico'))
if is_darwin:
    icon_file = os.path.normpath(os.path.join(os.getcwd(), 'freeze', 'SoundSpeedManager.icns'))

a = Analysis(['SoundSpeedManager.py'],
             pathex=[],
             hiddenimports=[],
             excludes=['qgis', 'pandas', 'fiona', 'PyQt5', 'PySide2', 'shiboken2', 'wx'],
             hookspath=None,
             runtime_hooks=None)

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='SoundSpeedManager',
          debug=False,
          strip=None,
          upx=True,
          console=True,
          icon=icon_file)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               # pyside6_data,
               sdm_data,
               pyproj_data,
               cartopy_data,
               abc_data,
               ssm2_data,
               strip=None,
               upx=True,
               name='SoundSpeedManager.%s%s' % (ssm_version, alphabeta))
