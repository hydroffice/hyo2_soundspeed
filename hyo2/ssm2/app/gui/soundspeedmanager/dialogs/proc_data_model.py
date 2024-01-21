from PySide6 import QtCore, QtWidgets

from collections import OrderedDict
from hyo2.soundspeed.profile.dicts import Dicts

QVariant = lambda value=None: value


class ProcDataModel(QtCore.QAbstractTableModel):
    data_dict = OrderedDict([
        ("Pressure", 0),
        ("Depth", 1),
        ("Speed", 2),
        ("Temp", 3),
        ("Cond", 4),
        ("Sal", 5),
        ("Source", 6),
        ("Flag", 7),
    ])

    def __init__(self, prj, table, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.table = table
        self.prj = prj
        self.editable = False

    # noinspection PyPep8Naming
    def setEditable(self, value):
        self.editable = value

    def flags(self, index):
        flags = super(ProcDataModel, self).flags(index)
        if self.editable:
            flags |= QtCore.Qt.ItemIsEditable
        return flags

    # noinspection PyMethodOverriding
    def rowCount(self, parent=None):
        return self.prj.cur.proc.num_samples

    # noinspection PyMethodOverriding
    def columnCount(self, parent=None):
        return 8

    # noinspection PyPep8Naming
    def signalUpdate(self):
        """This is full update, not efficient"""
        # noinspection PyUnresolvedReferences
        self.layoutChanged.emit()

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QVariant()
        if orientation == QtCore.Qt.Horizontal:
            try:
                return list(self.data_dict.keys())[section]
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

        if index.column() == self.data_dict['Pressure']:
            return QVariant(str(self.prj.cur.proc.pressure[index.row()]))
        elif index.column() == self.data_dict['Depth']:
            return QVariant(str(self.prj.cur.proc.depth[index.row()]))
        elif index.column() == self.data_dict['Speed']:
            return QVariant(str(self.prj.cur.proc.speed[index.row()]))
        elif index.column() == self.data_dict['Temp']:
            return QVariant(str(self.prj.cur.proc.temp[index.row()]))
        elif index.column() == self.data_dict['Cond']:
            return QVariant(str(self.prj.cur.proc.conductivity[index.row()]))
        elif index.column() == self.data_dict['Sal']:
            return QVariant(str(self.prj.cur.proc.sal[index.row()]))
        elif index.column() == self.data_dict['Source']:
            return QVariant("%.0f [%s]" % (self.prj.cur.proc.source[index.row()],
                                           Dicts.first_match(Dicts.sources, self.prj.cur.proc.source[index.row()])))
        elif index.column() == self.data_dict['Flag']:
            return QVariant("%.0f [%s]" % (self.prj.cur.proc.flag[index.row()],
                                           Dicts.first_match(Dicts.flags, self.prj.cur.proc.flag[index.row()])))
        else:
            return QVariant()

    # noinspection PyMethodOverriding
    def setData(self, index, value, role) -> bool:
        if not index.isValid():
            return False

        r = index.row()
        c = index.column()
        # test user input value
        try:
            user_value = float(value)
        except ValueError:
            msg = "invalid input: %s" % value
            # noinspection PyArgumentList
            QtWidgets.QMessageBox.critical(self.table, "Spreadsheet", msg, QtWidgets.QMessageBox.Ok)
            return False

        # switch among columns
        if c == self.data_dict['Pressure']:
            if (user_value > 20000) or (user_value < 0):
                # noinspection PyArgumentList
                ret = QtWidgets.QMessageBox.warning(self.table, "Spreadsheet",
                                                    "Do you really want to set the pressure to %s?" % user_value,
                                                    QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.No)
                if ret == QtWidgets.QMessageBox.No:
                    return False
            self.prj.cur.proc.pressure[r] = user_value

        elif c == self.data_dict['Depth']:
            # check to maintain depth monotonically descendant
            if r == 0:  # first sample
                if self.prj.cur.proc.depth[1] < user_value:
                    # noinspection PyArgumentList
                    QtWidgets.QMessageBox.critical(self.table, "Spreadsheet",
                                                   "Invalid input: %s" % user_value,
                                                   QtWidgets.QMessageBox.Ok)
                    return False
            elif r == (self.prj.cur.proc.num_samples - 1):  # last sample
                if self.prj.cur.proc.depth[-2] > user_value:
                    # noinspection PyArgumentList
                    QtWidgets.QMessageBox.critical(self.table, "Spreadsheet",
                                                   "Invalid input: %s" % user_value,
                                                   QtWidgets.QMessageBox.Ok)
                    return False
            else:
                if (self.prj.cur.proc.depth[r - 1] > user_value) or (self.prj.cur.proc.depth[r + 1] < user_value):
                    # noinspection PyArgumentList
                    QtWidgets.QMessageBox.critical(self.table, "Spreadsheet",
                                                   "Invalid input: %s" % user_value,
                                                   QtWidgets.QMessageBox.Ok)
                    return False
            self.prj.cur.proc.depth[r] = user_value

        elif c == self.data_dict['Speed']:
            if (user_value > 2000) or (user_value < 1000):
                # noinspection PyArgumentList
                ret = QtWidgets.QMessageBox.warning(self.table, "Spreadsheet",
                                                    "Do you really want to set the speed to %s?" % user_value,
                                                    QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.No)
                if ret == QtWidgets.QMessageBox.No:
                    return False
            self.prj.cur.proc.speed[r] = user_value

        elif c == self.data_dict['Temp']:
            if (user_value < 0) or (user_value > 100):
                # noinspection PyArgumentList
                ret = QtWidgets.QMessageBox.warning(self.table, "Spreadsheet",
                                                    "Do you really want to set the temperature to %s?" % user_value,
                                                    QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.No)
                if ret == QtWidgets.QMessageBox.No:
                    return False
            self.prj.cur.proc.temp[r] = user_value

        elif c == self.data_dict['Cond']:
            if (user_value < 0) or (user_value > 10000):
                # noinspection PyArgumentList
                ret = QtWidgets.QMessageBox.warning(self.table, "Spreadsheet",
                                                    "Do you really want to set the conductivity to %s?" % user_value,
                                                    QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.No)
                if ret == QtWidgets.QMessageBox.No:
                    return False
            self.prj.cur.proc.conductivity[r] = user_value

        elif c == self.data_dict['Sal']:
            if (user_value < 0) or (user_value > 100):
                # noinspection PyArgumentList
                ret = QtWidgets.QMessageBox.warning(self.table, "Spreadsheet",
                                                    "Do you really want to set the salinity to %s?" % user_value,
                                                    QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.No)
                if ret == QtWidgets.QMessageBox.No:
                    return False
            self.prj.cur.proc.sal[r] = user_value

        elif c == self.data_dict['Source']:
            if (user_value < 0) or (user_value >= len(Dicts.sources)):
                # noinspection PyArgumentList
                ret = QtWidgets.QMessageBox.warning(self.table, "Spreadsheet",
                                                    "Do you really want to set the data source to %s?" % user_value,
                                                    QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.No)
                if ret == QtWidgets.QMessageBox.No:
                    return False
            self.prj.cur.proc.source[r] = user_value

        elif c == self.data_dict['Flag']:
            if (user_value < 0) or (user_value >= len(Dicts.flags)):
                # noinspection PyArgumentList
                ret = QtWidgets.QMessageBox.warning(self.table, "Spreadsheet",
                                                    "Do you really want to set the data flag to %s?" % user_value,
                                                    QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.No)
                if ret == QtWidgets.QMessageBox.No:
                    return False
            self.prj.cur.proc.flag[r] = user_value

        else:
            return False
        return True
