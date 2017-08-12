from PySide import QtGui
from PySide import QtCore

import logging
logger = logging.getLogger(__name__)

from hyo.surveydatamonitor.monitor import SurveyDataMonitor
from hyo.soundspeedmanager.dialogs.dialog import AbstractDialog


class MonitorOption(AbstractDialog):

    def __init__(self, main_win, lib, monitor, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)
        if not isinstance(monitor, SurveyDataMonitor):
            raise RuntimeError("Passed invalid monitor object: %s" % type(lib))
        self._monitor = monitor

        self.setWindowTitle("Survey Data Monitor Options")
        self.setMinimumWidth(300)

        # outline ui
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLayout)
        self._tabs = QtGui.QTabWidget()
        self.mainLayout.addWidget(self._tabs)

        # ### view options ###

        view_options = QtGui.QWidget(self)
        options_mainLayout = QtGui.QVBoxLayout()
        view_options.setLayout(options_mainLayout)
        self._tabs.addTab(view_options, "Plots")

        options_mainLayout.addSpacing(12)

        # label
        hbox = QtGui.QHBoxLayout()
        options_mainLayout.addLayout(hbox)
        hbox.addStretch()
        self.max_samples_label = QtGui.QLabel("Plot latest samples:")
        hbox.addWidget(self.max_samples_label)
        hbox.addStretch()
        # slider
        hbox = QtGui.QHBoxLayout()
        options_mainLayout.addLayout(hbox)
        hbox.addStretch()
        self.max_samples = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.max_samples.setTickPosition(QtGui.QSlider.TicksBelow)
        self.max_samples.setSingleStep(1)
        self.max_samples.setTickInterval(1000)
        self.max_samples.setMinimum(1)
        self.max_samples.setMaximum(10000)
        self.max_samples.setMinimumWidth(260)
        self.max_samples.setValue(self.main_win.plotting_samples)
        self.max_samples_label.setText("Plot latest %d samples:" % self.max_samples.value())
        # noinspection PyUnresolvedReferences
        self.max_samples.valueChanged.connect(self.on_max_samples_changed)
        hbox.addWidget(self.max_samples)
        hbox.addStretch()

        options_mainLayout.addStretch()

        # ### estimator options ###

        estimator_options = QtGui.QWidget(self)
        estimator_mainLayout = QtGui.QVBoxLayout()
        estimator_options.setLayout(estimator_mainLayout)
        self._tabs.addTab(estimator_options, "Estimators")

        estimator_mainLayout.addSpacing(12)

        # label
        hbox = QtGui.QHBoxLayout()
        estimator_mainLayout.addLayout(hbox)
        hbox.addStretch()
        self.active_estimator_label = QtGui.QLabel("Active estimator:")
        hbox.addWidget(self.active_estimator_label)
        hbox.addStretch()
        # button group
        self.active_estimator = QtGui.QButtonGroup()
        # disabled
        hbox = QtGui.QHBoxLayout()
        estimator_mainLayout.addLayout(hbox)
        hbox.addSpacing(30)
        none_estimator = QtGui.QRadioButton("None")
        self.active_estimator.addButton(none_estimator)
        hbox.addWidget(none_estimator)
        hbox.addStretch()
        # cast time
        hbox = QtGui.QHBoxLayout()
        estimator_mainLayout.addLayout(hbox)
        hbox.addSpacing(30)
        casttime_estimator = QtGui.QRadioButton("CastTime")
        self.active_estimator.addButton(casttime_estimator)
        hbox.addWidget(casttime_estimator)
        hbox.addStretch()
        # fore cast
        hbox = QtGui.QHBoxLayout()
        estimator_mainLayout.addLayout(hbox)
        hbox.addSpacing(30)
        forecast_estimator = QtGui.QRadioButton("ForeCast")
        # temporarily disabled
        forecast_estimator.setDisabled(True)
        self.active_estimator.addButton(forecast_estimator)
        hbox.addWidget(forecast_estimator)
        hbox.addStretch()
        # noinspection PyUnresolvedReferences
        self.active_estimator.buttonClicked.connect(self.on_active_estimator_changed)

        estimator_mainLayout.addStretch()

        # ### cast time options ###

        casttime_options = QtGui.QWidget(self)
        casttime_mainLayout = QtGui.QVBoxLayout()
        casttime_options.setLayout(casttime_mainLayout)
        self.casttime_tab_idx = self._tabs.addTab(casttime_options, "CastTime")
        logger.debug("casttime idx: %d" % self.casttime_tab_idx)

        casttime_mainLayout.addStretch()

        double_validator = QtGui.QDoubleValidator(0, 10000, 4, self)
        # double_validator.setRange(0.0, 10000.0)

        casttime_mainLayout.addSpacing(12)

        hbox = QtGui.QHBoxLayout()
        casttime_mainLayout.addLayout(hbox)
        hbox.addStretch()
        self.time_intervals_label = QtGui.QLabel("<i>Time Intervals</i>")
        hbox.addWidget(self.time_intervals_label)
        hbox.addStretch()

        # initial interval
        hbox = QtGui.QHBoxLayout()
        casttime_mainLayout.addLayout(hbox)
        hbox.addStretch()
        # label
        self.initial_interval_label = QtGui.QLabel("Initial interval [min]:")
        self.initial_interval_label.setFixedWidth(150)
        hbox.addWidget(self.initial_interval_label)
        # input value
        self.initial_interval = QtGui.QLineEdit()
        self.initial_interval.setFixedHeight(20)
        self.initial_interval.setFixedWidth(60)
        self.initial_interval.setValidator(double_validator)
        # noinspection PyUnresolvedReferences
        self.initial_interval.textEdited.connect(self.on_casttime_options_changed)
        hbox.addWidget(self.initial_interval)
        hbox.addStretch()

        # minimum interval
        hbox = QtGui.QHBoxLayout()
        casttime_mainLayout.addLayout(hbox)
        hbox.addStretch()
        # label
        self.minimum_interval_label = QtGui.QLabel("Minimum interval [min]:")
        self.minimum_interval_label.setFixedWidth(150)
        hbox.addWidget(self.minimum_interval_label)
        # input value
        self.minimum_interval = QtGui.QLineEdit()
        self.minimum_interval.setFixedHeight(20)
        self.minimum_interval.setFixedWidth(60)
        self.minimum_interval.setValidator(double_validator)
        # noinspection PyUnresolvedReferences
        self.minimum_interval.textEdited.connect(self.on_casttime_options_changed)
        hbox.addWidget(self.minimum_interval)
        hbox.addStretch()

        # maximum interval
        hbox = QtGui.QHBoxLayout()
        casttime_mainLayout.addLayout(hbox)
        hbox.addStretch()
        # label
        self.maximum_interval_label = QtGui.QLabel("Maximum interval [min]:")
        self.maximum_interval_label.setFixedWidth(150)
        hbox.addWidget(self.maximum_interval_label)
        # input value
        self.maximum_interval = QtGui.QLineEdit()
        self.maximum_interval.setFixedHeight(20)
        self.maximum_interval.setFixedWidth(60)
        self.maximum_interval.setValidator(double_validator)
        # noinspection PyUnresolvedReferences
        self.maximum_interval.textEdited.connect(self.on_casttime_options_changed)
        hbox.addWidget(self.maximum_interval)
        hbox.addStretch()

        casttime_mainLayout.addSpacing(12)

        # Sonar info

        hbox = QtGui.QHBoxLayout()
        casttime_mainLayout.addLayout(hbox)
        hbox.addStretch()
        self.sonar_info_label = QtGui.QLabel("<i>Sonar Info</i>")
        hbox.addWidget(self.sonar_info_label)
        hbox.addStretch()

        # half swath angle
        hbox = QtGui.QHBoxLayout()
        casttime_mainLayout.addLayout(hbox)
        hbox.addStretch()
        # label
        self.half_swath_angle_label = QtGui.QLabel("Half Swath Angle [deg]:")
        self.half_swath_angle_label.setFixedWidth(150)
        hbox.addWidget(self.half_swath_angle_label)
        # input value
        self.half_swath_angle = QtGui.QLineEdit()
        self.half_swath_angle.setFixedHeight(20)
        self.half_swath_angle.setFixedWidth(60)
        self.half_swath_angle.setValidator(double_validator)
        # noinspection PyUnresolvedReferences
        self.half_swath_angle.textEdited.connect(self.on_casttime_options_changed)
        hbox.addWidget(self.half_swath_angle)
        hbox.addStretch()

        casttime_mainLayout.addSpacing(12)

        # Allowable error

        hbox = QtGui.QHBoxLayout()
        casttime_mainLayout.addLayout(hbox)
        hbox.addStretch()
        self.allowable_error_label = QtGui.QLabel("<i>Allowable Error</i>")
        hbox.addWidget(self.allowable_error_label)
        hbox.addStretch()

        # fixed component
        hbox = QtGui.QHBoxLayout()
        casttime_mainLayout.addLayout(hbox)
        hbox.addStretch()
        # label
        self.fixed_allowable_error_label = QtGui.QLabel("Fixed component [m]:")
        self.fixed_allowable_error_label.setFixedWidth(150)
        hbox.addWidget(self.fixed_allowable_error_label)
        # input value
        self.fixed_allowable_error = QtGui.QLineEdit()
        self.fixed_allowable_error.setFixedHeight(20)
        self.fixed_allowable_error.setFixedWidth(60)
        self.fixed_allowable_error.setValidator(double_validator)
        # noinspection PyUnresolvedReferences
        self.fixed_allowable_error.textEdited.connect(self.on_casttime_options_changed)
        hbox.addWidget(self.fixed_allowable_error)
        hbox.addStretch()

        # variable component
        hbox = QtGui.QHBoxLayout()
        casttime_mainLayout.addLayout(hbox)
        hbox.addStretch()
        # label
        self.variable_allowable_error_label = QtGui.QLabel("Percentage of depth [%]:")
        self.variable_allowable_error_label.setFixedWidth(150)
        hbox.addWidget(self.variable_allowable_error_label)
        # input value
        self.variable_allowable_error = QtGui.QLineEdit()
        self.variable_allowable_error.setFixedHeight(20)
        self.variable_allowable_error.setFixedWidth(60)
        self.variable_allowable_error.setValidator(double_validator)
        # noinspection PyUnresolvedReferences
        self.variable_allowable_error.textEdited.connect(self.on_casttime_options_changed)
        hbox.addWidget(self.variable_allowable_error)
        hbox.addStretch()

        casttime_mainLayout.addStretch()

        # ### bayes forecast options ###

        bayes_options = QtGui.QWidget(self)
        bayes_mainLayout = QtGui.QVBoxLayout()
        bayes_options.setLayout(bayes_mainLayout)
        self.bayer_tab_idx = self._tabs.addTab(bayes_options, "ForeCast")

        bayes_mainLayout.addSpacing(12)

        # initialization
        none_estimator.setChecked(True)
        self._tabs.setTabEnabled(self.casttime_tab_idx, False)
        self._tabs.setTabEnabled(self.bayer_tab_idx, False)

        # data-based initialization
        self._monitor.lock_data()
        self.initial_interval.setText("%s" % self._monitor.casttime.current_interval)
        self.minimum_interval.setText("%s" % self._monitor.casttime.minimum_interval)
        self.maximum_interval.setText("%s" % self._monitor.casttime.maximum_interval)
        self.half_swath_angle.setText("%s" % self._monitor.casttime.half_swath_angle)
        self.fixed_allowable_error.setText("%s" % self._monitor.casttime.fixed_allowable_error)
        self.variable_allowable_error.setText("%s" % self._monitor.casttime.variable_allowable_error)
        self._monitor.unlock_data()

    @QtCore.Slot()
    def on_max_samples_changed(self):
        self.main_win.plotting_samples = self.max_samples.value()
        self.max_samples_label.setText("Plot latest %d samples:" % self.max_samples.value())
        logger.debug(self.main_win.plotting_samples)
        self.main_win.update_plot_data()

    @QtCore.Slot()
    def on_active_estimator_changed(self, idx):
        button_label = idx.text()
        logger.debug("active estimator changed: %s" % button_label)

        if button_label == "None":

            self._tabs.setTabEnabled(self.casttime_tab_idx, False)
            self._tabs.setTabEnabled(self.bayer_tab_idx, False)
            self._monitor.disable_estimation()

        elif button_label == "CastTime":

            self._tabs.setTabEnabled(self.casttime_tab_idx, True)
            self._tabs.setTabEnabled(self.bayer_tab_idx, False)
            self._monitor.activate_casttime()

        elif button_label == "BayesForeCast":

            self._tabs.setTabEnabled(self.casttime_tab_idx, False)
            self._tabs.setTabEnabled(self.bayer_tab_idx, True)
            self._monitor.activate_forecast()

        else:

            raise RuntimeError("Unknown estimator: %s" % button_label)

    @QtCore.Slot()
    def on_casttime_options_changed(self, idx):
        logger.debug("CastTime options changed")

        self._monitor.lock_data()
        self._monitor.casttime.current_interval = float(self.initial_interval.text())
        self._monitor.casttime.minimum_interval = float(self.minimum_interval.text())
        self._monitor.casttime.maximum_interval = float(self.maximum_interval.text())
        self._monitor.casttime.half_swath_angle = float(self.half_swath_angle.text())
        self._monitor.casttime.fixed_allowable_error = float(self.fixed_allowable_error.text())
        self._monitor.casttime.variable_allowable_error = float(self.variable_allowable_error.text())
        self._monitor.unlock_data()
