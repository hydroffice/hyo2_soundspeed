from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

from PySide import QtGui, QtCore
from hydroffice.soundspeed.profile.dicts import Dicts

logger = logging.getLogger(__name__)

from .widget import AbstractWidget


class General(AbstractWidget):

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
        # -- right
        self.right_frame = QtGui.QFrame()
        self.right_layout = QtGui.QVBoxLayout()
        self.right_frame.setLayout(self.right_layout)
        hbox.addWidget(self.right_frame, stretch=1)

        # - current project
        hbox = QtGui.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Current project:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.current_project = QtGui.QLineEdit()
        rex = QtCore.QRegExp('[a-zA-Z0-9_.-]+')
        validator = QtGui.QRegExpValidator(rex)
        self.current_project.setValidator(validator)
        self.current_project.setReadOnly(True)
        vbox.addWidget(self.current_project)
        vbox.addStretch()

        self.left_layout.addStretch()

        self.main_layout.addStretch()

        self.setup_changed()  # to trigger the first data population

    def apply_sis_listen_port(self):
        logger.debug("listen SIS port")
        self.db.sis_listen_port = int(self.sis_listen_port.text())
        self.setup_changed()
        self.main_win.setup_changed()

    def setup_changed(self):
        """Refresh items"""
        # logger.debug("refresh input settings")

        # set the top label
        self.active_label.setText("<b>Current setup: %s [#%02d]</b>" % (self.db.setup_name, self.db.active_setup_id))

        # current_project
        self.current_project.setText("%s" % self.db.current_project)
