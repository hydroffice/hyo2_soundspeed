from PySide import QtGui
from PySide import QtCore

import logging
logger = logging.getLogger(__name__)

from hyo.soundspeedmanager.dialogs.dialog import AbstractDialog


class ButtonsDialog(AbstractDialog):

    def __init__(self, main_win, lib, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        self.btn_dict = {
            "Reference Cast": "reference",
            "Show/Edit Data Spreadsheet": "spreadsheet",
            "Show/Edit Cast Metadata": "metadata",
            "Filter/Smooth Data": "filter",
            "Preview Thinning": "thinning",
            "Restart Processing": "restart",
            "Export Data": "export",
            "Transmit Data": "transmit",
            "Save to Database": "database"
        }

        settings = QtCore.QSettings()

        self.setWindowTitle("Buttons Visibility Setup")
        self.setMinimumWidth(140)

        self.botton_min_width = 80
        lbl_width = 180

        # outline ui
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # input file formats
        self.importLayout = QtGui.QVBoxLayout()
        self.mainLayout.addLayout(self.importLayout)
        # - import
        import_hbox = QtGui.QHBoxLayout()
        self.importLayout.addLayout(import_hbox)
        import_hbox.addStretch()
        import_label = QtGui.QLabel("Set/unset buttons visibility:")
        import_hbox.addWidget(import_label)
        import_hbox.addSpacing(6)
        # - fmt layout
        self.fmtLayout = QtGui.QHBoxLayout()
        self.importLayout.addLayout(self.fmtLayout)
        # -- middle
        self.midButtonBox = QtGui.QDialogButtonBox(QtCore.Qt.Vertical)
        self.fmtLayout.addWidget(self.midButtonBox)
        # --- add buttons

        for btn_label in self.btn_dict:

            btn = QtGui.QPushButton("%s" % btn_label)
            btn.setToolTip("Import %s format" % btn_label)
            btn.setMinimumWidth(self.botton_min_width)
            btn.setCheckable(True)

            if settings.value("editor_buttons/%s" % self.btn_dict[btn_label], 0) == 1:
                btn.setChecked(True)

            self.midButtonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)

        self.mainLayout.addSpacing(12)
        self.mainLayout.addStretch()

        # edit/apply
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch()
        self.apply = QtGui.QPushButton("Apply")
        self.apply.setFixedWidth(40)
        # noinspection PyUnresolvedReferences
        self.apply.clicked.connect(self.on_apply)
        hbox.addWidget(self.apply)
        hbox.addStretch()
        self.mainLayout.addLayout(hbox)

    def on_apply(self):
        logger.debug("Apply new button visibility")

        settings = QtCore.QSettings()
        for b in self.midButtonBox.buttons():
            if b.isChecked():
                settings.setValue("editor_buttons/%s" % self.btn_dict[b.text()], 1)
            else:
                settings.setValue("editor_buttons/%s" % self.btn_dict[b.text()], 0)

        msg = "The new visibility settings for the buttons have been saved. \n" \
              "Close and re-open the app to apply the changes!"
        # noinspection PyCallByClass
        QtGui.QMessageBox.information(self, "Buttons visibility", msg, QtGui.QMessageBox.Ok)
        self.accept()
