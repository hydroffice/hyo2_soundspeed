from datetime import datetime
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
        z_max = max(max(self._d.new_rays[-1][2]),
                    max(self._d.old_rays[-1][2]))
        x_max = max(max(self._d.new_rays[-1][1]),
                    max(self._d.old_rays[-1][1]))

        old_last_ray_x = self._d.old_rays[-1][1]
        new_last_ray_x = self._d.new_rays[-1][1]
        old_last_ray_z = self._d.old_rays[-1][2]
        new_last_ray_z = self._d.new_rays[-1][2]
        old_x_ends = [ray[1][-1] for ray in self._d.old_rays]
        new_x_ends = [ray[1][-1] for ray in self._d.new_rays]
        old_z_ends = [ray[2][-1] for ray in self._d.old_rays]
        new_z_ends = [ray[2][-1] for ray in self._d.new_rays]
        up_tol = [(ray[2][-1] - ray[2][-1] * self._d.variable_allowable_error - self._d.fixed_allowable_error)
                  for ray in self._d.new_rays]
        down_tol = [(ray[2][-1] + ray[2][-1] * self._d.variable_allowable_error + self._d.fixed_allowable_error)
                    for ray in self._d.new_rays]

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

        z_max = max(max(self._d.new_rays[-1][2]),
                    max(self._d.old_rays[-1][2]))
        x_max = max(max(self._d.new_rays[-1][1]),
                    max(self._d.old_rays[-1][1]))

        xi = np.linspace(0, x_max, 1000)
        zi = np.linspace(0, z_max, 1000)

        t1 = np.zeros(0, dtype=np.float32)
        x1 = np.zeros(0, dtype=np.float32)
        z1 = np.zeros(0, dtype=np.float32)

        t2 = np.zeros(0, dtype=np.float32)
        x2 = np.zeros(0, dtype=np.float32)
        z2 = np.zeros(0, dtype=np.float32)

        dx = np.zeros(0, dtype=np.float32)
        dz = np.zeros(0, dtype=np.float32)

        for ang, ray in enumerate(self._d.new_rays):

            for idx in range(0, len(ray[0]), 100):

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
        dxi = griddata(x1, z1, dx, xi, zi, interp='linear')
        # noinspection PyTypeChecker
        dzi = griddata(x1, z1, dz, xi, zi, interp='linear')

        logger.debug("timing: %s" % (datetime.now() - start_time))

        # create figure
        fig = plt.figure(num="Across-swath bias plots",
                         figsize=(12, 8), dpi=80, facecolor='w', edgecolor='k')

        # vertical bias
        vb_ax = fig.add_subplot(2, 1, 1)
        vb_ax.set_title('Compared pair of profiles: %s and %s' % (self.old_tp_label, self.new_tp_label))
        vb_ax.set_xlabel('Across-Track Distance [m]')
        vb_ax.set_ylabel('Z from common minimum depth [m]')
        vb_ax.set_ylim((z_max, 0))
        vb_ax.set_xlim((0, x_max * 1.05))
        im = vb_ax.pcolormesh(xi, zi, dzi, cmap=plt.get_cmap('jet'))
        cb = fig.colorbar(im)
        cb.set_label("Absolute Depth Bias [m]")
        vb_ax.grid(True)
        # vb_ax.scatter(x1, z1, marker='o', c='b', s=10, zorder=10)

        # horizontal bias
        hb_ax = fig.add_subplot(2, 1, 2)
        hb_ax.set_xlabel('Across-Track Distance [m]')
        hb_ax.set_ylabel('Z from common minimum depth [m]')
        hb_ax.set_ylim((z_max, 0))
        hb_ax.set_xlim((0, x_max * 1.05))
        im = hb_ax.pcolormesh(xi, zi, dxi, cmap=plt.get_cmap('jet'))
        cb = fig.colorbar(im)
        cb.set_label("Absolute Horizontal Bias [m]")
        hb_ax.grid(True)
        # hb_ax.scatter(x1, z1, marker='o', c='b', s=10, zorder=10)

        fig.tight_layout()
        plt.show()
