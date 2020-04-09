from datetime import datetime

import numpy as np
from scipy import interpolate
# noinspection PyUnresolvedReferences
from PySide2 import QtWidgets
import matplotlib
# from matplotlib import rc_context as rc_context
from matplotlib import pyplot as plt
import logging

from hyo2.soundspeed.profile.ray_tracing.diff_tracedprofiles import DiffTracedProfiles

# matplotlib.use('qt5agg')
logger = logging.getLogger(__name__)


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

        # take care of labels and legend validity/inputs
        if not isinstance(self.old_tp_label, str):
            self.old_tp_label = None
        if not isinstance(self.new_tp_label, str):
            self.new_tp_label = None
        if not isinstance(self.legend_loc, str):
            self.legend_loc = None

        if self.old_tp_label is None:
            self.old_tp_label = "%s" % self._d.old_tp.date_time.strftime("%Y-%m-%d %H:%M:%S")
        if self.new_tp_label is None:
            self.new_tp_label = "%s" % self._d.new_tp.date_time.strftime("%Y-%m-%d %H:%M:%S")
        if self.legend_loc is None:
            self.legend_loc = "upper right"

    def make_comparison_plots(self):

        logger.debug("Plotting analysis")

        # create figure
        plt.close("Comparison of Ray-Traced Profiles")  # if any
        fig = plt.figure(num="Comparison of Ray-Traced Profiles",
                         figsize=(10, 6), dpi=80, facecolor='w', edgecolor='k')

        z_max = max(max(self._d.new_tp.data[0]), max(self._d.old_tp.data[0]))
        ss_min = min(min(self._d.new_tp.data[1]), min(self._d.old_tp.data[1]))
        ss_max = max(max(self._d.new_tp.data[1]), max(self._d.old_tp.data[1]))

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

        # calculate limits
        t_idx_max = max(np.nanargmax(self._d.new_rays[-1][0]),
                        np.nanargmax(self._d.old_rays[-1][0]))
        z_max = self._d.new_rays[-1][2][t_idx_max]
        x_max = max(max(self._d.new_rays[-1][1]),
                    max(self._d.old_rays[-1][1]))
        logger.debug("z max: %s, x max: %s" % (z_max, x_max))

        new_last_ray_x = self._d.new_rays[-1][1]
        new_last_ray_z = self._d.new_rays[-1][2]
        new_t_max = np.nanmax(self._d.new_rays[-1][0])
        old_t_idx_max = np.nanargmin(np.abs(self._d.old_rays[-1][0] - new_t_max))
        old_last_ray_x = self._d.old_rays[-1][1][:old_t_idx_max]
        old_last_ray_z = self._d.old_rays[-1][2][:old_t_idx_max]

        new_x_ends = list()
        new_z_ends = list()
        old_x_ends = list()
        old_z_ends = list()
        up_tol = list()
        down_tol = list()
        for ray_idx, new_ray in enumerate(self._d.new_rays):
            old_ray = self._d.old_rays[ray_idx]
            new_t_idx_max = np.nanargmax(new_ray[0])
            new_x_ends.append(new_ray[1][new_t_idx_max])
            new_z_ends.append(new_ray[2][new_t_idx_max])
            new_t_max = new_ray[0][new_t_idx_max]
            old_t_idx_max = np.nanargmin(np.abs(old_ray[0] - new_t_max))
            old_x_ends.append(old_ray[1][old_t_idx_max])
            old_z_ends.append(old_ray[2][old_t_idx_max])
            up_tol.append(new_ray[2][new_t_idx_max] - new_ray[2][new_t_idx_max] * self._d.variable_allowable_error -
                          self._d.fixed_allowable_error)
            down_tol.append(new_ray[2][new_t_idx_max] + new_ray[2][new_t_idx_max] * self._d.variable_allowable_error +
                            self._d.fixed_allowable_error)

        # error plot axis
        err_ax = fig.add_subplot(1, 2, 2)
        err_ax.set_title('Ray-Tracing Comparison')
        err_ax.set_xlabel('Across-track distance [m]')
        err_ax.set_ylabel('Z from common minimum depth [m]')
        err_ax.set_ylim((z_max + .05 * z_max, 0))
        err_ax.set_xlim((0, x_max + 0.05 * x_max))
        err_ax.plot(old_last_ray_x,
                    old_last_ray_z,
                    color=self.old_tp_color,
                    linestyle='--')
        err_ax.plot(new_last_ray_x,
                    new_last_ray_z,
                    color=self.new_tp_color,
                    linestyle=':')
        err_ax.plot(old_x_ends,
                    old_z_ends,
                    color=self.old_tp_color, linestyle='--', label=self.old_tp_label)
        err_ax.plot(new_x_ends,
                    new_z_ends,
                    color=self.new_tp_color, linestyle=':', label=self.new_tp_label)
        err_ax.plot(new_x_ends, up_tol, 'm', label="error tolerance")
        err_ax.plot(new_x_ends, down_tol, 'm')
        legend = err_ax.legend(loc=self.legend_loc, shadow=True, fontsize='small')
        legend.get_frame().set_facecolor(self.legend_color)
        err_ax.grid(True)

        fig.tight_layout()
        plt.show()

    def make_bias_plots(self):

        logger.debug("make bias plots")

        start_time = datetime.now()

        t_idx_max = max(np.nanargmax(self._d.new_rays[-1][0]),
                        np.nanargmax(self._d.old_rays[-1][0]))
        try:
            z_max = self._d.new_rays[-1][2][t_idx_max]
        except IndexError:
            z_max = self._d.old_rays[-1][2][t_idx_max]
        x_max = max(np.nanmax(self._d.new_rays[-1][1]),
                    np.nanmax(self._d.old_rays[-1][1]))
        logger.debug("z max: %s, x max: %s" % (z_max, x_max))

        xi, zi = np.mgrid[0:x_max:1000j, 0:z_max:1000j]

        t1 = np.zeros(0, dtype=np.float32)
        x1 = np.zeros(0, dtype=np.float32)
        z1 = np.zeros(0, dtype=np.float32)

        t2 = np.zeros(0, dtype=np.float32)
        x2 = np.zeros(0, dtype=np.float32)
        z2 = np.zeros(0, dtype=np.float32)

        dx = np.zeros(0, dtype=np.float32)
        dz = np.zeros(0, dtype=np.float32)

        for ang, ray in enumerate(self._d.new_rays):

            nr_samples = len(ray[0])
            if nr_samples < 500:
                nr_steps = 10
            elif nr_samples < 2500:
                nr_steps = 50
            else:
                nr_steps = 100

            for idx in range(0, nr_samples, nr_steps):

                try:
                    _ = ray[0][idx]
                    _ = self._d.old_rays[ang][0][idx]
                except IndexError:
                    logger.debug("skipping idx %s" % idx)
                    continue

                if np.isnan(ray[0][idx]) or np.isnan(ray[1][idx]):
                    continue
                if np.isnan(self._d.old_rays[ang][0][idx]) or np.isnan(self._d.old_rays[ang][1][idx]):
                    continue

                t1 = np.append(t1, ray[0][idx])
                x1 = np.append(x1, ray[1][idx])
                z1 = np.append(z1, ray[2][idx])

                t2 = np.append(t2, self._d.old_rays[ang][0][idx])
                x2 = np.append(x2, self._d.old_rays[ang][1][idx])
                z2 = np.append(z2, self._d.old_rays[ang][2][idx])

                dx = np.append(dx, np.abs(ray[1][idx] - self._d.old_rays[ang][1][idx]))
                # dz = np.append(dz, np.abs(ray[2][idx] - self._d.old_rays[ang][2][idx]))
                dz = np.append(dz, np.abs(ray[0][idx] - self._d.old_rays[ang][0][idx]) * 1500)

        logger.debug("timing: %s" % (datetime.now() - start_time))

        # noinspection PyTypeChecker
        dxi = interpolate.griddata((x1, z1), dx, (xi, zi), method='cubic')
        logger.debug("dxi: %s, min: %s, max: %s" % (dxi.shape, np.nanmin(dxi), np.nanmax(dxi)))
        # noinspection PyTypeChecker
        dzi = interpolate.griddata((x1, z1), dz, (xi, zi), method='cubic')
        logger.debug("dzi: %s, min: %s, max: %s" % (dzi.shape, np.nanmin(dzi), np.nanmax(dzi)))

        logger.debug("timing: %s" % (datetime.now() - start_time))

        # create figure
        plt.close("Across-swath bias plots")  # if already open
        fig = plt.figure(num="Across-swath bias plots",
                         figsize=(12, 8), dpi=80, facecolor='w', edgecolor='k')

        # vertical bias
        vb_ax = fig.add_subplot(2, 1, 1)
        vb_ax.set_title('Compared pair of profiles: %s and %s' % (self.old_tp_label, self.new_tp_label))
        vb_ax.set_xlabel('Across-Track Distance [m]')
        vb_ax.set_ylabel('Z from common minimum depth [m]')
        vb_ax.set_ylim(bottom=z_max, top=0)
        vb_ax.set_xlim(left=0, right=x_max * 1.05)
        im = vb_ax.pcolormesh(xi, zi, dzi, cmap=plt.get_cmap('jet'))
        cb = fig.colorbar(im)
        cb.set_label("Absolute Depth Bias [m]")
        vb_ax.grid(True)
        # vb_ax.scatter(x1, z1, marker='o', c='b', s=10, zorder=10)

        # horizontal bias
        hb_ax = fig.add_subplot(2, 1, 2)
        hb_ax.set_xlabel('Across-Track Distance [m]')
        hb_ax.set_ylabel('Z from common minimum depth [m]')
        hb_ax.set_ylim(bottom=z_max, top=0)
        hb_ax.set_xlim(left=0, right=x_max * 1.05)
        im = hb_ax.pcolormesh(xi, zi, dxi, cmap=plt.get_cmap('jet'))
        cb = fig.colorbar(im)
        cb.set_label("Absolute Horizontal Bias [m]")
        hb_ax.grid(True)
        # hb_ax.scatter(x1, z1, marker='o', c='b', s=10, zorder=10)

        fig.tight_layout()
        plt.show()
