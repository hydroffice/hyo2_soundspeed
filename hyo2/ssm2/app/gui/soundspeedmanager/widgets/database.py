import logging
import os
from typing import TYPE_CHECKING

from PySide6 import QtCore, QtGui, QtWidgets

from hyo2.ssm2.app.gui.soundspeedmanager.dialogs.common_metadata_dialog import CommonMetadataDialog
from hyo2.ssm2.app.gui.soundspeedmanager.dialogs.export_multi_profile_dialog import ExportMultiProfileDialog
from hyo2.ssm2.app.gui.soundspeedmanager.dialogs.export_profile_metadata_dialog import ExportProfileMetadataDialog
from hyo2.ssm2.app.gui.soundspeedmanager.dialogs.export_single_profile_dialog import ExportSingleProfileDialog
from hyo2.ssm2.app.gui.soundspeedmanager.dialogs.import_data_dialog import ImportDataDialog
from hyo2.ssm2.app.gui.soundspeedmanager.dialogs.import_multi_profile_dialog import ImportMultiProfileDialog
from hyo2.ssm2.app.gui.soundspeedmanager.dialogs.metadata_dialog import MetadataDialog
from hyo2.ssm2.app.gui.soundspeedmanager.dialogs.plot_multi_profile_dialog import PlotMultiProfileDialog
from hyo2.ssm2.app.gui.soundspeedmanager.dialogs.plot_profiles_dialog import PlotProfilesDialog
from hyo2.ssm2.app.gui.soundspeedmanager.dialogs.project_new_dialog import ProjectNewDialog
from hyo2.ssm2.app.gui.soundspeedmanager.dialogs.project_rename_dialog import ProjectRenameDialog
from hyo2.ssm2.app.gui.soundspeedmanager.dialogs.project_switch_dialog import ProjectSwitchDialog
from hyo2.ssm2.app.gui.soundspeedmanager.dialogs.text_editor_dialog import TextEditorDialog
from hyo2.ssm2.app.gui.soundspeedmanager.widgets.widget import AbstractWidget
from hyo2.ssm2.lib.profile.dicts import Dicts

if TYPE_CHECKING:
    from hyo2.ssm2.app.gui.soundspeedmanager.mainwin import MainWin
    from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary

logger = logging.getLogger(__name__)


