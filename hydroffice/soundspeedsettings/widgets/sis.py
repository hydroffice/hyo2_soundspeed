from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

from PySide import QtGui

logger = logging.getLogger(__name__)

from .widget import AbstractWidget


class Sis(AbstractWidget):

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

        # - sis_listen_port
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
        self.sis_listen_port = QtGui.QLineEdit()
        validator = QtGui.QIntValidator(0, 65535)
        self.sis_listen_port.setValidator(validator)
        vbox.addWidget(self.sis_listen_port)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        # noinspection PyUnresolvedReferences
        btn_apply.clicked.connect(self.apply_sis_listen_port)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        # - sis_listen_timeout
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
        self.sis_listen_timeout = QtGui.QLineEdit()
        validator = QtGui.QIntValidator(0, 9999)
        self.sis_listen_timeout.setValidator(validator)
        vbox.addWidget(self.sis_listen_timeout)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        # noinspection PyUnresolvedReferences
        btn_apply.clicked.connect(self.apply_sis_listen_timeout)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        # - sis_auto_apply_manual_casts
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Auto apply profile:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.sis_auto_apply_manual_casts = QtGui.QComboBox()
        self.sis_auto_apply_manual_casts.addItems(["True", "False"])
        vbox.addWidget(self.sis_auto_apply_manual_casts)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        # noinspection PyUnresolvedReferences
        btn_apply.clicked.connect(self.apply_sis_auto_apply_manual_casts)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        self.main_layout.addStretch()

        self.setup_changed()  # to trigger the first data population

    def apply_sis_listen_port(self):
        logger.debug("listen SIS port")
        self.db.sis_listen_port = int(self.sis_listen_port.text())
        self.setup_changed()

    def apply_sis_listen_timeout(self):
        logger.debug("listen SIS timeout")
        self.db.sis_listen_timeout = int(self.sis_listen_timeout.text())
        self.setup_changed()

    def apply_sis_auto_apply_manual_casts(self):
        logger.debug("auto-apply cast")
        self.db.sis_auto_apply_manual_casts = self.sis_auto_apply_manual_casts.currentText()
        self.setup_changed()

    def setup_changed(self):
        """Refresh items"""
        # logger.debug("refresh input settings")

        # set the top label
        self.active_label.setText("<b>Current setup: %s [#%02d]</b>" % (self.db.setup_name, self.db.active_setup_id))

        # sis_listen_port
        self.sis_listen_port.setText("%d" % self.db.sis_listen_port)
        # sis_listen_timeout
        self.sis_listen_timeout.setText("%d" % self.db.sis_listen_timeout)

        # sis_auto_apply_manual_casts
        if self.db.sis_auto_apply_manual_casts:
            self.sis_auto_apply_manual_casts.setCurrentIndex(0)  # True
        else:
            self.sis_auto_apply_manual_casts.setCurrentIndex(1)  # False
