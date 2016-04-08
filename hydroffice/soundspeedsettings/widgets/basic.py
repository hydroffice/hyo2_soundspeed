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

        self.main_layout.addStretch()

        self.setup_changed()  # to trigger the first data population

    def apply_profile_direction(self):
        logger.debug("apply profile direction")
        self.db.ssp_up_or_down = self.profile_direction.currentText()
        self.setup_changed()

    def setup_changed(self):
        """Refresh items"""
        logger.debug("refresh basic")

        # profile direction
        dir_str = self.db.ssp_up_or_down
        dir_idx = Dicts.ssp_directions[dir_str]
        self.profile_direction.setCurrentIndex(dir_idx)
