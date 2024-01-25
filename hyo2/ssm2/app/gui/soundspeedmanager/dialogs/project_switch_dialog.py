import logging

from PySide6 import QtWidgets

from hyo2.ssm2.app.gui.soundspeedmanager.dialogs.dialog import AbstractDialog

logger = logging.getLogger(__name__)


class ProjectSwitchDialog(AbstractDialog):

    def __init__(self, main_win, lib, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        self.fmt_outputs = list()

        self.setWindowTitle("Switch project")
        self.setMinimumWidth(160)

        # outline ui
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # -- label
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        label = QtWidgets.QLabel("Project name:")
        hbox.addWidget(label)
        hbox.addStretch()
        # -- value
        self.load_project = QtWidgets.QComboBox()
        self.load_project.addItems(self.lib.list_projects())
        self.mainLayout.addWidget(self.load_project)
        # -- space
        self.mainLayout.addSpacing(6)
        # -- button
        btn = QtWidgets.QPushButton("Switch")
        self.mainLayout.addWidget(btn)
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_load)

    def on_load(self):
        logger.debug("switching project")

        txt = self.load_project.currentText()

        self.lib.current_project = txt
        self.lib.save_settings_to_db()
        self.lib.reload_settings_from_db()
        self.accept()
