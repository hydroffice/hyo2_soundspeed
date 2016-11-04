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

        lbl_width = 60

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
        self.apply = QtGui.QPushButton("Apply")
        self.apply.setFixedHeight(self.editable.height())
        self.apply.setDisabled(True)
        # noinspection PyUnresolvedReferences
        self.apply.clicked.connect(self.on_apply)
        self.apply.setToolTip("Apply changes (if any)")
        hbox.addWidget(self.apply)
        hbox.addStretch()
        self.mainLayout.addLayout(hbox)

    def on_editable(self):
        logger.debug("editable: %s" % self.editable.isChecked())
        if self.editable.isChecked():
            self.apply.setEnabled(True)
            self.survey.setEnabled(True)
            self.vessel.setEnabled(True)
            self.sn.setEnabled(True)
        else:
            self.apply.setDisabled(True)
            self.survey.setDisabled(True)
            self.vessel.setDisabled(True)
            self.sn.setDisabled(True)

    def on_apply(self):
        logger.debug("apply")
        # apply changes
        try:
            self.lib.cur.meta.survey = self.survey.text()
            self.lib.cur.meta.vessel = self.vessel.text()
            self.lib.cur.meta.sn = self.sn.text()
        except RuntimeError as e:
            msg = "Issue in apply changes\n%s" % e
            # noinspection PyCallByClass
            QtGui.QMessageBox.critical(self, "Metadata error", msg, QtGui.QMessageBox.Ok)
            return

        # update proc_time widget
        self.proc_time.setText(self.lib.cur.meta.proc_time.strftime("%d/%m/%y %H:%M"))

        msg = "Changes have been applied!"
        # noinspection PyCallByClass
        QtGui.QMessageBox.information(self, "Metadata", msg, QtGui.QMessageBox.Ok)
