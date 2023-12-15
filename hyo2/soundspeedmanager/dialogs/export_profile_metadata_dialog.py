import logging

from PySide6 import QtCore, QtWidgets

from hyo2.abc2.lib.gdal_aux import GdalAux
from hyo2.soundspeedmanager.dialogs.dialog import AbstractDialog
from hyo2.soundspeedmanager.dialogs.export_profile_metadata_fields_dialog import ExportProfileMetadataFieldsDialog
from hyo2.soundspeed.db.export import ExportDbFields

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
        # noinspection PyUnresolvedReferences
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

        # option for opening the output folder
        settings = QtCore.QSettings()
        export_filter_fields = settings.value("export_filter_fields")
        if export_filter_fields is None:
            settings.setValue("export_filter_fields", False)
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        self.filterFields = QtWidgets.QCheckBox('Filter fields', self)
        self.filterFields.setChecked(settings.value("export_filter_fields") == 'true')
        hbox.addWidget(self.filterFields)
        hbox.addStretch()

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
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.warning(self, "Export warning", msg, QtWidgets.QMessageBox.Ok)
            return

        filter_fields = None
        if self.filterFields.isChecked():
            logger.debug("user want to filter the fields in output")
            filter_fields = ExportDbFields()
            settings = QtCore.QSettings()

            for ff in filter_fields.fields.keys():
                filter_fields.fields[ff] = settings.value("export_field_%s" % ff, "true") == "true"

            dlg = ExportProfileMetadataFieldsDialog(filter_fields=filter_fields, parent=self)
            ret = dlg.exec_()
            if ret:
                logger.debug("fields: %s" % (dlg.filter_fields.fields, ))

                filter_fields = dlg.filter_fields
                for ff in filter_fields.fields.keys():
                    settings.setValue("export_field_%s" % ff, filter_fields.fields[ff])

        # actually do the export
        self.progress.start()
        success = True

        # try:

        for fmt in self.fmt_outputs:
            ret = self.lib.export_db_profiles_metadata(ogr_format=GdalAux.ogr_formats[fmt],
                                                       filter_fields=filter_fields)
            if not ret:
                success = False
                # noinspection PyCallByClass,PyArgumentList
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
