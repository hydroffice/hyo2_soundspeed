from __future__ import absolute_import, division, print_function, unicode_literals

from PySide import QtGui
from PySide import QtCore

import os

import logging
logger = logging.getLogger(__name__)

from hydroffice.soundspeedmanager.dialogs.dialog import AbstractDialog
from hydroffice.soundspeedmanager.dialogs.raw_data_model import RawDataModel
from hydroffice.soundspeedmanager.dialogs.proc_data_model import ProcDataModel
from hydroffice.soundspeedmanager.dialogs.sis_data_model import SisDataModel


class SpreadSheetDialog(AbstractDialog):

    def __init__(self, main_win, lib, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMinMaxButtonsHint)

        self.setWindowTitle("Spreadsheet")
        self.setMinimumSize(QtCore.QSize(400, 300))

        # outline ui
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.tabs = QtGui.QTabWidget()
        self.mainLayout.addWidget(self.tabs)

        # raw
        self.raw_table = QtGui.QTableView()
        self.raw_model = RawDataModel(self.lib, table=self)
        self.raw_table.setModel(self.raw_model)
        self.raw_table.resizeColumnsToContents()
        idx = self.tabs.insertTab(0, self.raw_table, "Raw")
        self.tabs.setTabToolTip(idx, "Raw data")

        # proc
        self.proc_table = QtGui.QTableView()
        self.proc_model = ProcDataModel(self.lib, table=self)
        self.proc_table.setModel(self.proc_model)
        self.proc_table.resizeColumnsToContents()
        idx = self.tabs.insertTab(1, self.proc_table, "Processed")
        self.tabs.setTabToolTip(idx, "Processed data")

        # sis
        self.sis_table = QtGui.QTableView()
        self.sis_model = SisDataModel(self.lib, table=self)
        self.sis_table.setModel(self.sis_model)
        self.sis_table.resizeColumnsToContents()
        idx = self.tabs.insertTab(2, self.sis_table, "SIS")
        self.tabs.setTabToolTip(idx, "SIS-output data")

        self.mainLayout.addSpacing(8)

        # edit/apply
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch()
        self.editable = QtGui.QPushButton()
        self.editable.setIconSize(QtCore.QSize(30, 30))
        self.editable.setFixedHeight(34)
        edit_icon = QtGui.QIcon()
        edit_icon.addFile(os.path.join(self.media, 'lock.png'), state=QtGui.QIcon.Off)
        edit_icon.addFile(os.path.join(self.media, 'unlock.png'), state=QtGui.QIcon.On)
        self.editable.setIcon(edit_icon)
        self.editable.setCheckable(True)
        # noinspection PyUnresolvedReferences
        self.editable.clicked.connect(self.on_editable)
        self.editable.setToolTip("Unlock data editing")
        hbox.addWidget(self.editable)
        hbox.addStretch()
        self.mainLayout.addLayout(hbox)

        self.tabs.setCurrentIndex(1)

    def on_editable(self):
        logger.debug("editable: %s" % self.editable.isChecked())
        if self.editable.isChecked():
            msg = "Do you really want to manually edit the processed data?"
            # noinspection PyCallByClass
            ret = QtGui.QMessageBox.warning(self, "Spreadsheet", msg, QtGui.QMessageBox.Ok|QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                self.editable.setChecked(False)
                return
            self.proc_table.model().setEditable(True)
        else:
            self.proc_table.model().setEditable(False)
