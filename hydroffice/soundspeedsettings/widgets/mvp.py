from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

from PySide import QtGui, QtCore

logger = logging.getLogger(__name__)

from .widget import AbstractWidget
from hydroffice.soundspeed.profile.dicts import Dicts


class Mvp(AbstractWidget):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win, db):
        AbstractWidget.__init__(self, main_win=main_win, db=db)

        lbl_width = 100

        # outline ui
        self.main_layout = QtGui.QVBoxLayout()
        self.frame.setLayout(self.main_layout)

        # - mvp_ip_address
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Listen IP:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.mvp_ip_address = QtGui.QLineEdit()
        octet = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        reg_ex = QtCore.QRegExp("^%s\.%s\.%s\.%s$" % (octet, octet, octet, octet))
        validator = QtGui.QRegExpValidator(reg_ex)
        self.mvp_ip_address.setValidator(validator)
        vbox.addWidget(self.mvp_ip_address)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_mvp_ip_address)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        # - mvp_listen_port
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Listen port:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.mvp_listen_port = QtGui.QLineEdit()
        validator = QtGui.QIntValidator(0, 65535)
        self.mvp_listen_port.setValidator(validator)
        vbox.addWidget(self.mvp_listen_port)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_mvp_listen_port)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        # - mvp_listen_timeout
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Listen timeout:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.mvp_listen_timeout = QtGui.QLineEdit()
        validator = QtGui.QIntValidator(0, 65535)
        self.mvp_listen_timeout.setValidator(validator)
        vbox.addWidget(self.mvp_listen_timeout)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_mvp_listen_timeout)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        # - mvp_transmission_protocol
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Protocol:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.mvp_transmission_protocol = QtGui.QComboBox()
        self.mvp_transmission_protocol.addItems(Dicts.mvp_protocols.keys())
        vbox.addWidget(self.mvp_transmission_protocol)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_mvp_transmission_protocol)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        # - mvp_format
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Format:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.mvp_format = QtGui.QComboBox()
        self.mvp_format.addItems(Dicts.mvp_formats.keys())
        vbox.addWidget(self.mvp_format)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_mvp_format)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        # - mvp_winch_port
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Winch port:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.mvp_winch_port = QtGui.QLineEdit()
        validator = QtGui.QIntValidator(0, 65535)
        self.mvp_winch_port.setValidator(validator)
        vbox.addWidget(self.mvp_winch_port)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_mvp_winch_port)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        # - mvp_fish_port
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Fish port:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.mvp_fish_port = QtGui.QLineEdit()
        validator = QtGui.QIntValidator(0, 65535)
        self.mvp_fish_port.setValidator(validator)
        vbox.addWidget(self.mvp_fish_port)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_mvp_fish_port)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        # - mvp_nav_port
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Nav port:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.mvp_nav_port = QtGui.QLineEdit()
        validator = QtGui.QIntValidator(0, 65535)
        self.mvp_nav_port.setValidator(validator)
        vbox.addWidget(self.mvp_nav_port)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_mvp_nav_port)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        # - mvp_system_port
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("System port:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.mvp_system_port = QtGui.QLineEdit()
        validator = QtGui.QIntValidator(0, 65535)
        self.mvp_system_port.setValidator(validator)
        vbox.addWidget(self.mvp_system_port)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_mvp_system_port)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        # - mvp_sw_version
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("SW version:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.mvp_sw_version = QtGui.QLineEdit()
        vbox.addWidget(self.mvp_sw_version)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_mvp_sw_version)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        # - mvp_instrument_id
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Instrument ID:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.mvp_instrument_id = QtGui.QLineEdit()
        vbox.addWidget(self.mvp_instrument_id)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_mvp_instrument_id)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        # - mvp_instrument
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Instrument type:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.mvp_instrument = QtGui.QComboBox()
        self.mvp_instrument.addItems(Dicts.mvp_instruments.keys())
        vbox.addWidget(self.mvp_instrument)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_mvp_instrument)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        self.main_layout.addStretch()

        self.setup_changed()  # to trigger the first data population

    def apply_mvp_listen_port(self):
        logger.debug("apply listen port")
        self.db.mvp_listen_port = int(self.mvp_listen_port.text())
        self.setup_changed()

    def apply_mvp_listen_timeout(self):
        logger.debug("apply listen timeout")
        self.db.mvp_listen_timeout = int(self.mvp_listen_timeout.text())
        self.setup_changed()

    def apply_mvp_ip_address(self):
        logger.debug("apply listen IP")
        self.db.mvp_ip_address = self.mvp_ip_address.text()
        self.setup_changed()

    def apply_mvp_transmission_protocol(self):
        logger.debug("apply tx protocol")
        self.db.mvp_transmission_protocol = self.mvp_transmission_protocol.currentText()
        self.setup_changed()

    def apply_mvp_format(self):
        logger.debug("apply format")
        self.db.mvp_format = self.mvp_format.currentText()
        self.setup_changed()

    def apply_mvp_winch_port(self):
        logger.debug("apply winch port")
        self.db.mvp_winch_port = int(self.mvp_winch_port.text())
        self.setup_changed()

    def apply_mvp_fish_port(self):
        logger.debug("apply fish port")
        self.db.mvp_fish_port = int(self.mvp_fish_port.text())
        self.setup_changed()

    def apply_mvp_nav_port(self):
        logger.debug("apply nav port")
        self.db.mvp_nav_port = int(self.mvp_nav_port.text())
        self.setup_changed()

    def apply_mvp_system_port(self):
        logger.debug("apply system port")
        self.db.mvp_system_port = int(self.mvp_system_port.text())
        self.setup_changed()

    def apply_mvp_sw_version(self):
        logger.debug("apply software version")
        self.db.mvp_sw_version = int(self.mvp_sw_version.text())
        self.setup_changed()

    def apply_mvp_instrument_id(self):
        logger.debug("apply instrument ID")
        self.db.mvp_instrument_id = int(self.mvp_instrument_id.text())
        self.setup_changed()

    def apply_mvp_instrument(self):
        logger.debug("apply instrument type")
        self.db.mvp_instrument = self.mvp_instrument.currentText()
        self.setup_changed()

    def setup_changed(self):
        """Refresh items"""
        # logger.debug("refresh input settings")

        # mvp_ip_address
        self.mvp_ip_address.setText(self.db.mvp_ip_address)
        # mvp_listen_port
        self.mvp_listen_port.setText("%d" % self.db.mvp_listen_port)
        # mvp_listen_timeout
        self.mvp_listen_timeout.setText("%d" % self.db.mvp_listen_timeout)

        # mvp_transmission_protocol
        _str = self.db.mvp_transmission_protocol
        _idx = Dicts.mvp_protocols[_str]
        self.mvp_transmission_protocol.setCurrentIndex(_idx)

        # mvp_format
        _str = self.db.mvp_format
        _idx = Dicts.mvp_formats[_str]
        self.mvp_format.setCurrentIndex(_idx)

        # mvp_winch_port
        self.mvp_winch_port.setText("%d" % self.db.mvp_winch_port)
        # mvp_fish_port
        self.mvp_fish_port.setText("%d" % self.db.mvp_fish_port)
        # mvp_nav_port
        self.mvp_nav_port.setText("%d" % self.db.mvp_nav_port)
        # mvp_system_port
        self.mvp_system_port.setText("%d" % self.db.mvp_system_port)

        # mvp_sw_version
        self.mvp_sw_version.setText(self.db.mvp_sw_version)
        # mvp_instrument_id
        self.mvp_instrument_id.setText(self.db.mvp_instrument_id)

        # mvp_instrument
        _str = self.db.mvp_instrument
        _idx = Dicts.mvp_instruments[_str]
        self.mvp_instrument.setCurrentIndex(_idx)
