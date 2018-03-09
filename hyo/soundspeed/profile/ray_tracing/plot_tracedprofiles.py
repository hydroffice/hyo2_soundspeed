import numpy as np
import matplotlib

matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4'] = 'PySide'

# from matplotlib import rc_context as rc_context
from matplotlib import pyplot as plt
from matplotlib.mlab import griddata
import logging

logger = logging.getLogger(__name__)

from hyo.soundspeed.profile.ray_tracing.diff_tracedprofiles import DiffTracedProfiles


class PlotTracedProfiles:

    def __init__(self, diff_tps):

        if not isinstance(diff_tps, DiffTracedProfiles):
            raise RuntimeError("An instance of PlotTracedProfiles "
                               "is required, not %s" % type(diff_tps))
        self._d = diff_tps

        self.old_tp_label = None
        self.old_tp_color = "#FF8000"

        self.new_tp_label = None
        self.new_tp_color = "#3399FF"

        self.legend_loc = None
        self.legend_color = '#f5f5f5'

    def make_comparison_plots(self):

        if (self._d.new_ends is None) or (self._d.old_ends is None) or \
                (self._d.max_tolerances is None):
            logger.warning("Unable to plot comparison due to z values or "
                           "tolerance")
            return

        old_extend = False
        if self._d.new_tp.data[0][-1] > self._d.old_tp.data[0][-1]:
            old_extend = True

        step = 0
        old_extend = False
        if old_extend:

            step = len(self._d.new_tp.rays[-1][2])

        else:

            step = min(len(self._d.old_tp.rays[-1][2]),
                       len(self._d.new_tp.rays[-1][2]))

        new_outmost_raypath = [
            self._d.new_tp.rays[-1][1][0:step],
            self._d.new_tp.rays[-1][2][0:step]
        ]
        old_outmost_raypath = [
            self._d.old_tp.rays[-1][1][0:step],
            self._d.old_tp.rays[-1][2][0:step]
        ]
        if old_extend:

            old_outmost_raypath = [
                np.append(old_outmost_raypath[0],
                          self._d.old_tp.rays[-1][1][step - 1]),
                np.append(old_outmost_raypath[1],
                          self._d.old_tp.rays[-1][2][step - 1])
            ]

        # take care of labels and legend validity/inputs
        if not isinstance(self.old_tp_label, str):
            self.old_tp_label = None
        if not isinstance(self.new_tp_label, str):
            self.new_tp_label = None
        if not isinstance(self.legend_loc, str):
            self.legend_loc = None

        if self.old_tp_label is None:
            self.old_tp_label = "%s" % self._d.old_tp.date_time
        if self.new_tp_label is None:
            self.new_tp_label = "%s" % self._d.new_tp.date_time
        if self.legend_loc is None:
            self.legend_loc = "upper right"

        # calculate limits
        z_max = max(max(self._d.new_tp.rays[len(self._d.new_tp.rays) - 1][2]),
                    max(self._d.old_tp.rays[len(self._d.old_tp.rays) - 1][2]))
        x_max = max(max(self._d.new_tp.rays[len(self._d.new_tp.rays) - 1][1]),
                    max(self._d.old_tp.rays[len(self._d.old_tp.rays) - 1][1]))
        ss_min = min(min(self._d.new_tp.data[1]), min(self._d.old_tp.data[1]))
        ss_max = max(max(self._d.new_tp.data[1]), max(self._d.old_tp.data[1]))

        logger.debug("Plotting analysis")

        # create figure
        fig = plt.figure(num="Comparison of Ray-Traced Profiles",
                         figsize=(10, 6), dpi=80, facecolor='w', edgecolor='k')

        # profile comparison axis
        svp_ax = fig.add_subplot(1, 2, 1)
        svp_ax.set_title('Sound Speed Profiles')
        svp_ax.set_xlabel('Sound Speed [m/s]')
        svp_ax.set_ylabel('Depth [m]')
        svp_ax.set_ylim((z_max + .05 * z_max, 0))
        svp_ax.set_xlim((ss_min - 3.0, ss_max + 3.0))
        svp_ax.plot(self._d.old_tp.data[1],
                    self._d.old_tp.data[0],
                    color=self.old_tp_color, linestyle='--',
                    label=self.old_tp_label)
        svp_ax.plot(self._d.new_tp.data[1],
                    self._d.new_tp.data[0],
                    color=self.new_tp_color, linestyle=':',
                    label=self.new_tp_label)
        if self._d.old_tp.data[0][-1] < self._d.new_tp.data[0][-1]:
            svp_ax.plot(np.repeat(self._d.old_tp.data[1][-1], 2),
                        [self._d.old_tp.data[0][-1],
                         self._d.new_tp.data[0][-1]],
                        'r--')
        svp_ax.grid(True)

        # error plot axis
        err_ax = fig.add_subplot(1, 2, 2)
        err_ax.set_title('Ray-Tracing Comparison')
        err_ax.set_xlabel('Range [m]')
        err_ax.set_ylabel('Depth [m]')
        err_ax.set_ylim((z_max + .05 * z_max, 0))
        err_ax.set_xlim((0, x_max + 0.05 * x_max))
        err_ax.plot(old_outmost_raypath[0],
                    old_outmost_raypath[1],
                    color=self.old_tp_color,
                    linestyle='--')
        err_ax.plot(new_outmost_raypath[0],
                    new_outmost_raypath[1],
                    color=self.new_tp_color,
                    linestyle=':')
        err_ax.plot(self._d.old_ends[0],
                    self._d.old_ends[1],
                    color=self.old_tp_color, linestyle='--', label=self.old_tp_label)
        err_ax.plot(self._d.new_ends[0],
                    self._d.new_ends[1],
                    color=self.new_tp_color, linestyle=':', label=self.new_tp_label)
        err_ax.plot(self._d.new_ends[0], self._d.max_tolerances[0], 'm', label="error tolerance")
        err_ax.plot(self._d.new_ends[0], self._d.max_tolerances[1], 'm')
        legend = err_ax.legend(loc=self.legend_loc, shadow=True, fontsize='small')
        legend.get_frame().set_facecolor(self.legend_color)
        err_ax.grid(True)

        fig.tight_layout()
        plt.show()

    def make_bias_plots(self):

        logger.debug("make bias plots")

        ssp1_max_t = self._d.old_tp.rays[-1][0][-1]
        ssp2_max_t = self._d.new_tp.rays[-1][0][-1]
        ssp_max_t = max(ssp1_max_t, ssp2_max_t)
        logger.debug("max t: %.3f" % ssp_max_t)

        ssp1_max_x = self._d.old_tp.rays[-1][1][-1]
        ssp2_max_x = self._d.new_tp.rays[-1][1][-1]
        ssp_max_x = max(ssp1_max_x, ssp2_max_x)
        logger.debug("max x: %.3f" % ssp_max_x)

        ssp1_max_z = self._d.old_tp.rays[-1][2][-1]
        ssp2_max_z = self._d.new_tp.rays[-1][2][-1]
        ssp_max_z = max(ssp1_max_z, ssp2_max_z)
        logger.debug("max z: %.3f" % ssp_max_z)

        ti = np.linspace(0, ssp_max_t, 1000)
        xi = np.linspace(0, ssp_max_x, 1000)
        zi = np.linspace(0, ssp_max_z, 1000)

        t1 = np.zeros(0, dtype=np.float32)
        x1 = np.zeros(0, dtype=np.float32)
        z1 = np.zeros(0, dtype=np.float32)

        t2 = np.zeros(0, dtype=np.float32)
        x2 = np.zeros(0, dtype=np.float32)
        z2 = np.zeros(0, dtype=np.float32)

        dx = np.zeros(0, dtype=np.float32)
        dz = np.zeros(0, dtype=np.float32)

        for angle in np.arange(0, len(self._d.new_tp.rays)):
            angle_samples1 = len(self._d.old_tp.rays[angle][0])
            # logger.debug("%.2f -> %s" % (angle, angle_samples1))

            angle_samples2 = len(self._d.new_tp.rays[angle][0])
            # logger.debug("%.2f -> %s" % (angle, angle_samples2))

            min_angle_samples = min(angle_samples1, angle_samples2)

            t1 = np.append(t1, self._d.old_tp.rays[angle][0][:min_angle_samples])
            x1 = np.append(x1, self._d.old_tp.rays[angle][1][:min_angle_samples])
            z1 = np.append(z1, self._d.old_tp.rays[angle][2][:min_angle_samples])

            t2 = np.append(t2, self._d.new_tp.rays[angle][0][:min_angle_samples])
            x2 = np.append(x2, self._d.new_tp.rays[angle][1][:min_angle_samples])
            z2 = np.append(z2, self._d.new_tp.rays[angle][2][:min_angle_samples])

            dx = np.append(dx, np.abs(self._d.old_tp.rays[angle][1][:min_angle_samples] -
                                      self._d.new_tp.rays[angle][1][:min_angle_samples]))
            dz = np.append(dz, np.abs(self._d.old_tp.rays[angle][2][:min_angle_samples] -
                                      self._d.new_tp.rays[angle][2][:min_angle_samples]))

        # noinspection PyTypeChecker
        dxi = griddata(x1, z1, dx, xi, zi, interp='linear')
        # noinspection PyTypeChecker
        dzi = griddata(x1, z1, dz, xi, zi, interp='linear')

        # create figure
        fig = plt.figure(num="Bias Plots",
                         figsize=(8, 5), dpi=80, facecolor='w', edgecolor='k')

        # vertical bias
        vb_ax = fig.add_subplot(2, 1, 1)
        # vb_ax.set_xlabel('Across-Track Distance [m]')
        vb_ax.set_ylabel('Depth [m]')
        vb_ax.set_ylim((ssp_max_z, 0))
        vb_ax.set_xlim((0, ssp_max_x * 1.05))
        im = vb_ax.pcolormesh(xi, zi, dzi, cmap=plt.get_cmap('jet'))
        cb = fig.colorbar(im)
        cb.set_label("Absolute Depth Bias [m]")
        vb_ax.grid(True)
        # vb_ax.scatter(x1, z1, marker='o', c='b', s=10, zorder=10)

        # horizontal bias
        hb_ax = fig.add_subplot(2, 1, 2)
        hb_ax.set_xlabel('Across-Track Distance [m]')
        hb_ax.set_ylabel('Depth [m]')
        hb_ax.set_ylim((ssp_max_z, 0))
        hb_ax.set_xlim((0, ssp_max_x * 1.05))
        im = hb_ax.pcolormesh(xi, zi, dxi, cmap=plt.get_cmap('jet'))
        cb = fig.colorbar(im)
        cb.set_label("Absolute Horizontal Bias [m]")
        hb_ax.grid(True)
        # hb_ax.scatter(x1, z1, marker='o', c='b', s=10, zorder=10)

        fig.tight_layout()
        plt.show()
