from PySide import QtGui, QtCore

import logging

logger = logging.getLogger(__name__)


class FormattedInputDialog(QtGui.QDialog):
    def __init__(self, parent, title="", msg="", default="", fmt=""):
        super(FormattedInputDialog, self).__init__(parent, f=QtCore.Qt.WindowTitleHint)
        self.setWindowTitle(title)
        rex = QtCore.QRegExp(fmt)
        self.validator = QtGui.QRegExpValidator(rex)
        self.line_edit = QtGui.QLineEdit(default)

        label = QtGui.QLabel(msg)
        self.ok_btn = QtGui.QPushButton("OK")
        cancel_btn = QtGui.QPushButton("Cancel")
        layout = QtGui.QVBoxLayout()
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.ok_btn)
        hbox.addWidget(cancel_btn)
        layout.addWidget(label)
        layout.addWidget(self.line_edit)
        layout.addLayout(hbox)
        self.setLayout(layout)

        # noinspection PyUnresolvedReferences
        self.ok_btn.clicked.connect(self.accept)
        # noinspection PyUnresolvedReferences
        cancel_btn.clicked.connect(self.reject)
        # noinspection PyUnresolvedReferences
        self.line_edit.textChanged.connect(self._check_state)
        # noinspection PyUnresolvedReferences
        self.line_edit.editingFinished.connect(self._check_state)
        self._check_state()

    @classmethod
    def get_format_text(cls, parent, title="", msg="", default="", fmt=""):
        dialog = cls(parent, title, msg, default, fmt)
        if dialog.exec_() == QtGui.QDialog.Accepted:
            rtn = dialog.line_edit.text(), True
        else:
            rtn = None, False
        dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        dialog.close()
        return rtn

    def _check_state(self):
        input_text = self.line_edit.text()
        state = self.validator.validate(input_text, 0)[0]
        if state == QtGui.QValidator.Acceptable:
            color = '#c4df9b' # green
            self.ok_btn.setEnabled(True)
        elif state == QtGui.QValidator.Intermediate:
            color = '#fff79a' # yellow
            self.ok_btn.setEnabled(False)
        else:
            color = '#f6989d' # red
            if len(input_text) < 10:
                self.ok_btn.setEnabled(False)
            else:
                self.ok_btn.setEnabled(True) # make long incorrect input acceptable
        self.line_edit.setStyleSheet("background-color: %s;" % color)
