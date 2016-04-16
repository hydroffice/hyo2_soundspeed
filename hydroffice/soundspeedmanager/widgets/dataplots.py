from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

import numpy as np
from PySide import QtGui
from PySide import QtCore
from matplotlib import rcParams
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Tahoma', 'Bitstream Vera Sans', 'Lucida Grande', 'Verdana']
rcParams['font.size'] = 9
rcParams['figure.titlesize'] = rcParams['font.size'] + 1
rcParams['axes.labelsize'] = rcParams['font.size']
rcParams['legend.fontsize'] = rcParams['font.size'] - 1
rcParams['xtick.labelsize'] = rcParams['font.size'] - 2
rcParams['ytick.labelsize'] = rcParams['font.size'] - 2
rcParams['axes.linewidth'] = 0.5
rcParams['axes.xmargin'] = 0.01
rcParams['axes.ymargin'] = 0.01
rcParams['backend.qt4'] = 'PySide'
import matplotlib
matplotlib.use('Qt4Agg')

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

logger = logging.getLogger(__name__)

from .widget import AbstractWidget
from .navtoolbar import NavToolbar


class DataPlots(AbstractWidget):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win, prj):
        AbstractWidget.__init__(self, main_win=main_win, prj=prj)

        # mpl figure settings
        self.f_dpi = 120  # dots-per-inch
        self.f_sz = (6.0, 3.0)  # inches
        self.vi = None  # valid indices
        self.ii = None  # invalid indices
        self.draft_color = '#00cc66'
        self.seafloor_color = '#cc6600'
        self.sensor_color = '#00cc66'
        self.valid_color = '#3385ff'
        self.invalid_color = '#dddddd'
        self.woa09_color = '#ffaaaa'
        self.woa13_color = '#ffcc66'
        self.rtofs_color = '#99cc00'
        self.ref_color = '#ff6600'

        # outline ui
        self.top_widget = QtGui.QWidget()
        self.setCentralWidget(self.top_widget)
        self.vbox = QtGui.QVBoxLayout()
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.top_widget.setLayout(self.vbox)

        # figure and canvas
        self.f = Figure(figsize=self.f_sz, dpi=self.f_dpi)
        self.f.patch.set_alpha(0.0)
        self.c = FigureCanvas(self.f)
        self.c.setParent(self.top_widget)
        self.c.setFocusPolicy(QtCore.Qt.ClickFocus)  # key for press events!!!
        self.c.setFocus()
        self.vbox.addWidget(self.c)
        # axes
        self.speed_ax = self.f.add_subplot(131)
        self.speed_ax.invert_yaxis()
        self.temp_ax = self.f.add_subplot(132, sharey=self.speed_ax)
        self.temp_ax.invert_yaxis()
        self.sal_ax = self.f.add_subplot(133, sharey=self.speed_ax)
        self.sal_ax.invert_yaxis()
        # lines
        self.speed_draft = None
        self.speed_sensor = None
        self.speed_seafloor = None
        self.speed_woa09 = None
        self.temp_woa09 = None
        self.sal_woa09 = None
        self.speed_woa09_min = None
        self.temp_woa09_min = None
        self.sal_woa09_min = None
        self.speed_woa09_max = None
        self.temp_woa09_max = None
        self.sal_woa09_max = None
        self.speed_woa13 = None
        self.temp_woa13 = None
        self.sal_woa13 = None
        self.speed_woa13_min = None
        self.temp_woa13_min = None
        self.sal_woa13_min = None
        self.speed_woa13_max = None
        self.temp_woa13_max = None
        self.sal_woa13_max = None
        self.speed_rtofs = None
        self.temp_rtofs = None
        self.sal_rtofs = None
        self.speed_ref = None
        self.temp_ref = None
        self.sal_ref = None
        self.speed_valid = None
        self.temp_valid = None
        self.sal_valid = None
        self.speed_invalid = None
        self.temp_invalid = None
        self.sal_invalid = None
        # events

        # toolbar
        self.hbox = QtGui.QHBoxLayout()
        self.vbox.addLayout(self.hbox)
        # navigation
        self.nav = NavToolbar(canvas=self.c, parent=self.top_widget, plot_win=self, prj=self.prj)
        self.hbox.addWidget(self.nav)

        # # timer for updates
        # timer = QtCore.QTimer(self)
        # timer.timeout.connect(self.on_draw)
        # timer.start(500)

        self.on_draw()

    def _draw_grid(self):
        for a in self.f.get_axes():
            a.grid(True)

    def _draw_speed(self):
        self.speed_ax.clear()
        self.speed_ax.set_ylabel('Depth [m]')
        self.speed_ax.set_xlabel('Sound Speed [m/s]')
        if self.prj.cur.woa09:
            self.speed_woa09, = self.speed_ax.plot(self.prj.cur.woa09.l[0].proc.speed,
                                                   self.prj.cur.woa09.l[0].proc.depth,
                                                   color=self.woa09_color,
                                                   linestyle='--'
                                                   )
            if self.prj.cur.woa09.l[1]:
                self.speed_woa09_min, = self.speed_ax.plot(self.prj.cur.woa09.l[1].proc.speed,
                                                           self.prj.cur.woa09.l[1].proc.depth,
                                                           color=self.woa09_color,
                                                           linestyle=':'
                                                           )
            if self.prj.cur.woa09.l[2]:
                self.speed_woa09_max, = self.speed_ax.plot(self.prj.cur.woa09.l[2].proc.speed,
                                                           self.prj.cur.woa09.l[2].proc.depth,
                                                           color=self.woa09_color,
                                                           linestyle=':'
                                                           )
        if self.prj.cur.woa13:
            self.speed_woa13, = self.speed_ax.plot(self.prj.cur.woa13.l[0].proc.speed,
                                                   self.prj.cur.woa13.l[0].proc.depth,
                                                   color=self.woa13_color,
                                                   linestyle='--'
                                                   )
            if self.prj.cur.woa13.l[1]:
                self.speed_woa13_min, = self.speed_ax.plot(self.prj.cur.woa13.l[1].proc.speed,
                                                           self.prj.cur.woa13.l[1].proc.depth,
                                                           color=self.woa13_color,
                                                           linestyle=':'
                                                           )
            if self.prj.cur.woa13.l[2]:
                self.speed_woa13_max, = self.speed_ax.plot(self.prj.cur.woa13.l[2].proc.speed,
                                                           self.prj.cur.woa13.l[2].proc.depth,
                                                           color=self.woa13_color,
                                                           linestyle=':'
                                                           )
        if self.prj.cur.rtofs:
            self.speed_rtofs, = self.speed_ax.plot(self.prj.cur.rtofs.l[0].proc.speed,
                                                   self.prj.cur.rtofs.l[0].proc.depth,
                                                   color=self.rtofs_color,
                                                   linestyle='--'
                                                   )
        if self.prj.has_ref():
            self.speed_ref, = self.speed_ax.plot(self.prj.ref.l[0].proc.speed,
                                                 self.prj.ref.l[0].proc.depth,
                                                 color=self.ref_color,
                                                 linestyle='--'
                                                 )
        self.speed_invalid, = self.speed_ax.plot(self.prj.cur.proc.speed[self.ii],
                                                 self.prj.cur.proc.depth[self.ii],
                                                 color=self.invalid_color,
                                                 linestyle='None',
                                                 marker='o',
                                                 alpha=0.5,
                                                 ms=1,
                                                 picker=3)
        self.speed_valid, = self.speed_ax.plot(self.prj.cur.proc.speed[self.vi],
                                               self.prj.cur.proc.depth[self.vi],
                                               color=self.valid_color,
                                               picker=3)
        self.speed_draft = self.speed_ax.axhline(y=None, linewidth=1.5, color=self.draft_color, linestyle=':')
        self.speed_sensor = self.speed_ax.axvline(x=None, linewidth=1.5, color=self.sensor_color, linestyle=':')
        self.speed_seafloor = self.speed_ax.axhline(y=None, linewidth=1.5, color=self.seafloor_color, linestyle=':')
        self.speed_ax.set_label("speed")

    def _draw_temp(self):
        self.temp_ax.clear()
        self.temp_ax.set_xlabel('Temperature [deg C]')
        if self.prj.cur.woa09:
            self.temp_woa09, = self.temp_ax.plot(self.prj.cur.woa09.l[0].proc.temp,
                                                 self.prj.cur.woa09.l[0].proc.depth,
                                                 color=self.woa09_color,
                                                 linestyle='--'
                                                 )
            if self.prj.cur.woa09.l[1]:
                self.temp_woa09_min, = self.temp_ax.plot(self.prj.cur.woa09.l[1].proc.temp,
                                                         self.prj.cur.woa09.l[1].proc.depth,
                                                         color=self.woa09_color,
                                                         linestyle=':'
                                                         )
            if self.prj.cur.woa09.l[2]:
                self.temp_woa09_max, = self.temp_ax.plot(self.prj.cur.woa09.l[2].proc.temp,
                                                         self.prj.cur.woa09.l[2].proc.depth,
                                                         color=self.woa09_color,
                                                         linestyle=':'
                                                         )
        if self.prj.cur.woa13:
            self.temp_woa13, = self.temp_ax.plot(self.prj.cur.woa13.l[0].proc.temp,
                                                 self.prj.cur.woa13.l[0].proc.depth,
                                                 color=self.woa13_color,
                                                 linestyle='--'
                                                 )
            if self.prj.cur.woa13.l[1]:
                self.temp_woa13_min, = self.temp_ax.plot(self.prj.cur.woa13.l[1].proc.temp,
                                                          self.prj.cur.woa13.l[1].proc.depth,
                                                          color=self.woa13_color,
                                                          linestyle=':'
                                                          )
            if self.prj.cur.woa13.l[2]:
                self.temp_woa13_max, = self.temp_ax.plot(self.prj.cur.woa13.l[2].proc.temp,
                                                         self.prj.cur.woa13.l[2].proc.depth,
                                                         color=self.woa13_color,
                                                         linestyle=':'
                                                         )
        if self.prj.cur.rtofs:
            self.temp_rtofs, = self.temp_ax.plot(self.prj.cur.rtofs.l[0].proc.temp,
                                                 self.prj.cur.rtofs.l[0].proc.depth,
                                                 color=self.rtofs_color,
                                                 linestyle='--'
                                                 )
        if self.prj.has_ref():
            self.temp_ref, = self.temp_ax.plot(self.prj.ref.l[0].proc.temp,
                                               self.prj.ref.l[0].proc.depth,
                                               color=self.ref_color,
                                               linestyle='--'
                                               )
        self.temp_invalid, = self.temp_ax.plot(self.prj.cur.proc.temp[self.ii],
                                               self.prj.cur.proc.depth[self.ii],
                                               color=self.invalid_color,
                                               linestyle='None',
                                               marker='o',
                                               alpha=0.5,
                                               ms=1,
                                               picker=3)
        self.temp_valid, = self.temp_ax.plot(self.prj.cur.proc.temp[self.vi],
                                             self.prj.cur.proc.depth[self.vi],
                                             color=self.valid_color,
                                             picker=3)
        self.temp_ax.set_label("temp")
        # hide y-labels
        [label.set_visible(False) for label in self.temp_ax.get_yticklabels()]

    def _draw_sal(self):
        self.sal_ax.clear()
        self.sal_ax.set_xlabel('Salinity [PSU]')
        if self.prj.cur.woa09:
            self.sal_woa09, = self.sal_ax.plot(self.prj.cur.woa09.l[0].proc.sal,
                                               self.prj.cur.woa09.l[0].proc.depth,
                                               color=self.woa09_color,
                                               linestyle='--'
                                               )
            if self.prj.cur.woa09.l[1]:
                self.sal_woa09_min, = self.sal_ax.plot(self.prj.cur.woa09.l[1].proc.sal,
                                                       self.prj.cur.woa09.l[1].proc.depth,
                                                       color=self.woa09_color,
                                                       linestyle=':'
                                                       )
            if self.prj.cur.woa09.l[2]:
                self.sal_woa09_max, = self.sal_ax.plot(self.prj.cur.woa09.l[2].proc.sal,
                                                       self.prj.cur.woa09.l[2].proc.depth,
                                                       color=self.woa09_color,
                                                       linestyle=':'
                                                       )
        if self.prj.cur.woa13:
            self.sal_woa13, = self.sal_ax.plot(self.prj.cur.woa13.l[0].proc.sal,
                                               self.prj.cur.woa13.l[0].proc.depth,
                                               color=self.woa13_color,
                                               linestyle='--'
                                               )
            if self.prj.cur.woa13.l[1]:
                self.sal_woa13_min, = self.sal_ax.plot(self.prj.cur.woa13.l[1].proc.sal,
                                                       self.prj.cur.woa13.l[1].proc.depth,
                                                       color=self.woa13_color,
                                                       linestyle=':'
                                                       )
            if self.prj.cur.woa13.l[2]:
                self.sal_woa13_max, = self.sal_ax.plot(self.prj.cur.woa13.l[2].proc.sal,
                                                       self.prj.cur.woa13.l[2].proc.depth,
                                                       color=self.woa13_color,
                                                       linestyle=':'
                                                       )
        if self.prj.cur.rtofs:
            self.sal_rtofs, = self.sal_ax.plot(self.prj.cur.rtofs.l[0].proc.sal,
                                               self.prj.cur.rtofs.l[0].proc.depth,
                                               color=self.rtofs_color,
                                               linestyle='--'
                                               )
        if self.prj.has_ref():
            self.sal_ref, = self.sal_ax.plot(self.prj.ref.l[0].proc.sal,
                                             self.prj.ref.l[0].proc.depth,
                                             color=self.ref_color,
                                             linestyle='--'
                                             )
        self.sal_invalid, = self.sal_ax.plot(self.prj.cur.proc.sal[self.ii],
                                             self.prj.cur.proc.depth[self.ii],
                                             color=self.invalid_color,
                                             linestyle='None',
                                             marker='o',
                                             alpha=0.5,
                                             ms=1,
                                             picker=3)
        self.sal_valid, = self.sal_ax.plot(self.prj.cur.proc.sal[self.vi],
                                           self.prj.cur.proc.depth[self.vi],
                                           color=self.valid_color,
                                           picker=3)
        self.sal_ax.set_label("sal")
        # hide y-labels
        [label.set_visible(False) for label in self.sal_ax.get_yticklabels()]

    def on_draw(self):
        """Redraws the figure"""
        if self.prj.cur_file:
            self.f.suptitle(self.prj.cur_file)

        if self.prj.cur:
            self.update_validity_indices()
            self._draw_speed()
            self._draw_temp()
            self._draw_sal()

        self._draw_grid()

        # limits
        if self.prj.use_sis():  # in case of SIS enabled
            if self.prj.listeners.sis.xyz88:
                y_limits = self.speed_ax.get_ylim()
                x_limits = self.speed_ax.get_xlim()
                print(y_limits, x_limits)
                # y-limits
                mean_depth = self.prj.listeners.sis.xyz88.mean_depth
                if mean_depth:
                    mean_depth *= 0.1
                else:
                    mean_depth = 0
                if mean_depth > y_limits[0]:
                    max_depth = mean_depth
                else:
                    max_depth = y_limits[0]
                self.speed_ax.set_ylim([max_depth, -30])
                # x-limits
                # TODO

        self.c.draw()

    def update_data(self):
        """Update plot"""
        self.update_validity_indices()
        # speed
        if self.speed_valid:
            self.speed_valid.set_xdata(self.prj.cur.proc.speed[self.vi])
            self.speed_valid.set_ydata(self.prj.cur.proc.depth[self.vi])
        if self.speed_invalid:
            self.speed_invalid.set_xdata(self.prj.cur.proc.speed[self.ii])
            self.speed_invalid.set_ydata(self.prj.cur.proc.depth[self.ii])
        # temp
        if self.temp_valid:
            self.temp_valid.set_xdata(self.prj.cur.proc.temp[self.vi])
            self.temp_valid.set_ydata(self.prj.cur.proc.depth[self.vi])
        if self.temp_invalid:
            self.temp_invalid.set_xdata(self.prj.cur.proc.temp[self.ii])
            self.temp_invalid.set_ydata(self.prj.cur.proc.depth[self.ii])
        # sal
        if self.sal_valid:
            self.sal_valid.set_xdata(self.prj.cur.proc.sal[self.vi])
            self.sal_valid.set_ydata(self.prj.cur.proc.depth[self.vi])
        if self.sal_invalid:
            self.sal_invalid.set_xdata(self.prj.cur.proc.sal[self.ii])
            self.sal_invalid.set_ydata(self.prj.cur.proc.depth[self.ii])

        if not self.prj.use_sis():  # in case that SIS was disabled
            if self.speed_draft:
                self.speed_draft.set_ydata(None)
            if self.speed_sensor:
                self.speed_sensor.set_xdata(None)
            return

        # it means that data have not been plotted
        if (not self.speed_draft) or (not self.speed_sensor) or (not self.speed_seafloor):
            return

        if self.prj.listeners.sis.xyz88 is None:
            self.speed_draft.set_ydata(None)
            self.speed_sensor.set_xdata(None)
        else:
            # sensor speed
            if self.prj.listeners.sis.xyz88.sound_speed is None:
                self.speed_sensor.set_xdata(None)
            else:
                self.speed_sensor.set_xdata([self.prj.listeners.sis.xyz88.sound_speed, ])
            # draft
            if self.prj.listeners.sis.xyz88.transducer_draft is None:
                self.speed_draft.set_ydata(None)
            else:
                self.speed_draft.set_ydata([self.prj.listeners.sis.xyz88.transducer_draft, ])
            # seafloor
            mean_depth = self.prj.listeners.sis.xyz88.mean_depth
            if mean_depth:
                self.speed_seafloor.set_ydata([mean_depth, ])
            else:
                self.speed_seafloor.set_ydata(None)

    def redraw(self):
        """Redraw the canvases, update the locators"""
        for a in self.c.figure.get_axes():
            xaxis = getattr(a, 'xaxis', None)
            yaxis = getattr(a, 'yaxis', None)
            locators = []
            if xaxis is not None:
                locators.append(xaxis.get_major_locator())
                locators.append(xaxis.get_minor_locator())
            if yaxis is not None:
                locators.append(yaxis.get_major_locator())
                locators.append(yaxis.get_minor_locator())

            for loc in locators:
                loc.refresh()
        self.c.draw_idle()

    def update_validity_indices(self):
        self.vi = self.prj.cur.proc_valid  # valid indices
        self.ii = np.logical_and(~self.vi, ~self.prj.cur.proc_invalid_direction)  # selected invalid indices

    def set_invalid_visibility(self, value):
        self.speed_invalid.set_visible(value)
        self.temp_invalid.set_visible(value)
        self.sal_invalid.set_visible(value)

    def reset(self):
        self.nav.reset()
