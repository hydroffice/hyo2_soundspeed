# Builds a single-folder EXE for distribution.
# Note that an "unbundled" distribution launches much more quickly, but
# requires an installer program to distribute.
#
# To compile, execute the following within the source directory:
#
# python /path/to/pyinstaller.py SIS.spec
#
# The resulting .exe file is placed in the dist/SIS folder.
#
# - It may require to manually copy DLL libraries.
# - Uninstall PyQt and sip
# - For QtWebEngine:
#   . copy QtWebEngineProcess.exe in the root
#   . copy in PySide2 both "resources" and "translations" folder
#

from datetime import datetime
import os
import sys
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT, TOC
from PyInstaller.compat import is_darwin, is_win

from hyo2.sis5 import __version__ as sis_version

is_beta = True
if is_beta:
    beta = ".b%s" % datetime.now().strftime("%Y%m%d%H%M%S")
else:
    beta = str()


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


def collect_folder_data(input_data_folder: str, relative_output_folder: str):

    data_toc = TOC()
    if not os.path.exists(input_data_folder):
        print("issue with folder: %s" % input_data_folder)
        return data_toc

    for dir_path, dir_names, files in os.walk(input_data_folder):
        for f in files:
            source_file = os.path.join(dir_path, f)
            dest_file = os.path.join(relative_output_folder, f)
            data_toc.append((dest_file, source_file, 'DATA'))
        break

    return data_toc


share_folder = os.path.join(python_path(), "Library", "share")
output_folder = os.path.join("Library", "share")
pyproj_data = collect_folder_data(input_data_folder=share_folder, relative_output_folder=output_folder)
pyside2_data = collect_pkg_data('PySide2')
share_folder = os.path.join(python_path(), "Lib", "site-packages", "shiboken2", "support", "signature")
output_folder = os.path.join("shiboken2", "support", "signature")
shiboken2_data = collect_folder_data(input_data_folder=share_folder, relative_output_folder=output_folder)
share_folder = os.path.join(python_path(), "Lib", "site-packages", "shiboken2", "support", "signature", "lib")
output_folder = os.path.join("shiboken2", "support", "signature", "lib")
shiboken2_data2 = collect_folder_data(input_data_folder=share_folder, relative_output_folder=output_folder)
abc_data = collect_pkg_data('hyo2.abc')
sis_data = collect_pkg_data('hyo2.sis5')

icon_file = os.path.join('freeze', 'SIS5.ico')
if is_darwin:
    icon_file = os.path.join('freeze', 'SIS5.icns')

a = Analysis(['SIS5.py'],
             pathex=[],
             hiddenimports=["PIL"],
             excludes=["IPython", "PyQt4", "PyQt5", "pandas", "scipy", "sphinx", "sphinx_rtd_theme",
                       "OpenGL_accelerate", "FixTk", "tcl", "tk", "_tkinter", "tkinter", "Tkinter",
                       "wx"],
             hookspath=None,
             runtime_hooks=None)

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='SIS5.%s%s' % (sis_version, beta),
          debug=False,
          strip=None,
          upx=True,
          console=True,
          icon=icon_file)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               pyproj_data,
               pyside2_data,
               shiboken2_data,
               shiboken2_data2,
               abc_data,
               sis_data,
               strip=None,
               upx=True,
               name='SIS5.%s%s' % (sis_version, beta))
