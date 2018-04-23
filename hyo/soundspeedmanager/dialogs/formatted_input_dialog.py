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
        self.check_box = QtGui.QCheckBox("Nonstandard project name")
        self.check_box_checked = False
        layout = QtGui.QVBoxLayout()
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.ok_btn)
        hbox.addWidget(cancel_btn)
        layout.addWidget(label)
        layout.addWidget(self.line_edit)
        layout.addLayout(hbox)
        layout.addWidget(self.check_box)
        self.setLayout(layout)

        # noinspection PyUnresolvedReferences
        self.ok_btn.clicked.connect(self.accept)
        # noinspection PyUnresolvedReferences
        cancel_btn.clicked.connect(self.reject)
        # noinspection PyUnresolvedReferences
        self.line_edit.textChanged.connect(self._check_state)
        # noinspection PyUnresolvedReferences
        self.line_edit.editingFinished.connect(self._check_state)
        # noinspection PyUnresolvedReferences
        self.check_box.stateChanged.connect(self._check_state)
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

    def _check_state(self, state=None):
        if state == QtCore.Qt.Checked:
            self.check_box_checked = True
        elif state == QtCore.Qt.Unchecked:
            self.check_box_checked = False
        input_text = self.line_edit.text()
        status = self.validator.validate(input_text, 0)[0]
        if status == QtGui.QValidator.Acceptable:
            color = '#c4df9b' # green
            self.ok_btn.setEnabled(True)
        elif status == QtGui.QValidator.Intermediate:
            color = '#fff79a' # yellow
            self.ok_btn.setEnabled(False)
        else:
            color = '#f6989d' # red
            if len(input_text) >= 10 and input_text.find(' ') < 0 and self.check_box_checked:
                self.ok_btn.setEnabled(True) # make long incorrect input acceptable
            else:
                self.ok_btn.setEnabled(False)
        self.line_edit.setStyleSheet("background-color: %s;" % color)
