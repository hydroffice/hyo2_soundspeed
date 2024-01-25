from PySide6 import QtCore, QtWidgets, QtGui

import traceback
import logging

from hyo2.ssm2.lib.profile.oceanography import Oceanography
from hyo2.ssm2.app.gui.soundspeedmanager.dialogs.dialog import AbstractDialog

logger = logging.getLogger(__name__)


class ConstantGradientProfileDialog(AbstractDialog):

    def __init__(self, main_win, lib, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        self.oc = Oceanography()

        self.setWindowTitle("Constant-gradient Profile")
        self.setMinimumWidth(480)

        # outline ui
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setContentsMargins(3, 3, 3, 3)
        self.setLayout(self.mainLayout)

        value_validator = QtGui.QDoubleValidator(0, 12000, 2, self)

        self.mainLayout.addStretch()

        # start point
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        # depth label
        self.start_depth_label = QtWidgets.QLabel("Start [m]:")
        self.start_depth_label.setFixedWidth(50)
        self.start_depth_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        hbox.addWidget(self.start_depth_label)
        # depth value
        self.start_depth_value = QtWidgets.QLineEdit()
        self.start_depth_value.setFixedWidth(50)
        self.start_depth_value.setValidator(value_validator)
        self.start_depth_value.setText("0.0")
        # noinspection PyUnresolvedReferences
        self.start_depth_value.textEdited.connect(self.on_values_changed)
        hbox.addWidget(self.start_depth_value)
        # temp label
        self.start_temp_label = QtWidgets.QLabel("temp [°C]:")
        self.start_temp_label.setFixedWidth(70)
        self.start_temp_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        hbox.addWidget(self.start_temp_label)
        # temp value
        self.start_temp_value = QtWidgets.QLineEdit()
        self.start_temp_value.setFixedWidth(50)
        self.start_temp_value.setValidator(value_validator)
        self.start_temp_value.setText("12.94")
        # noinspection PyUnresolvedReferences
        self.start_temp_value.textEdited.connect(self.on_values_changed)
        hbox.addWidget(self.start_temp_value)
        # sal label
        self.start_sal_label = QtWidgets.QLabel("sal [PSU]:")
        self.start_sal_label.setFixedWidth(70)
        self.start_sal_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        hbox.addWidget(self.start_sal_label)
        # sal value
        self.start_sal_value = QtWidgets.QLineEdit()
        self.start_sal_value.setFixedWidth(50)
        self.start_sal_value.setValidator(value_validator)
        self.start_sal_value.setText("35.0")
        # noinspection PyUnresolvedReferences
        self.start_sal_value.textEdited.connect(self.on_values_changed)
        hbox.addWidget(self.start_sal_value)
        # speed label
        self.start_speed_label = QtWidgets.QLabel("speed [m/s]:")
        self.start_speed_label.setFixedWidth(70)
        self.start_speed_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        hbox.addWidget(self.start_speed_label)
        # speed value
        self.start_speed_value = QtWidgets.QLineEdit()
        self.start_speed_value.setFixedWidth(70)
        self.start_speed_value.setValidator(value_validator)
        self.start_speed_value.setText("1500.0")
        self.start_speed_value.setDisabled(True)
        # noinspection PyUnresolvedReferences
        self.start_speed_value.textEdited.connect(self.on_values_changed)
        hbox.addWidget(self.start_speed_value)
        hbox.addStretch()

        # end point
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        # depth label
        self.end_depth_label = QtWidgets.QLabel("End [m]:")
        self.end_depth_label.setFixedWidth(50)
        self.end_depth_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        hbox.addWidget(self.end_depth_label)
        # depth value
        self.end_depth_value = QtWidgets.QLineEdit()
        self.end_depth_value.setFixedWidth(50)
        self.end_depth_value.setValidator(value_validator)
        self.end_depth_value.setText("1000.0")
        # noinspection PyUnresolvedReferences
        self.end_depth_value.textEdited.connect(self.on_values_changed)
        hbox.addWidget(self.end_depth_value)
        # temp label
        self.end_temp_label = QtWidgets.QLabel("temp [°C]:")
        self.end_temp_label.setFixedWidth(70)
        self.end_temp_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        hbox.addWidget(self.end_temp_label)
        # temp value
        self.end_temp_value = QtWidgets.QLineEdit()
        self.end_temp_value.setFixedWidth(50)
        self.end_temp_value.setValidator(value_validator)
        self.end_temp_value.setText("12.94")
        # noinspection PyUnresolvedReferences
        self.end_temp_value.textEdited.connect(self.on_values_changed)
        hbox.addWidget(self.end_temp_value)
        # sal label
        self.end_sal_label = QtWidgets.QLabel("sal [PSU]:")
        self.end_sal_label.setFixedWidth(70)
        self.end_sal_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        hbox.addWidget(self.end_sal_label)
        # sal value
        self.end_sal_value = QtWidgets.QLineEdit()
        self.end_sal_value.setFixedWidth(50)
        self.end_sal_value.setValidator(value_validator)
        self.end_sal_value.setText("35.0")
        # noinspection PyUnresolvedReferences
        self.end_sal_value.textEdited.connect(self.on_values_changed)
        hbox.addWidget(self.end_sal_value)
        # speed label
        self.end_speed_label = QtWidgets.QLabel("speed [m/s]:")
        self.end_speed_label.setFixedWidth(70)
        self.end_speed_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        hbox.addWidget(self.end_speed_label)
        # speed value
        self.end_speed_value = QtWidgets.QLineEdit()
        self.end_speed_value.setFixedWidth(70)
        self.end_speed_value.setValidator(value_validator)
        self.end_speed_value.setText("1500.0")
        self.end_speed_value.setDisabled(True)
        # noinspection PyUnresolvedReferences
        self.end_speed_value.textEdited.connect(self.on_values_changed)
        hbox.addWidget(self.end_speed_value)
        hbox.addStretch()

        self.mainLayout.addSpacing(12)

        # apply
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch()
        self.apply = QtWidgets.QPushButton("Apply")
        # self.apply.setFixedHeight(30)
        # noinspection PyUnresolvedReferences
        self.apply.clicked.connect(self.on_apply)
        hbox.addWidget(self.apply)
        hbox.addStretch()
        self.mainLayout.addLayout(hbox)

        self.mainLayout.addStretch()

        self.on_values_changed()

    def on_values_changed(self):
        logger.debug("values changed")

        try:
            start_speed = self.oc.speed(d=float(self.start_depth_value.text()),
                                        t=float(self.start_temp_value.text()),
                                        s=float(self.start_sal_value.text()))
            self.start_speed_value.setText("%.2f" % start_speed)
        except Exception as e:
            logger.warning("Invalid start sound speed calculation: %s" % e)

        try:
            end_speed = self.oc.speed(d=float(self.end_depth_value.text()),
                                      t=float(self.end_temp_value.text()),
                                      s=float(self.end_sal_value.text()))
            self.end_speed_value.setText("%.2f" % end_speed)
        except Exception as e:
            logger.warning("Invalid end sound speed calculation: %s" % e)

    def on_apply(self):
        logger.debug("apply")

        try:
            start_depth = float(self.start_depth_value.text())
            end_depth = float(self.end_depth_value.text())
            if start_depth < 0:
                raise RuntimeError("Negative start depth: %s" % start_depth)
            if start_depth > end_depth:
                raise RuntimeError("Start depth > end depth: %s > %s" % (start_depth, end_depth))

        except Exception as e:
            msg = "Issue in depth fields!\n\n%s" % e
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.warning(self, "Constant-gradient profile", msg, QtWidgets.QMessageBox.Ok)
            return

        try:
            start_temp = float(self.start_temp_value.text())
            end_temp = float(self.end_temp_value.text())
            if start_temp < -1.0:
                raise RuntimeError("Too negative start temp: %s" % start_temp)

        except Exception as e:
            msg = "Issue in temperature fields!\n\n%s" % e
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.warning(self, "Constant-gradient profile", msg, QtWidgets.QMessageBox.Ok)
            return

        try:
            start_sal = float(self.start_sal_value.text())
            end_sal = float(self.end_sal_value.text())
            if start_sal < 0:
                raise RuntimeError("Negative start sal: %s" % start_sal)

        except Exception as e:
            msg = "Issue in salinity fields!\n\n%s" % e
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.warning(self, "Constant-gradient profile", msg, QtWidgets.QMessageBox.Ok)
            return

        try:
            start_speed = float(self.start_speed_value.text())
            end_speed = float(self.end_speed_value.text())
            if start_speed < 0:
                raise RuntimeError("Negative start speed: %s" % start_speed)

        except Exception as e:
            msg = "Issue in speed fields!\n\n%s" % e
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.warning(self, "Constant-gradient profile", msg, QtWidgets.QMessageBox.Ok)
            return

        try:
            self.lib.create_profile(start_depth=start_depth, start_temp=start_temp,
                                    start_sal=start_sal, start_speed=start_speed,
                                    end_depth=end_depth, end_temp=end_temp,
                                    end_sal=end_sal, end_speed=end_speed)

        except RuntimeError as e:
            traceback.print_exc()
            msg = "Issue in creating the profile:\n\n> %s" % e
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Creation error", msg, QtWidgets.QMessageBox.Ok)
            return

        self.accept()
