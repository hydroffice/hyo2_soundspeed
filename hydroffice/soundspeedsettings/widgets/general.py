from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

from PySide import QtGui, QtCore
from hydroffice.soundspeed.profile.dicts import Dicts

logger = logging.getLogger(__name__)

from .widget import AbstractWidget

vessel_list = [
    "RA Rainier (ship)",
    "R3 Rainier - Launch 2803",
    "R4 Rainier - Launch 2801",
    "R5 Rainier - Launch 2802",
    "R6 Rainier - Launch 2804",
    "TJ Thomas Jefferson (ship)",
    "T1 Thomas Jefferson - Launch 3101",
    "T2 Thomas Jefferson - Launch 3102",
    "BH Bay Hydro II",
    "N1 NRT-1  Gulf",
    "N2 NRT-2  Atlantic",
    "N3 NRT-3  Pacific",
    "N4 NRT-4  Great Lakes",
    "N5 NRT-5  New York",
    "N6 NRT-6  San Francisco",
    "N7 NRT-7  Middle Atlantic",
    "FH Ferdinand R. Hassler (Ship)",
    "FA Fairweather (Ship)",
    "F5 Fairweather - Launch 2805",
    "F6 Fairweather - Launch 2806",
    "F7 Fairweather - Launch 2807",
    "F8 Fairwaether - Launch 2808",
    "AR MCArthur",
    "NF Nancy Foster",
    "HI Hi'Ialakai",
    "GM Gloria Michelle",
    "EX Okeanos Explorer",
    "ZZ Other"
]


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

        # LEFT

        # - Project
        hbox = QtGui.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        hbox.addStretch()
        self.label = QtGui.QLabel("Project")
        hbox.addWidget(self.label)
        hbox.addStretch()

        # - current project
        hbox = QtGui.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        label = QtGui.QLabel("Current project:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- value
        self.current_project = QtGui.QLineEdit()
        rex = QtCore.QRegExp('[a-zA-Z0-9_.-]+')
        validator = QtGui.QRegExpValidator(rex)
        self.current_project.setValidator(validator)
        self.current_project.setReadOnly(True)
        hbox.addWidget(self.current_project)

        self.left_layout.addStretch()

        # RIGHT

        # - Default metadata
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        hbox.addStretch()
        self.label = QtGui.QLabel("Default metadata")
        hbox.addWidget(self.label)
        hbox.addStretch()

        # - default survey
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        label = QtGui.QLabel("Default survey:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- value
        self.default_survey = QtGui.QLineEdit()
        rex = QtCore.QRegExp('[a-zA-Z0-9_.-]+')
        validator = QtGui.QRegExpValidator(rex)
        self.default_survey.setValidator(validator)
        hbox.addWidget(self.default_survey)

        # - default vessel
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        label = QtGui.QLabel("Default vessel:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- value
        self.default_vessel = QtGui.QComboBox()
        self.default_vessel.setEditable(True)
        self.default_vessel.addItems(vessel_list)
        rex = QtCore.QRegExp('[a-zA-Z0-9_.-]+')
        validator = QtGui.QRegExpValidator(rex)
        self.default_vessel.setValidator(validator)
        hbox.addWidget(self.default_vessel)

        # - default sn
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        label = QtGui.QLabel("Default S/N:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- value
        self.default_sn = QtGui.QLineEdit()
        rex = QtCore.QRegExp('[a-zA-Z0-9_.-]+')
        validator = QtGui.QRegExpValidator(rex)
        self.default_sn.setValidator(validator)
        hbox.addWidget(self.default_sn)

        self.right_layout.addStretch()

        self.main_layout.addStretch()

        self.setup_changed()  # to trigger the first data population

        # methods
        # noinspection PyUnresolvedReferences
        self.default_survey.textChanged.connect(self.apply_default_survey)
        # noinspection PyUnresolvedReferences
        self.default_vessel.textChanged.connect(self.apply_default_vessel)
        # noinspection PyUnresolvedReferences
        self.default_sn.textChanged.connect(self.apply_default_sn)

    def apply_default_survey(self):
        # logger.debug("apply default survey")
        self.db.default_survey = self.default_survey.text()
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_default_vessel(self):
        # logger.debug("apply default vessel")
        self.db.default_vessel = self.default_vessel.currentText()
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_default_sn(self):
        # logger.debug("apply default sn")
        self.db.default_sn = self.default_sn.text()
        self.setup_changed()
        self.main_win.reload_settings()

    def setup_changed(self):
        """Refresh items"""
        # logger.debug("refresh input settings")

        # set the top label
        self.active_label.setText("<b>Current setup: %s [#%02d]</b>" % (self.db.setup_name, self.db.active_setup_id))

        # current_project
        self.current_project.setText("%s" % self.db.current_project)

        # default_survey
        self.default_survey.setText("%s" % self.db.default_survey)

        # default_vessel
        self.default_vessel.setEditText("%s" % self.db.default_vessel)

        # default_sn
        self.default_sn.setText("%s" % self.db.default_sn)
