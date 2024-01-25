import copy
import logging
from PySide6 import QtWidgets

from hyo2.ssm2.app.gui.soundspeedmanager.dialogs.dialog import AbstractDialog

logger = logging.getLogger(__name__)


class ReferenceDialog(AbstractDialog):

    def __init__(self, main_win, lib, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        self.setWindowTitle("Reference cast")

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

        self.mainLayout.addSpacing(12)

    def on_set_ref(self):
        if self.lib.has_ssp():
            logger.debug('cloning current profile')
            self.lib.ref = copy.deepcopy(self.lib.ssp)

        self.accept()

    def on_reload_ref(self):
        if self.lib.has_ref():
            logger.debug('reload current reference cast')
            self.lib.ssp = copy.deepcopy(self.lib.ref)

        self.accept()

    def on_clear_ref(self):
        if self.lib.has_ref():
            logger.debug('cleaning reference')
            self.lib.ref = None

        self.accept()
