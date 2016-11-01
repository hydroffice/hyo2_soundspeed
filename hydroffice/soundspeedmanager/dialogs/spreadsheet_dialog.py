from __future__ import absolute_import, division, print_function, unicode_literals

from PySide import QtGui
from PySide import QtCore
QVariant = lambda value=None: value

import os
from collections import OrderedDict
import logging
logger = logging.getLogger(__name__)

from hydroffice.soundspeedmanager.dialogs.dialog import AbstractDialog


class DataModel(QtCore.QAbstractTableModel):

    data_dict = OrderedDict([
        ("Depth", 0),
        ("Speed", 1),
        ("Temp", 2),
        ("Sal", 3),
        ("Source", 4),
        ("Flag", 5),
    ])

    def __init__(self, prj, table, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.table = table
        self.prj = prj
        self.editable = False

    def setEditable(self, value):
        self.editable = value

    def flags(self, index):
        flags = super(DataModel, self).flags(index)
        if self.editable:
            flags |= QtCore.Qt.ItemIsEditable
        return flags

    def rowCount(self, parent=None):
        return self.prj.cur.proc.num_samples

    def columnCount(self, parent=None):
        return 6

    def signalUpdate(self):
        """This is full update, not efficient"""
        self.layoutChanged.emit()

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QVariant()
        if orientation == QtCore.Qt.Horizontal:
            try:
                return self.data_dict.keys()[section]
            except IndexError:
                return QVariant()
        elif orientation == QtCore.Qt.Vertical:
            try:
                return '%05d' % section
            except IndexError:
                return QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QVariant()
        if not index.isValid():
            return QVariant()

        if index.column() == self.data_dict['Depth']:
            return QVariant(str(self.prj.cur.proc.depth[index.row()]))
        elif index.column() == self.data_dict['Speed']:
            return QVariant(str(self.prj.cur.proc.speed[index.row()]))
        elif index.column() == self.data_dict['Temp']:
            return QVariant(str(self.prj.cur.proc.temp[index.row()]))
        elif index.column() == self.data_dict['Sal']:
            return QVariant(str(self.prj.cur.proc.sal[index.row()]))
        elif index.column() == self.data_dict['Source']:
            return QVariant(str(self.prj.cur.proc.source[index.row()]))
        elif index.column() == self.data_dict['Flag']:
            return QVariant(str(self.prj.cur.proc.flag[index.row()]))
        else:
            return QVariant()

    def setData(self, index, value, role):
        if not index.isValid():
            return False

        r = index.row()
        c = index.column()
        # test user input value
        try:
            user_value = float(value)
        except ValueError:
            msg = "invalid input: %s" % value
            QtGui.QMessageBox.critical(self.table, "Spreadsheet", msg, QtGui.QMessageBox.Ok)
            return False

        # switch among columns
        if c == self.data_dict['Depth']:
            # check to maintain depth monotonically descendant
            if r == 0:  # first sample
                if self.prj.cur.proc.depth[1] < user_value:
                    QtGui.QMessageBox.critical(self.table, "Spreadsheet",
                                               "Invalid input: %s" % user_value,
                                               QtGui.QMessageBox.Ok)
                    return False
            elif r == (self.prj.cur.proc.num_samples - 1):  # last sample
                if self.prj.cur.proc.depth[-2] > user_value:
                    QtGui.QMessageBox.critical(self.table, "Spreadsheet",
                                               "Invalid input: %s" % user_value,
                                               QtGui.QMessageBox.Ok)
                    return False
            else:
                if (self.prj.cur.proc.depth[r - 1] > user_value) or (self.prj.cur.proc.depth[r + 1] < user_value):
                    QtGui.QMessageBox.critical(self.table, "Spreadsheet",
                                               "Invalid input: %s" % user_value,
                                               QtGui.QMessageBox.Ok)
                    return False
            self.prj.cur.proc.depth[r] = user_value

        elif c == self.data_dict['Speed']:
            if (user_value > 2000) or (user_value < 1000):
                ret = QtGui.QMessageBox.warning(self.table, "Spreadsheet",
                                                "Do you really want to set the speed to %s?" % user_value,
                                                QtGui.QMessageBox.Ok|QtGui.QMessageBox.No)
                if ret == QtGui.QMessageBox.No:
                    return False
            self.prj.cur.proc.speed[r] = user_value

        elif c == self.data_dict['Temp']:
            if (user_value < 0) or (user_value > 100):
                ret = QtGui.QMessageBox.warning(self.table, "Spreadsheet",
                                                "Do you really want to set the temperature to %s?" % user_value,
                                                QtGui.QMessageBox.Ok|QtGui.QMessageBox.No)
                if ret == QtGui.QMessageBox.No:
                    return False
            self.prj.cur.proc.temp[r] = user_value

        elif c == self.data_dict['Sal']:
            if (user_value < 0) or (user_value > 100):
                ret = QtGui.QMessageBox.warning(self.table, "Spreadsheet",
                                                "Do you really want to set the salinity to %s?" % user_value,
                                                QtGui.QMessageBox.Ok|QtGui.QMessageBox.No)
                if ret == QtGui.QMessageBox.No:
                    return False
            self.prj.cur.proc.sal[r] = user_value

        elif c == self.data_dict['Source']:
            if (user_value < 0) or (user_value > 100):
                ret = QtGui.QMessageBox.warning(self.table, "Spreadsheet",
                                                "Do you really want to set the data source to %s?" % user_value,
                                                QtGui.QMessageBox.Ok|QtGui.QMessageBox.No)
                if ret == QtGui.QMessageBox.No:
                    return False
            self.prj.cur.proc.source[r] = user_value

        elif c == self.data_dict['Flag']:
            if (user_value < 0) or (user_value > 100):
                ret = QtGui.QMessageBox.warning(self.table, "Spreadsheet",
                                                "Do you really want to set the data flag to %s?" % user_value,
                                                QtGui.QMessageBox.Ok|QtGui.QMessageBox.No)
                if ret == QtGui.QMessageBox.No:
                    return False
            self.prj.cur.proc.flag[r] = user_value

        else:
            return False
        return True


class SpreadSheetDialog(AbstractDialog):

    def __init__(self, main_win, lib, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMinMaxButtonsHint)

        self.setWindowTitle("Spreadsheet")
        self.setMinimumSize(QtCore.QSize(400, 300))

        # outline ui
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # types
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        self.table = QtGui.QTableView()
        self.model = DataModel(self.prj, table=self)
        self.table.setModel(self.model)
        self.table.resizeColumnsToContents()
        # self.table.resizeRowsToContents()

        hbox.addWidget(self.table)

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
        self.editable.clicked.connect(self.on_editable)
        self.editable.setToolTip("Unlock data editing")
        hbox.addWidget(self.editable)
        hbox.addStretch()
        self.mainLayout.addLayout(hbox)

    def on_editable(self):
        logger.debug("editable: %s" % self.editable.isChecked())
        if self.editable.isChecked():
            msg = "Do you really want to manually edit the data?"
            ret = QtGui.QMessageBox.warning(self, "Spreadsheet", msg, QtGui.QMessageBox.Ok|QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                self.editable.setChecked(False)
                return
            self.table.model().setEditable(True)
        else:
            self.table.model().setEditable(False)
