from __future__ import absolute_import, division, print_function, unicode_literals

import os
import numpy as np
from matplotlib import rcParams
rcParams.update(
    {
        'font.family': 'sans-serif',
        'font.size': 9
    }
)
rcParams['backend.qt4'] = 'PySide'
import matplotlib
matplotlib.use('Qt4Agg')

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
import logging

logger = logging.getLogger(__name__)


class PlotDb(object):
    """Class that plots sound speed db data"""

    def __init__(self, db):
        self.db = db

    @classmethod
    def raise_window(cls):
        cfm = plt.get_current_fig_manager()
        cfm.window.activateWindow()
        cfm.window.raise_()

    @classmethod
    def plots_folder(cls, output_folder):
        folder = os.path.join(output_folder, "plots")
        if not os.path.exists(folder):
            os.makedirs(folder)
        return folder

    def map_profiles(self, output_folder, save_fig=False):
        """plot all the ssp in the database"""

        if not save_fig:
            plt.ion()

        rows = self.db.list_profiles()
        if rows is None:
            raise RuntimeError("Unable to retrieve ssp view rows > Empty database?")
        if len(rows) == 0:
            raise RuntimeError("Unable to retrieve ssp view rows > Empty database?")

        # prepare the data
        ssp_x = list()
        ssp_y = list()
        ssp_label = list()
        for row in rows:
            ssp_x.append(row[2].x)
            ssp_y.append(row[2].y)
            ssp_label.append(row[0])
        ssp_x_min = min(ssp_x)
        ssp_x_max = max(ssp_x)
        ssp_x_mean = (ssp_x_min + ssp_x_max) / 2
        ssp_x_delta = max(0.05, abs(ssp_x_max - ssp_x_min) / 5)
        ssp_y_min = min(ssp_y)
        ssp_y_max = max(ssp_y)
        # ssp_y_mean = (ssp_y_min + ssp_y_max) / 2
        ssp_y_delta = max(0.05, abs(ssp_y_max - ssp_y_min) / 5)
        logger.info("data boundary: %.4f, %.4f (%.4f) / %.4f, %.4f (%.4f)"
                    % (ssp_x_min, ssp_x_max, ssp_x_delta, ssp_y_min, ssp_y_max, ssp_y_delta))

        # make the world map
        fig = plt.figure()
        # plt.title("SSP Map (%s profiles)" % len(view_rows))
        ax = fig.add_subplot(111)
        plt.ioff()

        wm = self._world_draw_map()
        # x, y = wm(ssp_x_mean, ssp_y_mean)
        # wm.scatter(x, y, s=18, color='y')

        if ssp_x_mean > 0:
            ssp_loc = 2
        else:
            ssp_loc = 1

        max_delta_range = max(abs(ssp_x_min - ssp_x_max), abs(ssp_y_min - ssp_y_max))
        logger.info("maximum delta range: %s" % max_delta_range)

        if max_delta_range > 50:
            ins_scale = 0  # no inset
        elif max_delta_range > 15:
            ins_scale = 6
        elif max_delta_range > 12:
            ins_scale = 9
        elif max_delta_range > 6:
            ins_scale = 12
        elif max_delta_range > 3:
            ins_scale = 15
            ssp_x_delta *= 2
            ssp_y_delta *= 2
        elif max_delta_range > 1:
            ins_scale = 18
            ssp_x_delta *= 5
            ssp_y_delta *= 5
        elif max_delta_range > 0.1:
            ins_scale = 21
            ssp_x_delta *= 10
            ssp_y_delta *= 10
        else:
            ins_scale = 24
            ssp_x_delta *= 40
            ssp_y_delta *= 40

        # to avoid inset for too large area
        if ins_scale != 0:

            ax_ins = zoomed_inset_axes(ax, ins_scale, loc=ssp_loc)
            ax_ins.set_xlim((ssp_x_min - ssp_x_delta), (ssp_x_max + ssp_x_delta))
            ax_ins.set_ylim((ssp_y_min - ssp_y_delta), (ssp_y_max + ssp_y_delta))

            m = self._inset_draw_map(llcrnrlon=(ssp_x_min - ssp_x_delta), llcrnrlat=(ssp_y_min - ssp_y_delta),
                                     urcrnrlon=(ssp_x_max + ssp_x_delta), urcrnrlat=(ssp_y_max + ssp_y_delta),
                                     ax_ins=ax_ins)

            x, y = m(ssp_x, ssp_y)
            m.scatter(x, y, marker='o', s=16, color='r')
            m.scatter(x, y, marker='.', s=1, color='k')

            if ssp_x_mean > 0:
                mark_inset(ax, ax_ins, loc1=1, loc2=4, fc="none", ec='y')
            else:
                mark_inset(ax, ax_ins, loc1=2, loc2=3, fc="none", ec='y')

            ax_ins.tick_params(color='y', labelcolor='y')
            for spine in ax_ins.spines.values():
                spine.set_edgecolor('y')

        else:
            x, y = wm(ssp_x, ssp_y)
            wm.scatter(x, y, marker='o', s=16, color='r')
            wm.scatter(x, y, marker='.', s=1, color='k')

        if save_fig:
            plt.savefig(os.path.join(self.plots_folder(output_folder), 'ssp_map.png'),
                        bbox_inches='tight')
        # else:
        #     plt.show()

        return True

    @staticmethod
    def _inset_draw_map(llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat, ax_ins):

        m = Basemap(llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon, urcrnrlat=urcrnrlat,
                    resolution='l', ax=ax_ins)
        # resolution c, l, i, h, f in that order

        m.drawmapboundary(fill_color='aqua', zorder=2)
        m.fillcontinents(color='coral', lake_color='aqua', zorder=1)

        m.drawcoastlines(color='0.6', linewidth=0.5)
        m.drawcountries(color='0.6', linewidth=0.5)

        par = m.drawparallels(np.arange(-90., 91., 5.), labels=[1, 0, 0, 1], dashes=[1, 1], linewidth=0.4, color='.2')
        PlotDb._set_inset_color(par, 'y')
        mer = m.drawmeridians(np.arange(0., 360., 5.), labels=[1, 0, 0, 1], dashes=[1, 1], linewidth=0.4, color='.2')
        PlotDb._set_inset_color(mer, 'y')

        return m

    @staticmethod
    def _world_draw_map():
        m = Basemap(resolution=None)
        # resolution c, l, i, h, f in that order
        m.bluemarble(zorder=0)
        return m

    @staticmethod
    def _set_inset_color(x, color):
        for m in x:
            for t in x[m][1]:
                t.set_color(color)

    class AvgSsp(object):
        def __init__(self):
            # create and populate list used in the calculations
            self.limits = list()  # bin limits
            self.depths = list()  # avg depth for each bin
            self.bins = list()  # a list of list with all the value within a bin

            # populating
            for i, z in enumerate(range(10, 781, 10)):
                self.limits.append(z)
                # self.depths.append(z + 5.)
                self.bins.append(list())

            # output lists
            self.min_2std = list()
            self.max_2std = list()
            self.mean = list()

        def add_samples(self, depths, values):

            for i, d in enumerate(depths):

                for j, lim in enumerate(self.limits):

                    if d < lim:
                        self.bins[j].append(values[i])
                        break

        def calc_avg(self):

            for i, i_bin in enumerate(self.bins):

                # to avoid unstable statistics
                if len(i_bin) < 3:
                    continue

                if i == 0:
                    self.depths.append(0.)
                elif i == (len(self.bins) - 1):
                    self.depths.append(780.)
                else:
                    self.depths.append(self.limits[i] - 5.)

                avg = np.mean(i_bin)
                std = np.std(i_bin)
                self.mean.append(avg)
                self.min_2std.append(avg - 2 * std)
                self.max_2std.append(avg + 2 * std)

    def aggregate_plot(self, dates, output_folder, save_fig=False):
        """aggregate plot with all the SSPs between the passed dates"""

        if not save_fig:
            plt.ion()

        ts_list = self.db.list_profiles()

        if ts_list is None:
            raise RuntimeError("Unable to retrieve the day list > Empty database?")
        if len(ts_list) == 0:
            raise RuntimeError("Unable to retrieve the day list > Empty database?")

        # start a new figure
        fig = plt.figure()
        plt.title("Aggregate SSP plot [from: %s to: %s]" % (dates[0], dates[1]))
        ax = fig.add_subplot(111)
        ax.invert_yaxis()
        ax.set_xlim(1460, 1580)
        ax.set_ylim(780, 0)
        plt.xlabel('Sound Speed [m/s]', fontsize=10)
        plt.ylabel('Depth [m]', fontsize=10)
        ax.grid(linewidth=0.8, color=(0.3, 0.3, 0.3))

        avg_ssp = PlotDb.AvgSsp()

        ssp_count = 0
        for ts_pk in ts_list:

            tmp_date = ts_pk[1].date()

            if (tmp_date < dates[0]) or (tmp_date > dates[1]):
                continue

            ssp_count += 1
            # print(ts_pk[1], ts_pk[0])
            tmp_ssp = self.db.profile_by_pk(ts_pk[0])
            # print(tmp_ssp)
            ax.plot(tmp_ssp.cur.data.speed[tmp_ssp.cur.data_valid], tmp_ssp.cur.data.depth[tmp_ssp.cur.data_valid], '.',
                    color=(0.85, 0.85, 0.85), markersize=2
                    # label='%s [%04d] ' % (ts_pk[0].time(), ts_pk[1])
                    )
            ax.hold(True)

            avg_ssp.add_samples(tmp_ssp.cur.data.depth[tmp_ssp.cur.data_valid],
                                tmp_ssp.cur.data.speed[tmp_ssp.cur.data_valid])

        avg_ssp.calc_avg()
        ax.plot(avg_ssp.mean, avg_ssp.depths, '-b', linewidth=2)
        ax.hold(True)
        ax.plot(avg_ssp.min_2std, avg_ssp.depths, '--b', linewidth=1)
        ax.hold(True)
        ax.plot(avg_ssp.max_2std, avg_ssp.depths, '--b', linewidth=1)
        ax.hold(True)
        # fill between std-curves
        # ax.fill_betweenx(avg_ssp.depths, avg_ssp.min_2std, avg_ssp.max_2std, color='b', alpha='0.1')
        # ax.hold(True)

        if save_fig:
            plt.savefig(os.path.join(self.plots_folder(output_folder), 'aggregate_%s_%s.png' % (dates[0], dates[1])),
                        bbox_inches='tight')
        else:
            plt.show()

        # if not save_fig:
        #     plt.show()  # issue: QCoreApplication::exec: The event loop is already running

        logger.debug("plotted SSPs: %d" % ssp_count)
        return True

    def daily_plots(self, project_name, output_folder, save_fig=False):
        """plot all the SSPs by day"""

        if not save_fig:
            plt.ion()

        rows = self.db.list_profiles()
        if rows is None:
            logger.warning("Unable to retrieve ssp view rows > Empty database?")
            return False
        if len(rows) == 0:
            logger.warning("Unable to retrieve ssp view rows > Empty database?")
            return False

        # retrieve the timestamps
        ts_list = self.db.timestamp_list()
        # print(ts_list)

        # find the days
        date_list = list()
        for ts in ts_list:
            date = ts[0].date()
            if date not in date_list:
                date_list.append(date)
        # print(date_list)

        # create the required figures and prepare the dict to count the plots
        date_plots = dict()
        for date in date_list:
            date_plots[date] = 0
            fig = plt.figure(date_list.index(date))
            ax = fig.add_subplot(111)
            ax.invert_yaxis()

        # plot each profile
        for row in rows:
            row_date = row[1].date()  # 1 is the cast_datetime
            date_plots[row_date] += 1

            fig = plt.figure(date_list.index(row_date))
            row_ssp = self.db.profile_by_pk(row[0])
            fig.get_axes()[0].plot(row_ssp.cur.data.speed[row_ssp.cur.data_valid],
                                   row_ssp.cur.data.depth[row_ssp.cur.data_valid],
                                   label='%s [%04d]' % (row[1].time(), row[0]))
            fig.get_axes()[0].hold(True)

        # print(date_plots)

        # finishing up the plots
        for date in date_list:
            fig = plt.figure(date_list.index(date))

            plt.title("Day #%s: %s (profiles: %s)" % (date_list.index(date) + 1, date, date_plots[date]))
            fig.get_axes()[0].set_xlim(1460, 1580)
            fig.get_axes()[0].set_ylim(780, 0)
            plt.xlabel('Sound Speed [m/s]', fontsize=10)
            plt.ylabel('Depth [m]', fontsize=10)
            plt.grid()

            # Now add the legend with some customizations.
            legend = fig.get_axes()[0].legend(loc='lower right', shadow=True)
            # The frame is matplotlib.patches.Rectangle instance surrounding the legend.
            frame = legend.get_frame()
            frame.set_facecolor('0.90')
            # Set the fontsize
            for label in legend.get_texts():
                label.set_fontsize('large')

            for label in legend.get_lines():
                label.set_linewidth(1.5)  # the legend line width

        # end
        for date in date_list:
            fig = plt.figure(date_list.index(date))

            if save_fig:
                fig.savefig(os.path.join(self.plots_folder(output_folder),
                                         '%s.day_%2d.png' % (project_name, date_list.index(date) + 1)),
                            bbox_inches='tight')
            else:
                fig.show()

        # if not save_fig:
        #     plt.show()  # issue: QCoreApplication::exec: The event loop is already running

        # for date in date_list:
        #     plt.close(plt.figure(date_list.index(date)))

        return True
