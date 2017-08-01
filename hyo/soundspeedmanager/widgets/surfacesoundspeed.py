import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4'] = 'PySide'

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import rc_context

import os
import logging

from PySide import QtGui, QtCore

logger = logging.getLogger(__name__)

from hyo.soundspeedmanager.widgets.widget import AbstractWidget


class SurfaceSoundSpeed(AbstractWidget):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')
    font_size = 6
    rc_context = {
        'font.family': 'sans-serif',
        'font.sans-serif': ['Tahoma', 'Bitstream Vera Sans', 'Lucida Grande', 'Verdana'],
        'font.size': font_size,
        'figure.titlesize': font_size + 1,
        'axes.labelsize': font_size,
        'legend.fontsize': font_size,
        'xtick.labelsize': font_size - 1,
        'ytick.labelsize': font_size - 1,
        'axes.linewidth': 0.5,
        'axes.xmargin': 0.01,
        'axes.ymargin': 0.01,
        'lines.linewidth': 1.0,
        'grid.alpha': 0.2,
        'backend.qt4': 'PySide'
    }

    def __init__(self, main_win, lib):
        AbstractWidget.__init__(self, main_win=main_win, lib=lib)

        self.monitor_bar = self.addToolBar('Monitor')
        self.monitor_bar.setIconSize(QtCore.QSize(40, 40))

        # start
        self.start_monitor_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'start.png')),
                                               'Start monitoring the surface sound speed', self)
        self.start_monitor_act.setShortcut('Alt+M')
        # noinspection PyUnresolvedReferences
        self.start_monitor_act.triggered.connect(self.on_start_monitor)
        self.monitor_bar.addAction(self.start_monitor_act)

        # pause
        self.pause_monitor_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'pause.png')),
                                               'Pause monitoring the surface sound speed', self)
        self.pause_monitor_act.setShortcut('Alt+P')
        # noinspection PyUnresolvedReferences
        self.pause_monitor_act.triggered.connect(self.on_pause_monitor)
        self.pause_monitor_act.setDisabled(True)
        self.monitor_bar.addAction(self.pause_monitor_act)

        # stop
        self.stop_monitor_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'stop.png')),
                                              'Stop monitoring the surface sound speed', self)
        self.stop_monitor_act.setShortcut('Alt+S')
        # noinspection PyUnresolvedReferences
        self.stop_monitor_act.triggered.connect(self.on_stop_monitor)
        self.stop_monitor_act.setDisabled(True)
        self.monitor_bar.addAction(self.stop_monitor_act)

        # create the overall layout
        self.main_layout = QtGui.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.frame.setLayout(self.main_layout)

        # mpl figure settings
        self.f_dpi = 120  # dots-per-inch
        self.f_sz = (6.0, 3.0)  # inches
        self.svi = None  # sis valid indices
        self.vi = None  # proc valid indices
        self.ii = None  # proc invalid indices
        self.draft_color = '#00cc66'
        self.seafloor_color = '#cc6600'
        self.sensor_color = '#00cc66'
        self.valid_color = '#3385ff'
        self.invalid_color = '#999966'
        self.woa09_color = '#ffaaaa'
        self.woa13_color = '#ffcc66'
        self.rtofs_color = '#99cc00'
        self.ref_color = '#ff6600'
        self.sis_color = '#0000e6'

        # figure and canvas

        with rc_context(self.rc_context):
            self.f3 = Figure(figsize=self.f_sz, dpi=self.f_dpi)
            self.f3.patch.set_alpha(0.0)
            self.c3 = FigureCanvas(self.f3)
            self.c3.setParent(self)
            self.c3.setFocusPolicy(QtCore.Qt.ClickFocus)  # key for press events!!!
            self.c3.setFocus()
            self.c3.setHidden(True)
        self.main_layout.addWidget(self.c3)

        self.dw1 = QtGui.QDockWidget("Surface Sound Speed vs. Time", self)
        self.dw1.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        with rc_context(self.rc_context):
            self.f1 = Figure(figsize=self.f_sz, dpi=self.f_dpi)
            self.f1.patch.set_alpha(0.0)
            self.c1 = FigureCanvas(self.f1)
            self.c1.setParent(self.dw1)
            self.c1.setFocusPolicy(QtCore.Qt.ClickFocus)  # key for press events!!!
            self.c1.setFocus()
        self.dw1.setHidden(True)
        self.dw1.setWidget(self.c1)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dw1)

        self.dw2 = QtGui.QDockWidget("Transducer Depth vs. Time", self)
        self.dw2.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        with rc_context(self.rc_context):
            self.f2 = Figure(figsize=self.f_sz, dpi=self.f_dpi)
            self.f2.patch.set_alpha(0.0)
            self.c2 = FigureCanvas(self.f2)
            self.c2.setParent(self.dw2)
            self.c2.setFocusPolicy(QtCore.Qt.ClickFocus)  # key for press events!!!
            self.c2.setFocus()
        self.dw2.setHidden(True)
        self.dw2.setWidget(self.c2)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dw2)

    @QtCore.Slot()
    def on_start_monitor(self):

        if not self.lib.use_sis():

            msg = "The SIS listener is disabled!\n\n" \
                  "To activate the listening, go to \"Setup\" tab, then \"Input\" sub-tab."
            # noinspection PyCallByClass
            QtGui.QMessageBox.warning(self, "Sound Speed Manager - SIS", msg, QtGui.QMessageBox.Ok)
            return

        if not self.lib.listen_sis():

            msg = "Unable to listen SIS!\n\nDouble check the SSM-SIS configuration."
            # noinspection PyCallByClass
            QtGui.QMessageBox.warning(self, "Sound Speed Manager - SIS", msg,
                                      QtGui.QMessageBox.Ok)
            return

        self.lib.monitor.start_monitor()

        self.start_monitor_act.setEnabled(False)
        self.pause_monitor_act.setEnabled(True)
        self.stop_monitor_act.setEnabled(True)
        self.dw1.setVisible(True)
        self.dw2.setVisible(True)
        self.c3.setVisible(True)

    @QtCore.Slot()
    def on_pause_monitor(self):

        self.lib.monitor.pause_monitor()

        self.start_monitor_act.setEnabled(True)
        self.pause_monitor_act.setEnabled(False)
        self.stop_monitor_act.setEnabled(True)

    @QtCore.Slot()
    def on_stop_monitor(self):

        self.lib.monitor.stop_monitor()

        self.start_monitor_act.setEnabled(True)
        self.pause_monitor_act.setEnabled(False)
        self.stop_monitor_act.setEnabled(False)
        self.dw1.setVisible(False)
        self.dw2.setVisible(False)
        self.c3.setVisible(False)
