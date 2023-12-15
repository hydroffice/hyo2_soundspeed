from PySide6 import QtCore, QtGui, QtWidgets

import logging

logger = logging.getLogger(__name__)


class MultiSelectionDialog(QtWidgets.QDialog):
    def __init__(self, title, message, items, parent=None):
        super().__init__(parent=parent)
        form = QtWidgets.QFormLayout(self)
        # noinspection PyArgumentList
        form.addRow(QtWidgets.QLabel(message))
        self.listView = QtWidgets.QListView(self)
        # noinspection PyArgumentList
        form.addRow(self.listView)
        model = QtGui.QStandardItemModel(self.listView)
        self.setWindowTitle(title)
        for item in items:
            # create an item with a caption
            standard_item = QtGui.QStandardItem(item)
            standard_item.setCheckable(True)
            model.appendRow(standard_item)
        self.listView.setModel(model)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
                                                QtCore.Qt.Horizontal, self)
        # noinspection PyArgumentList
        form.addRow(button_box)
        self.setLayout(form)

        # noinspection PyUnresolvedReferences
        button_box.accepted.connect(self.accept)
        # noinspection PyUnresolvedReferences
        button_box.rejected.connect(self.reject)

    def selected_items(self):
        selected = []
        model = self.listView.model()
        i = 0
        while model.item(i):
            if model.item(i).checkState():
                selected.append(model.item(i).text())
            i += 1
        return selected
