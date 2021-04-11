from PySide2 import QtCore

from collections import OrderedDict
from hyo2.soundspeed.profile.dicts import Dicts

QVariant = lambda value=None: value


class SisDataModel(QtCore.QAbstractTableModel):
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
        flags = super(SisDataModel, self).flags(index)
        if self.editable:
            flags |= QtCore.Qt.ItemIsEditable
        return flags

    # noinspection PyMethodOverriding
    def rowCount(self, parent=None):
        return self.prj.cur.sis.num_samples

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
                return list(list(self.data_dict)[section])
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
            return QVariant(str(self.prj.cur.sis.pressure[index.row()]))
        elif index.column() == self.data_dict['Depth']:
            return QVariant(str(self.prj.cur.sis.depth[index.row()]))
        elif index.column() == self.data_dict['Speed']:
            return QVariant(str(self.prj.cur.sis.speed[index.row()]))
        elif index.column() == self.data_dict['Temp']:
            return QVariant(str(self.prj.cur.sis.temp[index.row()]))
        elif index.column() == self.data_dict['Cond']:
            return QVariant(str(self.prj.cur.sis.conductivity[index.row()]))
        elif index.column() == self.data_dict['Sal']:
            return QVariant(str(self.prj.cur.sis.sal[index.row()]))
        elif index.column() == self.data_dict['Source']:
            return QVariant("%.0f [%s]" % (self.prj.cur.sis.source[index.row()],
                                           Dicts.first_match(Dicts.sources, self.prj.cur.sis.source[index.row()])))
        elif index.column() == self.data_dict['Flag']:
            return QVariant("%.0f [%s]" % (self.prj.cur.sis.flag[index.row()],
                                           Dicts.first_match(Dicts.flags, self.prj.cur.sis.flag[index.row()])))
        else:
            return QVariant()

    # noinspection PyMethodOverriding
    def setData(self, index, value, role):
        return False
