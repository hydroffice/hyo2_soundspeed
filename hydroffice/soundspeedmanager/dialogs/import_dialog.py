from __future__ import absolute_import, division, print_function, unicode_literals

from PySide import QtGui
from PySide import QtCore

import os
import logging
logger = logging.getLogger(__name__)

from hydroffice.soundspeedmanager.dialogs.dialog import AbstractDialog


class ImportDialog(AbstractDialog):

    def __init__(self, main_win, lib, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        self.setWindowTitle("Import data")

        # outline ui
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.buttonBox = QtGui.QDialogButtonBox(QtCore.Qt.Vertical)
        self.mainLayout.addWidget(self.buttonBox)

        # add buttons
        for idx, _ in enumerate(self.lib.name_readers):
            if len(self.lib.ext_readers[idx]) == 0:
                continue
            btn = QtGui.QPushButton("%s" % self.lib.desc_readers[idx])
            self.buttonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
            btn.setToolTip("Import %s format [*.%s]" % (self.lib.desc_readers[idx],
                                                        ", *.".join(self.lib.ext_readers[idx])))
        self.buttonBox.clicked.connect(self.on_click_btn)

    def on_click_btn(self, btn):
        # print("clicked %s" % btn.text())
        idx = self.lib.desc_readers.index(btn.text())
        name = self.lib.name_readers[idx]
        desc = self.lib.desc_readers[idx]
        ext = self.lib.ext_readers[idx]

        # ask the file path to the user
        flt = "Format %s(*.%s);;All files (*.*)" % (desc, " *.".join(ext))
        settings = QtCore.QSettings()
        selection, _ = QtGui.QFileDialog.getOpenFileName(self, "Load data file",
                                                         settings.value("import_folder"),
                                                         flt)
        if not selection:
            return
        settings.setValue("import_folder", os.path.dirname(selection))
        logger.debug('user selection: %s' % selection)

        self.progress.forceShow()
        self.progress.setValue(20)
        try:
            self.lib.import_data(data_path=selection, data_format=name)

        except RuntimeError as e:
            self.progress.setValue(100)
            msg = "Issue in importing the data:\n\n> %s" % e
            QtGui.QMessageBox.critical(self, "Import error", msg, QtGui.QMessageBox.Ok)
            return

        self.progress.setValue(100)
        self.accept()
