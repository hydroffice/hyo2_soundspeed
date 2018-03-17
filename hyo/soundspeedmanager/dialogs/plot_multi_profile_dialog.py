from PySide import QtGui
from PySide import QtCore

import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'

from matplotlib import rc_context
from matplotlib import pyplot as plt

import logging
logger = logging.getLogger(__name__)

from hyo.soundspeedmanager.dialogs.dialog import AbstractDialog


class PlotMultiProfileDialog(AbstractDialog):

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
        'backend.qt4': 'PySide'
    }

    def __init__(self, main_win, lib, pks, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        # check the passed primary keys
        if type(pks) is not list:
            raise RuntimeError("The dialog takes a list of primary keys, not %s" % type(pks))
        if len(pks) < 2:
            raise RuntimeError("The dialog takes a list of at least 2 primary keys, not %s" % len(pks))
        self._pks = pks

        # the list of selected writers passed to the library
        self.selected_writers = list()

        self.setWindowTitle("Plot multiple profiles")
        self.setMinimumWidth(160)

        self.f_dpi = 120  # dots-per-inch
        self.f_sz = (3.0, 6.0)  # inches

        settings = QtCore.QSettings()

        # outline ui
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # plot sound speed
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        btn = QtGui.QPushButton("Plot sound speed")
        btn.setFixedWidth(200)
        btn.setMinimumHeight(32)
        hbox.addWidget(btn)
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_plot_sound_speed)
        hbox.addStretch()

        # plot temp
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        btn = QtGui.QPushButton("Plot temperature")
        btn.setFixedWidth(200)
        btn.setMinimumHeight(32)
        hbox.addWidget(btn)
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_plot_temperature)
        hbox.addStretch()

        # plot sal
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        btn = QtGui.QPushButton("Plot salinity")
        btn.setFixedWidth(200)
        btn.setMinimumHeight(32)
        hbox.addWidget(btn)
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_plot_salinity)
        hbox.addStretch()

    @classmethod
    def raise_window(cls):
        cfm = plt.get_current_fig_manager()
        cfm.window.activateWindow()
        cfm.window.raise_()

    def on_plot_sound_speed(self):
        logger.debug("plot sound speed")

        with rc_context(self.rc_context):

            plt.ion()

            # figure and canvas
            plt.close("Plot Sound Speed")
            fig = plt.figure("Plot Sound Speed", figsize=self.f_sz, dpi=self.f_dpi)
            fig.patch.set_alpha(0.0)
            ax = fig.add_subplot(111)
            ax.invert_yaxis()

            y_min = None
            y_max = None
            x_min = None
            x_max = None

            # actually do the export
            for pk in self._pks:

                success = self.lib.load_profile(pk, skip_atlas=True)
                if not success:

                    # noinspection PyCallByClass
                    QtGui.QMessageBox.warning(self, "Database", "Unable to load profile #%02d!" % pk, QtGui.QMessageBox.Ok)
                    continue

                _x_min = self.lib.cur.proc.speed[self.lib.cur.proc_valid].min()
                if x_min is None:
                    x_min = _x_min
                else:
                    x_min = min(x_min, _x_min)

                _x_max = self.lib.cur.proc.speed[self.lib.cur.proc_valid].max()
                if x_max is None:
                    x_max = _x_max
                else:
                    x_max = max(x_max, _x_max)

                _y_min = self.lib.cur.proc.depth[self.lib.cur.proc_valid].min()
                if y_min is None:
                    y_min = _y_min
                else:
                    y_min = min(y_min, _y_min)

                _y_max = self.lib.cur.proc.depth[self.lib.cur.proc_valid].max()
                if y_max is None:
                    y_max = _y_max
                else:
                    y_max = max(y_max, _y_max)

                _, = ax.plot(
                    self.lib.cur.proc.speed[self.lib.cur.proc_valid],
                    self.lib.cur.proc.depth[self.lib.cur.proc_valid],
                    label='#%03d' % pk
                )

            logger.debug("x: min %.2f, max %.2f" % (x_min, x_max))
            logger.debug("y: min %.2f, max %.2f" % (y_min, y_max))

            x_range = x_max - x_min
            y_range = y_max - y_min

            ax.legend(loc='lower left')
            plt.xlabel('Sound Speed [m/s]', fontsize=8)
            plt.ylabel('Depth [m]', fontsize=8)
            fig.get_axes()[0].set_xlim(x_min - 0.1*x_range, x_max + 0.1*x_range)
            fig.get_axes()[0].set_ylim(y_max + 0.15*y_range, y_min - 0.05*y_range)
            plt.grid()
            plt.show()

        self.accept()

    def on_plot_temperature(self):
        logger.debug("plot temperature")

        with rc_context(self.rc_context):

            plt.ion()

            # figure and canvas
            plt.close("Plot Temperature")
            fig = plt.figure("Plot Temperature", figsize=self.f_sz, dpi=self.f_dpi)
            fig.patch.set_alpha(0.0)
            ax = fig.add_subplot(111)
            ax.invert_yaxis()

            y_min = None
            y_max = None
            x_min = None
            x_max = None

            # actually do the export
            for pk in self._pks:

                success = self.lib.load_profile(pk, skip_atlas=True)
                if not success:

                    # noinspection PyCallByClass
                    QtGui.QMessageBox.warning(self, "Database", "Unable to load profile #%02d!" % pk, QtGui.QMessageBox.Ok)
                    continue

                _x_min = self.lib.cur.proc.temp[self.lib.cur.proc_valid].min()
                if x_min is None:
                    x_min = _x_min
                else:
                    x_min = min(x_min, _x_min)

                _x_max = self.lib.cur.proc.temp[self.lib.cur.proc_valid].max()
                if x_max is None:
                    x_max = _x_max
                else:
                    x_max = max(x_max, _x_max)

                _y_min = self.lib.cur.proc.depth[self.lib.cur.proc_valid].min()
                if y_min is None:
                    y_min = _y_min
                else:
                    y_min = min(y_min, _y_min)

                _y_max = self.lib.cur.proc.depth[self.lib.cur.proc_valid].max()
                if y_max is None:
                    y_max = _y_max
                else:
                    y_max = max(y_max, _y_max)

                _, = ax.plot(
                    self.lib.cur.proc.temp[self.lib.cur.proc_valid],
                    self.lib.cur.proc.depth[self.lib.cur.proc_valid],
                    label='#%03d' % pk
                )

            logger.debug("x: min %.2f, max %.2f" % (x_min, x_max))
            logger.debug("y: min %.2f, max %.2f" % (y_min, y_max))

            x_range = x_max - x_min
            y_range = y_max - y_min

            ax.legend(loc='lower left')
            plt.xlabel('Temperature [deg C]', fontsize=8)
            plt.ylabel('Depth [m]', fontsize=8)
            fig.get_axes()[0].set_xlim(x_min - 0.1*x_range, x_max + 0.1*x_range)
            fig.get_axes()[0].set_ylim(y_max + 0.15*y_range, y_min - 0.05*y_range)
            plt.grid()
            plt.show()

        self.accept()

    def on_plot_salinity(self):
        logger.debug("plot salinity")

        with rc_context(self.rc_context):

            plt.ion()

            # figure and canvas
            plt.close("Plot Salinity")
            fig = plt.figure("Plot Salinity", figsize=self.f_sz, dpi=self.f_dpi)
            fig.patch.set_alpha(0.0)
            ax = fig.add_subplot(111)
            ax.invert_yaxis()

            y_min = None
            y_max = None
            x_min = None
            x_max = None

            # actually do the export
            for pk in self._pks:

                success = self.lib.load_profile(pk, skip_atlas=True)
                if not success:

                    # noinspection PyCallByClass
                    QtGui.QMessageBox.warning(self, "Database", "Unable to load profile #%02d!" % pk, QtGui.QMessageBox.Ok)
                    continue

                _x_min = self.lib.cur.proc.sal[self.lib.cur.proc_valid].min()
                if x_min is None:
                    x_min = _x_min
                else:
                    x_min = min(x_min, _x_min)

                _x_max = self.lib.cur.proc.sal[self.lib.cur.proc_valid].max()
                if x_max is None:
                    x_max = _x_max
                else:
                    x_max = max(x_max, _x_max)

                _y_min = self.lib.cur.proc.depth[self.lib.cur.proc_valid].min()
                if y_min is None:
                    y_min = _y_min
                else:
                    y_min = min(y_min, _y_min)

                _y_max = self.lib.cur.proc.depth[self.lib.cur.proc_valid].max()
                if y_max is None:
                    y_max = _y_max
                else:
                    y_max = max(y_max, _y_max)

                _, = ax.plot(
                    self.lib.cur.proc.sal[self.lib.cur.proc_valid],
                    self.lib.cur.proc.depth[self.lib.cur.proc_valid],
                    label='#%03d' % pk
                )

            logger.debug("x: min %.2f, max %.2f" % (x_min, x_max))
            logger.debug("y: min %.2f, max %.2f" % (y_min, y_max))

            x_range = x_max - x_min
            y_range = y_max - y_min

            ax.legend(loc='lower left')
            plt.xlabel('Salinity [PSU]', fontsize=8)
            plt.ylabel('Depth [m]', fontsize=8)
            fig.get_axes()[0].set_xlim(x_min - 0.1*x_range, x_max + 0.1*x_range)
            fig.get_axes()[0].set_ylim(y_max + 0.15*y_range, y_min - 0.05*y_range)
            plt.grid()
            plt.show()

        self.accept()
