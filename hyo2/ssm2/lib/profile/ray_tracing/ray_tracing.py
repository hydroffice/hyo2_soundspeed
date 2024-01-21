import numpy as np
from numpy import sin, cos, tan, arcsin, log, arctan, exp
import logging

logger = logging.getLogger(__name__)


class RayTracing:

    @classmethod
    def get_svp_layer_parameters(cls, launch_angle_radians, depths, speeds):
        return cls.get_svp_layer_parameters_slow(launch_angle_radians, depths, speeds)

    @classmethod
    def get_svp_layer_parameters_slow(cls, launch_angle_radians, depths, speeds):

        gamma = np.zeros(depths.shape, np.float64)
        radius = np.zeros(depths.shape, np.float64)
        total_time = np.zeros(depths.shape, np.float64)
        total_range = np.zeros(depths.shape, np.float64)

        speed = np.array(speeds, np.float64)  # need double precision for this computation
        depth = np.array(depths, np.float64)

        depth[0] = 0.0  # assume zero for top layer
        gamma[0] = launch_angle_radians
        total_time[0] = 0
        total_range[0] = 0

        delta_depth = np.diff(depth)
        gradient = np.diff(speed) / delta_depth
        for j in range(len(depth) - 1):

            gamma[j + 1] = arcsin((speed[j + 1] / speed[j]) * sin(gamma[j]))
            if gamma[j] == 0:  # // nadir beam (could cause division by zero errors below)
                radius[j] = 0
                total_time[j + 1] = total_time[j] + (delta_depth[j]) / ((speed[j + 1] + speed[j]) / 2.0)
                total_range[j + 1] = total_range[j]

            elif gradient[j] == 0:
                radius[j] = 0
                total_time[j + 1] = total_time[j] + (delta_depth[j]) / (speed[j] * cos(gamma[j]))
                total_range[j + 1] = total_range[j] + (delta_depth[j]) * tan(gamma[j])

            else:
                radius[j] = speed[j] / (gradient[j] * sin(gamma[j]))
                total_time[j + 1] = total_time[j] + log(tan(gamma[j + 1] / 2.0) / tan(gamma[j] / 2.0)) / gradient[j]
                total_range[j + 1] = total_range[j] + radius[j] * (cos(gamma[j]) - cos(gamma[j + 1]))

        # Note the last radius doen't get computed but that isn't important
        # we always want to be in the last layer, so we use the comptutations at the next to last layer
        # and interpolate to the depth/time which is before the end of the last layer
        return gradient, gamma, radius, total_time, total_range

    @classmethod
    def ray_trace(cls, travel_times, depths, speeds, params, b_project=False):

        nr_layers = len(depths) - 1

        speed = speeds.copy()
        depth = depths.copy()
        depth[0] = 0.0  # assume zero for top layer

        gradient, gamma, radius, total_time, total_range = params
        try:
            len(travel_times)  # make sure we get a list of indices back to iterate on
        except:
            travel_times = [travel_times]

        nr_end_layers = total_time.searchsorted(travel_times) - 1
        ret = np.zeros([len(travel_times), 2]) - 1.0  # create an array where -1 denotes out of range
        for ind, nr_end_layer in enumerate(nr_end_layers):

            if nr_end_layer == -1:
                nr_end_layer = 0

            if nr_end_layer < nr_layers or b_project:  # SVP deep enough

                tau = travel_times[ind] - total_time[nr_end_layer]
                # Note the last radius doen't get computed but that isn't important
                # we always want to be in the last layer, so we use the comptutations at the next to last layer
                # and interpolate to the depth/time which is before the end of the last layer
                if radius[nr_end_layer] == 0:

                    if nr_end_layer < nr_layers:

                        a1 = total_time[nr_end_layer]
                        a2 = total_time[nr_end_layer + 1]
                        a3 = speed[nr_end_layer]
                        a4 = speed[nr_end_layer + 1]
                        if isinstance(a1, np.ndarray):
                            a1 = a1[0]
                            a2 = a2[0]
                            a3 = a3[0]
                            a4 = a4[0]
                        endspeed = np.interp(travel_times[ind], [a1, a2], [a3, a4])
                        # endspeed = scipy.interp(traveltimes[ind], [totaltime[nEndLayer],totaltime[nEndLayer+1]],
                        # [speed[nEndLayer],speed[nEndLayer+1]])

                    else:  # projecting the last speed to infinite depth

                        endspeed = speed[nr_end_layer]

                    avg_speed = (speed[nr_end_layer] + endspeed) / 2.0
                    final_depth = avg_speed * tau * cos(gamma[nr_end_layer]) + depth[nr_end_layer]
                    final_range = avg_speed * tau * sin(gamma[nr_end_layer]) + total_range[nr_end_layer]

                else:

                    final_depth = radius[nr_end_layer] * (
                            sin(2 * arctan(tan(gamma[nr_end_layer] / 2.0) * exp(gradient[nr_end_layer] * tau))) - sin(
                        gamma[nr_end_layer])) + depth[nr_end_layer]
                    final_range = radius[nr_end_layer] * (
                            -cos(2 * arctan(tan(gamma[nr_end_layer] / 2.0) * exp(gradient[nr_end_layer] * tau))) + cos(
                        gamma[nr_end_layer])) + total_range[nr_end_layer]

                # this would translate to acrosstrack, alongtrack components if we passed in pitch, roll, launchangle
                # result[0]=finalrange*LaunchVector[0]/sqrt(LaunchVector[1]*LaunchVector[1]+LaunchVector[0]*LaunchVector[0])
                # result[1]=finalrange*LaunchVector[1]/sqrt(LaunchVector[1]*LaunchVector[1]+LaunchVector[0]*LaunchVector[0])
                # result[2]=finaldepth

                if isinstance(final_depth, np.ndarray):
                    final_depth = final_depth[0]
                    final_range = final_range[0]

                ret[ind] = (final_depth, final_range)

        return ret
