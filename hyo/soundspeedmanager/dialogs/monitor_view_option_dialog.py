from PySide import QtGui
from PySide import QtCore

import logging
logger = logging.getLogger(__name__)

from hyo.surveydatamonitor.monitor import SurveyDataMonitor
from hyo.soundspeedmanager.dialogs.dialog import AbstractDialog


class MonitorViewOption(AbstractDialog):

    def __init__(self, main_win, lib, monitor, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)
        if not isinstance(monitor, SurveyDataMonitor):
            raise RuntimeError("Passed invalid monitor object: %s" % type(lib))
        self._monitor = monitor

        self.setWindowTitle("Monitor Plotting Options")
        self.setMinimumWidth(160)

        # outline ui
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # label
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        self.max_samples_label = QtGui.QLabel("Plot latest samples:")
        hbox.addWidget(self.max_samples_label)
        hbox.addStretch()
        # slider
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
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

    @QtCore.Slot()
    def on_max_samples_changed(self):
        self.main_win.plotting_samples = self.max_samples.value()
        self.max_samples_label.setText("Plot latest %d samples:" % self.max_samples.value())
        logger.debug(self.main_win.plotting_samples)
        self.main_win.update_plot_data()
