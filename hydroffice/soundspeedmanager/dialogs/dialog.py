from __future__ import absolute_import, division, print_function, unicode_literals

import os

from PySide import QtGui
from PySide import QtCore

import logging
logger = logging.getLogger(__name__)

from hydroffice.soundspeed.project import Project


class AbstractDialog(QtGui.QDialog):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.abspath(os.path.join(here, os.pardir, "media"))

    def __init__(self, main_win, prj, parent=None):
        QtGui.QDialog.__init__(self, parent)
        if type(prj) != Project:
            raise RuntimeError("Passed invalid project object: %s" % type(prj))
        self.main_win = main_win
        self.prj = prj

        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        # progress dialog
        self.progress = QtGui.QProgressDialog(self)
        self.progress.setWindowTitle("Processing")
        self.progress.setCancelButtonText("Abort")
        self.progress.setWindowModality(QtCore.Qt.WindowModal)
