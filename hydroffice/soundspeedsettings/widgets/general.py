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

institution_list = [
    "NOAA Office of Coast Survey",
    "UNH CCOM/JHC"
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
        self.label = QtGui.QLabel("User-defined")
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

        # - path to projects
        hbox = QtGui.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        label = QtGui.QLabel("Path to projects:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- value
        self.projects_folder = QtGui.QLineEdit()
        hbox.addWidget(self.projects_folder)
        # -- button
        btn = QtGui.QPushButton("...")
        btn.setMaximumWidth(24)
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_projects_folder)
        hbox.addWidget(btn)

        # - path to outputs
        hbox = QtGui.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        label = QtGui.QLabel("Path to outputs:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- value
        self.outputs_folder = QtGui.QLineEdit()
        hbox.addWidget(self.outputs_folder)
        # -- button
        btn = QtGui.QPushButton("...")
        btn.setMaximumWidth(24)
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_outputs_folder)
        hbox.addWidget(btn)

        # - path to woa09
        hbox = QtGui.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        label = QtGui.QLabel("Path to WOA09:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- value
        self.woa09_folder = QtGui.QLineEdit()
        hbox.addWidget(self.woa09_folder)
        # -- button
        btn = QtGui.QPushButton("...")
        btn.setMaximumWidth(24)
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_woa09_folder)
        hbox.addWidget(btn)

        # - path to woa13
        hbox = QtGui.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        label = QtGui.QLabel("Path to WOA13:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- value
        self.woa13_folder = QtGui.QLineEdit()
        hbox.addWidget(self.woa13_folder)
        # -- button
        btn = QtGui.QPushButton("...")
        btn.setMaximumWidth(24)
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_woa13_folder)
        hbox.addWidget(btn)

        # - use woa09
        hbox = QtGui.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("NOAA tools:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.noaa_tools = QtGui.QComboBox()
        self.noaa_tools.addItems(["True", "False"])
        vbox.addWidget(self.noaa_tools)
        vbox.addStretch()

        self.left_layout.addStretch()

        # RIGHT

        # - Default metadata
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        hbox.addStretch()
        self.label = QtGui.QLabel("Default metadata")
        hbox.addWidget(self.label)
        hbox.addStretch()

        # - default institution
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        label = QtGui.QLabel("Default institution:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- value
        self.default_institution = QtGui.QComboBox()
        self.default_institution.setEditable(True)
        self.default_institution.addItems(institution_list)
        rex = QtCore.QRegExp('[a-zA-Z0-9_.-\s]+')
        validator = QtGui.QRegExpValidator(rex)
        self.default_institution.setValidator(validator)
        hbox.addWidget(self.default_institution)

        # - default survey
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        label = QtGui.QLabel("Default survey:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- value
        self.default_survey = QtGui.QLineEdit()
        rex = QtCore.QRegExp('[a-zA-Z0-9_.-\s]+')
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
        rex = QtCore.QRegExp('[a-zA-Z0-9_.-\s]+')
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
        rex = QtCore.QRegExp('[a-zA-Z0-9_.-\s]+')
        validator = QtGui.QRegExpValidator(rex)
        self.default_sn.setValidator(validator)
        hbox.addWidget(self.default_sn)

        self.right_layout.addStretch()

        self.main_layout.addStretch()

        self.setup_changed()  # to trigger the first data population

        # methods
        # noinspection PyUnresolvedReferences
        self.default_institution.textChanged.connect(self.apply_default_institution)
        # noinspection PyUnresolvedReferences
        self.default_survey.textChanged.connect(self.apply_default_survey)
        # noinspection PyUnresolvedReferences
        self.default_vessel.textChanged.connect(self.apply_default_vessel)
        # noinspection PyUnresolvedReferences
        self.projects_folder.textChanged.connect(self.apply_custom_folders)
        # noinspection PyUnresolvedReferences
        self.outputs_folder.textChanged.connect(self.apply_custom_folders)
        # noinspection PyUnresolvedReferences
        self.woa09_folder.textChanged.connect(self.apply_custom_folders)
        # noinspection PyUnresolvedReferences
        self.woa13_folder.textChanged.connect(self.apply_custom_folders)
        # noinspection PyUnresolvedReferences
        self.noaa_tools.currentIndexChanged.connect(self.apply_noaa_tools)
        # noinspection PyUnresolvedReferences
        self.default_sn.textChanged.connect(self.apply_default_sn)

    def apply_default_institution(self):
        # logger.debug("apply default institution")
        self.db.default_institution = self.default_institution.currentText()
        self.setup_changed()
        self.main_win.reload_settings()

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

    def apply_custom_folders(self):
        # logger.debug("apply default vessel")
        self.db.custom_projects_folder = self.projects_folder.text()
        self.db.custom_outputs_folder = self.outputs_folder.text()
        self.db.custom_woa09_folder = self.woa09_folder.text()
        self.db.custom_woa13_folder = self.woa13_folder.text()
        self.setup_changed()
        self.main_win.reload_settings()

    def on_projects_folder(self):
        logger.debug("user wants to set the folder for projects")

        # ask the file path to the user
        settings = QtCore.QSettings()
        selection = QtGui.QFileDialog.getExistingDirectory(self, "Path to projects",
                                                           settings.value("export_folder"))
        if not selection:
            return
        logger.debug('user selection: %s' % selection)

        self.db.custom_projects_folder = selection

        self.setup_changed()
        self.main_win.reload_settings()

    def on_outputs_folder(self):
        logger.debug("user wants to set the folder for outputs")

        # ask the file path to the user
        settings = QtCore.QSettings()
        selection = QtGui.QFileDialog.getExistingDirectory(self, "Path to outputs",
                                                           settings.value("export_folder"))
        if not selection:
            return
        logger.debug('user selection: %s' % selection)

        self.db.custom_outputs_folder = selection

        self.setup_changed()
        self.main_win.reload_settings()

    def on_woa09_folder(self):
        logger.debug("user wants to set the folder for woa09")

        # ask the file path to the user
        settings = QtCore.QSettings()
        selection = QtGui.QFileDialog.getExistingDirectory(self, "Path to WOA09",
                                                           settings.value("export_folder"))
        if not selection:
            return
        logger.debug('user selection: %s' % selection)

        self.db.custom_woa09_folder = selection

        self.setup_changed()
        self.main_win.reload_settings()

    def on_woa13_folder(self):
        logger.debug("user wants to set the folder for woa13")

        # ask the file path to the user
        settings = QtCore.QSettings()
        selection = QtGui.QFileDialog.getExistingDirectory(self, "Path to WOA13",
                                                           settings.value("export_folder"))
        if not selection:
            return
        logger.debug('user selection: %s' % selection)

        self.db.custom_woa13_folder = selection

        self.setup_changed()
        self.main_win.reload_settings()

    def apply_noaa_tools(self):
        # logger.debug("apply NOAA tools: %s" % self.noaa_tools.currentText())
        self.db.noaa_tools = self.noaa_tools.currentText() == "True"
        if self.noaa_tools.currentText() == "True":
            self.db.default_institution = institution_list[0]  # NOAA OCS
        else:
            self.db.default_institution = ""
        self.setup_changed()
        self.main_win.reload_settings()

    def setup_changed(self):
        """Refresh items"""
        # logger.debug("refresh input settings")

        # set the top label
        self.active_label.setText("<b>Current setup: %s [#%02d]</b>" % (self.db.setup_name, self.db.active_setup_id))

        # current_project
        self.current_project.setText("%s" % self.db.current_project)

        # projects_folder
        self.projects_folder.setText("%s" % self.db.custom_projects_folder)

        # outputs_folder
        self.outputs_folder.setText("%s" % self.db.custom_outputs_folder)

        # woa09_folder
        self.woa09_folder.setText("%s" % self.db.custom_woa09_folder)

        # woa13_folder
        self.woa13_folder.setText("%s" % self.db.custom_woa13_folder)

        # noaa tools
        if self.db.noaa_tools:
            self.noaa_tools.setCurrentIndex(0)  # True
        else:
            self.noaa_tools.setCurrentIndex(1)  # False

        # default_institution
        self.default_institution.setEditText("%s" % self.db.default_institution)

        # default_survey
        self.default_survey.setText("%s" % self.db.default_survey)

        # default_vessel
        self.default_vessel.setEditText("%s" % self.db.default_vessel)

        # default_sn
        self.default_sn.setText("%s" % self.db.default_sn)
