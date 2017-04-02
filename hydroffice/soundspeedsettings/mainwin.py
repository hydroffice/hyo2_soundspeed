import os
import sys

from PySide import QtGui
from PySide import QtCore

import logging
logger = logging.getLogger(__name__)

from hydroffice.soundspeedsettings import __version__ as sss_version
from hydroffice.soundspeedsettings import __doc__ as sss_name
from hydroffice.soundspeedsettings.widgets.main import Main
from hydroffice.soundspeedsettings.widgets.general import General
from hydroffice.soundspeedsettings.widgets.input import Input
from hydroffice.soundspeedsettings.widgets.output import Output
from hydroffice.soundspeedsettings.widgets.listeners import Listeners

from hydroffice.soundspeed.soundspeed import SoundSpeedLibrary


class MainWin(QtGui.QMainWindow):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, "media")

    def __init__(self, lib, main_win=None):
        super(MainWin, self).__init__()

        # check passed input parameters
        if type(lib) != SoundSpeedLibrary:
            raise RuntimeError("Invalid type (%s) in place of a Project instance" % type(lib))
        self.lib = lib
        self.db = lib.settings_db()
        self.main_win = main_win

        # set the application name and the version
        self.name = sss_name
        self.version = sss_version
        self.setWindowTitle('%s v.%s' % (self.name, self.version))

        # only called when stand-alone (without Sound Speed Manager)
        # noinspection PyArgumentList
        _app = QtCore.QCoreApplication.instance()
        if _app.applicationName() == 'python':
            _app.setApplicationName('%s v.%s' % (self.name, self.version))
            _app.setOrganizationName("HydrOffice")
            _app.setOrganizationDomain("hydroffice.org")
            logger.debug("set application name: %s" % _app.applicationName())

            # set icons
            icon_info = QtCore.QFileInfo(os.path.join(self.media, 'settings.png'))
            self.setWindowIcon(QtGui.QIcon(icon_info.absoluteFilePath()))
            if (sys.platform == 'win32') or (os.name is "nt"):  # is_windows()
                try:
                    # This is needed to display the app icon on the taskbar on Windows 7
                    import ctypes
                    app_id = '%s v.%s' % (self.name, self.version)
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
                except AttributeError as e:
                    logger.debug("Unable to change app icon: %s" % e)

        # set style
        style_info = QtCore.QFileInfo(os.path.join(self.here, 'styles', 'main.stylesheet'))
        style_content = open(style_info.filePath()).read()
        self.setStyleSheet(style_content)

        # make tabs
        self.tabs = QtGui.QTabWidget()
        self.tabs.setTabPosition(QtGui.QTabWidget.South)
        self.setCentralWidget(self.tabs)
        self.tabs.setIconSize(QtCore.QSize(45, 45))

        # main
        self.tab_main = Main(db=self.db, main_win=self)
        idx = self.tabs.insertTab(0, self.tab_main, "Main")
        self.tabs.setTabToolTip(idx, "Available setups")
        # general
        self.tab_general = General(db=self.db, main_win=self)
        idx = self.tabs.insertTab(1, self.tab_general, "General")
        self.tabs.setTabToolTip(idx, "General setup")
        # input
        self.tab_input = Input(db=self.db, main_win=self)
        idx = self.tabs.insertTab(2, self.tab_input, "Input")
        self.tabs.setTabToolTip(idx, "Input setup")
        # output
        self.tab_output = Output(db=self.db, main_win=self)
        idx = self.tabs.insertTab(3, self.tab_output, "Output")
        self.tabs.setTabToolTip(idx, "Output setup")
        # listeners
        self.tab_listeners = Listeners(db=self.db, main_win=self)
        idx = self.tabs.insertTab(4, self.tab_listeners, "Listeners")
        self.tabs.setTabToolTip(idx, "Listeners setup")

        self.setup_changed()  # trigger the first update of all the tabs

    def set_editable(self, editable):
        """Helper function to disable/enable all the tabs"""
        if editable:
            self.tab_main.setEnabled(True)
            self.tab_general.setEnabled(True)
            self.tab_input.setEnabled(True)
            self.tab_output.setEnabled(True)
            self.tab_listeners.setEnabled(True)

        else:
            self.tab_main.setDisabled(True)
            self.tab_general.setDisabled(True)
            self.tab_input.setDisabled(True)
            self.tab_output.setDisabled(True)
            self.tab_listeners.setDisabled(True)

    def reload_settings(self):
        logger.debug("reload settings")
        try:
            self.lib.reload_settings_from_db()
        except RuntimeError as e:
            msg = "Issue in reloading settings\n%s" % e
            # noinspection PyCallByClass
            QtGui.QMessageBox.critical(self, "Settings error", msg, QtGui.QMessageBox.Ok)
            return

    def setup_changed(self):
        """Method used to update all the tabs (except the main)"""
        tabs_nr = self.tabs.count()
        for i in range(tabs_nr):
            self.tabs.widget(i).setup_changed()
