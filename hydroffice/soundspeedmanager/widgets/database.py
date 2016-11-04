from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

from PySide import QtGui, QtCore

logger = logging.getLogger(__name__)

from .widget import AbstractWidget
from ...soundspeed.base.gdal_aux import GdalAux
from hydroffice.soundspeed.base.helper import explore_folder
from hydroffice.soundspeedmanager.dialogs.export_profiles_dialog import ExportProfilesDialog


class Database(AbstractWidget):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win, lib):
        AbstractWidget.__init__(self, main_win=main_win, lib=lib)

        # create the overall layout
        self.main_layout = QtGui.QVBoxLayout()
        self.frame.setLayout(self.main_layout)

        # - label
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        hbox.addStretch()
        self.label = QtGui.QLabel("Database content")
        hbox.addWidget(self.label)
        hbox.addStretch()

        # - database table
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- list
        self.ssp_list = QtGui.QTableWidget()
        self.ssp_list.setFocus()
        self.ssp_list.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.ssp_list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.ssp_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # noinspection PyUnresolvedReferences
        self.ssp_list.customContextMenuRequested.connect(self.make_context_menu)
        hbox.addWidget(self.ssp_list)

        # -- button box
        self.btn_box = QtGui.QDialogButtonBox(QtCore.Qt.Horizontal)
        self.main_layout.addWidget(self.btn_box)
        # --- project folder
        self.btn_project_folder = QtGui.QPushButton("Project folder")
        # noinspection PyUnresolvedReferences
        self.btn_project_folder.clicked.connect(self.project_folder)
        self.btn_project_folder.setToolTip("Open the project folder")
        self.btn_box.addButton(self.btn_project_folder, QtGui.QDialogButtonBox.ActionRole)
        # --- profile map
        self.btn_profile_map = QtGui.QPushButton("Profile map")
        # noinspection PyUnresolvedReferences
        self.btn_profile_map.clicked.connect(self.profile_map)
        self.btn_profile_map.setToolTip("Create a map with all the profiles")
        self.btn_box.addButton(self.btn_profile_map, QtGui.QDialogButtonBox.ActionRole)
        # --- aggregate plot
        self.btn_aggregate_plot = QtGui.QPushButton("Aggregate plot")
        # noinspection PyUnresolvedReferences
        self.btn_aggregate_plot.clicked.connect(self.aggregate_plot)
        self.btn_aggregate_plot.setToolTip("Create a plot aggregating multiple profiles")
        self.btn_box.addButton(self.btn_aggregate_plot, QtGui.QDialogButtonBox.ActionRole)
        # --- create daily plots
        self.btn_plot_daily = QtGui.QPushButton("Plot daily")
        # noinspection PyUnresolvedReferences
        self.btn_plot_daily.clicked.connect(self.plot_daily_profiles)
        self.btn_plot_daily.setToolTip("Plot daily profiles")
        self.btn_box.addButton(self.btn_plot_daily, QtGui.QDialogButtonBox.ActionRole)
        # --- save daily plots
        self.btn_save_daily = QtGui.QPushButton("Save daily")
        # noinspection PyUnresolvedReferences
        self.btn_save_daily.clicked.connect(self.save_daily_profiles)
        self.btn_save_daily.setToolTip("Save daily profiles")
        self.btn_box.addButton(self.btn_save_daily, QtGui.QDialogButtonBox.ActionRole)
        # --- export profiles
        self.btn_export_profiles = QtGui.QPushButton("Export info")
        # noinspection PyUnresolvedReferences
        self.btn_export_profiles.clicked.connect(self.export_profiles)
        self.btn_export_profiles.setToolTip("Export profile locations and metadata")
        self.btn_box.addButton(self.btn_export_profiles, QtGui.QDialogButtonBox.ActionRole)

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
        explore_folder(self.lib.projects_folder)

    def profile_map(self):
        logger.debug("user want to map the profiles")
        success = self.lib.map_db_profiles()
        if not success:
            # noinspection PyCallByClass
            QtGui.QMessageBox.critical(self, "Database", "Unable to create a profile map!")

    def aggregate_plot(self):
        logger.debug("user want to create an aggregate plot")

        ssp_times = self.lib.db_timestamp_list()
        # print(ssp_times[0][0], ssp_times[-1][0])

        if len(ssp_times) == 0:
            # noinspection PyCallByClass
            QtGui.QMessageBox.information(self, "Database",
                                          "Missing SSPs in the database. Import and store them first!")

        class DateDialog(QtGui.QDialog):

            def __init__(self, date_start, date_end, *args, **kwargs):
                super(DateDialog, self).__init__(*args, **kwargs)

                self.setMinimumSize(300, 500)
                self.setWindowTitle('SSP date range to plot')

                self.start_date = QtGui.QLabel()
                self.start_date.setText("Start date:")
                self.cal_start_date = QtGui.QCalendarWidget()
                self.cal_start_date.setSelectedDate(date_start)

                self.end_date = QtGui.QLabel()
                self.end_date.setText("End date:")
                self.cal_end_date = QtGui.QCalendarWidget()
                self.cal_end_date.setSelectedDate(date_end)

                self.ok = QtGui.QPushButton("OK")
                # noinspection PyUnresolvedReferences
                self.ok.clicked.connect(self.on_click_ok)
                self.cancel = QtGui.QPushButton("Cancel")
                # noinspection PyUnresolvedReferences
                self.cancel.clicked.connect(self.on_click_cancel)

                vbox = QtGui.QVBoxLayout()
                self.setLayout(vbox)
                vbox.addWidget(self.start_date)
                vbox.addWidget(self.cal_start_date)
                vbox.addWidget(self.end_date)
                vbox.addWidget(self.cal_end_date)
                vbox.addWidget(self.ok)
                vbox.addWidget(self.cancel)

            def on_click_ok(self):
                logger.debug("button: ok")
                self.accept()

            def on_click_cancel(self):
                logger.debug("button: cancel")
                self.reject()

        dialog = DateDialog(date_start=ssp_times[0][0], date_end=ssp_times[-1][0], parent=self)
        ret = dialog.exec_()
        if ret == QtGui.QDialog.Accepted:
            dates = dialog.cal_start_date.selectedDate().toPython(), \
                    dialog.cal_end_date.selectedDate().toPython()
            dialog.destroy()
        else:
            dialog.destroy()
            return
        # print(dates)

        # check the user selection
        if dates[0] > dates[1]:
            # noinspection PyCallByClass
            QtGui.QMessageBox.critical(self, 'The start date (%s) comes after the end data (%s)' % (dates[0], dates[1]),
                                       'Invalid selection')
            return

        success = self.lib.aggregate_plot(dates=dates)
        if not success:
            # noinspection PyCallByClass
            QtGui.QMessageBox.critical(self, "Database", "Unable to create an aggregate plot!")

    def plot_daily_profiles(self):
        logger.debug("user want to plot daily profiles")
        success = self.lib.plot_daily_db_profiles()
        if not success:
            # noinspection PyCallByClass
            QtGui.QMessageBox.critical(self, "Database", "Unable to create daily plots!")

    def save_daily_profiles(self):
        logger.debug("user want to save daily profiles")
        success = self.lib.save_daily_db_profiles()
        if not success:
            # noinspection PyCallByClass
            QtGui.QMessageBox.critical(self, "Database", "Unable to save daily plots!")
        else:
            self.lib.open_outputs_folder()

    def export_profiles(self):
        logger.debug("user want to export profiles")
        dlg = ExportProfilesDialog(lib=self.lib, main_win=self.main_win, parent=self)
        dlg.exec_()

    def update_table(self):
        lst = self.lib.db_list_profiles()

        # prepare the table
        self.ssp_list.clear()
        self.ssp_list.setColumnCount(11)
        self.ssp_list.setHorizontalHeaderLabels(['id', 'time', 'location',
                                                 'sensor', 'probe', 'original path',
                                                 'survey', 'vessel', 'sn',
                                                 'processing time', 'processing info'])

        # populate the table
        if len(lst) == 0:
            self.ssp_list.resizeColumnsToContents()
            return
        self.ssp_list.setRowCount(len(lst))
        for i, ssp in enumerate(lst):
            for j, field in enumerate(ssp):
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
