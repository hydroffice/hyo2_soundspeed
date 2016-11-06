from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

from PySide import QtGui, QtCore

logger = logging.getLogger(__name__)

from hydroffice.soundspeed.profile.dicts import Dicts
from hydroffice.soundspeedmanager.widgets.widget import AbstractWidget
from hydroffice.soundspeedmanager.dialogs.export_profiles_dialog import ExportProfilesDialog
from hydroffice.soundspeedmanager.dialogs.plot_profiles_dialog import PlotProfilesDialog
from hydroffice.soundspeedmanager.dialogs.new_project_dialog import NewProjectDialog
from hydroffice.soundspeedmanager.dialogs.load_project_dialog import LoadProjectDialog
from hydroffice.soundspeedmanager.dialogs.import_data_dialog import ImportDataDialog


class Database(AbstractWidget):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win, lib):
        AbstractWidget.__init__(self, main_win=main_win, lib=lib)

        lbl_width = 60

        # create the overall layout
        self.main_layout = QtGui.QVBoxLayout()
        self.frame.setLayout(self.main_layout)

        # - active setup
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        hbox.addStretch()
        self.active_label = QtGui.QLabel()
        hbox.addWidget(self.active_label)
        hbox.addStretch()

        # - list of setups
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)

        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Profiles:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()

        # -- list
        self.ssp_list = QtGui.QTableWidget()
        self.ssp_list.setFocus()
        self.ssp_list.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.ssp_list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.ssp_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # noinspection PyUnresolvedReferences
        self.ssp_list.customContextMenuRequested.connect(self.make_context_menu)
        hbox.addWidget(self.ssp_list)

        # - RIGHT COLUMN
        right_vbox = QtGui.QVBoxLayout()
        hbox.addLayout(right_vbox)
        # -- manage button box
        self.manage_btn_box = QtGui.QDialogButtonBox(QtCore.Qt.Vertical)
        right_vbox.addWidget(self.manage_btn_box)
        right_vbox.addStretch()

        # --- new project
        self.btn_new_project = QtGui.QPushButton("New project")
        # noinspection PyUnresolvedReferences
        self.btn_new_project.clicked.connect(self.new_project)
        self.btn_new_project.setToolTip("Create a new project")
        self.manage_btn_box.addButton(self.btn_new_project, QtGui.QDialogButtonBox.ActionRole)
        # --- load project
        self.btn_load_project = QtGui.QPushButton("Load project")
        # noinspection PyUnresolvedReferences
        self.btn_load_project.clicked.connect(self.load_project)
        self.btn_load_project.setToolTip("Load a project")
        self.manage_btn_box.addButton(self.btn_load_project, QtGui.QDialogButtonBox.ActionRole)
        # --- import profiles
        self.btn_import_data = QtGui.QPushButton("Import data")
        # noinspection PyUnresolvedReferences
        self.btn_import_data.clicked.connect(self.import_data)
        self.btn_import_data.setToolTip("Import data from another project")
        self.manage_btn_box.addButton(self.btn_import_data, QtGui.QDialogButtonBox.ActionRole)
        # --- project folder
        self.btn_project_folder = QtGui.QPushButton("Project folder")
        # noinspection PyUnresolvedReferences
        self.btn_project_folder.clicked.connect(self.project_folder)
        self.btn_project_folder.setToolTip("Open the project folder")
        self.manage_btn_box.addButton(self.btn_project_folder, QtGui.QDialogButtonBox.ActionRole)

        self.main_layout.addSpacing(8)

        # - bottom
        bottom_vbox = QtGui.QVBoxLayout()
        right_vbox.addLayout(bottom_vbox)

        # -- products button box
        self.product_btn_box = QtGui.QDialogButtonBox(QtCore.Qt.Vertical)
        bottom_vbox.addStretch()
        bottom_vbox.addWidget(self.product_btn_box)
        # --- plot profiles
        btn = QtGui.QPushButton("Plot profiles")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.plot_profiles)
        btn.setToolTip("Create plots with profiles")
        self.product_btn_box.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
        # --- export profiles
        btn = QtGui.QPushButton("Export info")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.export_profiles)
        btn.setToolTip("Export profile locations and metadata")
        self.product_btn_box.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
        # --- output folder
        btn = QtGui.QPushButton("Output folder")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.output_folder)
        btn.setToolTip("Open the output folder")
        self.product_btn_box.addButton(btn, QtGui.QDialogButtonBox.ActionRole)

        # self.main_layout.addStretch()

        self.update_table()

    def make_context_menu(self, pos):
        """Make a context menu to deal with profile specific actions"""

        load_act = QtGui.QAction("Load", self, statusTip="Load a profile", triggered=self.load_profile)
        delete_act = QtGui.QAction("Delete", self, statusTip="Delete a profile", triggered=self.delete_profile)

        menu = QtGui.QMenu(parent=self)
        menu.addAction(load_act)
        menu.addAction(delete_act)
        menu.exec_(self.ssp_list.mapToGlobal(pos))

    def new_project(self):
        logger.debug("user want to create a new project")

        dlg = NewProjectDialog(lib=self.lib, main_win=self.main_win, parent=self)
        success = dlg.exec_()

        if success:
            self.update_table()

    def load_project(self):
        logger.debug("user want to load a project")

        dlg = LoadProjectDialog(lib=self.lib, main_win=self.main_win, parent=self)
        dlg.exec_()

        self.update_table()

    def import_data(self):
        logger.debug("user want to import data from another project")

        dlg = ImportDataDialog(lib=self.lib, main_win=self.main_win, parent=self)
        dlg.exec_()

        self.update_table()

    def load_profile(self):
        logger.debug("user want to load a profile")

        # check if any selection
        sel = self.ssp_list.selectedItems()
        if len(sel) == 0:
            # noinspection PyCallByClass
            QtGui.QMessageBox.information(self, "Database", "You need to select a profile before loading it!")
            return

        pk = int(sel[0].text())
        success = self.lib.load_profile(pk)
        if not success:
            msg = "Unable to load profile!"
            # noinspection PyCallByClass
            QtGui.QMessageBox.warning(self, "Database", msg, QtGui.QMessageBox.Ok)
            return

        if self.lib.has_ssp():
            self.main_win.data_imported()
            self.main_win.tabs.setCurrentIndex(0)

    def delete_profile(self):
        logger.debug("user want to delete a profile")

        # check if any selection
        sel = self.ssp_list.selectedItems()
        if len(sel) == 0:
            # noinspection PyCallByClass
            QtGui.QMessageBox.information(self, "Database", "You need to select a profile before deleting it!")
            return

        # ask if the user want to delete it
        pk = int(sel[0].text())
        msg = "Do you really want to delete profile #%02d?" % pk
        # noinspection PyCallByClass
        ret = QtGui.QMessageBox.warning(self, "Database", msg, QtGui.QMessageBox.Ok | QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.No:
            return

        success = self.lib.delete_db_profile(pk)
        if success:
            self.main_win.data_removed()
        else:
            # noinspection PyCallByClass
            QtGui.QMessageBox.critical(self, "Database", "Unable to remove the selected profile!")

    def project_folder(self):
        logger.debug("user want to open the project folder")
        self.lib.open_projects_folder()

    def output_folder(self):
        logger.debug("user want to open the output folder")
        self.lib.open_outputs_folder()

    def export_profiles(self):
        logger.debug("user want to export profiles")
        dlg = ExportProfilesDialog(lib=self.lib, main_win=self.main_win, parent=self)
        dlg.exec_()

    def plot_profiles(self):
        logger.debug("user want to plot profiles")

        dlg = PlotProfilesDialog(lib=self.lib, main_win=self.main_win, parent=self)
        success = dlg.exec_()

        if success and not dlg.only_saved:
            self.lib.raise_plot_window()

    def update_table(self):
        # set the top label
        self.active_label.setText("<b>Current project: %s</b>" % self.lib.current_project)

        lst = self.lib.db_list_profiles()

        # prepare the table
        self.ssp_list.clear()
        self.ssp_list.setColumnCount(17)
        self.ssp_list.setHorizontalHeaderLabels(['id', 'time', 'location',
                                                 'sensor', 'probe', 'original path',
                                                 'survey', 'vessel', 'sn',
                                                 'processing time', 'processing info',
                                                 'pressure uom', 'depth uom', 'speed uom',
                                                 'temperature uom', 'conductivity uom', 'salinity uom',
                                                 ])

        # populate the table
        self.ssp_list.setRowCount(len(lst))

        for i, ssp in enumerate(lst):
            for j, field in enumerate(ssp):
                if j == 3:
                    field = '%s' % Dicts.first_match(Dicts.sensor_types, int(field))
                    # logger.debug('%s' % Dicts.first_match(Dicts.sensor_types, int(field)))
                elif j == 4:
                    field = '%s' % Dicts.first_match(Dicts.probe_types, int(field))
                    # logger.debug('%s' % Dicts.first_match(Dicts.probe_types, int(field)))
                item = QtGui.QTableWidgetItem("%s" % field)

                item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.ssp_list.setItem(i, j, item)

        self.ssp_list.resizeColumnsToContents()

    def data_stored(self):
        self.update_table()

    def data_removed(self):
        self.update_table()

    def server_started(self):
        self.setDisabled(True)

    def server_stopped(self):
        self.setEnabled(True)
