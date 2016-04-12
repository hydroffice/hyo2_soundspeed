from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

from PySide import QtGui, QtCore
from hydroffice.soundspeed.profile.dicts import Dicts

logger = logging.getLogger(__name__)

from .widget import AbstractWidget


class Basic(AbstractWidget):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win, db):
        AbstractWidget.__init__(self, main_win=main_win, db=db)

        lbl_width = 100

        # outline ui
        self.main_layout = QtGui.QVBoxLayout()
        self.frame.setLayout(self.main_layout)

        # - processing
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        hbox.addStretch()
        self.label = QtGui.QLabel("Processing")
        hbox.addWidget(self.label)
        hbox.addStretch()

        # - profile direction
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Profile direction:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.profile_direction = QtGui.QComboBox()
        self.profile_direction.addItems(Dicts.ssp_directions.keys())
        vbox.addWidget(self.profile_direction)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_profile_direction)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        # - atlases
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        hbox.addStretch()
        self.label = QtGui.QLabel("Atlases")
        hbox.addWidget(self.label)
        hbox.addStretch()

        # - use woa09
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Use WOA09:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.use_woa09 = QtGui.QComboBox()
        self.use_woa09.addItems(["True", "False"])
        vbox.addWidget(self.use_woa09)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_use_woa09)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        # - use woa13
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Use WOA13:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.use_woa13 = QtGui.QComboBox()
        self.use_woa13.addItems(["True", "False"])
        # self.use_woa13.setDisabled(True)
        vbox.addWidget(self.use_woa13)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_use_woa13)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        # - use rtofs
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Use RTOFS:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.use_rtofs = QtGui.QComboBox()
        self.use_rtofs.addItems(["True", "False"])
        vbox.addWidget(self.use_rtofs)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_use_rtofs)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        # - logging
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        hbox.addStretch()
        self.label = QtGui.QLabel("Logging")
        hbox.addWidget(self.label)
        hbox.addStretch()

        # - log_user
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("User logging:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.log_user = QtGui.QComboBox()
        self.log_user.addItems(["True", "False"])
        vbox.addWidget(self.log_user)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_log_user)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        # - log_server
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Server logging:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.log_server = QtGui.QComboBox()
        self.log_server.addItems(["True", "False"])
        vbox.addWidget(self.log_server)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_log_server)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        self.main_layout.addStretch()

        self.setup_changed()  # to trigger the first data population

    def apply_profile_direction(self):
        logger.debug("apply profile direction")
        self.db.ssp_up_or_down = self.profile_direction.currentText()
        self.setup_changed()

    def apply_use_woa09(self):
        logger.debug("apply use woa09")
        self.db.use_woa09 = self.use_woa09.currentText()
        if self.db.use_woa09:
            self.main_win.main_win.check_woa09()
        self.setup_changed()

    def apply_use_woa13(self):
        logger.debug("apply use woa13")
        self.db.use_woa13 = self.use_woa13.currentText()
        if self.db.use_woa13:
            self.main_win.main_win.check_woa13()
        self.setup_changed()

    def apply_use_rtofs(self):
        logger.debug("apply use rtofs")
        self.db.use_rtofs = self.use_rtofs.currentText()
        self.setup_changed()

    def apply_log_user(self):
        logger.debug("apply log user")
        self.db.log_user = self.log_user.currentText()
        self.main_win.prj.logging()
        self.setup_changed()

    def apply_log_server(self):
        logger.debug("apply log server")
        self.db.log_server = self.log_server.currentText()
        self.main_win.prj.logging()
        self.setup_changed()

    def setup_changed(self):
        """Refresh items"""
        logger.debug("refresh basic")

        # profile direction
        dir_str = self.db.ssp_up_or_down
        dir_idx = Dicts.ssp_directions[dir_str]
        self.profile_direction.setCurrentIndex(dir_idx)

        # use woa09
        if self.db.use_woa09:
            self.use_woa09.setCurrentIndex(0)  # True
        else:
            self.use_woa09.setCurrentIndex(1)  # False

        # use woa13
        if self.db.use_woa13:
            self.use_woa13.setCurrentIndex(0)  # True
        else:
            self.use_woa13.setCurrentIndex(1)  # False

        # use rtofs
        if self.db.use_rtofs:
            self.use_rtofs.setCurrentIndex(0)  # True
        else:
            self.use_rtofs.setCurrentIndex(1)  # False

        # log_user
        if self.db.log_user:
            self.log_user.setCurrentIndex(0)  # True
        else:
            self.log_user.setCurrentIndex(1)  # False

        # log_server
        if self.db.log_server:
            self.log_server.setCurrentIndex(0)  # True
        else:
            self.log_server.setCurrentIndex(1)  # False
