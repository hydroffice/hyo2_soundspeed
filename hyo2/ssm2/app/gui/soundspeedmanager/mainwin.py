import logging
import math
import os
import sys
import traceback
from datetime import datetime, UTC
from urllib.request import urlopen

from PySide6 import QtCore, QtGui, QtWidgets


from hyo2.abc2.app.pkg_info.pkg_exception.pkg_exception_dialog import PkgExceptionDialog
from hyo2.abc2.app.pkg_info.pkg_info_tab import PkgInfoTab
from hyo2.abc2.app.qt_progress import QtProgress
from hyo2.abc2.lib.package.pkg_helper import PkgHelper
from hyo2.ssm2.app.gui.soundspeedmanager import app_info
from hyo2.ssm2.app.gui.soundspeedmanager.qt_callbacks import QtCallbacks
from hyo2.ssm2.app.gui.soundspeedmanager.widgets.database import Database
from hyo2.ssm2.app.gui.soundspeedmanager.widgets.editor import Editor
from hyo2.ssm2.app.gui.soundspeedmanager.widgets.server import Server
from hyo2.ssm2.app.gui.soundspeedmanager.widgets.settings import Settings
from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary

logger = logging.getLogger(__name__)


class MainWin(QtWidgets.QMainWindow):

    def __init__(self, use_sdm4: bool = False):
        QtWidgets.QMainWindow.__init__(self)

        os.environ.get("SSM_DEBUG") and logger.info("Main Windows init ...")

        # set the application name and the version
        self.name = app_info.app_name
        self.version = app_info.app_version
        if app_info.app_beta:
            self.version += ' BETA'
        self.setWindowTitle('%s v.%s' % (self.name, self.version))
        # noinspection PyArgumentList
        _app = QtCore.QCoreApplication.instance()
        _app.setApplicationName('%s' % self.name)
        _app.setOrganizationName("HydrOffice")
        _app.setOrganizationDomain("hydroffice.org")

        # set the minimum and the initial size
        # noinspection PyArgumentList
        self.setMinimumSize(640, 480)
        # noinspection PyArgumentList
        self.resize(920, 640)

        # set icons
        self.setWindowIcon(QtGui.QIcon(app_info.app_icon_path))

        # check if setup db exists; if yes, ask to copy
        has_setup = SoundSpeedLibrary.setup_exists()
        logger.info("setup exists: %s [%s]" % (has_setup, SoundSpeedLibrary.setup_path()))
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
        if use_sdm4:
            app_info.edit_deps_dict(delete_key="hyo2.sdm3", new_key="hyo2.sdm4", new_value="hyo2.sdm4")
        logger.info("current configuration:\n%s" % PkgHelper(pkg_info=app_info).pkg_info())
        self.check_woa09()
        self.check_woa13()
        self.check_woa18()
        self.check_woa23()
        self.check_sis()
        self.check_sippican()
        self.check_nmea()
        self.check_mvp()

        # init default settings
        settings = QtCore.QSettings()
        export_folder = settings.value("export_folder")
        if export_folder is None:
            settings.setValue("export_folder", self.lib.data_folder)
        elif not os.path.exists(str(export_folder)):
            settings.setValue("export_folder", self.lib.data_folder)
        import_folder = settings.value("import_folder")
        if import_folder is None:
            settings.setValue("import_folder", self.lib.data_folder)
        elif not os.path.exists(str(import_folder)):
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
        self.tabs.currentChanged.connect(self.on_change)  # changed!
        # editor
        self.tab_editor = Editor(lib=self.lib, main_win=self)
        # noinspection PyArgumentList
        self.idx_editor = self.tabs.insertTab(0, self.tab_editor,
                                              QtGui.QIcon(os.path.join(app_info.app_media_path, 'editor.png')), "")
        self.tabs.setTabToolTip(self.idx_editor, "Editor")
        # database
        self.tab_database = Database(lib=self.lib, main_win=self)
        # noinspection PyArgumentList
        self.idx_database = self.tabs.insertTab(1, self.tab_database,
                                                QtGui.QIcon(os.path.join(app_info.app_media_path, 'database.png')), "")
        self.tabs.setTabToolTip(self.idx_database, "Database")
        # survey data monitor
        self.has_sdm_support = True
        try:  # try.. except to make SSM working also without SDM
            if use_sdm4:
                # noinspection PyUnresolvedReferences
                from hyo2.sdm4.app.gui.surveydatamonitor.widgets.monitor import SurveyDataMonitor
            else:
                # noinspection PyUnresolvedReferences
                from hyo2.sdm3.app.gui.surveydatamonitor.widgets.monitor import SurveyDataMonitor

            self.tab_monitor = SurveyDataMonitor(lib=self.lib, main_win=self)
            # noinspection PyArgumentList
            self.idx_monitor = self.tabs.insertTab(3, self.tab_monitor,
                                                   QtGui.QIcon(
                                                       os.path.join(app_info.app_media_path, 'surveydatamonitor.png')),
                                                   "")
            self.tabs.setTabToolTip(self.idx_monitor, "Survey Data Monitor")
            logger.info("Support for Survey Monitor: ON %s" % ("[BETA]" if use_sdm4 else ""))
        except Exception as e:
            # traceback.print_exc()
            self.has_sdm_support = False
            logger.info("Support for Survey Monitor: OFF [%s]" % e, exc_info=True)
        # server
        self.tab_server = Server(lib=self.lib, main_win=self)
        # noinspection PyArgumentList
        self.idx_server = self.tabs.insertTab(4, self.tab_server,
                                              QtGui.QIcon(os.path.join(app_info.app_media_path, 'server.png')), "")
        self.tabs.setTabToolTip(self.idx_server, "Synthetic Profile Server")

        # setup
        self.tab_setup = Settings(lib=self.lib, main_win=self)
        # noinspection PyArgumentList
        self.idx_setup = self.tabs.insertTab(6, self.tab_setup,
                                             QtGui.QIcon(os.path.join(app_info.app_media_path, 'settings.png')), "")
        self.tabs.setTabToolTip(self.idx_setup, "Setup")
        # info
        self.tab_info = PkgInfoTab(main_win=self, app_info=app_info,
                                   with_online_manual=True,
                                   with_offline_manual=True,
                                   with_bug_report=True,
                                   with_hydroffice_link=True,
                                   with_ccom_link=True,
                                   with_noaa_link=True,
                                   with_unh_link=True,
                                   with_license=True)
        # noinspection PyArgumentList
        self.idx_info = self.tabs.insertTab(6, self.tab_info,
                                            QtGui.QIcon(os.path.join(app_info.app_media_path, 'info.png')), "")
        self.tabs.setTabToolTip(self.idx_info, "Info")
        # Help menu
        self.help_menu.addAction(self.tab_info.open_online_manual_action)
        self.help_menu.addAction(self.tab_info.open_offline_manual_action)
        self.help_menu.addAction(self.tab_info.fill_bug_report_action)
        self.help_menu.addAction(self.tab_info.authors_action)
        self.help_menu.addAction(self.tab_info.show_about_action)

        self.normal_stylesheet = "QStatusBar{color:rgba(0,0,0,128);font-size: 8pt;" \
                                 "background-color:rgba(0,0,0,0);}"
        self.orange_stylesheet = "QStatusBar{color:rgba(0,0,0,128);font-size: 8pt;" \
                                 "background-color:rgba(255,163,102,128);}"
        self.purple_stylesheet = "QStatusBar{color:rgba(0,0,0,128);font-size: 8pt;" \
                                 "background-color:rgba(221,160,221,128);}"
        self.khaki_stylesheet = "QStatusBar{color:rgba(0,0,0,128);font-size: 8pt;" \
                                "background-color:rgba(240,230,140,128);}"
        self.red_stylesheet = "QStatusBar{color:rgba(0,0,0,128);font-size: 8pt;" \
                              "background-color:rgba(255,0,0,128);}"
        self.yellow_stylesheet = "QStatusBar{color:rgba(0,0,0,128);font-size: 8pt;" \
                                 "background-color:rgba(255,255,0,128);}"
        self.cyan_stylesheet = "QStatusBar{color:rgba(0,0,0,128);font-size: 8pt;" \
                               "background-color:rgba(51,204,255,128);}"
        self.statusBar().setStyleSheet(self.normal_stylesheet)
        self.statusBar().showMessage("%s" % app_info.app_name, 2000)
        self.releaseInfo = QtWidgets.QLabel()
        self.statusBar().addPermanentWidget(self.releaseInfo)
        self.releaseInfo.setStyleSheet(self.normal_stylesheet)
        self.release_checked = False
        self.old_sis_xyz_data = False
        self.old_sis_nav_data = False
        self.old_nmea_nav_data = False
        timer = QtCore.QTimer(self)
        # noinspection PyUnresolvedReferences
        timer.timeout.connect(self.update_gui)
        # noinspection PyArgumentList
        timer.start(2000)
        self.timer_execs = 0

        self.data_cleared()
        self.tabs.blockSignals(False)

        # using in app tests
        self.skip_do_you_really_quit = False

        os.environ.get("SSM_DEBUG") and logger.info("* > APP: initialized!")

    def on_change(self, i):
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
            os.environ.get("SSM_DEBUG") and logger.debug('WOA09: disabled by settings')
            return

        if self.lib.has_woa09():
            os.environ.get("SSM_DEBUG") and logger.debug('WOA09: enabled')
            return

        msg = 'The WOA09 atlas is required by some advanced application functions.\n\n' \
              'The data set (~120MB) can be retrieved from:\n' \
              '   https://1drv.ms/u/c/3579835830bc10b0/EXg1dSjUVtlPkv1uN0KY3NEBoTCeO-IaQkfigxaTV7948w?e=TakkyO\n' \
              'then unzipped it into:\n' \
              '   %s\n\n' \
              'Do you want that I perform this operation for you?\n' \
              'Internet connection is required!\n' % self.lib.woa09_folder
        # noinspection PyCallByClass,PyArgumentList,PyUnresolvedReferences

        ret = QtWidgets.QMessageBox.information(
            self, "Sound Speed Manager - WOA09 Atlas", msg,
            QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.No)
        if ret == QtWidgets.QMessageBox.StandardButton.No:
            msg = 'You can also manually install it. The steps are:\n' \
                  ' - download the archive from:\n' \
                  '   https://1drv.ms/u/c/3579835830bc10b0/EXg1dSjUVtlPkv1uN0KY3NEBoTCeO-IaQkfigxaTV7948w?e=TakkyO\n' \
                  ' - unzip the archive into:\n' \
                  '   %s\n' \
                  ' - restart Sound Speed Manager\n' % self.lib.woa09_folder
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.information(self, "Sound Speed Manager - WOA09 Atlas", msg,
                                              QtWidgets.QMessageBox.StandardButton.Ok)
            os.environ.get("SSM_DEBUG") and logger.debug('WOA09: disabled')
            return

        success = self.lib.download_woa09()
        if not success:
            msg = 'Unable to retrieve the WOA09 atlas.\n\n ' \
                  'You may manually install it. The steps are:\n' \
                  ' - download the archive from:\n' \
                  '   https://1drv.ms/u/c/3579835830bc10b0/EXg1dSjUVtlPkv1uN0KY3NEBoTCeO-IaQkfigxaTV7948w?e=TakkyO\n' \
                  ' - unzip the archive into:\n' \
                  '   %s\n' \
                  ' - restart Sound Speed Manager\n' % self.lib.woa09_folder
            # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
            QtWidgets.QMessageBox.warning(self, "Sound Speed Manager - WOA09 Atlas", msg,
                                          QtWidgets.QMessageBox.StandardButton.Ok)
            os.environ.get("SSM_DEBUG") and logger.debug('WOA09: disabled')
            return

        os.environ.get("SSM_DEBUG") and logger.debug('WOA09: enabled')

    def check_woa13(self):
        """ helper function that looks after WOA13 database"""
        if not self.lib.use_woa13():
            os.environ.get("SSM_DEBUG") and logger.debug('WOA13: disabled by settings')
            return

        if self.lib.has_woa13():
            os.environ.get("SSM_DEBUG") and logger.debug('WOA13: enabled')
            return

        msg = 'The WOA13 atlas is required by some advanced application functions.\n\n' \
              'The data set (~4GB) can be retrieved from:\n' \
              '   https://1drv.ms/u/c/3579835830bc10b0/EQXFY3rWGZlGsaarQnb6HvgBV_0GbdtNGmgTq02K52nuQw?e=ZdfR10\n' \
              '   https://1drv.ms/u/c/3579835830bc10b0/Eau4zJisHeJFidaTzV0-MhkBOwxT-jRAQLPPXTueaBSYMw?e=HbqT2L\n' \
              'then unzipped it into:\n' \
              '   %s\n\n' \
              'Do you want that I perform this operation for you?\n' \
              'Internet connection is required!\n' % self.lib.woa13_folder
        # noinspection PyCallByClass,PyArgumentList,PyUnresolvedReferences
        ret = QtWidgets.QMessageBox.information(
            self, "Sound Speed Manager - WOA13 Atlas", msg,
            QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.No)
        if ret == QtWidgets.QMessageBox.StandardButton.No:
            msg = 'You can also manually install it. The steps are:\n' \
                  ' - download the archive from (anonymous ftp):\n' \
                  '   https://1drv.ms/u/c/3579835830bc10b0/EQXFY3rWGZlGsaarQnb6HvgBV_0GbdtNGmgTq02K52nuQw?e=ZdfR10\n' \
                  '   https://1drv.ms/u/c/3579835830bc10b0/Eau4zJisHeJFidaTzV0-MhkBOwxT-jRAQLPPXTueaBSYMw?e=HbqT2L\n' \
                  ' - unzip the archive into:\n' \
                  '   %s\n' \
                  ' - restart Sound Speed Manager\n' % self.lib.woa13_folder
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.information(self, "Sound Speed Manager - WOA13 Atlas", msg,
                                              QtWidgets.QMessageBox.StandardButton.Ok)
            os.environ.get("SSM_DEBUG") and logger.debug('WOA13: disabled')
            return

        success = self.lib.download_woa13()
        if not success:
            msg = 'Unable to retrieve the WOA13 atlas.\n\n ' \
                  'You may manually install it. The steps are:\n' \
                  ' - download the archive from (anonymous ftp):\n' \
                  '   https://1drv.ms/u/c/3579835830bc10b0/EQXFY3rWGZlGsaarQnb6HvgBV_0GbdtNGmgTq02K52nuQw?e=ZdfR10\n' \
                  '   https://1drv.ms/u/c/3579835830bc10b0/Eau4zJisHeJFidaTzV0-MhkBOwxT-jRAQLPPXTueaBSYMw?e=HbqT2L\n' \
                  ' - unzip the archive into:\n' \
                  '   %s\n' \
                  ' - restart Sound Speed Manager\n' % self.lib.woa13_folder
            # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
            QtWidgets.QMessageBox.warning(self, "Sound Speed Manager - WOA13 Atlas", msg,
                                          QtWidgets.QMessageBox.StandardButton.Ok)
            os.environ.get("SSM_DEBUG") and logger.debug('WOA13: disabled')
            return

        os.environ.get("SSM_DEBUG") and logger.debug('WOA13: enabled')

    def check_woa18(self):
        """ helper function that looks after WOA18 database"""
        if not self.lib.use_woa18():
            os.environ.get("SSM_DEBUG") and logger.debug('WOA18: disabled by settings')
            return

        if self.lib.has_woa18():
            os.environ.get("SSM_DEBUG") and logger.debug('WOA18: enabled')
            return

        msg = 'The WOA18 atlas is required by some advanced application functions.\n\n' \
              'The data set (~4GB) can be retrieved from:\n' \
              '   https://1drv.ms/u/c/3579835830bc10b0/EVKa9LZCIVhIsoEGwkP0d3cBuPooilizs8trzRsFRaF3YQ?e=4sklUP\n' \
              '   https://1drv.ms/u/c/3579835830bc10b0/Ecfe-ndRsYhIt3U_hgrrj-kB55jLYZiJ81b8ZUnOr4cPTQ?e=GmsdDJ\n' \
              'then unzipped it into:\n' \
              '   %s\n\n' \
              'Do you want that I perform this operation for you?\n' \
              'Internet connection is required!\n' % self.lib.woa18_folder
        # noinspection PyCallByClass,PyArgumentList,PyUnresolvedReferences
        ret = QtWidgets.QMessageBox.information(
            self, "Sound Speed Manager - WOA18 Atlas", msg,
            QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.No)
        if ret == QtWidgets.QMessageBox.StandardButton.No:
            msg = 'You can also manually install it. The steps are:\n' \
                  ' - download the archive from:\n' \
                  '   https://1drv.ms/u/c/3579835830bc10b0/EVKa9LZCIVhIsoEGwkP0d3cBuPooilizs8trzRsFRaF3YQ?e=4sklUP\n' \
                  '   https://1drv.ms/u/c/3579835830bc10b0/Ecfe-ndRsYhIt3U_hgrrj-kB55jLYZiJ81b8ZUnOr4cPTQ?e=GmsdDJ\n' \
                  ' - unzip the archive into:\n' \
                  '   %s\n' \
                  ' - restart Sound Speed Manager\n' % self.lib.woa18_folder
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.information(self, "Sound Speed Manager - WOA18 Atlas", msg,
                                              QtWidgets.QMessageBox.StandardButton.Ok)
            os.environ.get("SSM_DEBUG") and logger.debug('WOA18: disabled')
            return

        success = self.lib.download_woa18()
        if not success:
            msg = 'Unable to retrieve the WOA18 atlas.\n\n ' \
                  'You may manually install it. The steps are:\n' \
                  ' - download the archive from:\n' \
                  '   https://1drv.ms/u/c/3579835830bc10b0/EVKa9LZCIVhIsoEGwkP0d3cBuPooilizs8trzRsFRaF3YQ?e=4sklUP\n' \
                  '   https://1drv.ms/u/c/3579835830bc10b0/Ecfe-ndRsYhIt3U_hgrrj-kB55jLYZiJ81b8ZUnOr4cPTQ?e=GmsdDJ\n' \
                  ' - unzip the archive into:\n' \
                  '   %s\n' \
                  ' - restart Sound Speed Manager\n' % self.lib.woa18_folder
            # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
            QtWidgets.QMessageBox.warning(self, "Sound Speed Manager - WOA18 Atlas", msg,
                                          QtWidgets.QMessageBox.StandardButton.Ok)
            os.environ.get("SSM_DEBUG") and logger.debug('WOA18: disabled')
            return

        os.environ.get("SSM_DEBUG") and logger.debug('WOA18: enabled')

    def check_woa23(self):
        """ helper function that looks after WOA23 database"""
        if not self.lib.use_woa23():
            os.environ.get("SSM_DEBUG") and logger.debug('WOA23: disabled by settings')
            return

        if self.lib.has_woa23():
            os.environ.get("SSM_DEBUG") and logger.debug('WOA23: enabled')
            return

        msg = 'The WOA23 atlas is required by some advanced application functions.\n\n' \
              'The data set (~4GB) can be retrieved from:\n' \
              '   https://1drv.ms/u/c/3579835830bc10b0/EQ71R_-GothHgGWii3wuC3cB4yNJ4XxLmZlCrvHW8_Yz1Q?e=eoaSvW\n' \
              '   https://1drv.ms/u/c/3579835830bc10b0/Ed9FWFOkxFhMmWcP1sgdFekBcEsqY9BU5wnB74LKoLEN4g?e=bcYJyC\n' \
              'then unzipped it into:\n' \
              '   %s\n\n' \
              'Do you want that I perform this operation for you?\n' \
              'Internet connection is required!\n' % self.lib.woa23_folder
        # noinspection PyCallByClass,PyArgumentList,PyUnresolvedReferences
        ret = QtWidgets.QMessageBox.information(
            self, "Sound Speed Manager - WOA23 Atlas", msg,
            QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.No)
        if ret == QtWidgets.QMessageBox.StandardButton.No:
            msg = 'You can also manually install it. The steps are:\n' \
                  ' - download the archive from:\n' \
                  '   https://1drv.ms/u/c/3579835830bc10b0/EQ71R_-GothHgGWii3wuC3cB4yNJ4XxLmZlCrvHW8_Yz1Q?e=eoaSvW\n' \
                  '   https://1drv.ms/u/c/3579835830bc10b0/Ed9FWFOkxFhMmWcP1sgdFekBcEsqY9BU5wnB74LKoLEN4g?e=bcYJyC\n' \
                  ' - unzip the archive into:\n' \
                  '   %s\n' \
                  ' - restart Sound Speed Manager\n' % self.lib.woa23_folder
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.information(self, "Sound Speed Manager - WOA23 Atlas", msg,
                                              QtWidgets.QMessageBox.StandardButton.Ok)
            os.environ.get("SSM_DEBUG") and logger.debug('WOA23: disabled')
            return

        success = self.lib.download_woa23()
        if not success:
            msg = 'Unable to retrieve the WOA23 atlas.\n\n ' \
                  'You may manually install it. The steps are:\n' \
                  ' - download the archive from:\n' \
                  '   https://1drv.ms/u/c/3579835830bc10b0/EQ71R_-GothHgGWii3wuC3cB4yNJ4XxLmZlCrvHW8_Yz1Q?e=eoaSvW\n' \
                  '   https://1drv.ms/u/c/3579835830bc10b0/Ed9FWFOkxFhMmWcP1sgdFekBcEsqY9BU5wnB74LKoLEN4g?e=bcYJyC\n' \
                  ' - unzip the archive into:\n' \
                  '   %s\n' \
                  ' - restart Sound Speed Manager\n' % self.lib.woa23_folder
            # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
            QtWidgets.QMessageBox.warning(self, "Sound Speed Manager - WOA23 Atlas", msg,
                                          QtWidgets.QMessageBox.StandardButton.Ok)
            os.environ.get("SSM_DEBUG") and logger.debug('WOA23: disabled')
            return

        os.environ.get("SSM_DEBUG") and logger.debug('WOA233: enabled')

    def check_rtofs(self):
        """ helper function that looks after RTOFS connection"""
        if not self.lib.use_rtofs():
            os.environ.get("SSM_DEBUG") and logger.debug('RTOFS: disabled by settings')
            return

        if self.lib.has_rtofs():
            os.environ.get("SSM_DEBUG") and logger.debug('RTOFS: enabled')
            return

        success = self.lib.download_rtofs()
        if not success:
            msg = 'Unable to retrieve the RTOFS atlas.\n\n ' \
                  'The application needs an internet connection to access\n' \
                  'this server (with port 9090 open):\n' \
                  ' - http://nomads.ncep.noaa.gov:9090\n\n' \
                  'You can disable the RTOFS support in Settings/Basic/Use RTOFS.\n'
            # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
            QtWidgets.QMessageBox.warning(self, "Sound Speed Manager - RTOFS Atlas", msg,
                                          QtWidgets.QMessageBox.StandardButton.Ok)
            os.environ.get("SSM_DEBUG") and logger.debug('RTOFS: disabled')
            return

        os.environ.get("SSM_DEBUG") and logger.debug('RTOFS: enabled')

    def check_sis(self):
        if self.lib.use_sis():
            if not self.lib.listen_sis():
                msg = 'Unable to listen SIS.\nCheck whether another process is already using the SIS port.'
                # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
                QtWidgets.QMessageBox.warning(self, "Sound Speed Manager - SIS", msg,
                                              QtWidgets.QMessageBox.StandardButton.Ok)
        else:
            if not self.lib.stop_listen_sis():
                msg = 'Unable to stop listening SIS.'
                # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
                QtWidgets.QMessageBox.warning(self, "Sound Speed Manager - SIS", msg,
                                              QtWidgets.QMessageBox.StandardButton.Ok)

    def check_sippican(self):
        if self.lib.use_sippican():
            if not self.lib.listen_sippican():
                msg = 'Unable to listening Sippican.\nCheck whether another process is already using the Sippican port.'
                # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
                QtWidgets.QMessageBox.warning(self, "Sound Speed Manager - Sippican", msg,
                                              QtWidgets.QMessageBox.StandardButton.Ok)
        else:
            if not self.lib.stop_listen_sippican():
                msg = 'Unable to stop listening Sippican.'
                # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
                QtWidgets.QMessageBox.warning(self, "Sound Speed Manager - Sippican", msg,
                                              QtWidgets.QMessageBox.StandardButton.Ok)

    def check_nmea(self):
        if self.lib.use_nmea_0183():
            if not self.lib.listen_nmea():
                msg = ('Unable to listening NMEA 0183.\n'
                       'Check whether another process is already using the NMEA 0183 port.')
                # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
                QtWidgets.QMessageBox.warning(self, "Sound Speed Manager - NMEA 0183", msg,
                                              QtWidgets.QMessageBox.StandardButton.Ok)
        else:
            if not self.lib.stop_listen_nmea():
                msg = 'Unable to stop listening Nmea.'
                # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
                QtWidgets.QMessageBox.warning(self, "Sound Speed Manager - NMEA 0183", msg,
                                              QtWidgets.QMessageBox.StandardButton.Ok)

    def check_mvp(self):
        if self.lib.use_mvp():
            if not self.lib.listen_mvp():
                msg = 'Unable to listening MVP.\nCheck whether another process is already using the MVP port.'
                # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
                QtWidgets.QMessageBox.warning(self, "Sound Speed Manager - MVP", msg,
                                              QtWidgets.QMessageBox.StandardButton.Ok)
        else:
            if not self.lib.stop_listen_mvp():
                msg = 'Unable to stop listening MVP.'
                # noinspection PyCallByClass,PyArgumentList,PyTypeChecker
                QtWidgets.QMessageBox.warning(self, "Sound Speed Manager - MVP", msg,
                                              QtWidgets.QMessageBox.StandardButton.Ok)

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
        self.statusBar().setStyleSheet(self.cyan_stylesheet)

    def server_stopped(self):
        self.tab_editor.server_stopped()
        self.tab_database.server_stopped()
        self.tab_server.server_stopped()
        # self.tab_refraction.server_stopped()
        self.tab_setup.server_stopped()
        self.statusBar().setStyleSheet(self.normal_stylesheet)

    def _check_latest_release(self):
        os.environ.get("SSM_DEBUG") and logger.info("Checking latest release ...")

        new_release = False
        new_bugfix = False
        try:
            response = urlopen(app_info.app_latest_url, timeout=2)
            latest_version = response.read().split()[0].decode()

            cur_maj, cur_min, cur_fix = app_info.app_version.split('.')
            lat_maj, lat_min, lat_fix = latest_version.split('.')

            if int(lat_maj) > int(cur_maj):
                new_release = True

            elif (int(lat_maj) == int(cur_maj)) and (int(lat_min) > int(cur_min)):
                new_release = True

            elif (int(lat_maj) == int(cur_maj)) and (int(lat_min) == int(cur_min)) and (int(lat_fix) > int(cur_fix)):
                new_bugfix = True

            self.release_checked = True

        except Exception as ex:
            os.environ.get("SSM_DEBUG") and logger.info("Unable to check latest release (reason: %s)" % ex)
            return

        if new_release:
            logger.info("New release available: %s" % latest_version)
            self.releaseInfo.setText("New release available: %s" % latest_version)
            self.releaseInfo.setStyleSheet(self.red_stylesheet)

        elif new_bugfix:
            logger.info("New bugfix available: %s" % latest_version)
            self.releaseInfo.setText("New bugfix available: %s" % latest_version)
            self.releaseInfo.setStyleSheet(self.yellow_stylesheet)

        os.environ.get("SSM_DEBUG") and logger.info("Checking latest release ... DONE")

    def _update_gui_in_use(self) -> str:
        tokens = list()
        if self.lib.server.is_alive():
            tokens.append("SRV")
        if self.lib.has_ref():
            tokens.append("REF")
        if self.lib.use_rtofs():
            tokens.append("RTF")
        if self.lib.use_gomofs():
            tokens.append("GoM")
        if self.lib.use_woa09():
            tokens.append("W09")
        if self.lib.use_woa13():
            tokens.append("W13")
        if self.lib.use_woa18():
            tokens.append("W18")
        if self.lib.use_woa23():
            tokens.append("W23")
        if self.lib.use_sippican():
            tokens.append("SIP")
        if self.lib.use_nmea_0183():
            tokens.append("N0183")
        if self.lib.use_mvp():
            tokens.append("MVP")
        if self.lib.use_sis():
            if self.lib.use_sis4():
                tokens.append("SIS4")
            else:
                tokens.append("SIS5")
        return "|".join(tokens)

    def _update_gui_from_sis_nav(self, msg: str) -> str:
        self.old_sis_nav_data = False
        if self.lib.listeners.sis.nav_last_time is not None:
            diff_time = datetime.now(UTC) - self.lib.listeners.sis.nav_last_time
            self.old_sis_nav_data = diff_time.total_seconds() > (self.lib.setup.sis_listen_timeout * 10)
            if self.old_sis_nav_data:
                logger.warning("%s: navigation datagram is too old (%d seconds)"
                               % (datetime.now(UTC), diff_time.total_seconds()))

        # time stamp
        msg += "time:"
        if self.old_sis_nav_data:
            msg += "TOO OLD, "
        elif self.lib.listeners.sis.nav_timestamp is None:
            msg += "NA, "
        else:
            msg += "%s, " % (self.lib.listeners.sis.nav_timestamp.strftime("%H:%M:%S"))

        # position
        msg += "pos:"
        if self.old_sis_nav_data:
            msg += "(TOO OLD),  "
        elif (self.lib.listeners.sis.nav_latitude is None) or \
                (self.lib.listeners.sis.nav_longitude is None):
            msg += "(NA, NA),  "
        else:
            latitude = self.lib.listeners.sis.nav_latitude
            if latitude >= 0:
                letter = "N"
            else:
                letter = "S"
            lat_min = float(60 * math.fabs(latitude - int(latitude)))
            lat_str = "%02d\N{DEGREE SIGN}%7.3f'%s" % (int(math.fabs(latitude)), lat_min, letter)

            longitude = self.lib.listeners.sis.nav_longitude
            if longitude < 0:
                letter = "W"
            else:
                letter = "E"
            lon_min = float(60 * math.fabs(longitude - int(longitude)))
            lon_str = "%03d\N{DEGREE SIGN}%7.3f'%s" % (int(math.fabs(longitude)), lon_min, letter)

            msg += "(%s, %s),  " % (lat_str, lon_str)

        return msg

    def _update_gui_from_sis_xyz(self, msg: str) -> str:
        self.old_sis_xyz_data = False
        if self.lib.listeners.sis.xyz_last_time is not None:
            diff_time = datetime.now(UTC) - self.lib.listeners.sis.xyz_last_time
            self.old_sis_xyz_data = diff_time.total_seconds() > (self.lib.setup.sis_listen_timeout * 10)
            if self.old_sis_xyz_data:
                logger.warning("%s: xyz datagram is too old (%d seconds)"
                               % (datetime.now(UTC), diff_time.total_seconds()))

        if self.old_sis_xyz_data:
            msg += 'XYZ88 OLD [pinging?]'

        elif self.lib.listeners.sis.xyz is None:
            msg += 'XYZ88 NA [pinging?]'

        else:
            msg += 'tss:'
            if self.lib.listeners.sis.xyz_transducer_sound_speed is not None:
                msg += '%.1f m/s,  ' % self.lib.listeners.sis.xyz_transducer_sound_speed

            else:
                msg += 'NA m/s,  '

            msg += 'avg.depth:'
            mean_depth = self.lib.listeners.sis.xyz_mean_depth
            if mean_depth:
                msg += '%.1f m' % mean_depth
            else:
                msg += 'NA m'

        return msg

    def _update_gui_from_sis(self, msg: str) -> str:

        msg += "  -  "  # add some spacing

        msg = self._update_gui_from_sis_nav(msg=msg)

        msg = self._update_gui_from_sis_xyz(msg=msg)

        return msg

    def _update_gui_from_nmea_nav(self, msg: str) -> str:
        self.old_nmea_nav_data = False
        if self.lib.listeners.nmea.nav_last_time is not None:
            diff_time = datetime.now(UTC) - self.lib.listeners.nmea.nav_last_time
            self.old_nmea_nav_data = diff_time.total_seconds() > (self.lib.setup.nmea_listen_timeout * 10)
            if self.old_nmea_nav_data:
                logger.warning("%s: navigation message is too old (%d seconds)"
                               % (datetime.now(UTC), diff_time.total_seconds()))

        # position
        msg += "  -  pos:"
        if self.old_nmea_nav_data:
            msg += "(TOO OLD)"
        elif (self.lib.listeners.nmea.nav_latitude is None) or \
                (self.lib.listeners.nmea.nav_longitude is None):
            msg += "(NA, NA)"
        else:
            latitude = self.lib.listeners.nmea.nav_latitude
            if latitude >= 0:
                letter = "N"
            else:
                letter = "S"
            lat_min = float(60 * math.fabs(latitude - int(latitude)))
            lat_str = "%02d\N{DEGREE SIGN}%7.3f'%s" % (int(math.fabs(latitude)), lat_min, letter)

            longitude = self.lib.listeners.nmea.nav_longitude
            if longitude < 0:
                letter = "W"
            else:
                letter = "E"
            lon_min = float(60 * math.fabs(longitude - int(longitude)))
            lon_str = "%03d\N{DEGREE SIGN}%7.3f'%s" % (int(math.fabs(longitude)), lon_min, letter)

            msg += "(%s, %s)" % (lat_str, lon_str)

        return msg

    def update_gui(self):

        self.timer_execs += 1

        # update the windows title
        self.setWindowTitle('%s v.%s [project: %s]' % (self.name, self.version, self.lib.current_project))

        # check release
        if (self.timer_execs % 200 == 5) and not self.release_checked:
            # logger.debug("timer executions: %d" % self.timer_execs)
            self._check_latest_release()

        # list activated features
        msg = self._update_gui_in_use()
        self.old_sis_nav_data = False
        self.old_sis_xyz_data = False
        if self.lib.use_sis():  # in case that SIS4 and SIS5 are enabled
            msg = self._update_gui_from_sis(msg=msg)
        elif self.lib.use_nmea_0183():  # in case that the NMEA listener is enabled
            msg = self._update_gui_from_nmea_nav(msg=msg)
        self.statusBar().showMessage(msg, 2000)

        if self.lib.has_ssp():

            if self.lib.server.is_alive():  # server mode
                if not self.tab_server.dataplots.is_drawn:
                    self.tab_server.dataplots.reset()
                    self.tab_server.dataplots.on_first_draw()

                self.tab_server.dataplots.update_data()
                self.tab_server.dataplots.update_all_limits()
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
                self.statusBar().setStyleSheet(self.orange_stylesheet)
            else:
                if self.old_sis_nav_data or self.old_nmea_nav_data:
                    self.statusBar().setStyleSheet(self.purple_stylesheet)
                elif self.old_sis_xyz_data:
                    self.statusBar().setStyleSheet(self.khaki_stylesheet)
                else:
                    self.statusBar().setStyleSheet(self.normal_stylesheet)

    def change_info_url(self, url):
        self.tab_info.change_url(url)

    def exception_hook(self, ex_type: type, ex_value: BaseException, tb: traceback) -> None:
        # noinspection PyTypeChecker
        sys.__excepthook__(ex_type, ex_value, tb)

        # first manage case of not being an pkg_exception (e.g., keyboard interrupts)
        if not issubclass(ex_type, Exception):
            msg = str(ex_value)
            if not msg:
                msg = ex_value.__class__.__name__
            logger.info(msg)
            self.close()
            return

        dlg = PkgExceptionDialog(app_info=app_info, ex_type=ex_type, ex_value=ex_value, tb=tb)
        ret = dlg.exec()
        if ret == QtWidgets.QDialog.DialogCode.Rejected:
            if not dlg.user_triggered:
                self.close()
        else:
            logger.warning("ignored pkg_exception")

    # Quitting #

    def _do_you_really_want(self, title="Quit", text="quit"):
        """helper function that show to the user a message windows asking to confirm an action"""
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setIconPixmap(QtGui.QPixmap(app_info.app_icon_path).scaled(QtCore.QSize(36, 36)))
        msg_box.setText('Do you really want to %s?' % text)
        # noinspection PyUnresolvedReferences
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
        return msg_box.exec()

    def closeEvent(self, event):
        """ actions to be done before close the app """
        if self.skip_do_you_really_quit:
            self._close(event=event)
            return

        reply = self._do_you_really_want("Quit", "quit %s" % app_info.app_name)
        # reply = QtWidgets.QMessageBox.Yes
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self._close(event)
        else:
            event.ignore()

    def _close(self, event):
        event.accept()
        self.lib.close()
        if self.has_sdm_support:
            self.tab_monitor.stop_plotting()
        super(MainWin, self).closeEvent(event)

    # -------------------------- development-only --------------------------

    def do(self):
        """ development-mode only helper function """
        pass
