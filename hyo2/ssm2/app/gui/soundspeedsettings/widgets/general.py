import logging
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6 import QtCore, QtGui, QtWidgets

from hyo2.ssm2.app.gui.soundspeedsettings.widgets.widget import AbstractWidget
from hyo2.ssm2.lib.base.setup_sql import vessel_list, institution_list

if TYPE_CHECKING:
    from hyo2.ssm2.app.gui.soundspeedsettings.mainwin import MainWin
    from hyo2.ssm2.lib.base.setup_db import SetupDb

logger = logging.getLogger(__name__)


class General(AbstractWidget):

    def __init__(self, main_win: "MainWin", db: "SetupDb") -> None:
        AbstractWidget.__init__(self, main_win=main_win, db=db)

        lbl_width = 120

        # outline ui
        self.main_layout = QtWidgets.QVBoxLayout()
        self.frame.setLayout(self.main_layout)

        # - active setup
        hbox = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        hbox.addStretch()
        self.active_label = QtWidgets.QLabel()
        hbox.addWidget(self.active_label)
        hbox.addStretch()

        # - left and right sub-frames
        hbox = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- left
        self.left_frame = QtWidgets.QFrame()
        self.left_layout = QtWidgets.QVBoxLayout()
        self.left_frame.setLayout(self.left_layout)
        hbox.addWidget(self.left_frame, stretch=1)
        # -- right
        self.right_frame = QtWidgets.QFrame()
        self.right_layout = QtWidgets.QVBoxLayout()
        self.right_frame.setLayout(self.right_layout)
        hbox.addWidget(self.right_frame, stretch=1)

        # LEFT

        # - Project
        hbox = QtWidgets.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        hbox.addStretch()
        self.label = QtWidgets.QLabel("User-defined")
        hbox.addWidget(self.label)
        hbox.addStretch()

        # - current project
        hbox = QtWidgets.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        label = QtWidgets.QLabel("Current project:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- value
        self.current_project = QtWidgets.QLineEdit()
        rex = QtCore.QRegularExpression('[a-zA-Z0-9_.-]+')
        if not rex.isValid():
            logger.warning(rex.errorString())
        validator = QtGui.QRegularExpressionValidator(rex)
        self.current_project.setValidator(validator)
        self.current_project.setReadOnly(True)
        self.current_project.setStyleSheet("QLineEdit { color: #666666 }")
        self.current_project.setToolTip("Go to the 'Database' tab, "
                                        "then 'Rename Project' button if you want to change the current project")
        hbox.addWidget(self.current_project)

        # - path to projects
        hbox = QtWidgets.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        label = QtWidgets.QLabel("Path to projects:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- value
        self.projects_folder = QtWidgets.QLineEdit()
        self.projects_folder.setReadOnly(True)
        hbox.addWidget(self.projects_folder)
        # -- button
        btn = QtWidgets.QPushButton("...")
        btn.setMaximumWidth(24)
        btn.clicked.connect(self.on_projects_folder)
        hbox.addWidget(btn)

        # - path to outputs
        hbox = QtWidgets.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        label = QtWidgets.QLabel("Path to outputs:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- value
        self.outputs_folder = QtWidgets.QLineEdit()
        self.outputs_folder.setReadOnly(True)
        hbox.addWidget(self.outputs_folder)
        # -- button
        btn = QtWidgets.QPushButton("...")
        btn.setMaximumWidth(24)
        btn.clicked.connect(self.on_outputs_folder)
        hbox.addWidget(btn)

        # - path to woa09
        hbox = QtWidgets.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        label = QtWidgets.QLabel("Path to WOA09:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- value
        self.woa09_folder = QtWidgets.QLineEdit()
        self.woa09_folder.setReadOnly(True)
        hbox.addWidget(self.woa09_folder)
        # -- button
        btn = QtWidgets.QPushButton("...")
        btn.setMaximumWidth(24)
        btn.clicked.connect(self.on_woa09_folder)
        hbox.addWidget(btn)

        # - path to woa13
        hbox = QtWidgets.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        label = QtWidgets.QLabel("Path to WOA13:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- value
        self.woa13_folder = QtWidgets.QLineEdit()
        self.woa13_folder.setReadOnly(True)
        hbox.addWidget(self.woa13_folder)
        # -- button
        btn = QtWidgets.QPushButton("...")
        btn.setMaximumWidth(24)
        btn.clicked.connect(self.on_woa13_folder)
        hbox.addWidget(btn)

        # - path to woa18
        hbox = QtWidgets.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        label = QtWidgets.QLabel("Path to WOA18:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- value
        self.woa18_folder = QtWidgets.QLineEdit()
        self.woa18_folder.setReadOnly(True)
        hbox.addWidget(self.woa18_folder)
        # -- button
        btn = QtWidgets.QPushButton("...")
        btn.setMaximumWidth(24)
        btn.clicked.connect(self.on_woa18_folder)
        hbox.addWidget(btn)

        # - path to woa23
        hbox = QtWidgets.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        label = QtWidgets.QLabel("Path to WOA23:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- value
        self.woa23_folder = QtWidgets.QLineEdit()
        self.woa23_folder.setReadOnly(True)
        hbox.addWidget(self.woa23_folder)
        # -- button
        btn = QtWidgets.QPushButton("...")
        btn.setMaximumWidth(24)
        btn.clicked.connect(self.on_woa23_folder)
        hbox.addWidget(btn)

        # - NOAA Tools
        hbox = QtWidgets.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtWidgets.QLabel("NOAA tools:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.noaa_tools = QtWidgets.QComboBox()
        self.noaa_tools.addItems(["True", "False"])
        vbox.addWidget(self.noaa_tools)
        vbox.addStretch()

        self.left_layout.addStretch()

        # RIGHT

        # - Default metadata
        hbox = QtWidgets.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        hbox.addStretch()
        self.label = QtWidgets.QLabel("Default metadata")
        hbox.addWidget(self.label)
        hbox.addStretch()

        # - default institution
        hbox = QtWidgets.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        label = QtWidgets.QLabel("Default institution:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- value
        self.default_institution = QtWidgets.QComboBox()
        self.default_institution.setEditable(True)
        self.default_institution.addItems(institution_list)
        rex = QtCore.QRegularExpression(r'[a-zA-Z0-9_.\-\s]+')
        if not rex.isValid():
            logger.warning(rex.errorString())
        validator = QtGui.QRegularExpressionValidator(rex)
        self.default_institution.setValidator(validator)
        hbox.addWidget(self.default_institution)

        # - default survey
        hbox = QtWidgets.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        label = QtWidgets.QLabel("Default survey(*):")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- value
        self.default_survey = QtWidgets.QLineEdit()
        rex = QtCore.QRegularExpression(r'[a-zA-Z0-9_.\-\s]+')
        if not rex.isValid():
            logger.warning(rex.errorString())
        validator = QtGui.QRegularExpressionValidator(rex)
        self.default_survey.setValidator(validator)
        hbox.addWidget(self.default_survey)

        # - default vessel
        hbox = QtWidgets.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        label = QtWidgets.QLabel("Default vessel:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- value
        self.default_vessel = QtWidgets.QComboBox()
        self.default_vessel.setEditable(True)
        self.default_vessel.addItems(vessel_list)
        rex = QtCore.QRegularExpression(r'[a-zA-Z0-9_.\-\s]+')
        if not rex.isValid():
            logger.warning(rex.errorString())
        validator = QtGui.QRegularExpressionValidator(rex)
        self.default_vessel.setValidator(validator)
        hbox.addWidget(self.default_vessel)

        # - option weighted harmonic mean sound speed
        hbox = QtWidgets.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        label = QtWidgets.QLabel("Average sound speed:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # - value
        self.average_sound_speed = QtWidgets.QComboBox()
        self.average_sound_speed.addItems(["True", "False"])
        hbox.addWidget(self.average_sound_speed)        
        
        # - auto_apply_default_metadata
        hbox = QtWidgets.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        label = QtWidgets.QLabel("Auto apply default:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- label
        self.auto_apply_default_metadata = QtWidgets.QComboBox()
        self.auto_apply_default_metadata.addItems(["True", "False"])
        hbox.addWidget(self.auto_apply_default_metadata)

        hbox = QtWidgets.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        label = QtWidgets.QLabel("")
        label.setFixedHeight(22)
        hbox.addWidget(label)

        hbox = QtWidgets.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        label = QtWidgets.QLabel("<i>* If yellow, press 'return' to apply changes.</i>")
        label.setFixedHeight(22)
        label.setStyleSheet("QLabel { color : #aaaaaa; }")
        hbox.addWidget(label)

        self.right_layout.addStretch()

        self.main_layout.addStretch()

        self.setup_changed()  # to trigger the first data population

        # methods
        self.default_institution.editTextChanged.connect(self.apply_default_institution)
        self.default_survey.textChanged.connect(self.modified_default_survey)
        self.default_survey.returnPressed.connect(self.apply_default_survey)
        self.default_vessel.editTextChanged.connect(self.apply_default_vessel)
        self.default_vessel.currentIndexChanged.connect(self.apply_default_vessel)
        self.projects_folder.textChanged.connect(self.apply_custom_folders)
        self.outputs_folder.textChanged.connect(self.apply_custom_folders)
        self.woa09_folder.textChanged.connect(self.apply_custom_folders)
        self.woa13_folder.textChanged.connect(self.apply_custom_folders)
        self.woa18_folder.textChanged.connect(self.apply_custom_folders)
        self.woa23_folder.textChanged.connect(self.apply_custom_folders)
        # noinspection PyUnresolvedReferences
        self.noaa_tools.currentIndexChanged.connect(self.apply_noaa_tools)
        # noinspection PyUnresolvedReferences
        self.average_sound_speed.currentIndexChanged.connect(self.apply_average_sound_speed)
        self.auto_apply_default_metadata.currentIndexChanged.connect(self.apply_auto_apply_default_metadata)

    def apply_default_institution(self):
        # logger.debug("apply default institution")
        self.db.default_institution = self.default_institution.currentText()
        self.setup_changed()
        self.main_win.reload_settings()

    def modified_default_survey(self):
        self.default_survey.setStyleSheet("background-color: rgba(255,255,153, 255);")

    def apply_default_survey(self):
        # logger.debug("apply default survey")
        self.db.default_survey = self.default_survey.text()
        self.setup_changed()
        self.main_win.reload_settings()
        self.default_survey.setStyleSheet("background-color: rgba(255,255,255, 255);")

    def apply_default_vessel(self):
        # logger.debug("apply default vessel")
        self.db.default_vessel = self.default_vessel.currentText()
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_custom_folders(self):
        # logger.debug("apply default vessel")
        self.db.custom_projects_folder = self.projects_folder.text()
        self.db.custom_outputs_folder = self.outputs_folder.text()
        self.db.custom_woa09_folder = self.woa09_folder.text()
        self.db.custom_woa13_folder = self.woa13_folder.text()
        self.db.custom_woa18_folder = self.woa18_folder.text()
        self.db.custom_woa23_folder = self.woa23_folder.text()
        self.setup_changed()
        self.main_win.reload_settings()

    def on_projects_folder(self):
        logger.debug("user wants to set the folder for projects")

        # ask the file path to the user
        settings = QtCore.QSettings()
        # noinspection PyCallByClass
        selection = QtWidgets.QFileDialog.getExistingDirectory(self, "Path to projects",
                                                               str(settings.value("export_folder")))
        if not selection:
            return
        logger.debug('user selection: %s' % selection)

        self.db.custom_projects_folder = str(Path(selection))

        self.setup_changed()
        self.main_win.reload_settings()

    def on_outputs_folder(self):
        logger.debug("user wants to set the folder for outputs")

        # ask the file path to the user
        settings = QtCore.QSettings()
        # noinspection PyCallByClass
        selection = QtWidgets.QFileDialog.getExistingDirectory(self, "Path to outputs",
                                                               str(settings.value("export_folder")))
        if not selection:
            return
        logger.debug('user selection: %s' % selection)

        self.db.custom_outputs_folder = str(Path(selection))

        self.setup_changed()
        self.main_win.reload_settings()

    def on_woa09_folder(self):
        logger.debug("user wants to set the folder for woa09")

        # ask the file path to the user
        settings = QtCore.QSettings()
        # noinspection PyCallByClass
        selection = QtWidgets.QFileDialog.getExistingDirectory(self, "Path to WOA09",
                                                               str(settings.value("export_folder")))
        if not selection:
            msg = "Do you want to just clear the folder path?"
            # noinspection PyCallByClass
            ret = QtWidgets.QMessageBox.information(
                self, "WOA09 Folder", msg,
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            if ret == QtWidgets.QMessageBox.StandardButton.No:
                return
            selection = ""
        logger.debug('user selection: %s' % selection)

        self.db.custom_woa09_folder = str(Path(selection))

        self.setup_changed()
        self.main_win.reload_settings()

        msg = "Restart the application to apply changes!"
        # noinspection PyCallByClass
        QtWidgets.QMessageBox.information(self, "WOA09 Folder", msg, QtWidgets.QMessageBox.StandardButton.Ok)

    def on_woa13_folder(self):
        logger.debug("user wants to set the folder for woa13")

        # ask the file path to the user
        settings = QtCore.QSettings()
        # noinspection PyCallByClass
        selection = QtWidgets.QFileDialog.getExistingDirectory(self, "Path to WOA13",
                                                               str(settings.value("export_folder")))
        if not selection:
            msg = "Do you want to just clear the folder path?"
            # noinspection PyCallByClass
            ret = QtWidgets.QMessageBox.information(
                self, "WOA13 Folder", msg,
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            if ret == QtWidgets.QMessageBox.StandardButton.No:
                return
            selection = ""
        logger.debug('user selection: %s' % selection)

        self.db.custom_woa13_folder = str(Path(selection))

        self.setup_changed()
        self.main_win.reload_settings()

        msg = "Restart the application to apply changes!"
        # noinspection PyCallByClass
        QtWidgets.QMessageBox.information(self, "WOA13 Folder", msg, QtWidgets.QMessageBox.StandardButton.Ok)

    def on_woa18_folder(self):
        logger.debug("user wants to set the folder for woa18")

        # ask the file path to the user
        settings = QtCore.QSettings()
        # noinspection PyCallByClass
        selection = QtWidgets.QFileDialog.getExistingDirectory(self, "Path to WOA18",
                                                               str(settings.value("export_folder")))
        if not selection:
            msg = "Do you want to just clear the folder path?"
            # noinspection PyCallByClass
            ret = QtWidgets.QMessageBox.information(
                self, "WOA18 Folder", msg,
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            if ret == QtWidgets.QMessageBox.StandardButton.No:
                return
            selection = ""
        logger.debug('user selection: %s' % selection)

        self.db.custom_woa18_folder = str(Path(selection))

        self.setup_changed()
        self.main_win.reload_settings()

        msg = "Restart the application to apply changes!"
        # noinspection PyCallByClass
        QtWidgets.QMessageBox.information(self, "WOA18 Folder", msg, QtWidgets.QMessageBox.StandardButton.Ok)

    def on_woa23_folder(self):
        logger.debug("user wants to set the folder for woa23")

        # ask the file path to the user
        settings = QtCore.QSettings()
        # noinspection PyCallByClass
        selection = QtWidgets.QFileDialog.getExistingDirectory(self, "Path to WOA23",
                                                               str(settings.value("export_folder")))
        if not selection:
            msg = "Do you want to just clear the folder path?"
            # noinspection PyCallByClass
            ret = QtWidgets.QMessageBox.information(
                self, "WOA23 Folder", msg,
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            if ret == QtWidgets.QMessageBox.StandardButton.No:
                return
            selection = ""
        logger.debug('user selection: %s' % selection)

        self.db.custom_woa23_folder = str(Path(selection))

        self.setup_changed()
        self.main_win.reload_settings()

        msg = "Restart the application to apply changes!"
        # noinspection PyCallByClass
        QtWidgets.QMessageBox.information(self, "WOA23 Folder", msg, QtWidgets.QMessageBox.StandardButton.Ok)

    def apply_noaa_tools(self):
        # logger.debug("apply NOAA tools: %s" % self.noaa_tools.currentText())
        self.db.noaa_tools = self.noaa_tools.currentText() == "True"
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_average_sound_speed(self):
        logger.debug("apply average sound speed: %s" % self.average_sound_speed.currentText())
        self.db.average_sound_speed = self.average_sound_speed.currentText() == "True"
        self.setup_changed()
        self.main_win.reload_settings()
        
    def apply_auto_apply_default_metadata(self):
        # logger.debug("auto_apply_default_metadata: %s" % self.auto_apply_default_metadata.currentText())
        self.db.auto_apply_default_metadata = self.auto_apply_default_metadata.currentText() == "True"
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
        self.projects_folder.setText("%s" % Path(self.db.custom_projects_folder))

        # outputs_folder
        self.outputs_folder.setText("%s" % Path(self.db.custom_outputs_folder))

        # woa09_folder
        self.woa09_folder.setText("%s" % Path(self.db.custom_woa09_folder))

        # woa13_folder
        self.woa13_folder.setText("%s" % Path(self.db.custom_woa13_folder))

        # woa18_folder
        self.woa18_folder.setText("%s" % Path(self.db.custom_woa18_folder))

        # woa23_folder
        self.woa23_folder.setText("%s" % Path(self.db.custom_woa23_folder))

        # noaa tools and default_vessel
        if self.db.noaa_tools:
            self.noaa_tools.setCurrentIndex(0)  # True
        else:
            self.noaa_tools.setCurrentIndex(1)  # False

        self.default_vessel.setEditText("%s" % self.db.default_vessel)

        # default_institution
        self.default_institution.setEditText("%s" % self.db.default_institution)

        # default_survey
        self.default_survey.setText("%s" % self.db.default_survey)  

        # average sound speed
        if self.db.average_sound_speed:
            self.average_sound_speed.setCurrentIndex(0)  # True
        else:
            self.average_sound_speed.setCurrentIndex(1)  # False
        
        # auto_apply_default_metadata
        if self.db.auto_apply_default_metadata:
            self.auto_apply_default_metadata.setCurrentIndex(0)  # True
        else:
            self.auto_apply_default_metadata.setCurrentIndex(1)  # False
