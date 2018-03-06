import numpy as np
import math
import logging

logger = logging.getLogger(__name__)

from hyo.soundspeed.profile.dicts import Dicts


class TracedProfile:

    def __init__(self, tss_depth, tss_value, avg_depth, half_swath, ssp):

        self.avg_depth = avg_depth
        self.half_swath = half_swath

        # select samples for the ray tracing (must be deeper than the transducer depth)
        depth = [tss_depth, ]
        speed = [tss_value, ]
        for z_idx in range(0, len(ssp.cur.proc.depth)):

            # skip samples at depth less than the draft
            if ssp.cur.proc.depth[z_idx] <= tss_depth:
                # logger.debug("skipping sample at depth: %.1f" % ssp.cur.proc.depth[n])
                continue

            if ssp.cur.proc.flag[z_idx] != Dicts.flags['valid']:
                continue

            depth.append(ssp.cur.proc.depth[z_idx])
            speed.append(ssp.cur.proc.speed[z_idx])

            # stop after the first sample deeper than the avg depth (safer)
            if ssp.cur.proc.depth[z_idx] > self.avg_depth:
                break

        # remove extension value (if any)
        if (depth[-1] - depth[-2]) > 1000:
            logger.info("removed latest extension depth: %s" % depth[-1])
            del depth[-1]

        # logger.debug("samples: %d" % len(depth))
        # logger.debug("depths: %s" % depth)
        # logger.debug("speeds: %s" % speed)

        # ray-trace a few angles (ref: Lurton, An Introduction to UA, p.50-52)
        txz_values = list()
        for angle in np.arange(0, int(math.ceil(self.half_swath + 1))):

            # ray angles
            beta = list()
            beta.append(math.acos(speed[0]/tss_value * math.cos(math.radians(90.0 - angle))))
            total_z = list()
            total_z.append(depth[0])
            total_x = list()
            total_x.append(0)
            total_t = list()  # total travel time
            total_t.append(0)

            # logger.debug("angle %d: beta0 %s" % (angle, math.degrees(beta[0])))

            for idx in range(0, len(depth) - 1):

                # calculate delta (next - current)
                dz = depth[idx+1] - depth[idx]
                dc = speed[idx+1] - speed[idx]
                # logger.debug("%s: dy %s, dc %s" % (x, dy, dc))

                if dc == 0:  # "constant speed" case: no curvature

                    if dz == 0:  # if (dc == 0) and (dy == 0):

                        logger.warning("skipping duplicated point: #%d" % idx)
                        continue

                    # gradient = dc/dy
                    beta.append(beta[idx])  # beta does not change
                    dx = dz / (math.tan(beta[idx+1]))  # no curvature!
                    dt = (((dx**2)+(dz**2))**.5) / speed[idx+1]

                elif dz == 0:  # "same depth" case: just adjust the ray angle

                    beta.append(math.acos((speed[idx + 1] / speed[idx]) * (math.cos(beta[idx]))))
                    continue

                else:  # if (dc != 0) and (dz != 0):

                    gradient = dc / dz  # Lurton, (2.64)
                    if math.cos(beta[idx]) == 0:
                        curve = 0
                    else:  # if math.cos(beta[x]) != 0:
                        curve = speed[idx] / (gradient * math.cos(beta[idx]))  # Lurton, (2.66)

                    # try:
                    beta.append(math.acos(speed[idx + 1] / speed[idx] * (math.cos(beta[idx]))))  # Derived from Lurton, (2.65)
                    # except Exception as e:
                    #     logger.debug("%s: %s, %s, %s -> %s" % (x, speed[x + 1], speed[x], math.degrees(beta[x]),
                    #     (speed[x + 1] / speed[x]) * (math.cos(beta[x]))))
                    #     raise e

                    dx = curve * ((math.sin(beta[idx])) - (math.sin(beta[idx + 1])))  # Lurton, (2.67)
                    dt = abs((1 / gradient) *
                             math.log(
                                (speed[idx + 1] / speed[idx]) *
                                (abs((1 + math.sin(beta[idx])) / (1 + math.sin(beta[idx + 1]))))))  # Lurton, (2.70)

                total_z.append(total_z[-1] + dz)
                total_x.append(total_x[-1] + dx)
                total_t.append(total_t[-1] + dt)

            interp_t = np.arange(total_t[0], ((round(total_t[len(total_t) - 1] * 1e3)) / 1e3), 1e-3)
            interp_x = np.interp(interp_t, total_t, total_x)
            interp_z = np.interp(interp_t, total_t, total_z)
            txz_values.append(np.array([interp_t, interp_x, interp_z]))

        self.rays = txz_values
        self.date_time = ssp.cur.meta.utc_time
        self.latitude = ssp.cur.meta.latitude
        self.longitude = ssp.cur.meta.longitude
        self.data = [depth, speed]

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__

        msg += "  <timestamp: %s>\n" % self.date_time
        msg += "  <latitude: %.7f>\n" % self.latitude
        msg += "  <longitude: %.7f>\n" % self.longitude
        msg += "  <avg depth: %.3f>\n" % self.avg_depth
        msg += "  <half swatch: %.1f>\n" % self.half_swath
        msg += "  <rays: %d>\n" % len(self.rays)
        msg += "  <samples: %d>" % len(self.data[0])

        return msg
