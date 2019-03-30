import logging
from PySide2 import QtCore, QtWidgets

logger = logging.getLogger(__name__)


class ExportProfileMetadataFieldsDialog(QtWidgets.QDialog):
    def __init__(self, filter_fields, parent=None):
        super().__init__(parent=parent)
        self.filter_fields = filter_fields

        self.setWindowTitle("Fields filter")
        self.setMinimumWidth(160)

        # outline ui
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # label
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        label = QtWidgets.QLabel("Select output fields:")
        hbox.addWidget(label)
        hbox.addStretch()
        # buttons
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        # - fmt layout
        self.fmtLayout = QtWidgets.QHBoxLayout()
        hbox.addLayout(self.fmtLayout)
        # -- left
        self.leftButtonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        self.leftButtonBox.setFixedWidth(100)
        self.fmtLayout.addWidget(self.leftButtonBox)
        # -- right
        self.rightButtonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        self.rightButtonBox.setFixedWidth(100)
        self.fmtLayout.addWidget(self.rightButtonBox)
        hbox.addStretch()
        # add buttons (retrieving name, description and extension from the library)
        for idx, name in enumerate(self.filter_fields.fields.keys()):

            btn = QtWidgets.QPushButton("%s" % name)
            btn.setCheckable(True)
            btn.setToolTip("Select %s field" % (name, ))
            btn.setChecked(self.filter_fields.fields[name])

            if (idx % 2) == 0:
                self.leftButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
            else:
                self.rightButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)

        # noinspection PyUnresolvedReferences
        self.leftButtonBox.clicked.connect(self.on_select_field)
        # noinspection PyUnresolvedReferences
        self.rightButtonBox.clicked.connect(self.on_select_field)

        self.mainLayout.addSpacing(16)

        # export
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        btn = QtWidgets.QPushButton("Apply filter")
        btn.setMinimumHeight(32)
        hbox.addWidget(btn)
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_apply_filter_fields)
        hbox.addStretch()

    def on_select_field(self, btn):
        """Update the list of writers to pass to the library"""
        logger.debug("%s -> %s" % (btn.text(), btn.isChecked()))
        self.filter_fields.fields[btn.text()] = btn.isChecked()

    def on_apply_filter_fields(self):
        logger.debug("apply fields filtering")
        self.accept()
