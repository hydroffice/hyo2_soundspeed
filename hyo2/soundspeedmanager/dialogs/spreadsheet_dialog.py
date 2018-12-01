from PySide2 import QtCore, QtGui, QtWidgets

import os

import logging
logger = logging.getLogger(__name__)

from hyo2.soundspeedmanager.dialogs.dialog import AbstractDialog
from hyo2.soundspeedmanager.dialogs.raw_data_model import RawDataModel
from hyo2.soundspeedmanager.dialogs.proc_data_model import ProcDataModel
from hyo2.soundspeedmanager.dialogs.sis_data_model import SisDataModel


class SpreadSheetDialog(AbstractDialog):

    def __init__(self, main_win, lib, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMinMaxButtonsHint)

        self.setWindowTitle("Spreadsheet")
        self.setMinimumSize(QtCore.QSize(400, 300))

        # outline ui
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.tabs = QtWidgets.QTabWidget()
        self.mainLayout.addWidget(self.tabs)

        # raw
        self.raw_table = QtWidgets.QTableView()
        self.raw_model = RawDataModel(self.lib, table=self)
        self.raw_table.setModel(self.raw_model)
        self.raw_table.resizeColumnsToContents()
        idx = self.tabs.insertTab(0, self.raw_table, "Raw")
        self.tabs.setTabToolTip(idx, "Raw data")

        # proc
        self.proc_table = QtWidgets.QTableView()
        self.proc_model = ProcDataModel(self.lib, table=self)
        self.proc_table.setModel(self.proc_model)
        self.proc_table.resizeColumnsToContents()
        idx = self.tabs.insertTab(1, self.proc_table, "Processed")
        self.tabs.setTabToolTip(idx, "Processed data")

        # sis
        self.sis_table = QtWidgets.QTableView()
        self.sis_model = SisDataModel(self.lib, table=self)
        self.sis_table.setModel(self.sis_model)
        self.sis_table.resizeColumnsToContents()
        idx = self.tabs.insertTab(2, self.sis_table, "SIS")
        self.tabs.setTabToolTip(idx, "SIS-output data")

        self.mainLayout.addSpacing(8)

        # edit/apply
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch()
        self.editable = QtWidgets.QPushButton()
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
            ret = QtWidgets.QMessageBox.warning(self, "Spreadsheet", msg, QtWidgets.QMessageBox.Ok|QtWidgets.QMessageBox.No)
            if ret == QtWidgets.QMessageBox.No:
                self.editable.setChecked(False)
                return
            self.proc_table.model().setEditable(True)
        else:
            self.proc_table.model().setEditable(False)
