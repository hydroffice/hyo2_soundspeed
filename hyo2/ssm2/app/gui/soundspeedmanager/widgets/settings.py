import os
import logging

from PySide6 import QtCore, QtGui, QtWidgets

logger = logging.getLogger(__name__)

from hyo2.ssm2.app.gui.soundspeedmanager.widgets.widget import AbstractWidget
from hyo2.ssm2.app.gui.soundspeedsettings.mainwin import MainWin


class Settings(AbstractWidget):
    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win, lib):
        AbstractWidget.__init__(self, main_win=main_win, lib=lib)

        # create the overall layout
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.frame.setLayout(self.mainLayout)
        # settings
        self.settings_widget = MainWin(lib=lib, main_win=self.main_win)
        self.settings_widget.set_editable(False)
        self.mainLayout.addWidget(self.settings_widget)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch()

        # lock/unlock
        self.editable = QtWidgets.QPushButton()
        self.editable.setIconSize(QtCore.QSize(30, 30))
        self.editable.setFixedHeight(34)
        edit_icon = QtGui.QIcon()
        edit_icon.addFile(os.path.join(self.media, 'lock.png'), state=QtGui.QIcon.Off)
        edit_icon.addFile(os.path.join(self.media, 'unlock.png'), state=QtGui.QIcon.On)
        self.editable.setIcon(edit_icon)
        self.editable.setCheckable(True)
        # noinspection PyUnresolvedReferences
        self.editable.clicked.connect(self.on_editable)
        self.editable.setToolTip("Unlock settings editing")
        hbox.addWidget(self.editable)
        hbox.addStretch()
        self.mainLayout.addLayout(hbox)

        # view setup
        self.view_act = QtGui.QAction('View Setup', self)
        self.view_act.setShortcut('Ctrl+S')
        # noinspection PyUnresolvedReferences
        self.view_act.triggered.connect(self.on_view_setup)
        self.main_win.setup_menu.addAction(self.view_act)

        # edit setup
        self.edit_act = QtGui.QAction('Edit Setup', self)
        # self.edit_act.setShortcut('Ctrl+Alt+S')
        # noinspection PyUnresolvedReferences
        self.edit_act.triggered.connect(self.on_edit_setup)
        self.main_win.setup_menu.addAction(self.edit_act)

    def on_view_setup(self):
        self.main_win.switch_to_setup_tab()

    def on_edit_setup(self):
        self.main_win.switch_to_setup_tab()
        self.editable.setChecked(True)
        self.on_editable()

    def on_editable(self):
        logger.debug("editable: %s" % self.editable.isChecked())
        if self.editable.isChecked():
            msg = "Do you really want to change the settings?"
            # noinspection PyCallByClass
            ret = QtWidgets.QMessageBox.warning(self, "Settings", msg,
                                                QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.No)
            if ret == QtWidgets.QMessageBox.StandardButton.No:
                self.editable.setChecked(False)
                return
            self.settings_widget.set_editable(True)
        else:
            self.settings_widget.set_editable(False)

    def setup_changed(self):
        self.settings_widget.setup_changed()

    def server_started(self):
        self.setDisabled(True)

    def server_stopped(self):
        self.setEnabled(True)
