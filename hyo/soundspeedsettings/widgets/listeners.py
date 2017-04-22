import os
import logging

from PySide import QtGui, QtCore

logger = logging.getLogger(__name__)

from hyo.soundspeedsettings.widgets.widget import AbstractWidget
from hyo.soundspeed.profile.dicts import Dicts


class Listeners(AbstractWidget):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win, db):
        AbstractWidget.__init__(self, main_win=main_win, db=db)

        lbl_width = 120

        # outline ui
        self.main_layout = QtGui.QVBoxLayout()
        self.frame.setLayout(self.main_layout)

        # - active setup
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        hbox.addStretch()
        self.active_label = QtGui.QLabel()
        hbox.addWidget(self.active_label)
        hbox.addStretch()

        # - left and right sub-frames
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- left
        self.left_frame = QtGui.QFrame()
        self.left_layout = QtGui.QVBoxLayout()
        self.left_frame.setLayout(self.left_layout)
        hbox.addWidget(self.left_frame, stretch=1)
        # -- stretch
        hbox.addStretch()
        # -- right
        self.right_frame = QtGui.QFrame()
        self.right_layout = QtGui.QVBoxLayout()
        self.right_frame.setLayout(self.right_layout)
        hbox.addWidget(self.right_frame, stretch=1)

        # LEFT

        # - Editor settings
        hbox = QtGui.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        hbox.addStretch()
        self.label = QtGui.QLabel("SIS:")
        hbox.addWidget(self.label)
        hbox.addStretch()

        # - sis_listen_port
        hbox = QtGui.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        label = QtGui.QLabel("Listen port:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- value
        self.sis_listen_port = QtGui.QLineEdit()
        validator = QtGui.QIntValidator(0, 65535)
        self.sis_listen_port.setValidator(validator)
        hbox.addWidget(self.sis_listen_port)

        # - sis_listen_timeout
        hbox = QtGui.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        label = QtGui.QLabel("Listen timeout:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- value
        self.sis_listen_timeout = QtGui.QLineEdit()
        validator = QtGui.QIntValidator(0, 9999)
        self.sis_listen_timeout.setValidator(validator)
        hbox.addWidget(self.sis_listen_timeout)

        # - sis_auto_apply_manual_casts
        hbox = QtGui.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        label = QtGui.QLabel("Auto apply profile:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- value
        self.sis_auto_apply_manual_casts = QtGui.QComboBox()
        self.sis_auto_apply_manual_casts.addItems(["True", "False"])
        hbox.addWidget(self.sis_auto_apply_manual_casts)

        self.left_layout.addSpacing(12)

        # - Editor settings
        hbox = QtGui.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        hbox.addStretch()
        self.label = QtGui.QLabel("Sippican:")
        hbox.addWidget(self.label)
        hbox.addStretch()

        # - sippican_listen_port
        hbox = QtGui.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        label = QtGui.QLabel("Listen port:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- value
        self.sippican_listen_port = QtGui.QLineEdit()
        validator = QtGui.QIntValidator(0, 99999)
        self.sippican_listen_port.setValidator(validator)
        hbox.addWidget(self.sippican_listen_port)

        # - sippican_listen_timeout
        hbox = QtGui.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        label = QtGui.QLabel("Listen timeout:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- value
        self.sippican_listen_timeout = QtGui.QLineEdit()
        validator = QtGui.QIntValidator(0, 99999)
        self.sippican_listen_timeout.setValidator(validator)
        hbox.addWidget(self.sippican_listen_timeout)

        self.left_layout.addStretch()

        # RIGHT

        # - Editor settings
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        hbox.addStretch()
        self.label = QtGui.QLabel("MVP:")
        hbox.addWidget(self.label)
        hbox.addStretch()

        # - mvp_ip_address
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Listen IP:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
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

        # - mvp_listen_port
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Listen port:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.mvp_listen_port = QtGui.QLineEdit()
        validator = QtGui.QIntValidator(0, 65535)
        self.mvp_listen_port.setValidator(validator)
        vbox.addWidget(self.mvp_listen_port)
        vbox.addStretch()

        # - mvp_listen_timeout
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Listen timeout:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.mvp_listen_timeout = QtGui.QLineEdit()
        validator = QtGui.QIntValidator(0, 65535)
        self.mvp_listen_timeout.setValidator(validator)
        vbox.addWidget(self.mvp_listen_timeout)
        vbox.addStretch()

        # - mvp_transmission_protocol
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Protocol:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.mvp_transmission_protocol = QtGui.QComboBox()
        self.mvp_transmission_protocol.addItems([k for k in Dicts.mvp_protocols.keys()])
        vbox.addWidget(self.mvp_transmission_protocol)
        vbox.addStretch()

        # - mvp_format
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Format:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.mvp_format = QtGui.QComboBox()
        self.mvp_format.addItems([k for k in Dicts.mvp_formats.keys()])
        vbox.addWidget(self.mvp_format)
        vbox.addStretch()

        # - mvp_winch_port
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Winch port:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.mvp_winch_port = QtGui.QLineEdit()
        validator = QtGui.QIntValidator(0, 65535)
        self.mvp_winch_port.setValidator(validator)
        vbox.addWidget(self.mvp_winch_port)
        vbox.addStretch()

        # - mvp_fish_port
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Fish port:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.mvp_fish_port = QtGui.QLineEdit()
        validator = QtGui.QIntValidator(0, 65535)
        self.mvp_fish_port.setValidator(validator)
        vbox.addWidget(self.mvp_fish_port)
        vbox.addStretch()

        # - mvp_nav_port
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Nav port:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.mvp_nav_port = QtGui.QLineEdit()
        validator = QtGui.QIntValidator(0, 65535)
        self.mvp_nav_port.setValidator(validator)
        vbox.addWidget(self.mvp_nav_port)
        vbox.addStretch()

        # - mvp_system_port
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("System port:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.mvp_system_port = QtGui.QLineEdit()
        validator = QtGui.QIntValidator(0, 65535)
        self.mvp_system_port.setValidator(validator)
        vbox.addWidget(self.mvp_system_port)
        vbox.addStretch()

        # - mvp_sw_version
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("SW version:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.mvp_sw_version = QtGui.QLineEdit()
        vbox.addWidget(self.mvp_sw_version)
        vbox.addStretch()

        # - mvp_instrument_id
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Instrument ID:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.mvp_instrument_id = QtGui.QLineEdit()
        vbox.addWidget(self.mvp_instrument_id)
        vbox.addStretch()

        # - mvp_instrument
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
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
        self.mvp_instrument.addItems([k for k in Dicts.mvp_instruments.keys()])
        vbox.addWidget(self.mvp_instrument)
        vbox.addStretch()

        self.right_layout.addStretch()

        self.main_layout.addStretch()

        self.setup_changed()  # to trigger the first data population

        # -- functions
        # --- left
        # noinspection PyUnresolvedReferences
        self.sis_listen_port.textChanged.connect(self.apply_sis_listen_port)
        # noinspection PyUnresolvedReferences
        self.sis_listen_timeout.textChanged.connect(self.apply_sis_listen_timeout)
        # noinspection PyUnresolvedReferences
        self.sis_auto_apply_manual_casts.currentIndexChanged.connect(self.apply_sis_auto_apply_manual_casts)
        # noinspection PyUnresolvedReferences
        self.sippican_listen_port.textChanged.connect(self.apply_sippican_listen_port)
        # noinspection PyUnresolvedReferences
        self.sippican_listen_timeout.textChanged.connect(self.apply_sippican_listen_timeout)
        # --- right
        # noinspection PyUnresolvedReferences
        self.mvp_ip_address.textChanged.connect(self.apply_mvp_ip_address)
        # noinspection PyUnresolvedReferences
        self.mvp_listen_port.textChanged.connect(self.apply_mvp_listen_port)
        # noinspection PyUnresolvedReferences
        self.mvp_listen_timeout.textChanged.connect(self.apply_mvp_listen_timeout)
        # noinspection PyUnresolvedReferences
        self.mvp_transmission_protocol.currentIndexChanged.connect(self.apply_mvp_transmission_protocol)
        # noinspection PyUnresolvedReferences
        self.mvp_format.currentIndexChanged.connect(self.apply_mvp_format)
        # noinspection PyUnresolvedReferences
        self.mvp_winch_port.textChanged.connect(self.apply_mvp_winch_port)
        # noinspection PyUnresolvedReferences
        self.mvp_fish_port.textChanged.connect(self.apply_mvp_fish_port)
        # noinspection PyUnresolvedReferences
        self.mvp_nav_port.textChanged.connect(self.apply_mvp_nav_port)
        # noinspection PyUnresolvedReferences
        self.mvp_system_port.textChanged.connect(self.apply_mvp_system_port)
        # noinspection PyUnresolvedReferences
        self.mvp_sw_version.textChanged.connect(self.apply_mvp_sw_version)
        # noinspection PyUnresolvedReferences
        self.mvp_instrument_id.textChanged.connect(self.apply_mvp_instrument_id)
        # noinspection PyUnresolvedReferences
        self.mvp_instrument.currentIndexChanged.connect(self.apply_mvp_instrument)

    def apply_sis_listen_port(self):
        # logger.debug("listen SIS port")
        self.db.sis_listen_port = int(self.sis_listen_port.text())
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_sis_listen_timeout(self):
        # logger.debug("listen SIS timeout")
        self.db.sis_listen_timeout = int(self.sis_listen_timeout.text())
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_sis_auto_apply_manual_casts(self):
        # logger.debug("auto-apply cast")
        self.db.sis_auto_apply_manual_casts = self.sis_auto_apply_manual_casts.currentText() == "True"
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_sippican_listen_timeout(self):
        # logger.debug("apply listen timeout")
        self.db.sippican_listen_timeout = int(self.sippican_listen_timeout.text())
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_sippican_listen_port(self):
        # logger.debug("apply listen port")
        self.db.sippican_listen_port = int(self.sippican_listen_port.text())
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_mvp_listen_port(self):
        # logger.debug("apply listen port")
        self.db.mvp_listen_port = int(self.mvp_listen_port.text())
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_mvp_listen_timeout(self):
        # logger.debug("apply listen timeout")
        self.db.mvp_listen_timeout = int(self.mvp_listen_timeout.text())
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_mvp_ip_address(self):
        # logger.debug("apply listen IP")
        self.db.mvp_ip_address = self.mvp_ip_address.text()
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_mvp_transmission_protocol(self):
        # logger.debug("apply tx protocol")
        self.db.mvp_transmission_protocol = self.mvp_transmission_protocol.currentText()
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_mvp_format(self):
        # logger.debug("apply format")
        self.db.mvp_format = self.mvp_format.currentText()
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_mvp_winch_port(self):
        # logger.debug("apply winch port")
        self.db.mvp_winch_port = int(self.mvp_winch_port.text())
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_mvp_fish_port(self):
        # logger.debug("apply fish port")
        self.db.mvp_fish_port = int(self.mvp_fish_port.text())
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_mvp_nav_port(self):
        # logger.debug("apply nav port")
        self.db.mvp_nav_port = int(self.mvp_nav_port.text())
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_mvp_system_port(self):
        # logger.debug("apply system port")
        self.db.mvp_system_port = int(self.mvp_system_port.text())
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_mvp_sw_version(self):
        # logger.debug("apply software version")
        self.db.mvp_sw_version = self.mvp_sw_version.text()
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_mvp_instrument_id(self):
        # logger.debug("apply instrument ID")
        self.db.mvp_instrument_id = self.mvp_instrument_id.text()
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_mvp_instrument(self):
        # logger.debug("apply instrument type")
        self.db.mvp_instrument = self.mvp_instrument.currentText()
        self.setup_changed()
        self.main_win.reload_settings()

    def setup_changed(self):
        """Refresh items"""
        # logger.debug("refresh input settings")

        # set the top label
        self.active_label.setText("<b>Current setup: %s [#%02d]</b>" % (self.db.setup_name, self.db.active_setup_id))

        # - SIS

        # sis_listen_port
        self.sis_listen_port.setText("%d" % self.db.sis_listen_port)
        # sis_listen_timeout
        self.sis_listen_timeout.setText("%d" % self.db.sis_listen_timeout)

        # sis_auto_apply_manual_casts
        if self.db.sis_auto_apply_manual_casts:
            self.sis_auto_apply_manual_casts.setCurrentIndex(0)  # True
        else:
            self.sis_auto_apply_manual_casts.setCurrentIndex(1)  # False

        # - SIPPICAN

        # sippican_listen_port
        self.sippican_listen_port.setText("%d" % self.db.sippican_listen_port)

        # sippican_listen_timeout
        self.sippican_listen_timeout.setText("%d" % self.db.sippican_listen_timeout)

        # - MVP

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
