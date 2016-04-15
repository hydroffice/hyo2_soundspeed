from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

from PySide import QtGui, QtCore

logger = logging.getLogger(__name__)

from .widget import AbstractWidget
from hydroffice.soundspeed.profile.dicts import Dicts


class Sippican(AbstractWidget):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win, db):
        AbstractWidget.__init__(self, main_win=main_win, db=db)

        lbl_width = 100

        # outline ui
        self.main_layout = QtGui.QVBoxLayout()
        self.frame.setLayout(self.main_layout)

        # - sippican_listen_port
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
        self.sippican_listen_port = QtGui.QLineEdit()
        validator = QtGui.QIntValidator(0, 99999)
        self.sippican_listen_port.setValidator(validator)
        vbox.addWidget(self.sippican_listen_port)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_sippican_listen_port)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        # - sippican_listen_timeout
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
        self.sippican_listen_timeout = QtGui.QLineEdit()
        validator = QtGui.QIntValidator(0, 99999)
        self.sippican_listen_timeout.setValidator(validator)
        vbox.addWidget(self.sippican_listen_timeout)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_sippican_listen_timeout)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        self.main_layout.addStretch()

        self.setup_changed()  # to trigger the first data population

    def apply_sippican_listen_timeout(self):
        logger.debug("apply listen timeout")
        self.db.sippican_listen_timeout = int(self.sippican_listen_timeout.text())
        self.setup_changed()

    def apply_sippican_listen_port(self):
        logger.debug("apply listen port")
        self.db.sippican_listen_port = int(self.sippican_listen_port.text())
        self.setup_changed()

    def setup_changed(self):
        """Refresh items"""
        # logger.debug("refresh input settings")

        # sippican_listen_port
        self.sippican_listen_port.setText("%d" % self.db.sippican_listen_port)

        # sippican_listen_timeout
        self.sippican_listen_timeout.setText("%d" % self.db.sippican_listen_timeout)
