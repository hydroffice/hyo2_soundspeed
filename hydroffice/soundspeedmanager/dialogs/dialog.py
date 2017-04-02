import os

from PySide import QtGui
from PySide import QtCore

import logging
logger = logging.getLogger(__name__)

from hydroffice.soundspeed.soundspeed import SoundSpeedLibrary
from hydroffice.soundspeedmanager.qt_progress import QtProgress


class AbstractDialog(QtGui.QDialog):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.abspath(os.path.join(here, os.pardir, "media"))

    def __init__(self, main_win, lib, parent=None):
        QtGui.QDialog.__init__(self, parent)
        if type(lib) != SoundSpeedLibrary:
            raise RuntimeError("Passed invalid project object: %s" % type(lib))
        self.main_win = main_win
        self.lib = lib

        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        # progress dialog
        self.progress = QtProgress(parent=self)
