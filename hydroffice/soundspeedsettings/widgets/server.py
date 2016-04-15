from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

from PySide import QtGui, QtCore

logger = logging.getLogger(__name__)

from .widget import AbstractWidget
from hydroffice.soundspeed.profile.dicts import Dicts


class Server(AbstractWidget):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win, db):
        AbstractWidget.__init__(self, main_win=main_win, db=db)

        lbl_width = 100

        # outline ui
        self.main_layout = QtGui.QVBoxLayout()
        self.frame.setLayout(self.main_layout)

        # - ssp_extension_source
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Source:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.server_source = QtGui.QComboBox()
        self.server_source.addItems(Dicts.atlases.keys())
        vbox.addWidget(self.server_source)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_server_source)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        # - server_apply_surface_sound_speed
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Surface sound speed:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.server_apply_surface_sound_speed= QtGui.QComboBox()
        self.server_apply_surface_sound_speed.addItems(["True", "False"])
        vbox.addWidget(self.server_apply_surface_sound_speed)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_server_apply_surface_sound_speed)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        self.main_layout.addStretch()

        # - server_auto_export_on_send
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Export of send:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.server_auto_export_on_send = QtGui.QComboBox()
        self.server_auto_export_on_send.addItems(["True", "False"])
        vbox.addWidget(self.server_auto_export_on_send)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_server_auto_export_on_send)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        # - server_append_caris_file
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Append Caris file:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.server_append_caris_file = QtGui.QComboBox()
        self.server_append_caris_file.addItems(["True", "False"])
        vbox.addWidget(self.server_append_caris_file)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_server_append_caris_file)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        self.main_layout.addStretch()

        self.setup_changed()  # to trigger the first data population

    def apply_server_source(self):
        logger.debug("apply server source")
        self.db.server_source = self.server_source.currentText()
        self.setup_changed()

    def apply_server_append_caris_file(self):
        logger.debug("apply append caris file")
        self.db.server_append_caris_file = self.server_append_caris_file.currentText()
        self.setup_changed()

    def apply_server_apply_surface_sound_speed(self):
        logger.debug("apply apply surface sound speed")
        self.db.server_apply_surface_sound_speed = self.server_apply_surface_sound_speed.currentText()
        self.setup_changed()

    def apply_server_auto_export_on_send(self):
        logger.debug("apply export on send")
        self.db.server_auto_export_on_send = self.server_auto_export_on_send.currentText()
        self.setup_changed()

    def setup_changed(self):
        """Refresh items"""
        # logger.debug("refresh server settings")

        # extension source
        _str = self.db.server_source
        _idx = Dicts.atlases[_str]
        self.server_source.setCurrentIndex(_idx)

        # server_append_caris_file
        if self.db.server_append_caris_file:
            self.server_append_caris_file.setCurrentIndex(0)  # True
        else:
            self.server_append_caris_file.setCurrentIndex(1)  # False

        # server_apply_surface_sound_speed
        if self.db.server_apply_surface_sound_speed:
            self.server_apply_surface_sound_speed.setCurrentIndex(0)  # True
        else:
            self.server_apply_surface_sound_speed.setCurrentIndex(1)  # False

        # server_auto_export_on_send
        if self.db.server_auto_export_on_send:
            self.server_auto_export_on_send.setCurrentIndex(0)  # True
        else:
            self.server_auto_export_on_send.setCurrentIndex(1)  # False