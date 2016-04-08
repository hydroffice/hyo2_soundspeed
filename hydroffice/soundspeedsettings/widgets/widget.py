from __future__ import absolute_import, division, print_function, unicode_literals

import os

from PySide import QtGui
from PySide import QtCore

import logging
logger = logging.getLogger(__name__)

from hydroffice.soundspeed.base.settingsdb import SettingsDb


class AbstractWidget(QtGui.QMainWindow):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded

    def __init__(self, main_win, db):
        QtGui.QMainWindow.__init__(self)
        if type(db) != SettingsDb:
            raise RuntimeError("Passed invalid settings db object: %s" % type(db))
        self.main_win = main_win
        self.db = db

        # set palette
        style_info = QtCore.QFileInfo(os.path.join(self.here, 'styles', 'widget.stylesheet'))
        style_content = open(style_info.filePath()).read()
        self.setStyleSheet(style_content)

        self.setContentsMargins(0, 0, 0, 0)

        # add a frame
        self.frame = QtGui.QFrame()
        self.setCentralWidget(self.frame)

        # progress dialog
        self.progress = QtGui.QProgressDialog(self)
        self.progress.setWindowTitle("Processing")
        self.progress.setCancelButtonText("Abort")
        self.progress.setWindowModality(QtCore.Qt.WindowModal)

    def setup_changed(self):
        pass