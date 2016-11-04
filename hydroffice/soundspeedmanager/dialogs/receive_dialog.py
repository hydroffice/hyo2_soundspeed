from __future__ import absolute_import, division, print_function, unicode_literals

from PySide import QtGui
from PySide import QtCore

import os
import logging
logger = logging.getLogger(__name__)

from hydroffice.soundspeedmanager.dialogs.dialog import AbstractDialog


class ReceiveDialog(AbstractDialog):

    def __init__(self, main_win, lib, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        self.setWindowTitle("Receive data")

        # outline ui
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.buttonBox = QtGui.QDialogButtonBox(QtCore.Qt.Vertical)
        self.mainLayout.addWidget(self.buttonBox)

        # add buttons
        # -- WOA09
        btn = QtGui.QPushButton("Retrieve WOA09 data")
        self.buttonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve synthetic data from WOA09 Atlas")
        btn.clicked.connect(self.on_click_woa09)
        # -- WOA13
        btn = QtGui.QPushButton("Retrieve WOA13 data")
        self.buttonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve synthetic data from WOA13 Atlas")
        btn.clicked.connect(self.on_click_woa13)
        # -- RTOFS
        btn = QtGui.QPushButton("Retrieve RTOFS data")
        self.buttonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve synthetic data from RTOFS Atlas")
        btn.clicked.connect(self.on_click_rtofs)
        # -- SIS
        btn = QtGui.QPushButton("Retrieve from SIS")
        self.buttonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve current profile from SIS")
        btn.clicked.connect(self.on_click_sis)

    def on_click_woa09(self):
        """Retrieve WOA09 data"""
        try:
            self.lib.retrieve_woa09()

        except RuntimeError as e:
            msg = "Issue in importing the data:\n\n> %s" % e
            QtGui.QMessageBox.critical(self, "Receive error", msg, QtGui.QMessageBox.Ok)
            return

        self.accept()

    def on_click_woa13(self):
        """Retrieve WOA13 data"""
        try:
            self.lib.retrieve_woa13()

        except RuntimeError as e:
            msg = "Issue in importing the data:\n\n> %s" % e
            QtGui.QMessageBox.critical(self, "Receive error", msg, QtGui.QMessageBox.Ok)
            return

        self.accept()

    def on_click_rtofs(self):
        """Retrieve RTOFS data"""
        try:
            self.lib.retrieve_rtofs()

        except RuntimeError as e:
            msg = "Issue in importing the data:\n\n> %s" % e
            QtGui.QMessageBox.critical(self, "Receive error", msg, QtGui.QMessageBox.Ok)
            return

        self.accept()

    def on_click_sis(self):
        """Retrieve SIS data"""
        if not self.lib.use_sis():
            msg = "The SIS listening is not activated!\n\nGo to Settings/Input/Listen SIS"
            QtGui.QMessageBox.critical(self, "Receive error", msg, QtGui.QMessageBox.Ok)
            return

        try:
            self.lib.retrieve_sis()

        except RuntimeError as e:
            msg = "Issue in retrieving data from SIS:\n\n%s" % e
            QtGui.QMessageBox.critical(self, "Receive error", msg, QtGui.QMessageBox.Ok)
            return

        self.accept()

