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

    here = os.path.abspath(os.path.dirname(__file__))  # to be overloaded
    media = os.path.join(here, "media")

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        # set the application name
        self.name = "Sound Speed Manager"
        self.version = ssm_version
        self.setWindowTitle('%s v.%s' % (self.name, self.version))
        self.setMinimumSize(400, 250)
        self.resize(900, 600)
        _app = QtCore.QCoreApplication.instance()
        _app.setApplicationName('%s v.%s' % (self.name, self.version))
        _app = QtCore.QCoreApplication.instance()
        _app.setOrganizationName("HydrOffice")
        _app.setOrganizationDomain("hydroffice.org")

        # set icons
        icon_info = QtCore.QFileInfo(os.path.join(self.media, 'favicon.png'))
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

        self.progress = QtGui.QProgressDialog(self)
        self.progress.setWindowTitle("Downloading")
        self.progress.setCancelButtonText("Abort")
        self.progress.setWindowModality(QtCore.Qt.WindowModal)

        # create the project
        self.prj = Project(qprogress=QtGui.QProgressDialog, qparent=self)
        self.prj.set_callbacks(Callbacks(self))  # set the PySide callbacks
        self.check_woa09()
        self.check_woa13()
        # self.check_rtofs()  # no need to wait for the download at the beginning

        # init default settings
        settings = QtCore.QSettings()
        export_folder = settings.value("export_folder")
        if (export_folder is None) or (not os.path.exists(export_folder)):
            settings.setValue("export_folder", self.prj.data_folder)
        import_folder = settings.value("import_folder")
        if (import_folder is None) or (not os.path.exists(import_folder)):
            settings.setValue("import_folder", self.prj.data_folder)

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

    def check_woa09(self):
        if not self.prj.use_woa09():
            return
        if self.prj.has_woa09():
            return

        msg = 'The WOA09 atlas is required by some advanced application functions.\n\n' \
              'The data set (~120MB) can be retrieved from:\n' \
              '   ftp.ccom.unh.edu/fromccom/hydroffice/woa09.red.zip\n' \
              'then unzipped it into:\n' \
              '   %s\n\n' \
              'Do you want that I perform this operation for you?\n' \
              'Internet connection is required!\n' % self.prj.woa09_folder()
        ret = QtGui.QMessageBox.information(self, "Sound Speed Manager - WOA09 Atlas", msg,
                                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.No:
            msg = 'You can also manually install it. The steps are:\n' \
                  ' - download the archive from (anonymous ftp):\n' \
                  '   ftp.ccom.unh.edu/fromccom/hydroffice/woa09.red.zip\n' \
                  ' - unzip the archive into:\n' \
                  '   %s\n' \
                  ' - restart Sound Speed Manager\n' % self.prj.woa09_folder()
            QtGui.QMessageBox.information(self, "Sound Speed Manager - WOA09 Atlas", msg,
                                          QtGui.QMessageBox.Ok)
            return

        success = self.prj.download_woa09()

        if not success:
            msg = 'Unable to retrieve the WOA09 atlas.\n\n ' \
                  'You may manually install it. The steps are:\n' \
                  ' - download the archive from (anonymous ftp):\n' \
                  '   ftp.ccom.unh.edu/fromccom/hydroffice/woa09.red.zip\n' \
                  ' - unzip the archive into:\n' \
                  '   %s\n' \
                  ' - restart Sound Speed Manager\n' % self.prj.woa09_folder()
            QtGui.QMessageBox.warning(self, "Sound Speed Manager - WOA09 Atlas", msg,
                                      QtGui.QMessageBox.Ok)

    def check_woa13(self):
        if not self.prj.use_woa13():
            return
        if self.prj.has_woa13():
            return

        msg = 'The WOA13 atlas is required by some advanced application functions.\n\n' \
              'The data set (~4GB) can be retrieved from:\n' \
              '   ftp.ccom.unh.edu/fromccom/hydroffice/woa13_temp.red.zip\n' \
              '   ftp.ccom.unh.edu/fromccom/hydroffice/woa13_sal.red.zip\n' \
              'then unzipped it into:\n' \
              '   %s\n\n' \
              'Do you want that I perform this operation for you?\n' \
              'Internet connection is required!\n' % self.prj.woa13_folder()
        ret = QtGui.QMessageBox.information(self, "Sound Speed Manager - WOA13 Atlas", msg,
                                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.No:
            msg = 'You can also manually install it. The steps are:\n' \
                  ' - download the archive from (anonymous ftp):\n' \
                  '   ftp.ccom.unh.edu/fromccom/hydroffice/woa13_temp.red.zip\n' \
                  '   ftp.ccom.unh.edu/fromccom/hydroffice/woa13_sal.red.zip\n' \
                  ' - unzip the archive into:\n' \
                  '   %s\n' \
                  ' - restart Sound Speed Manager\n' % self.prj.woa13_folder()
            QtGui.QMessageBox.information(self, "Sound Speed Manager - WOA13 Atlas", msg,
                                          QtGui.QMessageBox.Ok)
            return

        success = self.prj.download_woa13()

        if not success:
            msg = 'Unable to retrieve the WOA13 atlas.\n\n ' \
                  'You may manually install it. The steps are:\n' \
                  ' - download the archive from (anonymous ftp):\n' \
                  '   ftp.ccom.unh.edu/fromccom/hydroffice/woa13_temp.red.zip\n' \
                  '   ftp.ccom.unh.edu/fromccom/hydroffice/woa13_sal.red.zip\n' \
                  ' - unzip the archive into:\n' \
                  '   %s\n' \
                  ' - restart Sound Speed Manager\n' % self.prj.woa13_folder()
            QtGui.QMessageBox.warning(self, "Sound Speed Manager - WOA13 Atlas", msg,
                                      QtGui.QMessageBox.Ok)

    def check_rtofs(self):
        if not self.prj.use_rtofs():
            return
        if self.prj.has_rtofs():
            return

        success = self.prj.download_rtofs()
        if not success:
            msg = 'Unable to retrieve the RTOFS atlas.\n\n ' \
                  'The application needs an internet connection to access\n' \
                  'this server (with port 9090 open):\n' \
                  ' - http://nomads.ncep.noaa.gov:9090\n\n' \
                  'You can disable the RTOFS support in Settings/Basic/Use RTOFS.\n'
            QtGui.QMessageBox.warning(self, "Sound Speed Manager - RTOFS Atlas", msg,
                                      QtGui.QMessageBox.Ok)

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

    def data_stored(self):
        self.tabEditor.data_stored()
        self.tabDatabase.data_stored()
        self.tabServer.data_stored()
        self.tabSettings.data_stored()

    def data_removed(self):
        self.tabEditor.data_removed()
        self.tabDatabase.data_removed()
        self.tabServer.data_removed()
        self.tabSettings.data_removed()

    # Quitting #

    def do_you_really_want(self, title="Quit", text="quit"):
        msg_box = QtGui.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setIconPixmap(QtGui.QPixmap(os.path.join(self.media, 'favicon.png')).scaled(QtCore.QSize(36, 36)))
        msg_box.setText('Do you really want to %s?' % text)
        msg_box.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        msg_box.setDefaultButton(QtGui.QMessageBox.No)
        return msg_box.exec_()

    def closeEvent(self, event):
        """ actions to be done before close the app """
        reply = self.do_you_really_want("Quit", "quit %s" % self.name)
        # reply = QtGui.QMessageBox.Yes
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
            super(MainWin, self).closeEvent(event)
        else:
            event.ignore()

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
