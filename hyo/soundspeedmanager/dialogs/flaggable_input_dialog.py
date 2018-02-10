from PySide import QtGui, QtCore

import logging

logger = logging.getLogger(__name__)


class FlaggableInputDialog(QtGui.QDialog):
    def __init__(self, parent, title="", msg="", flag_label=""):
        super(FlaggableInputDialog, self).__init__(parent, f=QtCore.Qt.WindowTitleHint)
        self.setWindowTitle(title)

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        label = QtGui.QLabel(msg)
        layout.addWidget(label)
        self.line_edit = QtGui.QLineEdit()
        layout.addWidget(self.line_edit)
        layout.addSpacing(6)
        self.flag = QtGui.QCheckBox(flag_label)
        layout.addWidget(self.flag)
        layout.addSpacing(12)

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch()
        self.ok_btn = QtGui.QPushButton("OK")
        hbox.addWidget(self.ok_btn)
        cancel_btn = QtGui.QPushButton("Cancel")
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
        if dialog.exec_() == QtGui.QDialog.Accepted:
            rtn = dialog.line_edit.text(), True
        else:
            rtn = None, False
        dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        dialog.close()
        return rtn
