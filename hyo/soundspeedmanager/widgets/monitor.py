import matplotlib

matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4'] = 'PySide'

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavToolBar
from matplotlib.figure import Figure
from matplotlib import rc_context
from matplotlib import cm
from mpl_toolkits.basemap import Basemap
import numpy as np

from threading import Timer, Lock
from datetime import datetime, timedelta
import os
import logging

from PySide import QtGui, QtCore

logger = logging.getLogger(__name__)

from hyo.soundspeedmanager.widgets.widget import AbstractWidget
from hyo.soundspeedmanager.dialogs.export_data_monitor_dialog import ExportDataMonitorDialog
from hyo.surveydatamonitor import monitor


class SurveyDataMonitor(AbstractWidget):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.abspath(os.path.join(here, os.pardir, 'media')).replace("\\", "/")
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
        'lines.linewidth': 0.8,
        'grid.alpha': 0.2,
        'backend.qt4': 'PySide'
    }

    def __init__(self, main_win, lib, timing=2.0):
        AbstractWidget.__init__(self, main_win=main_win, lib=lib)
        self.monitor = monitor.SurveyDataMonitor(ssm=self.lib)
        self._plotting_timing = timing

        self._plotting_active = False
        self._plotting_pause = False
        self._last_nr_samples = 0

        # ###    ACTIONS   ###

        # ### Data Monitor ###

        self.monitor_bar = self.addToolBar('Data Monitor')
        self.monitor_bar.setIconSize(QtCore.QSize(40, 40))

        # start
        self.start_monitor_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'start.png')),
                                               'Start monitoring survey data', self)
        self.start_monitor_act.setShortcut('Alt+M')
        # noinspection PyUnresolvedReferences
        self.start_monitor_act.triggered.connect(self.on_start_monitor)
        self.monitor_bar.addAction(self.start_monitor_act)

        # pause
        self.pause_monitor_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'pause.png')),
                                               'Pause monitoring survey data', self)
        self.pause_monitor_act.setShortcut('Alt+P')
        # noinspection PyUnresolvedReferences
        self.pause_monitor_act.triggered.connect(self.on_pause_monitor)
        self.pause_monitor_act.setDisabled(True)
        self.monitor_bar.addAction(self.pause_monitor_act)

        # stop
        self.stop_monitor_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'stop.png')),
                                              'Stop monitoring survey data', self)
        self.stop_monitor_act.setShortcut('Alt+S')
        # noinspection PyUnresolvedReferences
        self.stop_monitor_act.triggered.connect(self.on_stop_monitor)
        self.stop_monitor_act.setDisabled(True)
        self.monitor_bar.addAction(self.stop_monitor_act)

        # ### Data Manager ###

        self.manager_bar = self.addToolBar('Data Manager')
        self.manager_bar.setIconSize(QtCore.QSize(40, 40))

        # open output folder
        self.open_output_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'load.png')),
                                             'Open output folder', self)
        self.open_output_act.setShortcut('Alt+O')
        # noinspection PyUnresolvedReferences
        self.open_output_act.triggered.connect(self.on_open_output)
        self.manager_bar.addAction(self.open_output_act)

        # add data
        self.add_data_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'import_data.png')),
                                          'Add data to the current data set', self)
        self.add_data_act.setShortcut('Alt+A')
        # noinspection PyUnresolvedReferences
        self.add_data_act.triggered.connect(self.on_add_data)
        self.manager_bar.addAction(self.add_data_act)

        # export data
        self.export_data_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'export_data.png')),
                                             'Export data', self)
        self.export_data_act.setShortcut('Alt+X')
        # noinspection PyUnresolvedReferences
        self.export_data_act.triggered.connect(self.on_export_data)
        self.manager_bar.addAction(self.export_data_act)

        # ### Data Views ###

        self.views_bar = self.addToolBar('Data Views')
        self.views_bar.setIconSize(QtCore.QSize(40, 40))

        # view tss vs time plot
        self.view_tss_time_plot_action = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'tss_plot.png')),
                                                       'View TSS vs time plot', self, checkable=True)
        self.view_tss_time_plot_action.setShortcut('Ctrl+T')
        # noinspection PyUnresolvedReferences
        self.view_tss_time_plot_action.triggered.connect(self.on_view_tss_time_plot)
        self.views_bar.addAction(self.view_tss_time_plot_action)

        # view draft vs time plot
        self.view_draft_time_plot_action = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'draft_plot.png')),
                                                         'View draft vs time plot', self, checkable=True)
        self.view_draft_time_plot_action.setShortcut('Ctrl+D')
        # noinspection PyUnresolvedReferences
        self.view_draft_time_plot_action.triggered.connect(self.on_view_draft_time_plot)
        self.views_bar.addAction(self.view_draft_time_plot_action)

        # view avg depth vs time plot
        self.view_avg_depth_time_plot_action = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'avg_depth_plot.png')),
                                                             'View avg depth vs time plot', self, checkable=True)
        self.view_avg_depth_time_plot_action.setShortcut('Ctrl+A')
        # noinspection PyUnresolvedReferences
        self.view_avg_depth_time_plot_action.triggered.connect(self.on_view_avg_depth_time_plot)
        self.views_bar.addAction(self.view_avg_depth_time_plot_action)

        # ###    PLOTS    ###

        # create the overall layout
        self.main_layout = QtGui.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.frame.setLayout(self.main_layout)

        # mpl settings
        self.f_dpi = 120  # dots-per-inch
        self.f_sz = (3.5, 2.5)  # inches
        self.f_map_sz = (4.5, 2.5)  # inches
        self.draft_color = '#00cc66'
        self.tss_color = '#3385ff'
        self.avg_depth_color = '#ffb266'

        # figures

        # ###   TSS VS TIME   ###

        self.w1 = QtGui.QWidget()
        vbox = QtGui.QVBoxLayout(self.w1)
        self.w1.setLayout(vbox)
        with rc_context(self.rc_context):

            self.f1 = Figure(figsize=self.f_sz, dpi=self.f_dpi)
            self.f1.patch.set_alpha(0.0)
            self.c1 = FigureCanvas(self.f1)
            self.c1.setParent(self.w1)
            self.c1.setFocusPolicy(QtCore.Qt.ClickFocus)  # key for press events!!!
            self.c1.setFocus()
            self.tss_ax = self.f1.add_subplot(111)
            # self.tss_ax.set_ylabel('Sound Speed [m/s]')
            # self.tss_ax.set_xlabel('Time')
            self.tss, = self.tss_ax.plot([], [],
                                         color=self.tss_color,
                                         linestyle='--',
                                         marker='o',
                                         label='TSS',
                                         ms=3
                                         )
            self.tss_ax.set_ylim(1450.0, 1550.0)
            self.tss_ax.set_xlim(datetime.now(), datetime.now() + timedelta(seconds=60))
            self.tss_ax.grid(True)
            # dates = matplotlib.dates.date2num(list_of_datetimes)
            self.nv1 = NavToolBar(canvas=self.c1, parent=self.w1, coordinates=True)
            self.nv1.setIconSize(QtCore.QSize(14, 14))
        vbox.addWidget(self.c1)
        vbox.addWidget(self.nv1)
        vbox.setContentsMargins(0, 0, 0, 0)
        self.dw1 = QtGui.QDockWidget("Surface Sound Speed vs. Time", self)
        self.dw1.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dw1)
        self.dw1.setWidget(self.w1)
        self.dw1.installEventFilter(self)

        # ###   DRAFT VS TIME   ###

        self.w2 = QtGui.QWidget()
        vbox = QtGui.QVBoxLayout(self.w2)
        self.w2.setLayout(vbox)
        with rc_context(self.rc_context):
            self.f2 = Figure(figsize=self.f_sz, dpi=self.f_dpi)
            self.f2.patch.set_alpha(0.0)
            self.c2 = FigureCanvas(self.f2)
            self.c2.setParent(self.w2)
            self.c2.setFocusPolicy(QtCore.Qt.ClickFocus)  # key for press events!!!
            self.c2.setFocus()
            self.draft_ax = self.f2.add_subplot(111, sharex=self.tss_ax)
            self.draft_ax.invert_yaxis()
            # self.draft_ax.set_ylabel('Depth [m]')
            # self.draft_ax.set_xlabel('Time')
            self.draft, = self.draft_ax.plot([], [],
                                             color=self.draft_color,
                                             linestyle='--',
                                             marker='o',
                                             label='TSS',
                                             ms=3
                                             )
            self.draft_ax.set_ylim(10.0, 0.0)
            self.draft_ax.set_xlim(datetime.now(), datetime.now() + timedelta(seconds=60))
            self.draft_ax.grid(True)
            self.nv2 = NavToolBar(canvas=self.c2, parent=self.w2, coordinates=True)
            self.nv2.setIconSize(QtCore.QSize(14, 14))
        vbox.addWidget(self.c2)
        vbox.addWidget(self.nv2)
        vbox.setContentsMargins(0, 0, 0, 0)
        self.dw2 = QtGui.QDockWidget("Transducer Depth vs. Time", self)
        self.dw2.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dw2)
        self.dw2.setWidget(self.w2)
        self.dw2.installEventFilter(self)

        # ###   AVG DEPTH VS TIME   ###

        self.w3 = QtGui.QWidget()
        vbox = QtGui.QVBoxLayout(self.w3)
        self.w3.setLayout(vbox)
        with rc_context(self.rc_context):
            self.f3 = Figure(figsize=self.f_sz, dpi=self.f_dpi)
            self.f3.patch.set_alpha(0.0)
            self.c3 = FigureCanvas(self.f3)
            self.c3.setParent(self.w3)
            self.c3.setFocusPolicy(QtCore.Qt.ClickFocus)  # key for press events!!!
            self.c3.setFocus()
            self.avg_depth_ax = self.f3.add_subplot(111, sharex=self.tss_ax)
            self.avg_depth_ax.invert_yaxis()
            # self.avg_depth_ax.set_ylabel('Depth [m]')
            # self.avg_depth_ax.set_xlabel('Time')
            self.avg_depth, = self.avg_depth_ax.plot([], [],
                                                    color=self.avg_depth_color,
                                                    linestyle='--',
                                                    marker='o',
                                                    label='Avg Depth',
                                                    ms=3
                                                    )
            self.avg_depth_ax.set_ylim(1000.0, 0.0)
            self.avg_depth_ax.set_xlim(datetime.now(), datetime.now() + timedelta(seconds=60))
            self.avg_depth_ax.grid(True)
            self.nv3 = NavToolBar(canvas=self.c3, parent=self.w3, coordinates=True)
            self.nv3.setIconSize(QtCore.QSize(14, 14))
        vbox.addWidget(self.c3)
        vbox.addWidget(self.nv3)
        vbox.setContentsMargins(0, 0, 0, 0)
        self.dw3 = QtGui.QDockWidget("Average Depth vs. Time", self)
        self.dw3.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dw3)
        self.dw3.setWidget(self.w3)
        self.dw3.installEventFilter(self)

        # ###   MAP   ###

        self.w0 = QtGui.QWidget()
        vbox = QtGui.QVBoxLayout(self.w0)
        self.w0.setLayout(vbox)
        with rc_context(self.rc_context):

            self.f0 = Figure(figsize=self.f_map_sz, dpi=self.f_dpi)
            self.f0.patch.set_alpha(0.0)
            self.c0 = FigureCanvas(self.f0)
            self.c0.setParent(self.w0)
            self.c0.setFocusPolicy(QtCore.Qt.ClickFocus)  # key for press events!!!
            self.c0.setFocus()
            self.map_ax = self.f0.add_subplot(111)
            self.map = Basemap(projection='kav7', lon_0=0, resolution='c', ax=self.map_ax)
            self.map.drawcoastlines(zorder=1)
            self.map.fillcontinents(color='lightgray', zorder=1)
            self.map.drawparallels(np.arange(-90., 120., 30.), color="#cccccc", labels=[False, True, True, False])
            self.map.drawmeridians(np.arange(0., 360., 60.), color="#cccccc", labels=[True, False, False, True])
            self.map_colormap = cm.get_cmap('gist_rainbow')
            self.map_points = self.map.scatter([], [], c=[], zorder=2, s=20,
                                               vmin=1450.0, vmax=1550.0, cmap=self.map_colormap)

            def format_coord(x, y):
                pair = self.map(x, y, inverse=True)
                return '%.6f, %.6f' % pair

            self.map_ax.format_coord = format_coord
            self.f0_colorbar = None
            self.nv0 = NavToolBar(canvas=self.c0, parent=self.w0, coordinates=True)
            self.nv0.setIconSize(QtCore.QSize(14, 14))

        vbox.addWidget(self.c0)
        vbox.addWidget(self.nv0)
        vbox.setContentsMargins(0, 0, 0, 0)
        self.dw0 = QtGui.QDockWidget("Surface Sound Speed Map", self)
        self.dw0.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dw0)
        self.dw0.setWidget(self.w0)
        self.dw0.installEventFilter(self)
        self.dw0.setHidden(True)

        # initial plot views
        self._make_tss_time_plot_visible(False)
        self._make_draft_time_plot_visible(False)
        self._make_avg_depth_time_plot_visible(False)

    def plotting(self):
        if not self._plotting_active:
            return

        if self._plotting_pause:
            logger.debug("pause")
            Timer(self._plotting_timing, self.plotting).start()
            return

        cur_nr_samples = self.monitor.nr_of_samples()
        if cur_nr_samples > self._last_nr_samples:
            logger.debug("plotting -> samples: %d" % cur_nr_samples)
            self._update_plot_data(cur_nr_samples)

        self._last_nr_samples = cur_nr_samples

        Timer(self._plotting_timing, self.plotting).start()

    def _refresh_plots(self):
        self.c1.draw()
        self.c2.draw()
        self.c3.draw()
        self.c0.draw()

        self.update()

    def _clear_plot_data(self):

        self.tss.set_xdata([])
        self.tss.set_ydata([])
        self.draft.set_xdata([])
        self.draft.set_ydata([])
        self.avg_depth.set_xdata([])
        self.avg_depth.set_ydata([])
        self.map_points = self.map.scatter([], [], c=[], zorder=2, s=20,
                                           vmin=1450.0, vmax=1550.0, cmap=self.map_colormap)

        self._refresh_plots()

    def _update_plot_data(self, nr_of_samples):

        if nr_of_samples < 2:
            return

        self.monitor.lock_data()

        self.tss.set_xdata(self.monitor.times)
        self.tss.set_ydata(self.monitor.tsss)
        self.draft.set_xdata(self.monitor.times)
        self.draft.set_ydata(self.monitor.drafts)
        self.avg_depth.set_xdata(self.monitor.times)
        self.avg_depth.set_ydata(self.monitor.depths)
        xs, ys = self.map(self.monitor.longs, self.monitor.lats)
        self.map_points = self.map.scatter(xs, ys,
                                           zorder=2, s=20,
                                           c=self.monitor.tsss,
                                           vmin=(min(self.monitor.tsss) - 0.1),
                                           vmax=(max(self.monitor.tsss) + 0.1),
                                           cmap=self.map_colormap, alpha=0.4)
        if self.f0_colorbar is None:

            with rc_context(self.rc_context):
                self.f0_colorbar = self.f0.colorbar(self.map_points, ax=self.map_ax, aspect=50,
                                                    orientation='horizontal', format='%.1f')
                self.f0_colorbar.solids.set(alpha=1)
                self.f0.tight_layout()

        vmin_tss, vmax_tss = self.monitor.calc_plot_good_tss()
        self.f0_colorbar.set_clim(vmin=vmin_tss, vmax=vmax_tss)

        self.tss_ax.set_xlim(min(self.monitor.times) - timedelta(seconds=10),
                             max(self.monitor.times) + timedelta(seconds=10))
        self.tss_ax.set_ylim(min(self.monitor.tsss) - 0.5,
                             max(self.monitor.tsss) + 0.5)
        # self.draft_ax.set_xlim(min(self.monitor.times) - timedelta(seconds=10),
        #                        max(self.monitor.times) + timedelta(seconds=10))
        self.draft_ax.set_ylim(max(self.monitor.drafts) + 0.5,
                               min(self.monitor.drafts) - 0.5)
        self.avg_depth_ax.set_ylim(max(self.monitor.depths) + 0.5,
                                   min(self.monitor.depths) - 0.5)

        self.monitor.unlock_data()

        self._refresh_plots()
        logger.debug("updated")

    def start_plotting(self):
        if self._plotting_pause:
            logger.debug("resume plotting")
            self._plotting_pause = False
            return

        self._plotting_active = True
        self._plotting_pause = False
        self._last_nr_samples = 0

        logger.debug("start plotting")

        self.plotting()

    def pause_plotting(self):
        self._plotting_active = True
        self._plotting_pause = True
        logger.debug("pause plotting")

    def stop_plotting(self):
        if self.monitor.active:
            self.monitor.stop_monitor()
        self._plotting_active = False
        self._plotting_pause = False
        logger.debug("stop plotting")

    # ### SLOTS ###

    # data monitor

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

        clear_data = True
        nr_of_samples = self.monitor.nr_of_samples()
        if nr_of_samples > 0:

            msg = "Some data are already present(%s samples)!\n\n" \
                  "Do you want to start a new monitoring session?\n" \
                  "If you click on No, the data will be appended." % nr_of_samples
            # noinspection PyCallByClass
            ret = QtGui.QMessageBox.warning(self, "Survey Data Monitor", msg,
                                            QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                clear_data = False

        if clear_data:
            self.monitor.clear_data()
            self._clear_plot_data()

        self.monitor.start_monitor(clear_data=clear_data)
        self.start_plotting()

        self.start_monitor_act.setEnabled(False)
        self.pause_monitor_act.setEnabled(True)
        self.stop_monitor_act.setEnabled(True)
        self._make_tss_time_plot_visible(True)
        self._make_draft_time_plot_visible(True)
        self._make_avg_depth_time_plot_visible(False)
        self.dw0.setVisible(True)

    def _make_tss_time_plot_visible(self, flag):
        if flag:
            self.dw1.setVisible(True)
            self.view_tss_time_plot_action.setChecked(True)
        else:
            self.dw1.setVisible(False)
            self.view_tss_time_plot_action.setChecked(False)

    def _make_draft_time_plot_visible(self, flag):
        if flag:
            self.dw2.setVisible(True)
            self.view_draft_time_plot_action.setChecked(True)
        else:
            self.dw2.setVisible(False)
            self.view_draft_time_plot_action.setChecked(False)

    def _make_avg_depth_time_plot_visible(self, flag):
        if flag:
            self.dw3.setVisible(True)
            self.view_avg_depth_time_plot_action.setChecked(True)
        else:
            self.dw3.setVisible(False)
            self.view_avg_depth_time_plot_action.setChecked(False)

    @QtCore.Slot()
    def on_pause_monitor(self):

        self.monitor.pause_monitor()
        self.pause_plotting()

        self.start_monitor_act.setEnabled(True)
        self.pause_monitor_act.setEnabled(False)
        self.stop_monitor_act.setEnabled(True)

    @QtCore.Slot()
    def on_stop_monitor(self):

        self.monitor.stop_monitor()
        self.stop_plotting()

        self.start_monitor_act.setEnabled(True)
        self.pause_monitor_act.setEnabled(False)
        self.stop_monitor_act.setEnabled(False)

        if self.monitor.nr_of_samples() == 0:
            self._make_tss_time_plot_visible(False)
            self._make_draft_time_plot_visible(False)
            self._make_avg_depth_time_plot_visible(False)
            self.dw0.setVisible(False)

    # data manager

    @QtCore.Slot()
    def on_open_output(self):
        self.monitor.open_output_folder()

    @QtCore.Slot()
    def on_add_data(self):
        logger.debug("Adding data")

        if self.monitor.active:

            msg = "The survey data monitoring is ongoing!\n\n" \
                  "To add data, you have to first stop the monitoring."
            # noinspection PyCallByClass
            QtGui.QMessageBox.warning(self, "Survey Data Monitor", msg, QtGui.QMessageBox.Ok)
            return

        # noinspection PyCallByClass
        selections, _ = QtGui.QFileDialog.getOpenFileNames(self, "Add data", self.monitor.output_folder,
                                                           "Monitor db(*.mon);;Kongsberg EM Series(*.all)")
        if not selections:
            return
        logger.debug("user selected %d files" % len(selections))

        # check if data are already present
        clear_data = False
        nr_of_samples = self.monitor.nr_of_samples()
        if nr_of_samples > 0:

            msg = "Some data are already present(%s samples)!\n\n" \
                  "Do you want to merge the new samples with the existing ones?\n" \
                  "If you click on No, a different session will be used." % nr_of_samples
            # noinspection PyCallByClass
            ret = QtGui.QMessageBox.warning(self, "Survey Data Monitor", msg,
                                            QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                clear_data = True

        if clear_data:
            self.monitor.clear_data()
            self._clear_plot_data()

        file_ext = os.path.splitext(selections[0])[-1]
        if file_ext == ".mon":

            self.progress.start(title="Survey Data Monitor", text="Database data loading")
            self.progress.update(20)
            self.monitor.add_db_data(filenames=selections)
            self.progress.end()

        elif file_ext == ".all":

            self.progress.start(title="Survey Data Monitor", text="Kongsberg data loading")
            self.progress.update(20)
            self.monitor.add_kongsberg_data(filenames=selections)
            self.progress.end()

        else:
            raise RuntimeError("Passed unsupported file extension: %s" % file_ext)

        nr_of_samples = self.monitor.nr_of_samples()
        self._update_plot_data(nr_of_samples=nr_of_samples)
        if nr_of_samples > 2:
            self.dw1.setVisible(True)
            self.dw2.setVisible(True)
            self.w0.setVisible(True)

    @QtCore.Slot()
    def on_export_data(self):
        logger.debug("Exporting data")

        nr_of_samples = self.monitor.nr_of_samples()
        if nr_of_samples == 0:
            msg = "There are currently not samples to export!\n"
            # noinspection PyCallByClass
            QtGui.QMessageBox.warning(self, "Survey Data Monitor", msg, QtGui.QMessageBox.Ok)
            return

        dlg = ExportDataMonitorDialog(lib=self.lib, monitor=self.monitor, main_win=self.main_win, parent=self)
        dlg.exec_()

    # data views

    @QtCore.Slot()
    def on_view_tss_time_plot(self):
        if self.dw1.isVisible():
            self._make_tss_time_plot_visible(False)
        else:
            self._make_tss_time_plot_visible(True)

        self._refresh_plots()

    @QtCore.Slot()
    def on_view_draft_time_plot(self):
        if self.dw2.isVisible():
            self._make_draft_time_plot_visible(False)
        else:
            self._make_draft_time_plot_visible(True)

        self._refresh_plots()

    @QtCore.Slot()
    def on_view_avg_depth_time_plot(self):
        if self.dw3.isVisible():
            self._make_avg_depth_time_plot_visible(False)
        else:
            self._make_avg_depth_time_plot_visible(True)

        self._refresh_plots()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Resize:
            self._refresh_plots()

        super().eventFilter(obj, event)