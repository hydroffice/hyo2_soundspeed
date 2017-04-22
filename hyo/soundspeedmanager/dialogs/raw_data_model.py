from PySide import QtGui
from PySide import QtCore
QVariant = lambda value=None: value

from collections import OrderedDict


class RawDataModel(QtCore.QAbstractTableModel):

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

    def setEditable(self, value):
        self.editable = value

    def flags(self, index):
        flags = super(RawDataModel, self).flags(index)
        if self.editable:
            flags |= QtCore.Qt.ItemIsEditable
        return flags

    def rowCount(self, parent=None):
        return self.prj.cur.data.num_samples

    def columnCount(self, parent=None):
        return 8

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
            return QVariant(str(self.prj.cur.data.pressure[index.row()]))
        elif index.column() == self.data_dict['Depth']:
            return QVariant(str(self.prj.cur.data.depth[index.row()]))
        elif index.column() == self.data_dict['Speed']:
            return QVariant(str(self.prj.cur.data.speed[index.row()]))
        elif index.column() == self.data_dict['Temp']:
            return QVariant(str(self.prj.cur.data.temp[index.row()]))
        elif index.column() == self.data_dict['Cond']:
            return QVariant(str(self.prj.cur.data.conductivity[index.row()]))
        elif index.column() == self.data_dict['Sal']:
            return QVariant(str(self.prj.cur.data.sal[index.row()]))
        elif index.column() == self.data_dict['Source']:
            return QVariant(str(self.prj.cur.data.source[index.row()]))
        elif index.column() == self.data_dict['Flag']:
            return QVariant(str(self.prj.cur.data.flag[index.row()]))
        else:
            return QVariant()

    def setData(self, index, value, role):
        return False
