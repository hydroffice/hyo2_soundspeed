import logging
import os

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
# noinspection PyUnresolvedReferences
from PySide6 import QtWidgets
from cartopy.feature import NaturalEarthFeature
from matplotlib import rc_context

logger = logging.getLogger(__name__)


class PlotDb:
    """Class that plots sound speed db data"""

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
    }

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

    def map_profiles(self, pks=None, output_folder=None, save_fig=False, show_plot=False):
        """plot all the ssp in the database"""

        with rc_context(self.rc_context):

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

                if pks is not None:  # only if a pk-based filter was passed
                    if row[0] in pks:
                        ssp_x.append(row[2].x)
                        ssp_y.append(row[2].y)
                        ssp_label.append(row[0])

                else:
                    ssp_x.append(row[2].x)
                    ssp_y.append(row[2].y)
                    ssp_label.append(row[0])

            # make the world map
            plt.close("Profiles Map")
            _ = plt.figure("Profiles Map")
            ax = plt.subplot(111, projection=ccrs.PlateCarree())
            plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
            plt.ioff()

            # noinspection PyUnresolvedReferences
            ax.scatter(ssp_x, ssp_y, marker='o', s=14, color='r', zorder=4)
            # noinspection PyUnresolvedReferences
            ax.scatter(ssp_x, ssp_y, marker='.', s=1, color='k', zorder=4)

            delta = 5.0
            y_min = min(ssp_y)
            if (y_min - delta) < -90.0:
                y_min = -90.0
            else:
                y_min -= delta
            y_max = max(ssp_y)
            if (y_max + delta) > 90.0:
                y_max = 90.0
            else:
                y_max += delta

            x_min = min(ssp_x)
            if (x_min - delta) < -180.0:
                x_min = -180.0
            else:
                x_min = x_min - delta
            x_max = max(ssp_x)
            if (x_max + delta) > 180.0:
                x_max = 180.0
            else:
                x_max += delta
            # logger.debug("%s %s, %s %s" % (y_min, y_max, x_min, x_max))
            # noinspection PyUnresolvedReferences
            ax.set_extent([x_min, x_max, y_min, y_max], crs=ccrs.PlateCarree())

            scale = '110m'
            # if (x_max - x_min) < 30 and (y_max - y_min) < 30:
            #     scale = '50m'
            ocean = NaturalEarthFeature('physical', 'ocean', scale, edgecolor='#777777',
                                        facecolor="#5da1c9", zorder=2)
            # noinspection PyUnresolvedReferences
            ax.add_feature(ocean)
            # noinspection PyUnresolvedReferences
            ax.gridlines(color='#909090', linestyle='--', zorder=3)

            if save_fig and (output_folder is not None):
                plt.savefig(os.path.join(self.plots_folder(output_folder), 'ssp_map.png'),
                            bbox_inches='tight')
            elif show_plot:
                plt.show()

        return True

    @staticmethod
    def _set_inset_color(x, color):
        for m in x:
            for t in x[m][1]:
                t.set_color(color)

    class AvgSsp:
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

            skip_counter = 0

            for i, i_bin in enumerate(self.bins):

                # to avoid unstable statistics
                if len(i_bin) < 3:
                    # logger.debug("[%d] too few samples: %s -> skip" % (i, i_bin))
                    skip_counter += 1
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

            if skip_counter > 0:
                logger.debug("skipped depth bins: %d" % skip_counter)

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
        plt.close("Aggregate Plot")
        fig, ax = plt.subplots(num="Aggregate Plot")
        plt.title("Aggregate SSP plot [from: %s to: %s]" % (dates[0], dates[1]))
        ax.invert_yaxis()
        ax.set_xlim(1440, 1580)
        ax.set_ylim(780, 0)
        plt.xlabel('Sound Speed [m/s]', fontsize=10)
        plt.ylabel('Depth [m]', fontsize=10)
        ax.grid(linewidth=0.8, color=(0.3, 0.3, 0.3))

        avg_ssp = PlotDb.AvgSsp()

        ssp_count = 0
        for ts_pk in ts_list:

            tmp_date = ts_pk[1].date()
            logger.debug("profile date: %s" % tmp_date)

            if (tmp_date < dates[0]) or (tmp_date > dates[1]):
                logger.debug("skip for date")
                continue

            ssp_count += 1
            # print(ts_pk[1], ts_pk[0])
            tmp_ssp = self.db.profile_by_pk(ts_pk[0])
            # print(tmp_ssp)
            ax.plot(tmp_ssp.cur.proc.speed[tmp_ssp.cur.proc_valid], tmp_ssp.cur.proc.depth[tmp_ssp.cur.proc_valid], '.',
                    color=(0.85, 0.85, 0.85), markersize=2
                    # label='%s [%04d] ' % (ts_pk[0].time(), ts_pk[1])
                    )

            avg_ssp.add_samples(tmp_ssp.cur.proc.depth[tmp_ssp.cur.proc_valid],
                                tmp_ssp.cur.proc.speed[tmp_ssp.cur.proc_valid])

        avg_ssp.calc_avg()
        ax.plot(avg_ssp.mean, avg_ssp.depths, '-b', linewidth=2)
        ax.plot(avg_ssp.min_2std, avg_ssp.depths, '--b', linewidth=1)
        ax.plot(avg_ssp.max_2std, avg_ssp.depths, '--b', linewidth=1)
        # fill between std-curves
        # ax.fill_betweenx(avg_ssp.depths, avg_ssp.min_2std, avg_ssp.max_2std, color='b', alpha='0.1')

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
            fig, ax = plt.subplots(num=date_list.index(date))
            ax.invert_yaxis()
            logger.info("created plot #%d" % date_list.index(date))

        # plot each profile
        max_depth = None
        min_speed = None
        max_speed = None
        for row in rows:
            row_date = row[1].date()  # 1 is the cast_datetime
            logger.info("added profile to plot #%d" % date_list.index(row_date))
            date_plots[row_date] += 1

            fig = plt.figure(date_list.index(row_date))
            row_ssp = self.db.profile_by_pk(row[0])
            fig.get_axes()[0].plot(row_ssp.cur.proc.speed[row_ssp.cur.proc_valid],
                                   row_ssp.cur.proc.depth[row_ssp.cur.proc_valid],
                                   label='%s [%04d]' % (row[1].time(), row[0]))

            # check max depth
            max_d = np.max(row_ssp.cur.proc.depth[row_ssp.cur.proc_valid])
            if not max_depth:
                max_depth = max_d
            else:
                if max_d > max_depth:
                    max_depth = max_d

            # check min sound speed
            min_s = np.min(row_ssp.cur.proc.speed[row_ssp.cur.proc_valid])
            if not min_speed:
                min_speed = min_s
            else:
                if min_s < min_speed:
                    min_speed = min_s

            # check max sound speed
            max_s = np.max(row_ssp.cur.proc.speed[row_ssp.cur.proc_valid])
            if not max_speed:
                max_speed = max_s
            else:
                if max_s > max_speed:
                    max_speed = max_s

        # print(date_plots)
        y_max = max_depth * 1.05
        logger.debug("y lim: %s, 0" % y_max)
        dx = max_speed * 0.05
        x_min = min_speed - dx
        x_max = max_speed + dx
        logger.debug("x lim: %s, %s" % (x_min, x_max))

        # finishing up the plots
        for date in date_list:
            fig = plt.figure(date_list.index(date))

            plt.title("Day #%s: %s (profiles: %s)" % (date_list.index(date) + 1, date, date_plots[date]))
            fig.get_axes()[0].set_xlim(x_min, x_max)
            fig.get_axes()[0].set_ylim(y_max, 0)
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
