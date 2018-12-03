import logging
import math
import os
import socket
import ssl
import sys
import traceback
from urllib.error import URLError
from urllib.request import urlopen

from PySide2 import QtCore, QtGui, QtWidgets

from hyo2.abc.app.qt_progress import QtProgress
from hyo2.abc.app.dialogs.exception.exception_dialog import ExceptionDialog
from hyo2.abc.app.tabs.info.info_tab import InfoTab
from hyo2.abc.lib.helper import Helper

from hyo2.soundspeed import lib_info
from hyo2.soundspeedmanager import app_info

# from hyo2.soundspeedmanager import __version__ as ssm_version
# from hyo2.soundspeedmanager import __doc__ as ssm_name
from hyo2.soundspeed.soundspeed import SoundSpeedLibrary

# from hyo2.soundspeed.base.helper import is_pydro, info_libs, web_url
from hyo2.soundspeedmanager.qt_callbacks import QtCallbacks

from hyo2.soundspeedmanager.widgets.editor import Editor
from hyo2.soundspeedmanager.widgets.database import Database
from hyo2.soundspeedmanager.widgets.server import Server
from hyo2.soundspeedmanager.widgets.refraction import Refraction
from hyo2.soundspeedmanager.widgets.settings import Settings

# from hyo2.soundspeedmanager.widgets.info import Info

logger = logging.getLogger(__name__)


