from __future__ import absolute_import, division, print_function, unicode_literals

import os
from PySide import QtGui
from PySide import QtCore

import logging
logger = logging.getLogger(__name__)

from hydroffice.soundspeedmanager.dialogs.dialog import AbstractDialog


class ImportDataDialog(AbstractDialog):

    def __init__(self, main_win, lib, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        self.fmt_outputs = list()

        self.setWindowTitle("Import data from another project")
        self.setMinimumWidth(220)

        # outline ui
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # -- label
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        label = QtGui.QLabel("Input Project DB:")
        hbox.addWidget(label)
        hbox.addStretch()
        # -- value
        self.db_path = QtGui.QLineEdit()
        self.db_path.setReadOnly(True)
        self.mainLayout.addWidget(self.db_path)
        # -- button
        btn = QtGui.QPushButton("Browse")
        self.mainLayout.addWidget(btn)
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_browse)
        # -- space
        self.mainLayout.addSpacing(6)
        # -- button
        btn = QtGui.QPushButton("Import")
        self.mainLayout.addWidget(btn)
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_import)

    def on_browse(self):
        logger.debug("browsing for db files")

        # ask the file path to the user
        flt = "Project DB(*.db);;All files (*.*)"
        selection, _ = QtGui.QFileDialog.getOpenFileName(self, "Select input project DB",
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
            QtGui.QMessageBox.warning(self, "Import warning", msg, QtGui.QMessageBox.Ok)
            return
        logger.debug('input db: %s' % path)

        pk_issues, pk_done = self.lib.db_import_data_from_db(path)

        if len(pk_issues) == 0:
            msg = "Successfully imported %d profile(s)" % len(pk_done)
            QtGui.QMessageBox.information(self, "Import data", msg, QtGui.QMessageBox.Ok)
            self.accept()

        else:
            msg = "Issue in importing %s profile(s)\n" % ", ".join(["#%02d" % pk for pk in pk_issues])
            msg += "Possible primary key duplication!"
            QtGui.QMessageBox.warning(self, "Import warning", msg, QtGui.QMessageBox.Ok)
            return
