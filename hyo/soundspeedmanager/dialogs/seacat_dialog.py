import os
from PySide import QtGui
from PySide import QtCore

import logging
logger = logging.getLogger(__name__)

from hyo.soundspeedmanager.dialogs.dialog import AbstractDialog
from hyo.soundspeedmanager.widgets.seacat import Seacat


class SeacatDialog(AbstractDialog):

    def __init__(self, main_win, lib, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        self.fmt_outputs = list()

        self.setWindowTitle("Import data from Sea-Bird SeaCAT CTD")
        self.setMinimumWidth(220)

        # outline ui
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.addWidget(Seacat(main_win=main_win, lib=lib))
