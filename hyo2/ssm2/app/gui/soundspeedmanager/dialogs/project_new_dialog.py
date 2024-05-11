import logging

from PySide6 import QtCore, QtGui, QtWidgets

from hyo2.ssm2.app.gui.soundspeedmanager.dialogs.dialog import AbstractDialog

logger = logging.getLogger(__name__)


class ProjectNewDialog(AbstractDialog):

    def __init__(self, main_win, lib, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        self.fmt_outputs = list()

        self.setWindowTitle("New project")
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
        self.new_project = QtWidgets.QLineEdit()
        rex = QtCore.QRegularExpression('[a-zA-Z0-9_.-]+')
        if not rex.isValid():
            logger.warning(rex.errorString())
        validator = QtGui.QRegularExpressionValidator(rex)
        self.new_project.setValidator(validator)
        self.mainLayout.addWidget(self.new_project)
        # -- space
        self.mainLayout.addSpacing(6)
        # -- button
        btn = QtWidgets.QPushButton("Create")
        self.mainLayout.addWidget(btn)
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_create)

    def on_create(self):
        logger.debug("creating project")

        txt = self.new_project.text()

        if len(txt) == 0:
            msg = "Set the project name!"
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.warning(self, "Creation warning", msg, QtWidgets.QMessageBox.StandardButton.Ok)
            return

        if txt in self.lib.list_projects():
            msg = "The project '%s' already exists. Load it!" % txt
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.warning(self, "Creation warning", msg, QtWidgets.QMessageBox.StandardButton.Ok)
            return

        self.lib.current_project = txt
        self.lib.save_settings_to_db()
        self.lib.reload_settings_from_db()
        self.accept()
