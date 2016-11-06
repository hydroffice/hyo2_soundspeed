from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

from PySide import QtGui

logger = logging.getLogger(__name__)

from .widget import AbstractWidget


class Seacat(AbstractWidget):

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
        # -- connect
        btn = QtGui.QPushButton("Connect")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_connect)
        btn.setToolTip("Connect to instrument")
        hbox.addWidget(btn)
        # -- retrieve
        btn = QtGui.QPushButton("Retrieve")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_retrieve)
        btn.setToolTip("Retrieve data from instrument")
        hbox.addWidget(btn)
        hbox.addStretch()

        self.main_layout.addStretch()

    def on_connect(self):
        logger.debug('connecting ...')
        msg = "To be implemented!"
        QtGui.QMessageBox.warning(self, "SBE SeaCAT", msg, QtGui.QMessageBox.Ok | QtGui.QMessageBox.No)

    def on_retrieve(self):
        logger.debug('retrieving ...')
        msg = "To be implemented!"
        QtGui.QMessageBox.warning(self, "SBE SeaCAT", msg, QtGui.QMessageBox.Ok | QtGui.QMessageBox.No)

