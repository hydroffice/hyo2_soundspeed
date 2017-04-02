import os

from PySide import QtGui
from PySide import QtCore

import logging
logger = logging.getLogger(__name__)

from hydroffice.soundspeed.soundspeed import SoundSpeedLibrary
from hydroffice.soundspeedmanager.qt_progress import QtProgress


class AbstractWidget(QtGui.QMainWindow):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded

    def __init__(self, main_win, lib):
        QtGui.QMainWindow.__init__(self)
        if type(lib) != SoundSpeedLibrary:
            raise RuntimeError("Passed invalid project object: %s" % type(lib))
        self.main_win = main_win
        self.lib = lib

        # set palette
        style_info = QtCore.QFileInfo(os.path.join(self.here, 'styles', 'widget.stylesheet'))
        style_content = open(style_info.filePath()).read()
        self.setStyleSheet(style_content)

        self.setContentsMargins(0, 0, 0, 0)

        # add a frame
        self.frame = QtGui.QFrame()
        self.setCentralWidget(self.frame)

        # progress dialog
        self.progress = QtProgress(parent=self)

    def data_cleared(self):
        pass

    def data_imported(self):
        pass

    def data_stored(self):
        pass

    def data_removed(self):
        pass

    def server_started(self):
        pass

    def server_stopped(self):
        pass
