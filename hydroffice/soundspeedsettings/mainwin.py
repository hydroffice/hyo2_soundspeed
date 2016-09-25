from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys

from PySide import QtGui
from PySide import QtCore

import logging
logger = logging.getLogger(__name__)

from . import __version__ as sss_version
from . import __doc__ as sss_name
from .widgets.main import Main
from .widgets.input import Input
from .widgets.output import Output
from .widgets.sis import Sis
from .widgets.sippican import Sippican
from .widgets.mvp import Mvp
from .widgets.server import Server

from hydroffice.soundspeed.project import Project


class MainWin(QtGui.QMainWindow):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, "media")

    def __init__(self, prj, main_win=None):
        QtGui.QMainWindow.__init__(self)

        # check passed input parameters
        if type(prj) != Project:
            raise RuntimeError("Invalid type (%s) in place of a Project instance" % type(prj))
        self.prj = prj
        self.db = prj.settings_db()
        self.main_win = main_win

        # set the application name and the version
        self.name = sss_name
        self.version = sss_version
        self.setWindowTitle('%s v.%s' % (self.name, self.version))

        # only called when stand-alone (without Sound Speed Manager)
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
        # input
        self.tab_input = Input(db=self.db, main_win=self)
        idx = self.tabs.insertTab(1, self.tab_input, "Input")
        self.tabs.setTabToolTip(idx, "Input settings")
        # output
        self.tab_output = Output(db=self.db, main_win=self)
        idx = self.tabs.insertTab(2, self.tab_output, "Output")
        self.tabs.setTabToolTip(idx, "Output settings")
        # sis
        self.tab_sis = Sis(db=self.db, main_win=self)
        idx = self.tabs.insertTab(3, self.tab_sis, "SIS")
        self.tabs.setTabToolTip(idx, "SIS settings")
        # sippican
        self.tab_sippican = Sippican(db=self.db, main_win=self)
        idx = self.tabs.insertTab(4, self.tab_sippican, "Sippican")
        self.tabs.setTabToolTip(idx, "Sippican settings")
        # mvp
        self.tab_mvp = Mvp(db=self.db, main_win=self)
        idx = self.tabs.insertTab(5, self.tab_mvp, "MVP")
        self.tabs.setTabToolTip(idx, "MVP settings")
        # server
        self.tab_server = Server(db=self.db, main_win=self)
        idx = self.tabs.insertTab(6, self.tab_server, "Server")
        self.tabs.setTabToolTip(idx, "Server settings")

        self.setup_changed()  # trigger the first update of all the tabs

    def set_editable(self, editable):
        """Helper function to disable/enable all the tabs"""
        if editable:
            self.tab_main.setEnabled(True)
            self.tab_input.setEnabled(True)
            self.tab_output.setEnabled(True)
            self.tab_sis.setEnabled(True)
            self.tab_sippican.setEnabled(True)
            self.tab_mvp.setEnabled(True)
            self.tab_server.setEnabled(True)
        else:
            self.tab_main.setDisabled(True)
            self.tab_input.setDisabled(True)
            self.tab_output.setDisabled(True)
            self.tab_sis.setDisabled(True)
            self.tab_sippican.setDisabled(True)
            self.tab_mvp.setDisabled(True)
            self.tab_server.setDisabled(True)

    def setup_changed(self):
        """Method used to update all the tabs (except the main)"""
        tabs_nr = self.tabs.count()
        for i in range(tabs_nr):
            self.tabs.widget(i).setup_changed()
