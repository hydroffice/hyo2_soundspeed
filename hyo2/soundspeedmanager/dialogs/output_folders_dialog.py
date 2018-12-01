from PySide2 import QtCore, QtGui, QtWidgets

import os
import logging
logger = logging.getLogger(__name__)

from hyo2.soundspeedmanager.dialogs.dialog import AbstractDialog


class OutputFoldersDialog(AbstractDialog):

    def __init__(self, main_win, lib, writers, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        # check the passed list writers
        if type(writers) is not list:
            raise RuntimeError("The dialog takes a list of writers, not %s" % type(writers))
        if len(writers) < 1:
            raise RuntimeError("The dialog takes a list with at least 1 writer, not %s" % len(writers))
        self._writers = writers

        # a dict of output folders (one for each writer)
        self.output_folders = dict()

        self.setWindowTitle("Output folders")
        self.setMinimumWidth(420)

        settings = QtCore.QSettings()

        # outline ui
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # label
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        label = QtWidgets.QLabel("Click on the format name to change its output folder:")
        hbox.addWidget(label)
        hbox.addStretch()

        self.mainLayout.addSpacing(3)

        self.paths = dict()
        for writer in writers:
            output_folder = settings.value("output_folder_%s" % writer)
            if output_folder is None:
                settings.setValue("output_folder_%s" % writer, self.lib.outputs_folder)
                output_folder = self.lib.outputs_folder
            if not os.path.exists(output_folder):
                settings.setValue("output_folder_%s" % writer, self.lib.outputs_folder)
                output_folder = self.lib.outputs_folder

            # buttons
            hbox = QtWidgets.QHBoxLayout()
            self.mainLayout.addLayout(hbox)
            # hbox.addStretch()
            btn = QtWidgets.QPushButton("%s" % writer)
            btn.setToolTip("Select output folder for %s format" % (writer, ))
            btn.setMinimumWidth(80)
            # noinspection PyUnresolvedReferences
            btn.clicked.connect(self.on_change_folder)
            hbox.addWidget(btn)
            path = QtWidgets.QLineEdit("%s" % output_folder)
            path.setReadOnly(True)
            path.setMinimumWidth(200)
            hbox.addWidget(path)
            self.paths[writer] = path
            # hbox.addStretch()

        self.mainLayout.addStretch()

        # apply
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        btn = QtWidgets.QPushButton("Apply")
        btn.setMinimumHeight(32)
        hbox.addWidget(btn)
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_apply)
        hbox.addStretch()

        self.mainLayout.addStretch()

    def on_change_folder(self):
        """Update the output folder"""
        btn = self.sender()
        logger.debug("changing output folder for %s format" % (btn.text(), ))

        # ask user for output folder path
        # noinspection PyCallByClass
        output_folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select output folder",
                                                               self.paths[btn.text()].text())
        if not output_folder:
            return

        self.paths[btn.text()].setText(output_folder)

    def on_apply(self):
        logger.debug("apply clicked")

        settings = QtCore.QSettings()

        self.output_folders.clear()
        for writer, path_btn in self.paths.items():
            path = path_btn.text()
            self.output_folders[writer] = path
            settings.setValue("output_folder_%s" % writer, path)

        # logger.debug("%s" % self.output_folders)
        self.accept()
