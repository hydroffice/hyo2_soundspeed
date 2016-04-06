from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys

from PySide import QtGui
from PySide import QtCore

import logging
logger = logging.getLogger(__name__)

from . import __version__ as ssm_version
from hydroffice.soundspeed.project import Project
from .callbacks import Callbacks
from .widgets.editor import Editor
from .widgets.database import Database
from .widgets.server import Server
from .widgets.settings import Settings
from .widgets.info import Info


class MainWin(QtGui.QMainWindow):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        # create the project
        self.prj = Project()
        self.prj.set_callbacks(Callbacks(self))  # set the PySide callbacks

        # set the application name
        self.name = "Sound Speed Manager"
        self.version = ssm_version
        self.setWindowTitle('%s v.%s' % (self.name, self.version))
        self.setMinimumSize(700, 400)
        _app = QtCore.QCoreApplication.instance()
        _app.setApplicationName('%s v.%s' % (self.name, self.version))
        _app = QtCore.QCoreApplication.instance()
        _app.setOrganizationName("HydrOffice")
        _app.setOrganizationDomain("hydroffice.org")

        # init default settings
        settings = QtCore.QSettings()
        export_folder = settings.value("export_folder")
        if (export_folder is None) or (not os.path.exists(export_folder)):
            settings.setValue("export_folder", self.prj.data_folder)
        import_folder = settings.value("import_folder")
        if (import_folder is None) or (not os.path.exists(import_folder)):
            settings.setValue("import_folder", self.prj.data_folder)

        # set icons
        icon_info = QtCore.QFileInfo(os.path.join(self.here, 'media', 'favicon.png'))
        self.setWindowIcon(QtGui.QIcon(icon_info.absoluteFilePath()))
        if (sys.platform == 'win32') or (os.name is "nt"):  # is_windows()
            try:
                # This is needed to display the app icon on the taskbar on Windows 7
                import ctypes
                app_id = '%s v.%s' % (self.name, self.version)
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
            except AttributeError as e:
                logger.debug("Unable to change app icon: %s" % e)

        # set palette
        style_info = QtCore.QFileInfo(os.path.join(self.here, 'styles', 'main.stylesheet'))
        style_content = open(style_info.filePath()).read()
        self.setStyleSheet(style_content)

        # make tabs
        self.tabs = QtGui.QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.setIconSize(QtCore.QSize(45, 45))
        # editor
        self.tabEditor = Editor(prj=self.prj, main_win=self)
        idx = self.tabs.insertTab(0, self.tabEditor,
                                  QtGui.QIcon(os.path.join(self.here, 'media', 'editor.png')), "")
        self.tabs.setTabToolTip(idx, "Editor")
        # database
        self.tabDatabase = Database(prj=self.prj, main_win=self)
        idx = self.tabs.insertTab(1, self.tabDatabase,
                                  QtGui.QIcon(os.path.join(self.here, 'media', 'database.png')), "")
        self.tabs.setTabToolTip(idx, "Database")
        # server
        self.tabServer = Server(prj=self.prj, main_win=self)
        idx = self.tabs.insertTab(2, self.tabServer,
                                  QtGui.QIcon(os.path.join(self.here, 'media', 'server.png')), "")
        self.tabs.setTabToolTip(idx, "Server")
        # server
        self.tabSettings = Settings(prj=self.prj, main_win=self)
        idx = self.tabs.insertTab(3, self.tabSettings,
                                  QtGui.QIcon(os.path.join(self.here, 'media', 'settings.png')), "")
        self.tabs.setTabToolTip(idx, "Settings")
        # info
        self.tabInfo = Info(default_url='http://www.hydroffice.org/soundspeed/')
        idx = self.tabs.insertTab(4, self.tabInfo,
                                  QtGui.QIcon(os.path.join(self.here, 'media', 'info.png')), "")
        self.tabs.setTabToolTip(idx, "Info")

        self.data_cleared()

        self.do()

    def data_cleared(self):
        self.tabEditor.data_cleared()
        self.tabDatabase.data_cleared()
        self.tabServer.data_cleared()
        self.tabSettings.data_cleared()

    def data_imported(self):
        self.tabEditor.data_imported()
        self.tabDatabase.data_imported()
        self.tabServer.data_imported()
        self.tabSettings.data_imported()

    def do(self):
        """DEBUGGING"""
        from hydroffice.soundspeed.base import helper
        data_input = helper.get_testing_input_folder()
        data_sub_folders = helper.get_testing_input_subfolders()

        def pair_reader_and_folder(folders, readers):
            """Create pair of folder and reader"""
            pairs = dict()
            for folder in folders:
                for reader in readers:
                    if reader.name.lower() != 'valeport':  # reader filter
                        continue
                    if reader.name.lower() != folder.lower():  # skip not matching readers
                        continue
                    pairs[folder] = reader
            logger.info('pairs: %s' % pairs.keys())
            return pairs

        def list_test_files(data_input, pairs):
            """Create a dictionary of test file and reader to use with"""
            tests = dict()
            for folder in pairs.keys():
                reader = pairs[folder]
                reader_folder = os.path.join(data_input, folder)

                for root, dirs, files in os.walk(reader_folder):
                    for file in files:

                        # check the extension
                        ext = file.split('.')[-1].lower()
                        if ext not in reader.ext:
                            continue

                        tests[os.path.join(root, file)] = reader
            # logger.info("tests: %s" % tests)
            return tests

        pairs = pair_reader_and_folder(folders=data_sub_folders, readers=self.prj.readers)
        tests = list_test_files(data_input=data_input, pairs=pairs)
        self.prj.import_data(data_path=tests.keys()[0], data_format=tests[tests.keys()[0]].name)
        self.data_imported()