class Database(AbstractWidget):
    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win: 'MainWin', lib: 'SoundSpeedLibrary') -> None:
        AbstractWidget.__init__(self, main_win=main_win, lib=lib)

        lbl_width = 60

        # create the overall layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.frame.setLayout(self.main_layout)

        # - active setup
        hbox = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        hbox.addStretch()
        self.active_label = QtWidgets.QLabel()
        hbox.addWidget(self.active_label)
        hbox.addStretch()

        # - list of setups
        hbox = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(hbox)

        # -- label
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtWidgets.QLabel("Profiles:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()

        # -- list
        self.ssp_list = QtWidgets.QTableWidget()
        self.ssp_list.setSortingEnabled(True)
        self.ssp_list.setFocus()
        self.ssp_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.ssp_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.ssp_list.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.ssp_list.customContextMenuRequested.connect(self.make_context_menu)
        self.ssp_list.itemDoubleClicked.connect(self.load_profile)
        hbox.addWidget(self.ssp_list)

        # - RIGHT COLUMN
        right_vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(right_vbox)

        # -- project box
        self.project_box = QtWidgets.QGroupBox("Project")
        right_vbox.addWidget(self.project_box)
        # --- manage button box
        project_vbox = QtWidgets.QVBoxLayout()
        self.project_box.setLayout(project_vbox)
        self.manage_btn_box = QtWidgets.QDialogButtonBox(QtCore.Qt.Orientation.Vertical)
        project_vbox.addWidget(self.manage_btn_box)

        # ---- new project
        self.btn_new_project = QtWidgets.QPushButton("New project")
        self.btn_new_project.clicked.connect(self.new_project)
        self.btn_new_project.setToolTip("Create a new project")
        self.manage_btn_box.addButton(self.btn_new_project, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
        self.new_project_act = QtGui.QAction('New Project DB', self)
        self.new_project_act.setShortcut('Ctrl+N')
        self.new_project_act.triggered.connect(self.new_project)
        self.main_win.database_menu.addAction(self.new_project_act)

        # ---- rename project
        self.btn_rename_project = QtWidgets.QPushButton("Rename project")
        self.btn_rename_project.clicked.connect(self.rename_project)
        self.btn_rename_project.setToolTip("Rename the current project")
        self.manage_btn_box.addButton(self.btn_rename_project, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
        self.rename_project_act = QtGui.QAction('Rename Current Project DB', self)
        self.rename_project_act.triggered.connect(self.rename_project)
        self.main_win.database_menu.addAction(self.rename_project_act)

        # ---- load project
        self.btn_load_project = QtWidgets.QPushButton("Switch project")
        self.btn_load_project.clicked.connect(self.switch_project)
        self.btn_load_project.setToolTip("Switch to another existing project")
        self.manage_btn_box.addButton(self.btn_load_project, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
        self.load_project_act = QtGui.QAction('Switch Project DB', self)
        self.load_project_act.triggered.connect(self.switch_project)
        self.main_win.database_menu.addAction(self.load_project_act)

        # ---- import data
        self.btn_import_data = QtWidgets.QPushButton("Import data")
        self.btn_import_data.clicked.connect(self.import_data)
        self.btn_import_data.setToolTip("Import data from another project")
        self.manage_btn_box.addButton(self.btn_import_data, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
        self.import_data_act = QtGui.QAction('Import Data from Project DB', self)
        self.import_data_act.triggered.connect(self.import_data)
        self.main_win.database_menu.addAction(self.import_data_act)

        # ---- project folder
        self.btn_project_folder = QtWidgets.QPushButton("Open folder")
        self.btn_project_folder.clicked.connect(self.project_folder)
        self.btn_project_folder.setToolTip("Open projects folder")
        self.manage_btn_box.addButton(self.btn_project_folder, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
        self.project_folder_act = QtGui.QAction('Open Projects DB Folder', self)
        self.project_folder_act.triggered.connect(self.project_folder)
        self.main_win.database_menu.addAction(self.project_folder_act)

        # ---- show stats
        self.btn_show_stats = QtWidgets.QPushButton("Show stats")
        self.btn_show_stats.setCheckable(True)
        self.btn_show_stats.clicked.connect(self.update_table)
        self.btn_show_stats.setToolTip("Show stats for DB entries")
        self.manage_btn_box.addButton(self.btn_show_stats, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)

        # ---- refresh DB
        self.btn_refresh_db = QtWidgets.QPushButton("Refresh DB")
        self.btn_refresh_db.clicked.connect(self.update_table)
        self.btn_refresh_db.setToolTip("Refresh DB entries")
        self.manage_btn_box.addButton(self.btn_refresh_db, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
        self.refresh_db_act = QtGui.QAction('Refresh DB entries', self)
        self.refresh_db_act.triggered.connect(self.update_table)
        self.main_win.database_menu.addAction(self.refresh_db_act)

        right_vbox.addStretch()
        right_vbox.addStretch()

        # -- profiles box
        self.profiles_box = QtWidgets.QGroupBox("Profiles")
        right_vbox.addWidget(self.profiles_box)

        # --- manage button box
        profiles_vbox = QtWidgets.QVBoxLayout()
        self.profiles_box.setLayout(profiles_vbox)
        self.product_btn_box = QtWidgets.QDialogButtonBox(QtCore.Qt.Orientation.Vertical)
        profiles_vbox.addWidget(self.product_btn_box)

        # ---- import profiles
        btn = QtWidgets.QPushButton("Import profiles")
        btn.clicked.connect(self.import_profiles)
        btn.setToolTip("Import multiple profiles")
        self.product_btn_box.addButton(btn, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
        self.import_profiles_act = QtGui.QAction('Import Multiple Profiles', self)
        self.import_profiles_act.setShortcut('Ctrl+I')
        self.import_profiles_act.triggered.connect(self.import_profiles)
        self.main_win.database_menu.addSeparator()
        self.main_win.database_menu.addAction(self.import_profiles_act)

        # ---- export profiles
        btn = QtWidgets.QPushButton("Export profiles")
        btn.clicked.connect(self.export_profile_switch)
        btn.setToolTip("Export profile data")
        self.product_btn_box.addButton(btn, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
        self.export_profiles_act = QtGui.QAction('Export Multiple Profiles', self)
        self.export_profiles_act.setShortcut('Ctrl+X')
        self.export_profiles_act.triggered.connect(self.export_profile_switch)
        self.main_win.database_menu.addAction(self.export_profiles_act)

        # ---- plot profiles
        btn = QtWidgets.QPushButton("Make plots")
        btn.clicked.connect(self.plot_profiles)
        btn.setToolTip("Create plots with all the profiles")
        self.product_btn_box.addButton(btn, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
        self.plot_profiles_act = QtGui.QAction('Make Plots from Data', self)
        self.plot_profiles_act.triggered.connect(self.plot_profiles)
        self.main_win.database_menu.addAction(self.plot_profiles_act)

        # ---- export metadata
        btn = QtWidgets.QPushButton("Export info")
        btn.clicked.connect(self.export_profile_metadata)
        btn.setToolTip("Export profile locations and metadata")
        self.product_btn_box.addButton(btn, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
        self.export_profile_metadata_act = QtGui.QAction('Export Data Info', self)
        self.export_profile_metadata_act.triggered.connect(self.export_profile_metadata)
        self.main_win.database_menu.addAction(self.export_profile_metadata_act)

        # ---- output folder
        btn = QtWidgets.QPushButton("Output folder")
        btn.clicked.connect(self.output_folder)
        btn.setToolTip("Open the output folder")
        self.product_btn_box.addButton(btn, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
        self.output_folder_act = QtGui.QAction('Open Output Folder', self)
        self.output_folder_act.triggered.connect(self.output_folder)
        self.main_win.database_menu.addAction(self.output_folder_act)

        self.update_table()
        logger.debug("Database tab is now initialized")

    def make_context_menu(self, pos):
        """Make a context menu to deal with profile specific actions"""

        # check if any selection
        rows = self.ssp_list.selectionModel().selectedRows()
        if len(rows) == 0:
            logger.debug('Not profile selected')
            return

        menu = QtWidgets.QMenu(parent=self)
        qa_menu = QtWidgets.QMenu('Check quality', self)
        qa_menu.setIcon(QtGui.QIcon(os.path.join(self.media, 'qa.png')))

        # single selection
        if len(rows) == 1:

            map_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'map.png')), "Show map", self)
            map_act.setToolTip("Show a map with the profile location")
            map_act.triggered.connect(self.show_map_for_selected)
            menu.addAction(map_act)

            stats_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'stats.png')), "Profile stats", self)
            stats_act.setToolTip("Get some statistical info about the profile")
            stats_act.triggered.connect(self.stats_profile)
            menu.addAction(stats_act)

            metadata_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'metadata_profile.png')), "Metadata info",
                                         self)
            metadata_act.setToolTip("View/edit the profile metadata")
            metadata_act.triggered.connect(self.metadata_profile)
            menu.addAction(metadata_act)

            menu.addMenu(qa_menu)
            dqa_compare_ref_act = QtGui.QAction("DQA (with reference)", self)
            dqa_compare_ref_act.setToolTip("Assess data quality by comparison with the reference cast")
            dqa_compare_ref_act.triggered.connect(self.dqa_full_profile)
            qa_menu.addAction(dqa_compare_ref_act)

            dqa_at_surface_act = QtGui.QAction("DQA (at surface)", self)
            dqa_at_surface_act.setToolTip("DQA with surface sound speed")
            dqa_at_surface_act.triggered.connect(self.dqa_at_surface)
            qa_menu.addAction(dqa_at_surface_act)

            menu.addSeparator()

            load_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'load_profile.png')), "Load profile", self)
            load_act.setToolTip("Load a profile")
            load_act.triggered.connect(self.load_profile)
            menu.addAction(load_act)

            export_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'export_profile.png')), "Export profile",
                                       self)
            export_act.setToolTip("Export a single profile")
            export_act.triggered.connect(self.export_single_profile)
            menu.addAction(export_act)

            delete_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'delete.png')), "Delete profile", self)
            delete_act.setToolTip("Delete selected profile")
            delete_act.triggered.connect(self.delete_profile)
            menu.addAction(delete_act)

            def handle_menu_hovered(action):
                QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), action.toolTip(), menu, menu.actionGeometry(action))

            menu.hovered.connect(handle_menu_hovered)

        else:  # multiple selection

            map_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'map.png')), "Show map", self)
            map_act.setToolTip("Show a map with profiles location")
            map_act.triggered.connect(self.show_map_for_selected)
            menu.addAction(map_act)

            metadata_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'metadata_profile.png')),
                                         "Edit metadata", self)
            metadata_act.setToolTip("Edit common metadata fields for multiple profiles")
            metadata_act.triggered.connect(self.metadata_profile)
            menu.addAction(metadata_act)

            if len(rows) == 2:
                ray_tracing_comparison_act = QtGui.QAction(
                    QtGui.QIcon(os.path.join(self.media, 'raytracing_comparison.png')), "Ray-tracing comparison", self)
                ray_tracing_comparison_act.setToolTip("Compare ray-tracing using the selected pair")
                ray_tracing_comparison_act.triggered.connect(self.ray_tracing_comparison)
                menu.addAction(ray_tracing_comparison_act)

                bias_plots_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'bias_plots.png')),
                                               "Across-swath bias", self)
                bias_plots_act.setToolTip("Create depth and horizontal bias plots across the swath")
                bias_plots_act.triggered.connect(self.bias_plots)
                menu.addAction(bias_plots_act)

            menu.addMenu(qa_menu)
            if len(rows) == 2:
                dqa_compare_two_act = QtGui.QAction("DQA (among selections)", self)
                dqa_compare_two_act.setToolTip("Assess data quality by comparison between two casts")
                dqa_compare_two_act.triggered.connect(self.dqa_full_profile)
                qa_menu.addAction(dqa_compare_two_act)

            dqa_at_surface_act = QtGui.QAction("DQA (at surface)", self)
            dqa_at_surface_act.setToolTip("DQA with surface sound speed")
            dqa_at_surface_act.triggered.connect(self.dqa_at_surface)
            qa_menu.addAction(dqa_at_surface_act)

            plot_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'plot_comparison.png')),
                                     "Comparison plot", self)
            plot_act.setToolTip("Plot profiles for comparison")
            plot_act.triggered.connect(self.plot_comparison)
            menu.addAction(plot_act)

            menu.addSeparator()

            export_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'export_profile.png')), "Export profiles",
                                       self)
            export_act.setToolTip("Export multiple profiles")
            export_act.triggered.connect(self.export_multi_profile)
            menu.addAction(export_act)

            delete_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'delete.png')), "Delete profiles", self)
            delete_act.setToolTip("Delete selected profiles")
            delete_act.triggered.connect(self.delete_profile)
            menu.addAction(delete_act)

            def handle_menu_hovered(action):
                # noinspection PyArgumentList
                QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), action.toolTip(), menu, menu.actionGeometry(action))

            # noinspection PyUnresolvedReferences
            menu.hovered.connect(handle_menu_hovered)

        menu.exec(self.ssp_list.mapToGlobal(pos))

    def load_profile(self):
        logger.debug("user want to load a profile")

        # check if any selection
        rows = self.ssp_list.selectionModel().selectedRows()
        if len(rows) != 1:
            QtWidgets.QMessageBox.information(self, "Database",
                                              "You need to select a single profile before loading it!")
            return

        if (self.ssp_list.item(rows[0].row(), 3).text() == "Future") or \
                (self.ssp_list.item(rows[0].row(), 4).text() == "Future"):
            QtWidgets.QMessageBox.information(self, "Database",
                                              "You cannot load the selected profile from the database!\n\n"
                                              "If you need to access it, update to a newer version of "
                                              "Sound Speed Manager.")
            return

        # the primary key is the first column (= 0)
        pk = int(self.ssp_list.item(rows[0].row(), 0).text())
        success = self.lib.load_profile(pk)
        if not success:
            QtWidgets.QMessageBox.warning(self, "Database", "Unable to load profile!",
                                          QtWidgets.QMessageBox.StandardButton.Ok)
            return

        if self.lib.has_ssp():
            self.main_win.data_imported()
            self.main_win.switch_to_editor_tab()

    def stats_profile(self):
        logger.debug("user wants some stats on a single profile")

        # first, we clear the current data (if any)
        self.lib.clear_data()
        self.main_win.data_cleared()

        # check if any selection
        rows = self.ssp_list.selectionModel().selectedRows()
        if len(rows) != 1:
            QtWidgets.QMessageBox.information(self, "Database", "Select a single profile before exporting it!")
            return

        # the primary key is the first column (= 0)
        pk = int(self.ssp_list.item(rows[0].row(), 0).text())
        success = self.lib.load_profile(pk, skip_atlas=True)
        if not success:
            QtWidgets.QMessageBox.warning(self, "Database", "Unable to load profile!",
                                          QtWidgets.QMessageBox.StandardButton.Ok)
            return

        msg = self.lib.profile_stats()
        if msg is not None:
            basename = "%s_%03d_stats" % (self.lib.current_project, pk)
            dlg = TextEditorDialog(title="Profile Statistical Info", basename=basename, body=msg,
                                   main_win=self, lib=self.lib, parent=self)
            dlg.exec()

        # finally, we clear the just loaded data
        self.lib.clear_data()
        self.main_win.data_cleared()

    def metadata_profile(self):
        logger.debug("user wants view the profile metadata")

        # first, we clear the current data (if any)
        self.lib.clear_data()
        self.main_win.data_cleared()

        # check if any selection
        rows = self.ssp_list.selectionModel().selectedRows()
        if len(rows) == 1:  # single selection

            # the primary key is the first column (= 0)
            pk = int(self.ssp_list.item(rows[0].row(), 0).text())
            success = self.lib.load_profile(pk, skip_atlas=True)
            if not success:
                QtWidgets.QMessageBox.warning(self, "Database", "Unable to load profile!",
                                              QtWidgets.QMessageBox.StandardButton.Ok)
                return

            dlg = MetadataDialog(lib=self.lib, main_win=self.main_win, parent=self)
            dlg.exec()

        else:  # multiple selection

            logger.debug("User wants to edit the metadata of multiple profiles")

            pks = [int(self.ssp_list.item(row.row(), 0).text()) for row in rows]
            logger.debug("pks: %s" % (pks,))

            dlg = CommonMetadataDialog(lib=self.lib, main_win=self.main_win, pks=pks, parent=self)
            dlg.exec()

        # finally, we clear the just loaded data
        self.lib.clear_data()
        self.main_win.data_cleared()

    def export_single_profile(self):
        logger.debug("user want to export a single profile")

        # first, we clear the current data (if any)
        self.lib.clear_data()
        self.main_win.data_cleared()

        # check if any selection
        rows = self.ssp_list.selectionModel().selectedRows()
        if len(rows) != 1:
            QtWidgets.QMessageBox.information(self, "Database", "Select a single profile before exporting it!")
            return

        # the primary key is the first column (= 0)
        pk = int(self.ssp_list.item(rows[0].row(), 0).text())
        success = self.lib.load_profile(pk)
        if not success:
            QtWidgets.QMessageBox.warning(self, "Database", "Unable to load profile!",
                                          QtWidgets.QMessageBox.StandardButton.Ok)
            return

        dlg = ExportSingleProfileDialog(lib=self.lib, main_win=self.main_win, parent=self)
        dlg.exec()

        # finally, we clear the just loaded data
        self.lib.clear_data()
        self.main_win.data_cleared()

    def plot_comparison(self):
        logger.debug("user want to plot multiple profiles for comparison")

        self.lib.clear_data()
        self.main_win.data_cleared()

        # check if any selection
        rows = self.ssp_list.selectionModel().selectedRows()
        if len(rows) < 2:
            QtWidgets.QMessageBox.information(self, "Database", "Select multiple profiles before plotting them!")
            return

        pks = list()
        for row in rows:
            pks.append(int(self.ssp_list.item(row.row(), 0).text()))

        dlg = PlotMultiProfileDialog(main_win=self.main_win, lib=self.lib, pks=pks, parent=self)
        dlg.exec()
        dlg.raise_window()

    def export_multi_profile(self):
        logger.debug("user want to export multiple profiles")

        self.lib.clear_data()
        self.main_win.data_cleared()

        # check if any selection
        rows = self.ssp_list.selectionModel().selectedRows()
        if len(rows) < 2:
            QtWidgets.QMessageBox.information(self, "Database", "Select multiple profiles before exporting them!")
            return

        pks = list()
        for row in rows:
            pks.append(int(self.ssp_list.item(row.row(), 0).text()))

        dlg = ExportMultiProfileDialog(main_win=self.main_win, lib=self.lib, pks=pks, parent=self)
        dlg.exec()

    def delete_profile(self):

        # check if any selection
        rows = self.ssp_list.selectionModel().selectedRows()
        nr_rows = len(rows)
        if nr_rows == 0:
            QtWidgets.QMessageBox.information(self, "Database", "You need to select a profile before deleting it!")
            return

        logger.debug("user want to delete %d profiles" % nr_rows)

        # ask if the user want to delete it
        if nr_rows == 1:
            pk = int(self.ssp_list.item(rows[0].row(), 0).text())
            msg = "Do you really want to delete profile #%02d?" % pk
        else:
            msg = "Do you really want to delete %d profiles?" % nr_rows
        ret = QtWidgets.QMessageBox.warning(
            self, "Database", msg,
            QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.No)
        if ret == QtWidgets.QMessageBox.StandardButton.No:
            return

        # actually perform the removal
        for row in rows:
            pk = int(self.ssp_list.item(row.row(), 0).text())
            success = self.lib.delete_db_profile(pk)
            if not success:
                QtWidgets.QMessageBox.critical(self, "Database", "Unable to remove the #%02d profile!" % pk)

        self.main_win.data_removed()

    def dqa_at_surface(self):
        logger.debug("user want to do DQA at surface")

        for row in self.ssp_list.selectionModel().selectedRows():

            pk = int(self.ssp_list.item(row.row(), 0).text())

            msg = self.lib.dqa_at_surface(pk)
            if msg is not None:
                basename = "%s_%03d_dqa_surface" % (self.lib.current_project, pk)
                dlg = TextEditorDialog(title="Surface DQA", basename=basename, body=msg, main_win=self, lib=self.lib,
                                       parent=self)
                dlg.exec()

    def dqa_full_profile(self):
        logger.debug("user want to do a profile DQA")

        rows = self.ssp_list.selectionModel().selectedRows()
        if len(rows) == 1:

            pk = int(self.ssp_list.item(rows[0].row(), 0).text())
            if self.lib.ref is None:
                QtWidgets.QMessageBox.information(self, "DQA compare with reference cast",
                                                  "You should set reference cast first!")
                return
            else:
                try:
                    msg = self.lib.dqa_full_profile(pk)
                except RuntimeError as e:
                    QtWidgets.QMessageBox.critical(self, "DQA error", "%s" % e)
                    return

        elif len(rows) == 2:

            pk = int(self.ssp_list.item(rows[0].row(), 0).text())
            pk_ref = int(self.ssp_list.item(rows[1].row(), 0).text())
            try:
                msg = self.lib.dqa_full_profile(pk, pk_ref)

            except RuntimeError as e:
                QtWidgets.QMessageBox.critical(self, "DQA error", "%s" % e)
                return

        else:
            QtWidgets.QMessageBox.information(self, "DQA comparison",
                                              "You need to select 1 or 2 profiles to do DQA comparison!")
            return

        if msg is not None:
            basename = "%s_dqa" % self.lib.current_project
            dlg = TextEditorDialog(title="Profile DQA", basename=basename, body=msg, init_size=QtCore.QSize(800, 800),
                                   main_win=self, lib=self.lib, parent=self)
            dlg.exec()

    def ray_tracing_comparison(self):
        logger.debug("user want to do a comparison between two ray-traced profiles")

        rows = self.ssp_list.selectionModel().selectedRows()
        if len(rows) != 2:
            QtWidgets.QMessageBox.information(self, "Ray-Tracing comparison",
                                              "You need to select exactly 2 profiles to do this comparison!")
            return

        self.progress.start(title="Comparison plots", text="Retrieving profiles")

        self.progress.update(10)
        pk1 = int(self.ssp_list.item(rows[0].row(), 0).text())
        pk2 = int(self.ssp_list.item(rows[1].row(), 0).text())

        self.progress.update(text="Ray-tracing", value=20)
        try:
            self.lib.ray_tracing_comparison(pk1, pk2)

        except RuntimeError as e:
            QtWidgets.QMessageBox.critical(self, "Ray-Tracing error", "%s" % e)
            self.progress.end()
            return

        self.progress.end()

    def bias_plots(self):
        logger.debug("user want to make bias plots")

        rows = self.ssp_list.selectionModel().selectedRows()
        if len(rows) != 2:
            QtWidgets.QMessageBox.information(self, "Across-swath bias plots",
                                              "You need to select exactly 2 profiles to create these plots!")
            return

        self.progress.start(title="Bias plots", text="Retrieving profiles")

        self.progress.update(10)
        pk1 = int(self.ssp_list.item(rows[0].row(), 0).text())
        self.progress.update(20)
        pk2 = int(self.ssp_list.item(rows[1].row(), 0).text())
        try:
            self.progress.update(text="Ray-tracing", value=40)
            self.lib.bias_plots(pk1, pk2)
            self.progress.end()
        except RuntimeError as e:
            QtWidgets.QMessageBox.critical(self, "Bias plots error", "%s" % e)
            self.progress.end()
            return

    def new_project(self):
        logger.debug("user want to create a new project")

        self.main_win.switch_to_database_tab()

        dlg = ProjectNewDialog(lib=self.lib, main_win=self.main_win, parent=self)
        success = dlg.exec()

        if success:
            self.update_table()

    def rename_project(self):
        logger.debug("user want to rename a project")

        self.main_win.switch_to_database_tab()

        dlg = ProjectRenameDialog(lib=self.lib, main_win=self.main_win, parent=self)
        success = dlg.exec()

        if success:
            self.update_table()

    def switch_project(self):
        logger.debug("user want to switch to another project")

        self.main_win.switch_to_database_tab()

        dlg = ProjectSwitchDialog(lib=self.lib, main_win=self.main_win, parent=self)
        dlg.exec()

        self.update_table()

    def import_data(self):
        logger.debug("user want to import data from another project")

        self.main_win.switch_to_database_tab()

        dlg = ImportDataDialog(lib=self.lib, main_win=self.main_win, parent=self)
        dlg.exec()

        self.update_table()

    def project_folder(self):
        logger.debug("user want to open the project folder")

        self.main_win.switch_to_database_tab()
        self.lib.open_projects_folder()

    def output_folder(self):
        logger.debug("user want to open the output folder")

        self.main_win.switch_to_database_tab()
        self.lib.open_outputs_folder()

    def import_profiles(self):
        logger.debug("user want to import multiple profiles")

        self.main_win.switch_to_database_tab()

        QtWidgets.QMessageBox.warning(self, "Warning about multi-profile import",
                                      "The multi-profile dialog allows you to directly\n"
                                      "import profiles into the database, BUT skipping\n"
                                      "all the processing steps and the visual inspection!\n"
                                      "\n"
                                      "For your convenience, all the imported profiles are\n"
                                      "highlighted in red until loaded for visual inspection\n"
                                      "and saved back into the database.")

        dlg = ImportMultiProfileDialog(main_win=self.main_win, lib=self.lib, parent=self)
        dlg.exec()

        self.update_table()

    def export_profile_switch(self):
        logger.debug("user want to export profile data")

        self.main_win.switch_to_database_tab()

        # check if any selection
        rows = self.ssp_list.selectionModel().selectedRows()

        nr_rows = len(rows)
        if nr_rows == 0:
            QtWidgets.QMessageBox.information(self, "Profile Export", "You need to select at least 1 profile!")

        elif nr_rows == 1:
            self.export_single_profile()

        else:
            self.export_multi_profile()

    def export_profile_metadata(self):
        logger.debug("user want to export profile metadata")

        self.main_win.switch_to_database_tab()
        dlg = ExportProfileMetadataDialog(lib=self.lib, main_win=self.main_win, parent=self)
        dlg.exec()

    def plot_profiles(self):
        logger.debug("user want to plot profiles")

        self.main_win.switch_to_database_tab()

        dlg = PlotProfilesDialog(lib=self.lib, main_win=self.main_win, parent=self)
        success = dlg.exec()

        if success and not dlg.only_saved:
            self.lib.raise_plot_window()

    def show_map_for_selected(self):
        logger.debug("user want to show a map with the selected profiles")

        self.main_win.switch_to_database_tab()

        rows = self.ssp_list.selectionModel().selectedRows()
        if len(rows) == 0:
            QtWidgets.QMessageBox.information(self, "Map", "You need to select at least profile for the map!")
            return

        # actually perform the removal
        pks = list()
        for row in rows:
            pks.append(int(self.ssp_list.item(row.row(), 0).text()))

        self.lib.map_db_profiles(pks)
        self.lib.raise_plot_window()

    def update_table(self):

        self.lib.progress.start(title="Sound Speed Profiles", text="Loading casts", init_value=5)

        class NumberWidgetItem(QtWidgets.QTableWidgetItem):

            def __lt__(self, other):
                try:
                    return float(self.text()) < float(other.text())

                except (ValueError, TypeError):
                    return True

        class LocationWidgetItem(QtWidgets.QTableWidgetItem):

            def __lt__(self, other):
                self_lon = self.text()[1:].split(';')[0]
                other_lon = other.text()[1:].split(';')[0]
                self_lat = self.text()[:-1].split(';')[-1]
                other_lat = other.text()[:-1].split(';')[-1]
                logger.debug("%s %s < %s %s" % (self_lon, self_lat, other_lon, other_lat))
                try:
                    if self_lon == other_lon:
                        return float(self_lat) < float(other_lat)
                    return float(self_lon) < float(other_lon)

                except (ValueError, TypeError):
                    return True

        with_stats = self.btn_show_stats.isChecked()

        if with_stats:
            labels = ['id', 'time', 'location',
                      'sensor', 'probe',
                      'ss@min depth', 'min depth', 'avg speed',
                      'max depth', 'max depth[raw]',
                      'original path', 'institution',
                      'survey', 'vessel', 'sn',
                      'processing time', 'processing info', 'surveylines', 'comments',
                      'pressure uom', 'depth uom', 'speed uom',
                      'temperature uom', 'conductivity uom', 'salinity uom',
                      ]
        else:
            labels = ['id', 'time', 'location',
                      'sensor', 'probe',
                      'original path', 'institution',
                      'survey', 'vessel', 'sn',
                      'processing time', 'processing info', 'surveylines', 'comments',
                      'pressure uom', 'depth uom', 'speed uom',
                      'temperature uom', 'conductivity uom', 'salinity uom',
                      ]

        # set the top label
        self.active_label.setText("<b>Current project: %s</b>" % self.lib.current_project)

        lst = self.lib.db_list_profiles(with_stats=with_stats)

        # prepare the table
        self.ssp_list.setSortingEnabled(False)
        self.ssp_list.clear()
        self.ssp_list.setColumnCount(len(labels))
        self.ssp_list.setHorizontalHeaderLabels(labels)

        # populate the table
        self.ssp_list.setRowCount(len(lst))

        nr_rows = len(lst)
        quantum = 95 / (nr_rows + 1)

        # logger.debug("Populating %d table entries ..." % len(lst))
        for i, ssp_ in enumerate(lst):

            processed = True
            tokens = ssp_[11].split(";")
            if with_stats:
                # Re-arrange index to match the new items and labels
                ssp = ssp_[0:5] + ssp_[20:25] + ssp_[5:20]
            else:
                ssp = ssp_[0:20]

            if Dicts.proc_user_infos['PLOTTED'] not in tokens:
                processed = False

            for j, field in enumerate(ssp):

                if j == 3:
                    label = '%s' % Dicts.first_match(Dicts.sensor_types, int(field))
                    # logger.debug('%s' % Dicts.first_match(Dicts.sensor_types, int(field)))

                elif j == 4:
                    label = '%s' % Dicts.first_match(Dicts.probe_types, int(field))
                    # logger.debug('%s' % Dicts.first_match(Dicts.probe_types, int(field)))

                else:
                    label = field

                if j in [0, ]:
                        item = NumberWidgetItem("%s" % label)
                elif j in [5, 6, 7, 8, 9] and with_stats:
                    item = NumberWidgetItem("%s" % label)
                elif j in [2, ]:
                    item = LocationWidgetItem("%s" % label)
                else:
                    item = QtWidgets.QTableWidgetItem("%s" % label)

                if (j == 3) and (int(field) == Dicts.sensor_types['Future']):
                    item.setForeground(QtGui.QColor(200, 100, 100))

                elif (j == 4) and (int(field) == Dicts.sensor_types['Future']):
                    item.setForeground(QtGui.QColor(200, 100, 100))

                if not processed:
                    item.setBackground(QtGui.QColor(200, 100, 100, 50))

                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignHCenter)
                item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)

                self.ssp_list.setItem(i, j, item)

            self.lib.progress.add(quantum=quantum, text="%d/%d" % (i + 1, nr_rows))

        # logger.debug("Populating %d table entries ... (sorting)" % len(lst))
        self.ssp_list.setSortingEnabled(True)
        # logger.debug("Populating %d table entries ... (resizing)" % len(lst))
        self.ssp_list.resizeColumnsToContents()

        # logger.debug("Populating %d table entries ... DONE" % len(lst))

        self.lib.progress.end()

    def data_stored(self):
        self.update_table()

    def data_removed(self):
        self.update_table()

    def server_started(self):
        self.setDisabled(True)

    def server_stopped(self):
        self.setEnabled(True)
