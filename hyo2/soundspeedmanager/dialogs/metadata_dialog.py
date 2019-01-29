from PySide2 import QtCore, QtGui, QtWidgets

import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

from hyo2.soundspeedmanager.dialogs.dialog import AbstractDialog
from hyo2.soundspeed.base.setup_sql import vessel_list


class MetadataDialog(AbstractDialog):

    def __init__(self, main_win, lib, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        settings = QtCore.QSettings()

        self.setWindowTitle("Profile metadata")
        self.setMinimumWidth(400)

        lbl_width = 90

        # outline ui
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # types
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtWidgets.QLabel("Data type:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.sensor_type = QtWidgets.QLineEdit()
        self.sensor_type.setDisabled(True)
        self.sensor_type.setText(self.lib.cur.meta.sensor)
        hbox.addWidget(self.sensor_type)
        self.probe_type = QtWidgets.QLineEdit()
        self.probe_type.setDisabled(True)
        self.probe_type.setText(self.lib.cur.meta.probe)
        hbox.addWidget(self.probe_type)

        # original path
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtWidgets.QLabel("Path:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.original_path = QtWidgets.QLineEdit()
        self.original_path.setDisabled(True)
        self.original_path.setText(self.lib.cur.meta.original_path)
        hbox.addWidget(self.original_path)

        # location
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtWidgets.QLabel("Location:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.latitude = QtWidgets.QLineEdit()
        self.latitude.setDisabled(True)
        self.latitude.setText("%s" % self.lib.cur.meta.latitude)
        hbox.addWidget(self.latitude)
        # noinspection PyUnresolvedReferences
        self.latitude.textChanged.connect(self.changed_latitude)
        self.longitude = QtWidgets.QLineEdit()
        self.longitude.setDisabled(True)
        self.longitude.setText("%s" % self.lib.cur.meta.longitude)
        hbox.addWidget(self.longitude)
        # noinspection PyUnresolvedReferences
        self.longitude.textChanged.connect(self.changed_longitude)

        # datetime
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtWidgets.QLabel("Timestamp:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.timestamp = QtWidgets.QLineEdit()
        self.timestamp.setDisabled(True)
        self.timestamp.setText(self.lib.cur.meta.utc_time.strftime("%d/%m/%y %H:%M:%S.%f"))
        hbox.addWidget(self.timestamp)
        # noinspection PyUnresolvedReferences
        self.timestamp.textChanged.connect(self.changed_timestamp)

        # last edit
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtWidgets.QLabel("Last edit:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.proc_time = QtWidgets.QLineEdit()
        self.proc_time.setDisabled(True)
        self.proc_time.setText(self.lib.cur.meta.proc_time.strftime("%d/%m/%y %H:%M:%S.%f"))
        hbox.addWidget(self.proc_time)

        # proc info
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtWidgets.QLabel("Proc. info:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.proc_info = QtWidgets.QLineEdit()
        self.proc_info.setDisabled(True)
        self.proc_info.setText("%s" % self.lib.cur.meta.proc_info)
        hbox.addWidget(self.proc_info)

        # institution
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtWidgets.QLabel("Institution:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.institution = QtWidgets.QLineEdit()
        self.institution.setDisabled(True)
        self.institution.setText("%s" % self.lib.cur.meta.institution)
        hbox.addWidget(self.institution)
        self.institution.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.institution.textChanged.connect(self.changed_institution)

        # survey
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtWidgets.QLabel("Survey:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.survey = QtWidgets.QLineEdit()
        self.survey.setDisabled(True)
        self.survey.setText("%s" % self.lib.cur.meta.survey)
        hbox.addWidget(self.survey)
        self.survey.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.survey.textChanged.connect(self.changed_survey)

        # vessel
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtWidgets.QLabel("Vessel:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.vessel = QtWidgets.QComboBox()
        self.vessel.setDisabled(True)
        if not lib.setup.noaa_tools:
            self.vessel.setEditable(True)
        self.vessel.addItems(vessel_list)
        if self.lib.cur.meta.vessel and self.vessel.findText(self.lib.cur.meta.vessel) < 0:
            self.vessel.insertItem(0, self.lib.cur.meta.vessel)
        self.vessel.setCurrentIndex(self.vessel.findText(self.lib.cur.meta.vessel))
        hbox.addWidget(self.vessel)
        self.vessel.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.vessel.editTextChanged.connect(self.changed_vessel)
        # noinspection PyUnresolvedReferences
        self.vessel.currentIndexChanged.connect(self.changed_vessel)

        # serial number
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtWidgets.QLabel("S/N:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.sn = QtWidgets.QLineEdit()
        self.sn.setDisabled(True)
        self.sn.setText("%s" % self.lib.cur.meta.sn)
        hbox.addWidget(self.sn)
        self.sn.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.sn.textChanged.connect(self.changed_sn)

        # comments
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtWidgets.QLabel("Comments:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.comments = QtWidgets.QTextEdit()
        self.comments.setMinimumHeight(24)
        self.comments.setMaximumHeight(60)
        self.comments.setDisabled(True)
        self.comments.setText("%s" % self.lib.cur.meta.comments)
        hbox.addWidget(self.comments)
        self.comments.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.comments.textChanged.connect(self.changed_comments)

        # pressure uom
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtWidgets.QLabel("Pressure UoM:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.pressure_uom = QtWidgets.QLineEdit()
        self.pressure_uom.setDisabled(True)
        self.pressure_uom.setText("%s" % self.lib.cur.meta.pressure_uom)
        hbox.addWidget(self.pressure_uom)
        self.pressure_uom.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.pressure_uom.textChanged.connect(self.changed_pressure_uom)

        # depth uom
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtWidgets.QLabel("depth UoM:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.depth_uom = QtWidgets.QLineEdit()
        self.depth_uom.setDisabled(True)
        self.depth_uom.setText("%s" % self.lib.cur.meta.depth_uom)
        hbox.addWidget(self.depth_uom)
        self.depth_uom.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.depth_uom.textChanged.connect(self.changed_depth_uom)

        # speed uom
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtWidgets.QLabel("speed UoM:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.speed_uom = QtWidgets.QLineEdit()
        self.speed_uom.setDisabled(True)
        self.speed_uom.setText("%s" % self.lib.cur.meta.speed_uom)
        hbox.addWidget(self.speed_uom)
        self.speed_uom.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.speed_uom.textChanged.connect(self.changed_speed_uom)

        # temperature uom
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtWidgets.QLabel("temperature UoM:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.temperature_uom = QtWidgets.QLineEdit()
        self.temperature_uom.setDisabled(True)
        self.temperature_uom.setText("%s" % self.lib.cur.meta.temperature_uom)
        hbox.addWidget(self.temperature_uom)
        self.temperature_uom.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.temperature_uom.textChanged.connect(self.changed_temperature_uom)

        # conductivity uom
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtWidgets.QLabel("conductivity UoM:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.conductivity_uom = QtWidgets.QLineEdit()
        self.conductivity_uom.setDisabled(True)
        self.conductivity_uom.setText("%s" % self.lib.cur.meta.conductivity_uom)
        hbox.addWidget(self.conductivity_uom)
        self.conductivity_uom.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.conductivity_uom.textChanged.connect(self.changed_conductivity_uom)

        # salinity uom
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtWidgets.QLabel("salinity UoM:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.salinity_uom = QtWidgets.QLineEdit()
        self.salinity_uom.setDisabled(True)
        self.salinity_uom.setText("%s" % self.lib.cur.meta.salinity_uom)
        hbox.addWidget(self.salinity_uom)
        self.salinity_uom.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.salinity_uom.textChanged.connect(self.changed_salinity_uom)

        self.mainLayout.addStretch()

        # edit/apply
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch()
        self.editable = QtWidgets.QPushButton()
        self.editable.setIconSize(QtCore.QSize(30, 30))
        self.editable.setFixedHeight(34)
        edit_icon = QtGui.QIcon()
        edit_icon.addFile(os.path.join(self.media, 'lock.png'), state=QtGui.QIcon.Off)
        edit_icon.addFile(os.path.join(self.media, 'unlock.png'), state=QtGui.QIcon.On)
        self.editable.setIcon(edit_icon)
        self.editable.setCheckable(True)
        # noinspection PyUnresolvedReferences
        self.editable.clicked.connect(self.on_editable)
        self.editable.setToolTip("Unlock metadata editing")
        hbox.addWidget(self.editable)
        # --
        self.load_default = QtWidgets.QPushButton("Load default")
        self.load_default.setFixedHeight(self.editable.height())
        self.load_default.setDisabled(True)
        # noinspection PyUnresolvedReferences
        self.load_default.clicked.connect(self.on_load_default)
        self.load_default.setToolTip("Load default metadata (if any)")
        hbox.addWidget(self.load_default)
        # --
        if self.lib.ssp.loaded_from_db:
            self.apply = QtWidgets.QPushButton("Apply and save")
        else:
            self.apply = QtWidgets.QPushButton("Apply")
        self.apply.setFixedHeight(self.editable.height())
        self.apply.setDisabled(True)
        # noinspection PyUnresolvedReferences
        self.apply.clicked.connect(self.on_apply)
        if self.lib.ssp.loaded_from_db:
            self.apply.setToolTip("Apply changes (if any) and store them in the database")
        else:
            self.apply.setToolTip("Apply changes (if any)")
        hbox.addWidget(self.apply)
        # --
        self.show_at_import = QtWidgets.QPushButton("Show at Import")
        self.show_at_import.setFixedHeight(self.editable.height())
        self.show_at_import.setCheckable(True)
        if settings.value("show_metadata_at_import") == 'true':
            self.show_at_import.setChecked(True)
        else:
            self.show_at_import.setChecked(False)
        # noinspection PyUnresolvedReferences
        self.show_at_import.clicked.connect(self.on_show_at_import)
        self.show_at_import.setToolTip("Show metadata at each cast import")
        hbox.addWidget(self.show_at_import)
        hbox.addStretch()
        self.mainLayout.addLayout(hbox)

    def changed_latitude(self):
        self.latitude.setStyleSheet("background-color: rgba(255,255,153, 255);")

    def changed_longitude(self):
        self.longitude.setStyleSheet("background-color: rgba(255,255,153, 255);")

    def changed_timestamp(self):
        self.timestamp.setStyleSheet("background-color: rgba(255,255,153, 255);")

    def changed_institution(self):
        self.institution.setStyleSheet("background-color: rgba(255,255,153, 255);")

    def changed_survey(self):
        self.survey.setStyleSheet("background-color: rgba(255,255,153, 255);")

    def changed_vessel(self):
        self.vessel.setStyleSheet("background-color: rgba(255,255,153, 255);")

    def changed_sn(self):
        self.sn.setStyleSheet("background-color: rgba(255,255,153, 255);")

    def changed_comments(self):
        self.comments.setStyleSheet("background-color: rgba(255,255,153, 255);")

    def changed_pressure_uom(self):
        self.pressure_uom.setStyleSheet("background-color: rgba(255,255,153, 255);")

    def changed_depth_uom(self):
        self.depth_uom.setStyleSheet("background-color: rgba(255,255,153, 255);")

    def changed_speed_uom(self):
        self.speed_uom.setStyleSheet("background-color: rgba(255,255,153, 255);")

    def changed_temperature_uom(self):
        self.temperature_uom.setStyleSheet("background-color: rgba(255,255,153, 255);")

    def changed_conductivity_uom(self):
        self.conductivity_uom.setStyleSheet("background-color: rgba(255,255,153, 255);")

    def changed_salinity_uom(self):
        self.salinity_uom.setStyleSheet("background-color: rgba(255,255,153, 255);")

    def on_editable(self):
        logger.debug("editable: %s" % self.editable.isChecked())

        if self.editable.isChecked():

            self.load_default.setEnabled(True)
            self.apply.setEnabled(True)
            self.latitude.setEnabled(True)
            self.longitude.setEnabled(True)
            self.timestamp.setEnabled(True)
            self.institution.setEnabled(True)
            self.survey.setEnabled(True)
            self.vessel.setEnabled(True)
            self.sn.setEnabled(True)
            self.comments.setEnabled(True)
            # self.pressure_uom.setEnabled(True)
            # self.depth_uom.setEnabled(True)
            # self.speed_uom.setEnabled(True)
            # self.temperature_uom.setEnabled(True)
            # self.conductivity_uom.setEnabled(True)
            # self.salinity_uom.setEnabled(True)

        else:

            self.load_default.setDisabled(True)
            self.apply.setDisabled(True)
            self.latitude.setDisabled(True)
            self.longitude.setDisabled(True)
            self.timestamp.setDisabled(True)
            self.institution.setDisabled(True)
            self.survey.setDisabled(True)
            self.vessel.setDisabled(True)
            self.sn.setDisabled(True)
            self.comments.setDisabled(True)
            self.pressure_uom.setDisabled(True)
            self.depth_uom.setDisabled(True)
            self.speed_uom.setDisabled(True)
            self.temperature_uom.setDisabled(True)
            self.conductivity_uom.setDisabled(True)
            self.salinity_uom.setDisabled(True)

    def on_load_default(self):
        logger.debug("load default")

        self.institution.setText(self.lib.setup.default_institution)
        self.survey.setText(self.lib.setup.default_survey)
        if self.lib.setup.default_vessel and self.vessel.findText(self.lib.setup.default_vessel) < 0:
            self.vessel.insertItem(0, self.lib.setup.default_vessel)
        self.vessel.setCurrentIndex(self.vessel.findText(self.lib.setup.default_vessel))

    def on_show_at_import(self):
        logger.debug("on show at import: %s" % self.show_at_import.isChecked())
        settings = QtCore.QSettings()
        if self.show_at_import.isChecked():
            settings.setValue("show_metadata_at_import", True)
        else:
            settings.setValue("show_metadata_at_import", False)

    def on_apply(self):
        logger.debug("apply")

        # apply changes
        try:

            # extra care on location and time variables, since they are PK
            try:
                latitude = float(self.latitude.text())
                if latitude < -90 or latitude > 90:
                    raise RuntimeError("invalid latitude: %s" % latitude)
                logger.debug("latitude: %s" % latitude)

                longitude = float(self.longitude.text())
                if longitude < -180 or longitude > 180:
                    raise RuntimeError("invalid longitude: %s" % longitude)
                logger.debug("longitude: %s" % longitude)

                timestamp = datetime.strptime(self.timestamp.text(), "%d/%m/%y %H:%M:%S.%f")
                logger.debug("timestamp: %s" % timestamp)

                if (latitude != self.lib.cur.meta.latitude) or \
                        (longitude != self.lib.cur.meta.longitude) or \
                        (timestamp != self.lib.cur.meta.utc_time):

                    # only if the timestamp or the location is changed
                    if not self.lib.remove_data():

                        # only if the profile was loaded from a db
                        if self.lib.ssp.loaded_from_db:
                            msg = "Unable to remove old profile!"
                            QtWidgets.QMessageBox.warning(self, "Database warning", msg, QtWidgets.QMessageBox.Ok)
                            return

            except Exception as e:
                msg = "Unable to interpret position or location!\n\n%s" % e
                QtWidgets.QMessageBox.warning(self, "Database warning", msg, QtWidgets.QMessageBox.Ok)
                return

            self.lib.cur.meta.latitude = latitude
            self.lib.cur.meta.longitude = longitude
            self.lib.cur.meta.utc_time = timestamp
            self.lib.cur.meta.institution = self.institution.text()
            self.lib.cur.meta.survey = self.survey.text()
            self.lib.cur.meta.vessel = self.vessel.currentText()
            self.lib.cur.meta.sn = self.sn.text()
            self.lib.cur.meta.comments = self.comments.toPlainText()
            self.lib.cur.meta.pressure_uom = self.pressure_uom.text()
            self.lib.cur.meta.depth_uom = self.depth_uom.text()
            self.lib.cur.meta.speed_uom = self.speed_uom.text()
            self.lib.cur.meta.temperature_uom = self.temperature_uom.text()
            self.lib.cur.meta.conductivity_uom = self.conductivity_uom.text()
            self.lib.cur.meta.salinity_uom = self.salinity_uom.text()

        except RuntimeError as e:
            msg = "Issue in apply changes\n%s" % e
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Metadata error", msg, QtWidgets.QMessageBox.Ok)
            return

        # update proc_time widget
        self.proc_time.setText(self.lib.cur.meta.proc_time.strftime("%d/%m/%y %H:%M:%S.%f"))

        # we also store the metadata to the db, but only if the profile was loading from a db
        if self.lib.ssp.loaded_from_db:

            if not self.lib.store_data():
                msg = "Unable to save to db!"
                QtWidgets.QMessageBox.warning(self, "Database warning", msg, QtWidgets.QMessageBox.Ok)
                return
            else:
                self.main_win.data_stored()

        # reset to transparent
        self.latitude.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.longitude.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.timestamp.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.institution.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.survey.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.vessel.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.sn.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.comments.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.pressure_uom.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.depth_uom.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.speed_uom.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.temperature_uom.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.conductivity_uom.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.salinity_uom.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
