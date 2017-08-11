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

        # ### estimator options ###

        estimator_options = QtGui.QWidget(self)
        estimator_mainLayout = QtGui.QVBoxLayout()
        estimator_options.setLayout(estimator_mainLayout)
        self._tabs.addTab(estimator_options, "Estimators")

        # label
        hbox = QtGui.QHBoxLayout()
        estimator_mainLayout.addLayout(hbox)
        hbox.addStretch()
        self.active_estimator_label = QtGui.QLabel("Active estimator:")
        hbox.addWidget(self.active_estimator_label)
        hbox.addStretch()
        # button group
        self.active_estimator = QtGui.QButtonGroup()
        # cast time
        hbox = QtGui.QHBoxLayout()
        estimator_mainLayout.addLayout(hbox)
        hbox.addSpacing(30)
        casttime_estimator = QtGui.QRadioButton("CastTime")
        self.active_estimator.addButton(casttime_estimator)
        hbox.addWidget(casttime_estimator)
        hbox.addStretch()
        # bayes
        hbox = QtGui.QHBoxLayout()
        estimator_mainLayout.addLayout(hbox)
        hbox.addSpacing(30)
        bayes_estimator = QtGui.QRadioButton("BayesForeCast")
        # temporarily disabled
        bayes_estimator.setDisabled(True)
        self.active_estimator.addButton(bayes_estimator)
        hbox.addWidget(bayes_estimator)
        hbox.addStretch()
        # noinspection PyUnresolvedReferences
        self.active_estimator.buttonClicked.connect(self.on_active_estimator_changed)

        # ### cast time options ###

        casttime_options = QtGui.QWidget(self)
        casttime_mainLayout = QtGui.QVBoxLayout()
        casttime_options.setLayout(casttime_mainLayout)
        self.casttime_tab_idx = self._tabs.addTab(casttime_options, "CastTime")
        logger.debug("casttime idx: %d" % self.casttime_tab_idx)

        # ### bayes forecast options ###

        bayes_options = QtGui.QWidget(self)
        bayes_mainLayout = QtGui.QVBoxLayout()
        bayes_options.setLayout(bayes_mainLayout)
        self.bayer_tab_idx = self._tabs.addTab(bayes_options, "BayesForeCast")

        # initialization
        casttime_estimator.setChecked(True)
        self._tabs.setTabEnabled(self.casttime_tab_idx, True)
        self._tabs.setTabEnabled(self.bayer_tab_idx, False)

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

        if button_label == "CastTime":

            self._tabs.setTabEnabled(self.casttime_tab_idx, True)
            self._tabs.setTabEnabled(self.bayer_tab_idx, False)
            self._monitor.activate_casttime()

        elif button_label == "BayesForeCast":

            self._tabs.setTabEnabled(self.casttime_tab_idx, False)
            self._tabs.setTabEnabled(self.bayer_tab_idx, True)
            self._monitor.activate_bayesforecast()

        else:

            raise RuntimeError("Unknown estimator: %s" % button_label)
