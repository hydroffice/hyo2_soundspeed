import logging

from PySide6 import QtCore, QtWidgets

from hyo2.soundspeedmanager.dialogs.dialog import AbstractDialog

logger = logging.getLogger(__name__)


class PlotProfilesDialog(AbstractDialog):

    def __init__(self, main_win, lib, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        self.only_saved = False

        self.fmt_outputs = list()

        self.setWindowTitle("Plot profiles")
        self.setMinimumWidth(160)

        # outline ui
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # label
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        label = QtWidgets.QLabel("Select plot product:")
        hbox.addWidget(label)
        hbox.addStretch()
        # buttons
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        self.buttonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        hbox.addWidget(self.buttonBox)
        hbox.addStretch()
        # - profile map
        btn = QtWidgets.QPushButton("Profiles Map")
        self.buttonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_profile_map)
        btn.setToolTip("Create a map with the profile locations")
        # - aggregate plot
        btn = QtWidgets.QPushButton("Aggregate Plot")
        self.buttonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_aggregate_plot)
        btn.setToolTip("Create a plot showing aggregated profiles")
        # - show per-day
        btn = QtWidgets.QPushButton("Plot per-day")
        self.buttonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_show_perday)
        btn.setToolTip("Create per-day plots")
        # - save per-day
        btn = QtWidgets.QPushButton("Save per-day")
        self.buttonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_save_perday)
        btn.setToolTip("Save per-day plots")

    def on_profile_map(self):
        logger.debug("user want to map the profiles")

        success = self.lib.map_db_profiles()
        if not success:
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Database", "Unable to create a profile map!")
        else:
            self.accept()

    def on_aggregate_plot(self):
        logger.debug("user want to create an aggregate plot")

        ssp_times = self.lib.db_timestamp_list()
        # print(ssp_times[0][0], ssp_times[-1][0])

        if len(ssp_times) == 0:
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.information(self, "Database",
                                              "Missing SSPs in the database. Import and store them first!")

        class DateDialog(QtWidgets.QDialog):

            def __init__(self, date_start, date_end, *args, **kwargs):
                super(DateDialog, self).__init__(*args, **kwargs)

                # noinspection PyArgumentList
                self.setMinimumSize(300, 500)
                self.setWindowTitle('SSP date range to plot')

                self.start_date = QtWidgets.QLabel()
                self.start_date.setText("Start date:")
                self.cal_start_date = QtWidgets.QCalendarWidget()
                self.cal_start_date.setSelectedDate(date_start)

                self.end_date = QtWidgets.QLabel()
                self.end_date.setText("End date:")
                self.cal_end_date = QtWidgets.QCalendarWidget()
                self.cal_end_date.setSelectedDate(date_end)

                self.ok = QtWidgets.QPushButton("OK")
                # noinspection PyUnresolvedReferences
                self.ok.clicked.connect(self.on_click_ok)
                self.cancel = QtWidgets.QPushButton("Cancel")
                # noinspection PyUnresolvedReferences
                self.cancel.clicked.connect(self.on_click_cancel)

                vbox = QtWidgets.QVBoxLayout()
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
        if ret == QtWidgets.QDialog.Accepted:
            dates = dialog.cal_start_date.selectedDate().toPython(), \
                    dialog.cal_end_date.selectedDate().toPython()
            dialog.destroy()
        else:
            dialog.destroy()
            return
        # print(dates)

        # check the user selection
        if dates[0] > dates[1]:
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self,
                                           'The start date (%s) comes after the end data (%s)' % (dates[0], dates[1]),
                                           'Invalid selection')
            return

        success = self.lib.aggregate_plot(dates=dates)
        if not success:
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Database", "Unable to create an aggregate plot!")
        else:
            self.accept()

    def on_show_perday(self):
        logger.debug("user want to show per-day plots")
        success = self.lib.plot_daily_db_profiles()
        if not success:
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Database", "Unable to create daily plots!")
        else:
            self.accept()

    def on_save_perday(self):
        logger.debug("user want to save per-day plots")
        success = self.lib.save_daily_db_profiles()
        if not success:
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Database", "Unable to save daily plots!")
        else:
            self.only_saved = True
            self.lib.open_outputs_folder()
            self.accept()
