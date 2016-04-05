from __future__ import absolute_import, division, print_function, unicode_literals

from PySide import QtGui
from PySide import QtCore

import logging
logger = logging.getLogger(__name__)

from hydroffice.soundspeedmanager.dialogs.dialog import AbstractDialog


class ImportDialog(AbstractDialog):

    def __init__(self, main_win, prj, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, prj=prj, parent=parent)

        # retrieve the available readers
        self.names = list()
        self.descs = list()
        self.exts = list()
        for rdr in self.prj.readers:
            if len(rdr.ext):
                self.names.append(rdr.name)
                self.descs.append(rdr.desc)
                self.exts.append(rdr.ext)

        self.setWindowTitle("Import data")

        # outline ui
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.buttonBox = QtGui.QDialogButtonBox(QtCore.Qt.Vertical)
        self.mainLayout.addWidget(self.buttonBox)

        # add buttons
        for idx, _ in enumerate(self.names):
            btn = QtGui.QPushButton("%s" % self.descs[idx])
            self.buttonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
            btn.setToolTip("Import %s format [*.%s]" % (self.descs[idx], ", *.".join(self.exts[idx])))
        self.buttonBox.clicked.connect(self.on_click_btn)

    def on_click_btn(self, btn):
        print("clicked %s" % btn.text())
        idx = self.descs.index(btn.text())
        name = self.names[idx]
        desc = self.descs[idx]
        ext = self.exts[idx]

        # ask the file path to the user
        flt = "Format %s(*.%s);;All files (*.*)" % (desc, " *.".join(ext))
        selection, _ = QtGui.QFileDialog.getOpenFileName(self, "Load data file", None, flt)
        if not selection:
            return

        logger.debug('user selection: %s' % selection)

        self.progress.forceShow()
        self.progress.setValue(20)

        self.progress.setValue(100)
