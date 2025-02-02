import logging

from PySide6 import QtWidgets

from hyo2.ssm2.app.gui.soundspeedmanager.dialogs.dialog import AbstractDialog

logger = logging.getLogger(__name__)


class ImportDataDialog(AbstractDialog):

    def __init__(self, main_win, lib, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        self.fmt_outputs = list()

        self.setWindowTitle("Import data from another project")
        self.setMinimumWidth(220)

        # outline ui
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # -- label
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        label = QtWidgets.QLabel("Input Project DB:")
        hbox.addWidget(label)
        hbox.addStretch()
        # -- value
        self.db_path = QtWidgets.QLineEdit()
        self.db_path.setReadOnly(True)
        self.mainLayout.addWidget(self.db_path)
        # -- button
        btn = QtWidgets.QPushButton("Browse")
        self.mainLayout.addWidget(btn)
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_browse)
        # -- space
        self.mainLayout.addSpacing(6)
        # -- button
        btn = QtWidgets.QPushButton("Import")
        self.mainLayout.addWidget(btn)
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_import)

    def on_browse(self):
        logger.debug("browsing for db files")

        # ask the file path to the user
        flt = "Project DB(*.db);;All files (*.*)"
        # noinspection PyCallByClass
        selection, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select input project DB",
                                                             self.lib.projects_folder,
                                                             flt)
        if not selection:
            return

        self.db_path.setText(selection)

    def on_import(self):
        logger.debug("importing for db files")

        path = self.db_path.text().lower()
        if len(path) == 0:
            msg = "Set the path to the project db!"
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.warning(self, "Import warning", msg, QtWidgets.QMessageBox.StandardButton.Ok)
            return
        logger.debug('input db: %s' % path)

        self.progress.start(title="Importing profiles", init_value=30.0)
        pk_issues, pk_done = self.lib.db_import_data_from_db(path)
        self.progress.end()

        if len(pk_issues) == 0:
            msg = "Successfully imported %d profile(s)" % len(pk_done)
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.information(self, "Import data", msg, QtWidgets.QMessageBox.StandardButton.Ok)
            self.accept()

        else:
            msg = "Issue in importing %s profile(s)\n" % ", ".join(["#%02d" % pk for pk in pk_issues])
            msg += "Possible primary key duplication!"
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.warning(self, "Import warning", msg, QtWidgets.QMessageBox.StandardButton.Ok)
            return
