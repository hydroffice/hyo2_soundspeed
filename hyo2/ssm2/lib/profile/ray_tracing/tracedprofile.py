import numpy as np
import math
import logging
from scipy.interpolate import interp1d

logger = logging.getLogger(__name__)


class TracedProfile:

    def __init__(self, ssp, half_swath=65, avg_depth=10000, tss_depth=None, tss_value=None):
        # PyDateTime_IMPORT
        self.avg_depth = avg_depth
        self.half_swath = half_swath

        # select samples for the ray tracing (must be deeper than the transducer depth)
        depths = list()
        speeds = list()
        if (tss_depth is not None) and (tss_value is not None):
            depths.append(tss_depth)
            speeds.append(tss_value)

        vi = ssp.proc_valid

        for z_idx in range(0, len(ssp.proc.depth[vi])):

            # skip samples at depth less than the draft
            if tss_depth is not None:
                if ssp.proc.depth[vi][z_idx] <= tss_depth:
                    # logger.debug("skipping sample at depth: %.1f" % ssp.proc.depth[z_idx])
                    continue

            depths.append(ssp.proc.depth[vi][z_idx])
            speeds.append(ssp.proc.speed[vi][z_idx])

            # stop after the first sample deeper than the avg depth (safer)
            if ssp.proc.depth[vi][z_idx] > self.avg_depth:
                break

        # remove extension value (if any)
        if len(depths) > 3:
            if (depths[-1] - depths[-2]) > 1000:
                logger.info("removed latest extension depth: %s" % depths[-1])
                del depths[-1]

        logger.info("profile timestamp: %s" % ssp.meta.utc_time)
        logger.debug("valid samples: %d" % (len(depths)), )
        logger.debug("depth: min %.2f, max %.2f" % (depths[0], depths[-1]))
        # logger.debug("depths: %s" % depth)
        # logger.debug("speeds: %s" % speed)

        # ray-trace a few angles (ref: Lurton, An Introduction to UA, p.50-52)
        self.rays = list()
        self.harmonic_means = list()
        for angle in np.arange(0, int(math.ceil(self.half_swath + 1))):

            # ray angles
            beta = list()
            beta.append(math.radians(90.0 - angle))
            total_z = list()
            total_z.append(depths[0])
            total_x = list()
            total_x.append(0)
            total_t = list()  # total travel time
            total_t.append(0)

            # logger.debug("angle %d: beta0 %s" % (angle, math.degrees(beta[0])))

            for idx in range(len(depths) - 1):

                # calculate delta (next - current)
                dz = depths[idx+1] - depths[idx]
                dc = speeds[idx+1] - speeds[idx]
                # logger.debug("%s: dy %s, dc %s" % (x, dy, dc))

                if dc == 0:  # "constant speed" case: no curvature

                    if dz == 0:  # if (dc == 0) and (dy == 0):

                        # logger.debug("duplicated point: #%d" % idx)
                        beta.append(beta[idx])  # beta does not change
                        continue

                    # gradient = dc/dy
                    beta.append(beta[idx])  # beta does not change
                    dx = dz / (math.tan(beta[idx+1]))  # no curvature!
                    dt = (((dx**2)+(dz**2))**.5) / speeds[idx+1]

                elif dz == 0:  # "same depth" case: just adjust the ray angle

                    beta.append(math.acos((speeds[idx + 1] / speeds[idx]) * (math.cos(beta[idx]))))
                    continue

                else:  # if (dc != 0) and (dz != 0):

                    gradient = dc / dz  # Lurton, (2.64)
                    if math.cos(beta[idx]) == 0:
                        curve = 0
                    else:  # if math.cos(beta[x]) != 0:
                        curve = speeds[idx] / (gradient * math.cos(beta[idx]))  # Lurton, (2.66)

                    beta_cos = speeds[idx + 1] * (math.cos(beta[idx])) / speeds[idx]
                    if beta_cos > 1.0:
                        logger.warning("angle %d, sample %d -> invalid beta cos: %s" %
                                       (angle, idx, beta_cos))
                        beta_cos = 1.0
                    if beta_cos < -1.0:
                        logger.warning("angle %d, sample %d -> invalid beta cos: %s" %
                                       (angle, idx, beta_cos))
                        beta_cos = -1.0

                    beta.append(math.acos(beta_cos))  # Derived from Lurton, (2.65)

                    dx = curve * ((math.sin(beta[idx])) - (math.sin(beta[idx + 1])))  # Lurton, (2.67)
                    dt = abs((1 / gradient) *
                             math.log(
                                (speeds[idx + 1] / speeds[idx]) *
                                (abs((1 + math.sin(beta[idx])) / (1 + math.sin(beta[idx + 1]))))))  # Lurton, (2.70)

                total_z.append(total_z[-1] + dz)
                total_x.append(total_x[-1] + dx)
                total_t.append(total_t[-1] + dt)

            # logger.debug("z:\n%s" % total_z)
            # logger.debug("x:\n%s" % total_x)
            # logger.debug("t:\n%s" % total_t)

            if len(depths) > 1:
                harm_mean = (total_z[-1] - total_z[0]) / (total_t[-1] - total_t[0])
            elif len(depths) == 1:
                harm_mean = depths[0]
            else:
                raise RuntimeError("invalid profile with zero valid depth values")
            self.harmonic_means.append(harm_mean)

            # interpolate between 0 and 5000 meters with decimetric resolution
            if len(depths) > 1:
                interp_z = np.linspace(0, 5000, num=25001, endpoint=True)
                fx = interp1d(total_z, total_x, kind='cubic', bounds_error=False, fill_value=np.nan)
                interp_x = fx(interp_z)
                ft = interp1d(total_z, total_t, kind='cubic', bounds_error=False, fill_value=np.nan)
                interp_t = ft(interp_z)
            elif len(depths) == 1:
                interp_z = total_z
                interp_x = total_x
                interp_t = total_t
            else:
                raise RuntimeError("invalid profile with zero valid depth values")

            self.rays.append(np.array([interp_t, interp_x, interp_z]))

        logger.debug("rays: %d (%d samples per-ray)" % (len(self.rays), len(self.rays[0][0])))
        self.date_time = ssp.meta.utc_time
        self.latitude = ssp.meta.latitude
        self.longitude = ssp.meta.longitude
        self.data = [depths, speeds]

    def debug_rays(self, ray_idx=0):
        nr_rays = len(self.rays)
        if (ray_idx < 0) or (ray_idx >= nr_rays):
            logger.warning("invalid ray index: %d (total rays: %d)" % (ray_idx, nr_rays))
            return

        logger.debug("[%d]" % ray_idx)
        logger.debug("t      | x      | z     |")
        for idx in range(len(self.rays[ray_idx][0])):
            logger.debug("%10.4f %10.3f %10.2f"
                         % (self.rays[ray_idx][0][idx], self.rays[ray_idx][1][idx], self.rays[ray_idx][2][idx]))

    def debug_plot(self, ray_idx=0):
        nr_rays = len(self.rays)
        if (ray_idx < 0) or (ray_idx >= nr_rays):
            logger.warning("invalid ray index: %d (total rays: %d)" % (ray_idx, nr_rays))
            return

        from matplotlib import pyplot as plt

        plt.figure("Traced Profile", dpi=120)

        plt.subplot(131)  # profile
        plt.plot(self.data[1], self.data[0])
        plt.gca().invert_yaxis()
        plt.grid(True)
        plt.title('profile')

        plt.subplot(132)  # time
        plt.plot(self.rays[ray_idx][0], self.rays[ray_idx][2])
        plt.gca().invert_yaxis()
        plt.grid(True)
        plt.title('z vs. time')

        plt.subplot(133)  # x
        plt.plot(self.rays[ray_idx][1], self.rays[ray_idx][2])
        plt.gca().invert_yaxis()
        plt.grid(True)
        plt.title('z vs. x')

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__

        msg += "  <timestamp: %s>\n" % self.date_time
        msg += "  <latitude: %.7f>\n" % self.latitude
        msg += "  <longitude: %.7f>\n" % self.longitude
        msg += "  <avg depth: %.3f>\n" % self.avg_depth
        msg += "  <half swatch: %.1f>\n" % self.half_swath
        msg += "  <profile valid samples: %d>\n" % len(self.data[0])
        msg += "  <rays: %d>\n" % len(self.rays)
        msg += "  <samples per ray: %d>\n" % len(self.rays[0][0])

        return msg
