from __future__ import absolute_import, division, print_function, unicode_literals

from PySide import QtGui
from PySide import QtCore

import os
import logging
logger = logging.getLogger(__name__)

from hydroffice.soundspeedmanager.dialogs.dialog import AbstractDialog


class MetadataDialog(AbstractDialog):

    def __init__(self, main_win, lib, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        self.setWindowTitle("Metadata")
        self.setMinimumWidth(550)

        lbl_width = 90

        # outline ui
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # types
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtGui.QLabel("Data type:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.sensor_type = QtGui.QLineEdit()
        self.sensor_type.setDisabled(True)
        self.sensor_type.setText(self.lib.cur.meta.sensor)
        hbox.addWidget(self.sensor_type)
        self.probe_type = QtGui.QLineEdit()
        self.probe_type.setDisabled(True)
        self.probe_type.setText(self.lib.cur.meta.probe)
        hbox.addWidget(self.probe_type)

        # original path
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtGui.QLabel("Path:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.original_path = QtGui.QLineEdit()
        self.original_path.setDisabled(True)
        self.original_path.setText(self.lib.cur.meta.original_path)
        hbox.addWidget(self.original_path)

        # location
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtGui.QLabel("Location:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.latitude = QtGui.QLineEdit()
        self.latitude.setDisabled(True)
        self.latitude.setText("%s" % self.lib.cur.meta.latitude)
        hbox.addWidget(self.latitude)
        self.longitude = QtGui.QLineEdit()
        self.longitude.setDisabled(True)
        self.longitude.setText("%s" % self.lib.cur.meta.longitude)
        hbox.addWidget(self.longitude)

        # datetime
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtGui.QLabel("Timestamp:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.timestamp = QtGui.QLineEdit()
        self.timestamp.setDisabled(True)
        self.timestamp.setText(self.lib.cur.meta.utc_time.strftime("%d/%m/%y %H:%M"))
        hbox.addWidget(self.timestamp)

        # last edit
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtGui.QLabel("Last edit:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.proc_time = QtGui.QLineEdit()
        self.proc_time.setDisabled(True)
        self.proc_time.setText(self.lib.cur.meta.proc_time.strftime("%d/%m/%y %H:%M"))
        hbox.addWidget(self.proc_time)

        # proc info
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtGui.QLabel("Proc. info:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.proc_info = QtGui.QLineEdit()
        self.proc_info.setDisabled(True)
        self.proc_info.setText("%s" % self.lib.cur.meta.proc_info)
        hbox.addWidget(self.proc_info)

        # institution
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtGui.QLabel("Institution:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.institution = QtGui.QLineEdit()
        self.institution.setDisabled(True)
        self.institution.setText("%s" % self.lib.cur.meta.institution)
        hbox.addWidget(self.institution)
        self.institution.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.institution.textChanged.connect(self.changed_institution)

        # survey
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtGui.QLabel("Survey:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.survey = QtGui.QLineEdit()
        self.survey.setDisabled(True)
        self.survey.setText("%s" % self.lib.cur.meta.survey)
        hbox.addWidget(self.survey)
        self.survey.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.survey.textChanged.connect(self.changed_survey)

        # vessel
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtGui.QLabel("Vessel:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.vessel = QtGui.QLineEdit()
        self.vessel.setDisabled(True)
        self.vessel.setText("%s" % self.lib.cur.meta.vessel)
        hbox.addWidget(self.vessel)
        self.vessel.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.vessel.textChanged.connect(self.changed_vessel)

        # serial number
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtGui.QLabel("S/N:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.sn = QtGui.QLineEdit()
        self.sn.setDisabled(True)
        self.sn.setText("%s" % self.lib.cur.meta.sn)
        hbox.addWidget(self.sn)
        self.sn.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.sn.textChanged.connect(self.changed_sn)

        # pressure uom
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtGui.QLabel("Pressure UoM:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.pressure_uom = QtGui.QLineEdit()
        self.pressure_uom.setDisabled(True)
        self.pressure_uom.setText("%s" % self.lib.cur.meta.pressure_uom)
        hbox.addWidget(self.pressure_uom)
        self.pressure_uom.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.pressure_uom.textChanged.connect(self.changed_pressure_uom)
        
        # depth uom
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtGui.QLabel("depth UoM:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.depth_uom = QtGui.QLineEdit()
        self.depth_uom.setDisabled(True)
        self.depth_uom.setText("%s" % self.lib.cur.meta.depth_uom)
        hbox.addWidget(self.depth_uom)
        self.depth_uom.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.depth_uom.textChanged.connect(self.changed_depth_uom)
        
        # speed uom
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtGui.QLabel("speed UoM:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.speed_uom = QtGui.QLineEdit()
        self.speed_uom.setDisabled(True)
        self.speed_uom.setText("%s" % self.lib.cur.meta.speed_uom)
        hbox.addWidget(self.speed_uom)
        self.speed_uom.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.speed_uom.textChanged.connect(self.changed_speed_uom)
        
        # temperature uom
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtGui.QLabel("temperature UoM:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.temperature_uom = QtGui.QLineEdit()
        self.temperature_uom.setDisabled(True)
        self.temperature_uom.setText("%s" % self.lib.cur.meta.temperature_uom)
        hbox.addWidget(self.temperature_uom)
        self.temperature_uom.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.temperature_uom.textChanged.connect(self.changed_temperature_uom)
        
        # conductivity uom
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtGui.QLabel("conductivity UoM:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.conductivity_uom = QtGui.QLineEdit()
        self.conductivity_uom.setDisabled(True)
        self.conductivity_uom.setText("%s" % self.lib.cur.meta.conductivity_uom)
        hbox.addWidget(self.conductivity_uom)
        self.conductivity_uom.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.conductivity_uom.textChanged.connect(self.changed_conductivity_uom)
        
        # salinity uom
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtGui.QLabel("salinity UoM:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.salinity_uom = QtGui.QLineEdit()
        self.salinity_uom.setDisabled(True)
        self.salinity_uom.setText("%s" % self.lib.cur.meta.salinity_uom)
        hbox.addWidget(self.salinity_uom)
        self.salinity_uom.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.salinity_uom.textChanged.connect(self.changed_salinity_uom)

        self.mainLayout.addStretch()

        # edit/apply
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch()
        self.editable = QtGui.QPushButton()
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
        self.load_default = QtGui.QPushButton("Load default")
        self.load_default.setFixedHeight(self.editable.height())
        self.load_default.setDisabled(True)
        # noinspection PyUnresolvedReferences
        self.load_default.clicked.connect(self.on_load_default)
        self.load_default.setToolTip("Load default metadata (if any)")
        hbox.addWidget(self.load_default)
        # --
        self.apply = QtGui.QPushButton("Apply")
        self.apply.setFixedHeight(self.editable.height())
        self.apply.setDisabled(True)
        # noinspection PyUnresolvedReferences
        self.apply.clicked.connect(self.on_apply)
        self.apply.setToolTip("Apply changes (if any)")
        hbox.addWidget(self.apply)
        hbox.addStretch()
        self.mainLayout.addLayout(hbox)

    def changed_institution(self):
        self.institution.setStyleSheet("background-color: rgba(255,255,153, 255);")

    def changed_survey(self):
        self.survey.setStyleSheet("background-color: rgba(255,255,153, 255);")

    def changed_vessel(self):
        self.vessel.setStyleSheet("background-color: rgba(255,255,153, 255);")

    def changed_sn(self):
        self.sn.setStyleSheet("background-color: rgba(255,255,153, 255);")

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
            self.institution.setEnabled(True)
            self.survey.setEnabled(True)
            self.vessel.setEnabled(True)
            self.sn.setEnabled(True)
            self.pressure_uom.setEnabled(True)
            self.depth_uom.setEnabled(True)
            self.speed_uom.setEnabled(True)
            self.temperature_uom.setEnabled(True)
            self.conductivity_uom.setEnabled(True)
            self.salinity_uom.setEnabled(True)

        else:
            self.load_default.setDisabled(True)
            self.apply.setDisabled(True)
            self.institution.setDisabled(True)
            self.survey.setDisabled(True)
            self.vessel.setDisabled(True)
            self.sn.setDisabled(True)
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
        self.vessel.setText(self.lib.setup.default_vessel)

    def on_apply(self):
        logger.debug("apply")
        # apply changes
        try:
            self.lib.cur.meta.institution = self.institution.text()
            self.lib.cur.meta.survey = self.survey.text()
            self.lib.cur.meta.vessel = self.vessel.text()
            self.lib.cur.meta.sn = self.sn.text()
            self.lib.cur.meta.pressure_uom = self.pressure_uom.text()
            self.lib.cur.meta.depth_uom = self.depth_uom.text()
            self.lib.cur.meta.speed_uom = self.speed_uom.text()
            self.lib.cur.meta.conductivity_uom = self.conductivity_uom.text()
            self.lib.cur.meta.salinity_uom = self.salinity_uom.text()

        except RuntimeError as e:
            msg = "Issue in apply changes\n%s" % e
            # noinspection PyCallByClass
            QtGui.QMessageBox.critical(self, "Metadata error", msg, QtGui.QMessageBox.Ok)
            return

        # update proc_time widget
        self.proc_time.setText(self.lib.cur.meta.proc_time.strftime("%d/%m/%y %H:%M"))

        # reset to transparent
        self.institution.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.survey.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.vessel.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.sn.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.pressure_uom.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.depth_uom.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.speed_uom.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.temperature_uom.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.conductivity_uom.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.salinity_uom.setStyleSheet("background-color: rgba(255, 255, 255, 255);")

        # msg = "Changes have been applied!"
        # # noinspection PyCallByClass
        # QtGui.QMessageBox.information(self, "Metadata", msg, QtGui.QMessageBox.Ok)
