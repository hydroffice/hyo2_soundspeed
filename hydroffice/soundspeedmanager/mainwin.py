from __future__ import absolute_import, division, print_function, unicode_literals

import math
import os
import sys

from PySide import QtGui
from PySide import QtCore

import logging
logger = logging.getLogger(__name__)

from . import __version__ as ssm_version
from . import __doc__ as ssm_name
from hydroffice.soundspeed.project import Project
from .qtcallbacks import QtCallbacks
from .widgets.editor import Editor
from .widgets.database import Database
from .widgets.server import Server
from .widgets.settings import Settings
from .widgets.refraction import Refraction
from .widgets.info import Info


class MainWin(QtGui.QMainWindow):

    here = os.path.abspath(os.path.dirname(__file__))  # to be overloaded
    media = os.path.join(here, "media")

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        # set the application name and the version
        self.name = ssm_name
        self.version = ssm_version
        self.setWindowTitle('%s v.%s' % (self.name, self.version))
        _app = QtCore.QCoreApplication.instance()
        _app.setApplicationName('%s v.%s' % (self.name, self.version))
        _app.setOrganizationName("HydrOffice")
        _app.setOrganizationDomain("hydroffice.org")

        # set the minimum and the initial size
        self.setMinimumSize(400, 250)
        self.resize(900, 600)

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

        # set palette/stylesheet
        style_info = QtCore.QFileInfo(os.path.join(self.here, 'styles', 'main.stylesheet'))
        style_content = open(style_info.filePath()).read()
        self.setStyleSheet(style_content)

        # TODO: check if progress is actually called somewhere
        self.progress = QtGui.QProgressDialog(self)
        self.progress.setWindowTitle("Downloading")
        self.progress.setCancelButtonText("Abort")
        self.progress.setWindowModality(QtCore.Qt.WindowModal)

        # create the project
        self.prj = Project(qt_progress=QtGui.QProgressDialog, qt_parent=self)
        self.prj.set_callbacks(QtCallbacks(parent=self))  # set the PySide callbacks
        self.check_woa09()
        self.check_woa13()
        # self.check_rtofs()  # no need to wait for the download at the beginning
        self.check_sis()
        self.check_sippican()
        self.check_mvp()

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
        self.tab_editor = Editor(prj=self.prj, main_win=self)
        idx = self.tabs.insertTab(0, self.tab_editor,
                                  QtGui.QIcon(os.path.join(self.here, 'media', 'editor.png')), "")
        self.tabs.setTabToolTip(idx, "Editor")
        # database
        self.tab_database = Database(prj=self.prj, main_win=self)
        idx = self.tabs.insertTab(1, self.tab_database,
                                  QtGui.QIcon(os.path.join(self.here, 'media', 'database.png')), "")
        self.tabs.setTabToolTip(idx, "Database")
        # server
        self.tab_server = Server(prj=self.prj, main_win=self)
        idx = self.tabs.insertTab(2, self.tab_server,
                                  QtGui.QIcon(os.path.join(self.here, 'media', 'server.png')), "")
        self.tabs.setTabToolTip(idx, "Server")
        # refraction
        self.tab_refraction = Refraction(prj=self.prj, main_win=self)
        idx = self.tabs.insertTab(3, self.tab_refraction,
                                  QtGui.QIcon(os.path.join(self.here, 'media', 'refraction.png')), "")
        self.tabs.setTabToolTip(idx, "Refraction Monitor")
        # server
        self.tab_settings = Settings(prj=self.prj, main_win=self)
        idx = self.tabs.insertTab(4, self.tab_settings,
                                  QtGui.QIcon(os.path.join(self.here, 'media', 'settings.png')), "")
        self.tabs.setTabToolTip(idx, "Settings")
        # info
        self.tab_info = Info(default_url='https://www.hydroffice.org/soundspeed/')
        idx = self.tabs.insertTab(5, self.tab_info,
                                  QtGui.QIcon(os.path.join(self.here, 'media', 'info.png')), "")
        self.tabs.setTabToolTip(idx, "Info")

        self.statusBar().setStyleSheet("QStatusBar{color:rgba(0,0,0,128);font-size: 8pt;}")
        self.status_bar_normal_style = self.statusBar().styleSheet()
        self.statusBar().showMessage("%s" % ssm_version, 2000)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_gui)
        timer.start(1500)

        self.data_cleared()

    def check_woa09(self):
        """ helper function that looks after WOA09 database"""
        if not self.prj.use_woa09():
            logger.debug('woa09: disabled by settings')
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
        """ helper function that looks after WOA13 database"""
        if not self.prj.use_woa13():
            logger.debug('woa13: disabled by settings')
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
        """ helper function that looks after RTOFS connection"""
        if not self.prj.use_rtofs():
            logger.debug('rtofs: disabled by settings')
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

    def check_sis(self):
        if self.prj.use_sis():
            if not self.prj.listen_sis():
                msg = 'Unable to listening SIS.'
                QtGui.QMessageBox.warning(self, "Sound Speed Manager - SIS", msg,
                                          QtGui.QMessageBox.Ok)
        else:
            if not self.prj.stop_listen_sis():
                msg = 'Unable to stop listening SIS.'
                QtGui.QMessageBox.warning(self, "Sound Speed Manager - SIS", msg,
                                          QtGui.QMessageBox.Ok)

    def check_sippican(self):
        if self.prj.use_sippican():
            if not self.prj.listen_sippican():
                msg = 'Unable to listening Sippican.'
                QtGui.QMessageBox.warning(self, "Sound Speed Manager - Sippican", msg,
                                          QtGui.QMessageBox.Ok)
        else:
            if not self.prj.stop_listen_sippican():
                msg = 'Unable to stop listening Sippican.'
                QtGui.QMessageBox.warning(self, "Sound Speed Manager - Sippican", msg,
                                          QtGui.QMessageBox.Ok)

    def check_mvp(self):
        if self.prj.use_mvp():
            if not self.prj.listen_mvp():
                msg = 'Unable to listening MVP.'
                QtGui.QMessageBox.warning(self, "Sound Speed Manager - MVP", msg,
                                          QtGui.QMessageBox.Ok)
        else:
            if not self.prj.stop_listen_mvp():
                msg = 'Unable to stop listening MVP.'
                QtGui.QMessageBox.warning(self, "Sound Speed Manager - MVP", msg,
                                          QtGui.QMessageBox.Ok)

    def data_cleared(self):
        self.tab_editor.data_cleared()
        self.tab_database.data_cleared()
        self.tab_server.data_cleared()
        self.tab_refraction.data_cleared()
        self.tab_settings.data_cleared()

    def data_imported(self):
        self.tab_editor.data_imported()
        self.tab_database.data_imported()
        self.tab_server.data_imported()
        self.tab_refraction.data_imported()
        self.tab_settings.data_imported()

    def data_stored(self):
        self.tab_editor.data_stored()
        self.tab_database.data_stored()
        self.tab_server.data_stored()
        self.tab_refraction.data_stored()
        self.tab_settings.data_stored()

    def data_removed(self):
        self.tab_editor.data_removed()
        self.tab_database.data_removed()
        self.tab_server.data_removed()
        self.tab_refraction.data_removed()
        self.tab_settings.data_removed()

    def server_started(self):
        # clear widgets as for data clear
        self.data_cleared()

        self.tab_editor.server_started()
        self.tab_database.server_started()
        self.tab_server.server_started()
        self.tab_refraction.server_started()
        self.tab_settings.server_started()
        self.statusBar().setStyleSheet("QStatusBar{color:rgba(0,0,0,128);font-size: 8pt;background-color:rgba(51,204,255,128);}")

    def server_stopped(self):
        self.tab_editor.server_stopped()
        self.tab_database.server_stopped()
        self.tab_server.server_stopped()
        self.tab_refraction.server_stopped()
        self.tab_settings.server_stopped()
        self.statusBar().setStyleSheet(self.status_bar_normal_style)

    def update_gui(self):
        msg = str()

        tokens = list()
        if self.prj.server.is_alive():
            tokens.append("SRV")
        if self.prj.has_ref():
            tokens.append("REF")
        if self.prj.use_rtofs():
            tokens.append("RTF")
        if self.prj.use_woa09():
            tokens.append("W09")
        if self.prj.use_woa13():
            tokens.append("W13")
        if self.prj.use_sippican():
            tokens.append("SIP")
        if self.prj.use_mvp():
            tokens.append("MVP")
        if self.prj.use_sis():
            tokens.append("SIS")
        msg += "|".join(tokens)

        if not self.prj.use_sis():  # in case that SIS was disabled
            self.statusBar().showMessage(msg, 1000)
            return

        msg += "  -  "  # add some spacing

        if self.prj.listeners.sis.nav is not None:
            # time stamp
            msg += "time:"
            if self.prj.listeners.sis.nav.dg_time is not None:
                msg += "%s, " % (self.prj.listeners.sis.nav.dg_time.strftime("%H:%M:%S"))

            else:
                msg += "NA, "

            # position
            msg += "pos:"
            if (self.prj.listeners.sis.nav.latitude is not None) and (self.prj.listeners.sis.nav.longitude is not None):

                latitude = self.prj.listeners.sis.nav.latitude
                if latitude >= 0:
                    letter = "N"
                else:
                    letter = "S"
                lat_min = float(60 * math.fabs(latitude - int(latitude)))
                lat_str = "%02d\N{DEGREE SIGN}%7.3f'%s" % (int(math.fabs(latitude)), lat_min, letter)

                longitude = self.prj.listeners.sis.nav.longitude
                if longitude < 0:
                    letter = "W"
                else:
                    letter = "E"
                lon_min = float(60 * math.fabs(longitude - int(longitude)))
                lon_str = "%03d\N{DEGREE SIGN}%7.3f'%s" % (int(math.fabs(longitude)), lon_min, letter)

                msg += "(%s, %s),  " % (lat_str, lon_str)

            else:
                msg += "(NA, NA),  "

        if self.prj.listeners.sis.xyz88 is not None:
            msg += 'tss:'
            if self.prj.listeners.sis.xyz88.sound_speed is not None:
                msg += '%.1f m/s,  ' % self.prj.listeners.sis.xyz88.sound_speed

            else:
                msg += 'NA m/s,  '

            msg += 'avg.depth:'
            mean_depth = self.prj.listeners.sis.xyz88.mean_depth
            if mean_depth:
                msg += '%.1f m' % mean_depth
            else:
                msg += 'NA m'

        else:
            msg += 'XYZ88 NA [pinging?]'

        self.statusBar().showMessage(msg, 2000)
        if self.prj.has_ssp():

            if self.prj.server.is_alive():  # server mode
                if not self.tab_server.dataplots.is_drawn:
                    self.tab_server.dataplots.reset()
                    self.tab_server.dataplots.on_draw()
                self.tab_server.dataplots.update_data()
                self.tab_server.dataplots.redraw()
            else:  # user mode
                if self.prj.has_mvp_to_process() or self.prj.has_sippican_to_process():
                    # logger.debug("plot drawn: %s" % self.tab_editor.dataplots.is_drawn)
                    if not self.tab_editor.dataplots.is_drawn:
                        self.data_imported()
                self.tab_editor.dataplots.update_data()
                self.tab_editor.dataplots.redraw()

        if not self.prj.server.is_alive():  # user mode - listeners
            if self.prj.has_mvp_to_process() or self.prj.has_sippican_to_process():
                self.statusBar().setStyleSheet("QStatusBar{color:rgba(0,0,0,128);font-size: 8pt;background-color:rgba(255,163,102,128);}")
            else:
                self.statusBar().setStyleSheet(self.status_bar_normal_style)

    # Quitting #

    def _do_you_really_want(self, title="Quit", text="quit"):
        """helper function that show to the user a message windows asking to confirm an action"""
        msg_box = QtGui.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setIconPixmap(QtGui.QPixmap(os.path.join(self.media, 'favicon.png')).scaled(QtCore.QSize(36, 36)))
        msg_box.setText('Do you really want to %s?' % text)
        msg_box.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        msg_box.setDefaultButton(QtGui.QMessageBox.No)
        return msg_box.exec_()

    def closeEvent(self, event):
        """ actions to be done before close the app """
        reply = self._do_you_really_want("Quit", "quit %s" % self.name)
        # reply = QtGui.QMessageBox.Yes
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
            self.prj.close()
            super(MainWin, self).closeEvent(event)
        else:
            event.ignore()

    # -------------------------- development-only --------------------------

    def do(self):
        """ development-mode only helper function """
        from hydroffice.soundspeed.base import helper
        data_input = helper.get_testing_input_folder()
        data_sub_folders = helper.get_testing_input_subfolders()

        def pair_reader_and_folder(folders, readers):
            """ create pairs of folder and reader"""
            pairs = dict()
            for folder in folders:
                for reader in readers:
                    if reader.name.lower() != 'sippican':  # reader filter
                        continue
                    if reader.name.lower() != folder.lower():  # skip not matching readers
                        continue
                    pairs[folder] = reader
            logger.info('pairs: %s' % pairs.keys())
            return pairs

        def list_test_files(data_input, pairs):
            """ create a dictionary of test file and reader to use with """
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
        self.prj.import_data(data_path=tests.keys()[8], data_format=tests[tests.keys()[8]].name)
        self.data_imported()