class MainWin(QtWidgets.QMainWindow):
    here = os.path.abspath(os.path.dirname(__file__))
    media = os.path.join(here, "media")

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)

        logger.info("* > APP: initializing ...")

        # set the application name and the version
        self.name = app_info.app_name
        self.version = app_info.app_version
        self.setWindowTitle('%s v.%s' % (self.name, self.version))
        # noinspection PyArgumentList
        _app = QtCore.QCoreApplication.instance()
        _app.setApplicationName('%s' % self.name)
        _app.setOrganizationName("HydrOffice")
        _app.setOrganizationDomain("hydroffice.org")

        # set the minimum and the initial size
        self.setMinimumSize(640, 480)
        self.resize(920, 600)

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

        # check if setup db exists; if yes, ask to copy
        has_setup = SoundSpeedLibrary.setup_exists()
        logger.info("setup exists: %s" % has_setup)
        if not has_setup:
            other_setups = SoundSpeedLibrary.list_other_setups()
            if len(other_setups) != 0:
                logger.debug("other existing setups: %d" % len(other_setups))
                # noinspection PyCallByClass
                sel, ok = QtWidgets.QInputDialog.getItem(self, 'Do you want to copy an existing setup?',
                                                         'Select one (or click on Cancel to create a new one):',
                                                         other_setups, 0, False)
                if ok:
                    SoundSpeedLibrary.copy_setup(input_setup=sel)

        # create the project
        self.lib = SoundSpeedLibrary(callbacks=QtCallbacks(parent=self), progress=QtProgress(parent=self))
        logger.info("current configuration:\n%s" % Helper(lib_info=lib_info).package_info())
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
            settings.setValue("export_folder", self.lib.data_folder)
        import_folder = settings.value("import_folder")
        if (import_folder is None) or (not os.path.exists(import_folder)):
            settings.setValue("import_folder", self.lib.data_folder)

        # menu

        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")
        self.edit_menu = self.menu.addMenu("Process")
        self.database_menu = self.menu.addMenu("Database")
        self.monitor_menu = self.menu.addMenu("Monitor")
        self.server_menu = self.menu.addMenu("Server")
        self.setup_menu = self.menu.addMenu("Setup")
        self.help_menu = self.menu.addMenu("Help")

        # make tabs
        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.setIconSize(QtCore.QSize(42, 42))
        self.tabs.blockSignals(True)  # during the initialization
        # noinspection PyUnresolvedReferences
        self.tabs.currentChanged.connect(self.onChange)  # changed!
        # editor
        self.tab_editor = Editor(lib=self.lib, main_win=self)
        self.idx_editor = self.tabs.insertTab(0, self.tab_editor,
                                              QtGui.QIcon(os.path.join(self.here, 'media', 'editor.png')), "")
        self.tabs.setTabToolTip(self.idx_editor, "Editor")
        # database
        self.tab_database = Database(lib=self.lib, main_win=self)
        self.idx_database = self.tabs.insertTab(1, self.tab_database,
                                                QtGui.QIcon(os.path.join(self.here, 'media', 'database.png')), "")
        self.tabs.setTabToolTip(self.idx_database, "Database")
        # survey data monitor
        self.has_sdm_support = True
        try:  # try.. except to make SSM working also without SDM
            # noinspection PyUnresolvedReferences
            from hyo2.surveydatamonitor.app.widgets.monitor import SurveyDataMonitor
            self.tab_monitor = SurveyDataMonitor(lib=self.lib, main_win=self)
            self.idx_monitor = self.tabs.insertTab(3, self.tab_monitor,
                                                   QtGui.QIcon(
                                                       os.path.join(self.here, 'media', 'surveydatamonitor.png')), "")
            self.tabs.setTabToolTip(self.idx_monitor, "Survey Data Monitor")
            logger.info("Support for Survey Monitor: ON")
        except Exception as e:
            traceback.print_exc()
            self.has_sdm_support = False
            logger.info("Support for Survey Monitor: OFF(%s)" % e)
        # server
        self.tab_server = Server(lib=self.lib, main_win=self)
        self.idx_server = self.tabs.insertTab(4, self.tab_server,
                                              QtGui.QIcon(os.path.join(self.here, 'media', 'server.png')), "")
        self.tabs.setTabToolTip(self.idx_server, "Synthetic Profile Server")

        # refraction
        # self.tab_refraction = Refraction(lib=self.lib, main_win=self)
        # idx = self.tabs.insertTab(5, self.tab_refraction,
        #                           QtGui.QIcon(os.path.join(self.here, 'media', 'refraction.png')), "")
        # self.tabs.setTabToolTip(idx, "Refraction Monitor")
        # setup
        self.tab_setup = Settings(lib=self.lib, main_win=self)
        self.idx_setup = self.tabs.insertTab(6, self.tab_setup,
                                             QtGui.QIcon(os.path.join(self.here, 'media', 'settings.png')), "")
        self.tabs.setTabToolTip(self.idx_setup, "Setup")
        # info
        self.tab_info = InfoTab(main_win=self, lib_info=lib_info, app_info=app_info,
                                with_online_manual=True,
                                with_offline_manual=True,
                                with_bug_report=True,
                                with_hydroffice_link=True,
                                with_ccom_link=True,
                                with_noaa_link=True,
                                with_unh_link=True,
                                with_license=True)
        self.idx_info = self.tabs.insertTab(6, self.tab_info,
                                            QtGui.QIcon(os.path.join(self.here, 'media', 'info.png')), "")
        self.tabs.setTabToolTip(self.idx_info, "Info")
        # Help menu
        self.help_menu.addAction(self.tab_info.open_online_manual_action)
        self.help_menu.addAction(self.tab_info.open_offline_manual_action)
        self.help_menu.addAction(self.tab_info.fill_bug_report_action)
        self.help_menu.addAction(self.tab_info.authors_action)
        self.help_menu.addAction(self.tab_info.show_about_action)

        self.statusBar().setStyleSheet("QStatusBar{color:rgba(0,0,0,128);font-size: 8pt;}")
        self.status_bar_normal_style = self.statusBar().styleSheet()
        self.statusBar().showMessage("%s" % app_info.app_name, 2000)
        self.releaseInfo = QtWidgets.QLabel()
        self.statusBar().addPermanentWidget(self.releaseInfo)
        self.releaseInfo.setStyleSheet("QLabel{color:rgba(0,0,0,128);font-size: 8pt;}")
        timer = QtCore.QTimer(self)
        # noinspection PyUnresolvedReferences
        timer.timeout.connect(self.update_gui)
        timer.start(1500)
        self.timer_execs = 0

        self.data_cleared()
        self.tabs.blockSignals(False)

        logger.info("* > APP: initialized!")

    def onChange(self, i):
        # logger.debug("Current Tab Index: %s" % type(self.tabs.widget(i)))
        if type(self.tabs.widget(i)) == Settings:
            self.tab_setup.setup_changed()

    def switch_to_editor_tab(self):
        if self.tabs.currentIndex() != self.idx_editor:
            self.tabs.setCurrentIndex(self.idx_editor)

    def switch_to_database_tab(self):
        if self.tabs.currentIndex() != self.idx_database:
            self.tabs.setCurrentIndex(self.idx_database)

    def switch_to_monitor_tab(self):
        if self.tabs.currentIndex() != self.idx_monitor:
            self.tabs.setCurrentIndex(self.idx_monitor)

    def switch_to_server_tab(self):
        if self.tabs.currentIndex() != self.idx_server:
            self.tabs.setCurrentIndex(self.idx_server)

    def switch_to_setup_tab(self):
        if self.tabs.currentIndex() != self.idx_setup:
            self.tabs.setCurrentIndex(self.idx_setup)

    def switch_to_info_tab(self):
        if self.tabs.currentIndex() != self.idx_info:
            self.tabs.setCurrentIndex(self.idx_info)

    def check_woa09(self):
        """ helper function that looks after WOA09 database"""
        if not self.lib.use_woa09():
            logger.debug('WOA09: disabled by settings')
            return

        if self.lib.has_woa09():
            logger.debug('WOA09: enabled')
            return

        msg = 'The WOA09 atlas is required by some advanced application functions.\n\n' \
              'The data set (~120MB) can be retrieved from:\n' \
              '   ftp.ccom.unh.edu/fromccom/hydroffice/woa09.red.zip\n' \
              'then unzipped it into:\n' \
              '   %s\n\n' \
              'Do you want that I perform this operation for you?\n' \
              'Internet connection is required!\n' % self.lib.woa09_folder
        # noinspection PyCallByClass
        ret = QtWidgets.QMessageBox.information(self, "Sound Speed Manager - WOA09 Atlas", msg,
                                                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.No)
        if ret == QtWidgets.QMessageBox.No:
            msg = 'You can also manually install it. The steps are:\n' \
                  ' - download the archive from (anonymous ftp):\n' \
                  '   ftp.ccom.unh.edu/fromccom/hydroffice/woa09.red.zip\n' \
                  ' - unzip the archive into:\n' \
                  '   %s\n' \
                  ' - restart Sound Speed Manager\n' % self.lib.woa09_folder
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.information(self, "Sound Speed Manager - WOA09 Atlas", msg,
                                              QtWidgets.QMessageBox.Ok)
            logger.debug('WOA09: disabled')
            return

        success = self.lib.download_woa09()
        if not success:
            msg = 'Unable to retrieve the WOA09 atlas.\n\n ' \
                  'You may manually install it. The steps are:\n' \
                  ' - download the archive from (anonymous ftp):\n' \
                  '   ftp.ccom.unh.edu/fromccom/hyo/woa09.red.zip\n' \
                  ' - unzip the archive into:\n' \
                  '   %s\n' \
                  ' - restart Sound Speed Manager\n' % self.lib.woa09_folder
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.warning(self, "Sound Speed Manager - WOA09 Atlas", msg,
                                          QtWidgets.QMessageBox.Ok)
            logger.debug('WOA09: disabled')
            return

        logger.debug('WOA09: enabled')

    def check_woa13(self):
        """ helper function that looks after WOA13 database"""
        if not self.lib.use_woa13():
            logger.debug('WOA13: disabled by settings')
            return

        if self.lib.has_woa13():
            logger.debug('WOA13: enabled')
            return

        msg = 'The WOA13 atlas is required by some advanced application functions.\n\n' \
              'The data set (~4GB) can be retrieved from:\n' \
              '   ftp.ccom.unh.edu/fromccom/hydroffice/woa13_temp.red.zip\n' \
              '   ftp.ccom.unh.edu/fromccom/hydroffice/woa13_sal.red.zip\n' \
              'then unzipped it into:\n' \
              '   %s\n\n' \
              'Do you want that I perform this operation for you?\n' \
              'Internet connection is required!\n' % self.lib.woa13_folder
        # noinspection PyCallByClass
        ret = QtWidgets.QMessageBox.information(self, "Sound Speed Manager - WOA13 Atlas", msg,
                                                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.No)
        if ret == QtWidgets.QMessageBox.No:
            msg = 'You can also manually install it. The steps are:\n' \
                  ' - download the archive from (anonymous ftp):\n' \
                  '   ftp.ccom.unh.edu/fromccom/hydroffice/woa13_temp.red.zip\n' \
                  '   ftp.ccom.unh.edu/fromccom/hydroffice/woa13_sal.red.zip\n' \
                  ' - unzip the archive into:\n' \
                  '   %s\n' \
                  ' - restart Sound Speed Manager\n' % self.lib.woa13_folder
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.information(self, "Sound Speed Manager - WOA13 Atlas", msg,
                                              QtWidgets.QMessageBox.Ok)
            logger.debug('WOA13: disabled')
            return

        success = self.lib.download_woa13()
        if not success:
            msg = 'Unable to retrieve the WOA13 atlas.\n\n ' \
                  'You may manually install it. The steps are:\n' \
                  ' - download the archive from (anonymous ftp):\n' \
                  '   ftp.ccom.unh.edu/fromccom/hyo/woa13_temp.red.zip\n' \
                  '   ftp.ccom.unh.edu/fromccom/hyo/woa13_sal.red.zip\n' \
                  ' - unzip the archive into:\n' \
                  '   %s\n' \
                  ' - restart Sound Speed Manager\n' % self.lib.woa13_folder
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.warning(self, "Sound Speed Manager - WOA13 Atlas", msg,
                                          QtWidgets.QMessageBox.Ok)
            logger.debug('WOA13: disabled')
            return

        logger.debug('WOA13: enabled')

    def check_rtofs(self):
        """ helper function that looks after RTOFS connection"""
        if not self.lib.use_rtofs():
            logger.debug('RTOFS: disabled by settings')
            return

        if self.lib.has_rtofs():
            logger.debug('RTOFS: enabled')
            return

        success = self.lib.download_rtofs()
        if not success:
            msg = 'Unable to retrieve the RTOFS atlas.\n\n ' \
                  'The application needs an internet connection to access\n' \
                  'this server (with port 9090 open):\n' \
                  ' - http://nomads.ncep.noaa.gov:9090\n\n' \
                  'You can disable the RTOFS support in Settings/Basic/Use RTOFS.\n'
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.warning(self, "Sound Speed Manager - RTOFS Atlas", msg,
                                          QtWidgets.QMessageBox.Ok)
            logger.debug('RTOFS: disabled')
            return

        logger.debug('RTOFS: enabled')

    def check_sis(self):
        if self.lib.use_sis():
            if not self.lib.listen_sis():
                msg = 'Unable to listen SIS.'
                # noinspection PyCallByClass
                QtWidgets.QMessageBox.warning(self, "Sound Speed Manager - SIS", msg,
                                              QtWidgets.QMessageBox.Ok)
        else:
            if not self.lib.stop_listen_sis():
                msg = 'Unable to stop listening SIS.'
                # noinspection PyCallByClass
                QtWidgets.QMessageBox.warning(self, "Sound Speed Manager - SIS", msg,
                                              QtWidgets.QMessageBox.Ok)

    def check_sippican(self):
        if self.lib.use_sippican():
            if not self.lib.listen_sippican():
                msg = 'Unable to listening Sippican.'
                # noinspection PyCallByClass
                QtWidgets.QMessageBox.warning(self, "Sound Speed Manager - Sippican", msg,
                                              QtWidgets.QMessageBox.Ok)
        else:
            if not self.lib.stop_listen_sippican():
                msg = 'Unable to stop listening Sippican.'
                # noinspection PyCallByClass
                QtWidgets.QMessageBox.warning(self, "Sound Speed Manager - Sippican", msg,
                                              QtWidgets.QMessageBox.Ok)

    def check_mvp(self):
        if self.lib.use_mvp():
            if not self.lib.listen_mvp():
                msg = 'Unable to listening MVP.'
                # noinspection PyCallByClass
                QtWidgets.QMessageBox.warning(self, "Sound Speed Manager - MVP", msg,
                                              QtWidgets.QMessageBox.Ok)
        else:
            if not self.lib.stop_listen_mvp():
                msg = 'Unable to stop listening MVP.'
                # noinspection PyCallByClass
                QtWidgets.QMessageBox.warning(self, "Sound Speed Manager - MVP", msg,
                                              QtWidgets.QMessageBox.Ok)

    def data_cleared(self):
        self.tab_editor.data_cleared()
        self.tab_database.data_cleared()
        self.tab_server.data_cleared()
        # self.tab_refraction.data_cleared()
        self.tab_setup.data_cleared()

    def data_imported(self):
        self.tab_editor.data_imported()
        self.tab_database.data_imported()
        self.tab_server.data_imported()
        # self.tab_refraction.data_imported()
        self.tab_setup.data_imported()

    def data_stored(self):
        self.tab_editor.data_stored()
        self.tab_database.data_stored()
        self.tab_server.data_stored()
        # self.tab_refraction.data_stored()
        self.tab_setup.data_stored()

    def data_removed(self):
        self.tab_editor.data_removed()
        self.tab_database.data_removed()
        self.tab_server.data_removed()
        # self.tab_refraction.data_removed()
        self.tab_setup.data_removed()

    def server_started(self):
        # clear widgets as for data clear
        self.data_cleared()

        self.tab_editor.server_started()
        self.tab_database.server_started()
        self.tab_server.server_started()
        # self.tab_refraction.server_started()
        self.tab_setup.server_started()
        self.statusBar().setStyleSheet("QStatusBar{color:rgba(0,0,0,128);"
                                       "font-size: 8pt;background-color:rgba(51,204,255,128);}")

    def server_stopped(self):
        self.tab_editor.server_stopped()
        self.tab_database.server_stopped()
        self.tab_server.server_stopped()
        # self.tab_refraction.server_stopped()
        self.tab_setup.server_stopped()
        self.statusBar().setStyleSheet(self.status_bar_normal_style)

    def _check_latest_release(self):

        new_release = False
        new_bugfix = False
        latest_version = None
        try:
            response = urlopen('http://www.hydroffice.org/latest/soundspeedmanager.txt', timeout=2)
            latest_version = response.read().split()[0].decode()

            cur_maj, cur_min, cur_fix = app_info.app_version.split('.')
            lat_maj, lat_min, lat_fix = latest_version.split('.')

            if int(lat_maj) > int(cur_maj):
                new_release = True

            elif (int(lat_maj) == int(cur_maj)) and (int(lat_min) > int(cur_min)):
                new_release = True

            elif (int(lat_maj) == int(cur_maj)) and (int(lat_min) == int(cur_min)) and (int(lat_fix) > int(cur_fix)):
                new_bugfix = True

        except (URLError, ssl.SSLError, socket.timeout, ConnectionResetError, ValueError) as e:
            logger.info("unable to check latest release (reason: %s)" % e)

        if new_release:
            logger.info("new release available: %s" % latest_version)
            self.releaseInfo.setText("New release available: %s" % latest_version)
            self.releaseInfo.setStyleSheet("QLabel{background-color:rgba(255,0,0,128);"
                                           "color:rgba(0,0,0,128);"
                                           "font-size: 8pt;}")

        elif new_bugfix:
            logger.info("new bugfix available: %s" % latest_version)
            self.releaseInfo.setText("New bugfix available: %s" % latest_version)
            self.releaseInfo.setStyleSheet("QLabel{background-color:rgba(255,255,0,128);"
                                           "color:rgba(0,0,0,128);"
                                           "font-size: 8pt;}")

    def update_gui(self):

        if self.timer_execs % 200 == 0:
            # logger.debug("timer executions: %d" % self.timer_execs)
            self._check_latest_release()

        self.timer_execs += 1

        # if self.lib.setup.noaa_tools:
        #     self.tab_seacat.setEnabled(True)
        # else:
        #     self.tab_seacat.setDisabled(True)

        # update the windows title
        self.setWindowTitle('%s v.%s [project: %s]' % (self.name, self.version, self.lib.current_project))

        msg = str()

        tokens = list()
        if self.lib.server.is_alive():
            tokens.append("SRV")
        if self.lib.has_ref():
            tokens.append("REF")
        if self.lib.use_rtofs():
            tokens.append("RTF")
        if self.lib.use_woa09():
            tokens.append("W09")
        if self.lib.use_woa13():
            tokens.append("W13")
        if self.lib.use_sippican():
            tokens.append("SIP")
        if self.lib.use_mvp():
            tokens.append("MVP")
        if self.lib.use_sis():
            tokens.append("SIS")
        msg += "|".join(tokens)

        if not self.lib.use_sis():  # in case that SIS was disabled
            self.statusBar().showMessage(msg, 1000)
            return

        msg += "  -  "  # add some spacing

        if self.lib.listeners.sis.nav is not None:
            # time stamp
            msg += "time:"
            if self.lib.listeners.sis.nav.dg_time is not None:
                msg += "%s, " % (self.lib.listeners.sis.nav.dg_time.strftime("%H:%M:%S"))

            else:
                msg += "NA, "

            # position
            msg += "pos:"
            if (self.lib.listeners.sis.nav.latitude is not None) and (self.lib.listeners.sis.nav.longitude is not None):

                latitude = self.lib.listeners.sis.nav.latitude
                if latitude >= 0:
                    letter = "N"
                else:
                    letter = "S"
                lat_min = float(60 * math.fabs(latitude - int(latitude)))
                lat_str = "%02d\N{DEGREE SIGN}%7.3f'%s" % (int(math.fabs(latitude)), lat_min, letter)

                longitude = self.lib.listeners.sis.nav.longitude
                if longitude < 0:
                    letter = "W"
                else:
                    letter = "E"
                lon_min = float(60 * math.fabs(longitude - int(longitude)))
                lon_str = "%03d\N{DEGREE SIGN}%7.3f'%s" % (int(math.fabs(longitude)), lon_min, letter)

                msg += "(%s, %s),  " % (lat_str, lon_str)

            else:
                msg += "(NA, NA),  "

        if self.lib.listeners.sis.xyz88 is not None:
            msg += 'tss:'
            if self.lib.listeners.sis.xyz88.sound_speed is not None:
                msg += '%.1f m/s,  ' % self.lib.listeners.sis.xyz88.sound_speed

            else:
                msg += 'NA m/s,  '

            msg += 'avg.depth:'
            mean_depth = self.lib.listeners.sis.xyz88.mean_depth
            if mean_depth:
                msg += '%.1f m' % mean_depth
            else:
                msg += 'NA m'

        else:
            msg += 'XYZ88 NA [pinging?]'

        self.statusBar().showMessage(msg, 2000)
        if self.lib.has_ssp():

            if self.lib.server.is_alive():  # server mode
                if not self.tab_server.dataplots.is_drawn:
                    self.tab_server.dataplots.reset()
                    self.tab_server.dataplots.on_first_draw()

                self.tab_server.dataplots.update_data()
                self.tab_server.dataplots.redraw()

            else:  # user mode
                if self.lib.has_mvp_to_process() or self.lib.has_sippican_to_process():
                    # logger.debug("data to import from listeners")
                    # logger.debug("plot drawn: %s" % self.tab_editor.dataplots.is_drawn)
                    if not self.tab_editor.dataplots.is_drawn:
                        self.data_imported()

                    if self.lib.cur.listener_completed and not self.lib.cur.listener_displayed:
                        self.tab_editor.dataplots.on_first_draw()
                        self.lib.cur.listener_displayed = True

                self.tab_editor.dataplots.update_data()
                self.tab_editor.dataplots.redraw()

        if not self.lib.server.is_alive():  # user mode - listeners
            if self.lib.has_mvp_to_process() or self.lib.has_sippican_to_process():
                self.statusBar().setStyleSheet("QStatusBar{color:rgba(0,0,0,128);"
                                               "font-size: 8pt;background-color:rgba(255,163,102,128);}")
            else:
                self.statusBar().setStyleSheet(self.status_bar_normal_style)

    def change_info_url(self, url):
        self.tab_info.change_url(url)

    def exception_hook(self, ex_type: type, ex_value: BaseException, tb: traceback) -> None:
        sys.__excepthook__(ex_type, ex_value, tb)

        # first manage case of not being an exception (e.g., keyboard interrupts)
        if not issubclass(ex_type, Exception):
            msg = str(ex_value)
            if not msg:
                msg = ex_value.__class__.__name__
            logger.info(msg)
            self.close()
            return

        dlg = ExceptionDialog(app_info=app_info, lib_info=lib_info, ex_type=ex_type, ex_value=ex_value, tb=tb)
        ret = dlg.exec_()
        if ret == QtWidgets.QDialog.Rejected:
            if not dlg.user_triggered:
                self.close()
        else:
            logger.warning("ignored exception")

    # Quitting #

    def _do_you_really_want(self, title="Quit", text="quit"):
        """helper function that show to the user a message windows asking to confirm an action"""
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setIconPixmap(QtGui.QPixmap(os.path.join(self.media, 'favicon.png')).scaled(QtCore.QSize(36, 36)))
        msg_box.setText('Do you really want to %s?' % text)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msg_box.setDefaultButton(QtWidgets.QMessageBox.No)
        return msg_box.exec_()

    def closeEvent(self, event):
        """ actions to be done before close the app """
        reply = self._do_you_really_want("Quit", "quit %s" % app_info.app_name)
        # reply = QtWidgets.QMessageBox.Yes
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
            self.lib.close()
            if self.has_sdm_support:
                self.tab_monitor.stop_plotting()
            super(MainWin, self).closeEvent(event)
        else:
            event.ignore()

    # -------------------------- development-only --------------------------

    def do(self):
        """ development-mode only helper function """
        pass
