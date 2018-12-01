from PySide2 import QtCore, QtGui, QtWidgets

import logging
logger = logging.getLogger(__name__)


class MultiSelectionDialog(QtWidgets.QDialog):
    def __init__(self, title, message, items, parent=None):
        super().__init__(parent=parent)
        form = QtWidgets.QFormLayout(self)
        form.addRow(QtWidgets.QLabel(message))
        self.listView = QtWidgets.QListView(self)
        form.addRow(self.listView)
        model = QtGui.QStandardItemModel(self.listView)
        self.setWindowTitle(title)
        for item in items:
            # create an item with a caption
            standardItem = QtGui.QStandardItem(item)
            standardItem.setCheckable(True)
            model.appendRow(standardItem)
        self.listView.setModel(model)

        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
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
