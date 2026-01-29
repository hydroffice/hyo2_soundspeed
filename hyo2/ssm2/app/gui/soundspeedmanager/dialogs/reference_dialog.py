import copy
import logging
from PySide6 import QtCore, QtWidgets

from hyo2.ssm2.app.gui.soundspeedmanager.dialogs.dialog import AbstractDialog

logger = logging.getLogger(__name__)


class ReferenceDialog(AbstractDialog):

    def __init__(self, main_win, lib, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        self.setWindowTitle("Reference cast")

        settings = QtCore.QSettings()

        # outline ui
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # set reference
        self.setRefLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(self.setRefLayout)
        # - label
        label = QtWidgets.QLabel("Set current profile as reference cast")
        self.setRefLayout.addWidget(label)
        # - button
        btn = QtWidgets.QPushButton("Apply")
        btn.setToolTip("Apply!")
        btn.setFixedWidth(60)
        if not self.lib.has_ssp():
            btn.setDisabled(True)
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_set_ref)
        self.setRefLayout.addWidget(btn)

        # set previous previous profile as reference 
        self.setPreRefLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(self.setPreRefLayout)
        # - label
        label = QtWidgets.QLabel("Set previous profile as reference cast\n(used for data reception only)")
        self.setPreRefLayout.addWidget(label)
        # - button
        btn = QtWidgets.QPushButton("Apply")
        btn.setCheckable(True)
        btn.setToolTip("Apply!")
        btn.setFixedWidth(60)
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_set_previous_ref)
        self.setPreRefLayout.addWidget(btn)
        # - enable only for data reception
        if not self.lib.use_mvp() and not self.lib.use_sippican():
            logger.debug("Not using network data reception")
            settings.setValue("previousRef", False)
            btn.setChecked(False)
            btn.setDisabled(True)
        # - settings
        btn_settings = settings.value("previousRef", False)
        logger.debug("Previous profile ref value: {}".format(btn_settings))
        if btn_settings is None:
            settings.setValue("previousRef", False)
        if btn_settings == 'true':
            btn.setChecked(True)
        
        # load reference
        self.loadLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(self.loadLayout)
        # - label
        label = QtWidgets.QLabel("Reload reference cast as current profile")
        self.loadLayout.addWidget(label)
        # - button
        btn = QtWidgets.QPushButton("Apply")
        btn.setToolTip("Apply!")
        btn.setFixedWidth(60)
        if not self.lib.has_ref():
            btn.setDisabled(True)
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_reload_ref)
        self.loadLayout.addWidget(btn)

        # clear reference
        self.clearLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(self.clearLayout)
        # - label
        label = QtWidgets.QLabel("Clear current reference cast")
        self.clearLayout.addWidget(label)
        # - button
        btn = QtWidgets.QPushButton("Apply")
        btn.setToolTip("Apply!")
        btn.setFixedWidth(60)
        if not self.lib.has_ref():
            btn.setDisabled(True)
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_clear_ref)
        self.clearLayout.addWidget(btn)

        # close reference dialog
        self.closeLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(self.closeLayout)
        # - button
        btn = QtWidgets.QPushButton("Close")
        btn.setToolTip("Close Window!")
        btn.setFixedWidth(60)
        btn.clicked.connect(self.on_close)
        self.closeLayout.addWidget(btn)
        
        self.mainLayout.addSpacing(12)

    def on_set_ref(self):
        if self.lib.has_ssp():
            logger.debug('cloning current profile')
            self.lib.ref = copy.deepcopy(self.lib.ssp)

    def on_set_previous_ref(self):
        settings = QtCore.QSettings()
        
        last_btn = self.setPreRefLayout.itemAt(1).widget()
        
        if isinstance(last_btn, QtWidgets.QPushButton):
            if last_btn.isChecked():
                last_btn.setChecked(True)
                settings.setValue("previousRef", True)
            else:
                last_btn.setChecked(False)                
                settings.setValue("previousRef", False)
        
    def on_reload_ref(self):
        if self.lib.has_ref():
            logger.debug('reload current reference cast')
            self.lib.ssp = copy.deepcopy(self.lib.ref)

    def on_clear_ref(self):
        if self.lib.has_ref():
            logger.debug('cleaning reference')
            self.lib.ref = None

    def on_close(self):
        self.accept()
