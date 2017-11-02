import os
from PySide import QtGui
from PySide import QtCore

import logging
logger = logging.getLogger(__name__)


class MultiSelectionDialog(QtGui.QDialog):
    def __init__(self, title, message, items, parent=None):
        super().__init__(parent=parent)
        form = QtGui.QFormLayout(self)
        form.addRow(QtGui.QLabel(message))
        self.listView = QtGui.QListView(self)
        form.addRow(self.listView)
        model = QtGui.QStandardItemModel(self.listView)
        self.setWindowTitle(title)
        for item in items:
            # create an item with a caption
            standardItem = QtGui.QStandardItem(item)
            standardItem.setCheckable(True)
            model.appendRow(standardItem)
        self.listView.setModel(model)

        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
                                           QtCore.Qt.Horizontal, self)
        form.addRow(buttonBox)
        self.setLayout(form)

        # noinspection PyUnresolvedReferences
        buttonBox.accepted.connect(self.accept)
        # noinspection PyUnresolvedReferences
        buttonBox.rejected.connect(self.reject)

    def selected_items(self):
        selected = []
        model = self.listView.model()
        i = 0
        while model.item(i):
            if model.item(i).checkState():
                selected.append(model.item(i).text())
            i += 1
        return selected
