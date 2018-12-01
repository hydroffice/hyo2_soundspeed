import logging

from PySide2 import QtCore, QtWidgets

from hyo2.abc.lib.gdal_aux import GdalAux
from hyo2.soundspeedmanager.dialogs.dialog import AbstractDialog

logger = logging.getLogger(__name__)


class ExportProfileMetadataDialog(AbstractDialog):

    def __init__(self, main_win, lib, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        self.fmt_outputs = list()

        self.setWindowTitle("Export metadata profiles")
        self.setMinimumWidth(160)

        # outline ui
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # label
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        label = QtWidgets.QLabel("Select output formats:")
        hbox.addWidget(label)
        hbox.addStretch()
        # buttons
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        self.buttonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        hbox.addWidget(self.buttonBox)
        hbox.addStretch()
        # add buttons
        for fmt in GdalAux.ogr_formats.keys():
            btn = QtWidgets.QPushButton("%s" % fmt)
            btn.setCheckable(True)
            self.buttonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
            btn.setToolTip("Select %s format [*.%s]" % (fmt, ", *.".join(GdalAux.ogr_exts[fmt])))

        # noinspection PyUnresolvedReferences
        self.buttonBox.clicked.connect(self.on_select_btn)

        self.mainLayout.addSpacing(16)

        # export
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        btn = QtWidgets.QPushButton("Export data")
        btn.setMinimumHeight(36)
        hbox.addWidget(btn)
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_export_btn)
        hbox.addStretch()

    def on_select_btn(self, btn):
        logger.debug("%s -> %s" % (btn.text(), btn.isChecked()))
        fmt = btn.text()

        if btn.isChecked():
            self.fmt_outputs.append(fmt)
        else:
            if fmt in self.fmt_outputs:
                self.fmt_outputs.remove(fmt)

    def on_export_btn(self):
        logger.debug("export clicked")
        if len(self.fmt_outputs) == 0:
            msg = "Select output formats before metadata export!"
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.warning(self, "Export warning", msg, QtWidgets.QMessageBox.Ok)
            return

        # actually do the export
        self.progress.start()
        success = True

        # try:

        for fmt in self.fmt_outputs:
            ret = self.lib.export_db_profiles_metadata(ogr_format=GdalAux.ogr_formats[fmt])
            if not ret:
                success = False
                # noinspection PyCallByClass
                QtWidgets.QMessageBox.critical(self, "Database", "Unable to export as %s!" % fmt)

        # except RuntimeError as e:
        #     self.progress.end()
        #     msg = "Issue in exporting the metadata.\nReason: %s" % e
        #     QtWidgets.QMessageBox.critical(self, "Export error", msg, QtWidgets.QMessageBox.Ok)
        #     return

        if success:
            self.lib.open_outputs_folder()

        self.progress.end()
        self.accept()
