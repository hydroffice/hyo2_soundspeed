from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

from PySide import QtGui, QtCore

logger = logging.getLogger(__name__)

from .widget import AbstractWidget
from hydroffice.soundspeedsettings.mainwin import MainWin


class Settings(AbstractWidget):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win, prj):
        AbstractWidget.__init__(self, main_win=main_win, prj=prj)

        # create the overall layout
        self.mainLayout = QtGui.QVBoxLayout()
        self.frame.setLayout(self.mainLayout)
        # settings
        self.settings_widget = MainWin(prj=prj, main_win=self.main_win)
        self.settings_widget.set_editable(False)
        self.mainLayout.addWidget(self.settings_widget)
        # lock/unlock
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch()
        self.editable = QtGui.QPushButton()
        self.editable.setIconSize(QtCore.QSize(30, 30))
        self.editable.setFixedHeight(34)
        edit_icon = QtGui.QIcon()
        edit_icon.addFile(os.path.join(self.media, 'lock.png'), state=QtGui.QIcon.Off)
        edit_icon.addFile(os.path.join(self.media, 'unlock.png'), state=QtGui.QIcon.On)
        self.editable.setIcon(edit_icon)
        self.editable.setCheckable(True)
        self.editable.clicked.connect(self.on_editable)
        self.editable.setToolTip("Unlock settings editing")
        hbox.addWidget(self.editable)
        self.reload = QtGui.QPushButton("Reload")
        self.reload.setFixedHeight(self.editable.height())
        self.reload.setDisabled(True)
        self.reload.clicked.connect(self.on_reload)
        self.reload.setToolTip("Reload settings")
        hbox.addWidget(self.reload)
        hbox.addStretch()
        self.mainLayout.addLayout(hbox)

    def on_editable(self):
        logger.debug("editable: %s" % self.editable.isChecked())
        if self.editable.isChecked():
            msg = "Do you really want to change the settings?"
            ret = QtGui.QMessageBox.warning(self, "Settings", msg, QtGui.QMessageBox.Ok|QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                self.editable.setChecked(False)
                return
            self.reload.setEnabled(True)
            self.settings_widget.set_editable(True)
        else:
            self.reload.setDisabled(True)
            self.settings_widget.set_editable(False)

    def on_reload(self):
        logger.debug("reload settings")
        try:
            self.prj.reload_settings_from_db()
        except RuntimeError as e:
            msg = "Issue in reloading settings\n%s" % e
            QtGui.QMessageBox.critical(self, "Settings error", msg, QtGui.QMessageBox.Ok)
            return

        msg = "New settings have been applied!"
        QtGui.QMessageBox.information(self, "Settings", msg, QtGui.QMessageBox.Ok)