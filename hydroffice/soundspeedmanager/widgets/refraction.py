from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

from PySide import QtGui

logger = logging.getLogger(__name__)

from .widget import AbstractWidget
from .dataplots import DataPlots


class Refraction(AbstractWidget):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win, lib):
        AbstractWidget.__init__(self, main_win=main_win, lib=lib)

        # create the overall layout
        self.main_layout = QtGui.QVBoxLayout()
        self.frame.setLayout(self.main_layout)

        # - buttons
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        hbox.addStretch()
        # -- start
        btn = QtGui.QPushButton("Enable monitor")
        btn.clicked.connect(self.on_enable_monitor)
        btn.setToolTip("Enable refraction monitor")
        hbox.addWidget(btn)
        # -- stop
        btn = QtGui.QPushButton("Disable monitor")
        btn.clicked.connect(self.on_disable_monitor)
        btn.setToolTip("Disable refraction monitor")
        hbox.addWidget(btn)
        hbox.addStretch()

        self.hidden = QtGui.QFrame()
        self.main_layout.addWidget(self.hidden)
        self.hidden.setVisible(True)

        self.setDisabled(True)

    def on_enable_monitor(self):
        logger.debug('enable monitor')
        msg = "Do you really want to enable the Refraction Monitor?\n\n"
        ret = QtGui.QMessageBox.warning(self, "Refraction Monitor", msg, QtGui.QMessageBox.Ok|QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.No:
            return

    def on_disable_monitor(self):
        logger.debug('disable monitor')

