from PySide6 import QtCore, QtWidgets

import logging

from hyo2.ssm2.app.gui.soundspeedmanager.dialogs.dialog import AbstractDialog

logger = logging.getLogger(__name__)


class ButtonsDialog(AbstractDialog):

    def __init__(self, main_win, lib, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        self.btn_dict = {
            "SeaBird CTD Setup": "input_buttons/seacat_plugin",
            "Reference Cast": "editor_buttons/reference",
            "Show/Edit Data Spreadsheet": "editor_buttons/spreadsheet",
            "Show/Edit Cast Metadata": "editor_buttons/metadata",
            "Filter/Smooth Data": "editor_buttons/filter",
            "Preview Thinning": "editor_buttons/thinning",
            "Restart Processing": "editor_buttons/restart",
            "Export Data": "editor_buttons/export",
            "Transmit Data": "editor_buttons/transmit",
            "Save to Database": "editor_buttons/database"
        }

        settings = QtCore.QSettings()

        self.setWindowTitle("Buttons Visibility Setup")
        self.setMinimumWidth(140)

        self.botton_min_width = 80

        # outline ui
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # input file formats
        self.importLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.addLayout(self.importLayout)
        # - import
        import_hbox = QtWidgets.QHBoxLayout()
        self.importLayout.addLayout(import_hbox)
        import_hbox.addStretch()
        import_label = QtWidgets.QLabel("Set/unset buttons visibility:")
        import_hbox.addWidget(import_label)
        import_hbox.addSpacing(6)
        # - fmt layout
        self.fmtLayout = QtWidgets.QHBoxLayout()
        self.importLayout.addLayout(self.fmtLayout)
        # -- middle
        self.midButtonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        self.fmtLayout.addWidget(self.midButtonBox)
        # --- add buttons

        for btn_label in self.btn_dict:

            btn = QtWidgets.QPushButton("%s" % btn_label)
            btn.setToolTip("Import %s format" % btn_label)
            btn.setMinimumWidth(self.botton_min_width)
            btn.setCheckable(True)

            if settings.value("%s" % self.btn_dict[btn_label], 0) == 1:
                btn.setChecked(True)

            self.midButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)

        self.mainLayout.addSpacing(12)
        self.mainLayout.addStretch()

        # edit/apply
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch()
        self.apply = QtWidgets.QPushButton("Apply")
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
                settings.setValue("%s" % self.btn_dict[b.text()], 1)
            else:
                settings.setValue("%s" % self.btn_dict[b.text()], 0)

        msg = "The new visibility settings for the buttons have been saved. \n" \
              "Close and re-open the app to apply the changes!"
        # noinspection PyCallByClass,PyArgumentList
        QtWidgets.QMessageBox.information(self, "Buttons visibility", msg, QtWidgets.QMessageBox.Ok)
        self.accept()
