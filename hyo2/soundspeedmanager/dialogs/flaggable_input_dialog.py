from PySide2 import QtCore, QtGui, QtWidgets

import logging

logger = logging.getLogger(__name__)


class FlaggableInputDialog(QtWidgets.QDialog):
    def __init__(self, parent, title="", msg="", flag_label=""):
        super(FlaggableInputDialog, self).__init__(parent, f=QtCore.Qt.WindowTitleHint)
        self.setWindowTitle(title)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        label = QtWidgets.QLabel(msg)
        layout.addWidget(label)
        self.line_edit = QtWidgets.QLineEdit()
        layout.addWidget(self.line_edit)
        layout.addSpacing(6)
        self.flag = QtWidgets.QCheckBox(flag_label)
        layout.addWidget(self.flag)
        layout.addSpacing(12)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch()
        self.ok_btn = QtWidgets.QPushButton("OK")
        hbox.addWidget(self.ok_btn)
        cancel_btn = QtWidgets.QPushButton("Cancel")
        hbox.addWidget(cancel_btn)
        layout.addLayout(hbox)
        hbox.addStretch()

        # noinspection PyUnresolvedReferences
        self.ok_btn.clicked.connect(self.accept)
        # noinspection PyUnresolvedReferences
        cancel_btn.clicked.connect(self.reject)

    @classmethod
    def get_text_with_flag(cls, parent, title="", msg="", flag_label=""):
        dialog = cls(parent, title, msg, flag_label)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            rtn = dialog.line_edit.text(), dialog.flag.isChecked()
        else:
            rtn = None, False
        dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        dialog.close()
        return rtn
