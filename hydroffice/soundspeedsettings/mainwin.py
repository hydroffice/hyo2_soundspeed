from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys

from PySide import QtGui
from PySide import QtCore

import logging
logger = logging.getLogger(__name__)

from . import __version__ as sss_version
from .widgets.main import Main
from .widgets.basic import Basic
from hydroffice.soundspeed.project import Project


class MainWin(QtGui.QMainWindow):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded

    def __init__(self, prj, main_win=None):
        QtGui.QMainWindow.__init__(self)

        # check passed input parameters
        if type(prj) != Project:
            raise RuntimeError("Invalid type (%s) in place of a Project instance" % type(prj))
        self.prj = prj
        self.db = prj.settings_db()
        self.main_win = main_win

        # set the application name
        self.name = "Sound Speed Settings"
        self.version = sss_version
        self.setWindowTitle('%s v.%s' % (self.name, self.version))

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
        # basic
        self.tab_basic = Basic(db=self.db, main_win=self)
        idx = self.tabs.insertTab(1, self.tab_basic, "Basic")
        self.tabs.setTabToolTip(idx, "Common processing settings")

        self.setup_changed()  # trigger the first update of all the tabs

    def set_editable(self, value):
        if value:
            self.tab_main.setEnabled(True)
            self.tab_basic.setEnabled(True)
        else:
            self.tab_main.setDisabled(True)
            self.tab_basic.setDisabled(True)

    def setup_changed(self):
        """Method used to update all the tabs (except the main)"""
        tabs_nr = self.tabs.count()
        for i in range(tabs_nr):
            self.tabs.widget(i).setup_changed()
