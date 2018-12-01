import os
import time
import math
import numpy as np
import logging

logger = logging.getLogger(__name__)

from hyo2.soundspeed import __version__ as soundspeed_version
from hyo2.soundspeed.profile.metadata import Metadata
from hyo2.soundspeed.profile.samples import Samples
from hyo2.soundspeed.profile.more import More
from hyo2.soundspeed.profile.dicts import Dicts
from hyo2.soundspeed.profile.oceanography import Oceanography as Oc
from hyo2.soundspeed.profile.ray_tracing.ray_tracing import RayTracing
from hyo2.soundspeed.profile.ray_tracing.ray_path import RayPath
from hyo2.soundspeed.profile.ray_tracing.tracedprofile import TracedProfile


class Profile:
    """"A sound speed profile with 3 sections: metadata, data specific to the task, and additional data"""

    def __init__(self):
        self.meta = Metadata()  # metadata
        self.data = Samples()  # raw data
        self.proc = Samples()  # processed data
        self.sis = Samples()  # sis data
        self.more = More()  # additional fields

        self.woa09 = None
        self.woa13 = None
        self.rtofs = None

        # variable for listener since the data are populated in another thread
        self.listener_completed = False
        self.listener_displayed = False

    def __repr__(self):
        msg = "<Profile>\n"
        msg += "%s" % self.meta
        msg += "%s" % self.data
        msg += "%s" % self.more
        return msg

    @classmethod
    def calc_weights(cls, depths):

        mids = (depths[1:] + depths[:-1]) / 2
        mids = np.insert(mids, 0, depths[0])
        mids = np.append(mids, depths[-1])
        diff = np.diff(mids)
        diff = diff / np.sum(diff)

        return diff

    @classmethod
    def weighted_median(cls, values, weights):
        # sort values and weights based on values
        sorted_indices = np.argsort(values)
        values_sorted = values[sorted_indices]
        weights_sorted = weights[sorted_indices]

        acc_prob = 0
        for idx, val in enumerate(values_sorted):
            acc_prob += weights_sorted[idx]
            if acc_prob >= 0.5:
                return val

        raise RuntimeError("unable to calculated median")

    def weighted_harmonic_mean(self):
        avg_depth = 10000.0  # just a very deep value
        half_swath_angle = 1.0  # a small angle since we just cure about nadir

        tp1 = TracedProfile(ssp=self, avg_depth=avg_depth,
                            half_swath=half_swath_angle)

        if len(tp1.harmonic_means) == 0:
            return 0

        return tp1.harmonic_means[0]

    @classmethod
    def weighted_arithmetic_std(cls, values, weights):
        avg = np.average(values, weights=weights)
        var = np.average((values - avg) ** 2, weights=weights)
        return math.sqrt(var)

    def weighted_harmonic_std(self):
        w = self.calc_weights(self.proc.speed[self.proc_valid])
        avg = self.weighted_harmonic_mean()
        var = np.average((self.proc.speed[self.proc_valid] - avg) ** 2, weights=w)
        return math.sqrt(var)

    def init_data(self, num_samples):
        if num_samples == 0:
            return

        self.data.num_samples = num_samples
        self.data.init_pressure()
        self.data.init_depth()
        self.data.init_speed()
        self.data.init_temp()
        self.data.init_conductivity()
        self.data.init_sal()
        self.data.init_source()
        self.data.init_flag()

    def init_proc(self, num_samples):
        if num_samples == 0:
            return

        self.proc.num_samples = num_samples
        self.proc.init_pressure()
        self.proc.init_depth()
        self.proc.init_speed()
        self.proc.init_temp()
        self.proc.init_conductivity()
        self.proc.init_sal()
        self.proc.init_source()
        self.proc.init_flag()

    def init_sis(self, num_samples=0):
        self.sis.num_samples = num_samples
        self.sis.init_pressure()
        self.sis.init_depth()
        self.sis.init_speed()
        self.sis.init_temp()
        self.sis.init_conductivity()
        self.sis.init_sal()
        self.sis.init_source()
        self.sis.init_flag()

    def init_more(self, more_fields):
        self.more.init_struct_array(self.data.num_samples, more_fields)

    def data_resize(self, count):
        self.data.resize(count)
        self.more.resize(count)

    @property
    def data_valid(self):
        """Return indices of valid data"""
        return np.equal(self.data.flag, Dicts.flags['valid'])

    @property
    def proc_valid(self):
        """Return indices of valid proc samples"""
        return np.equal(self.proc.flag, Dicts.flags['valid'])

    @property
    def nr_valid_proc_samples(self):
        """Return the number of valid proc samples"""
        return len(self.proc.depth[self.proc_valid])

    @property
    def proc_dqa_valid(self):
        """Return indices of DQA valid proc samples"""
        return np.logical_and(self.proc_valid, np.equal(self.proc.source, Dicts.sources['raw']))

    @property
    def sis_valid(self):
        """Return indices of valid sis samples"""
        return np.equal(self.sis.flag, Dicts.flags['valid'])

    @property
    def sis_thinned(self):
        """Return indices of thinned sis samples"""
        return np.equal(self.sis.flag, Dicts.flags['thin'])

    @property
    def proc_invalid_direction(self):
        """Return indices of invalid data for direction"""
        return np.equal(self.proc.flag, Dicts.flags['direction'])  # numpy 1.10.4 if a warning

    @property
    def proc_depth_min(self):
        return self.proc.depth[self.proc_valid].min()

    @property
    def proc_speed_min(self):
        return self.proc.speed[self.proc_valid].min()

    @property
    def proc_temp_min(self):
        return self.proc.temp[self.proc_valid].min()

    @property
    def proc_sal_min(self):
        return self.proc.sal[self.proc_valid].min()

    @property
    def proc_depth_max(self):
        return self.proc.depth[self.proc_valid].max()

    @property
    def proc_speed_max(self):
        return self.proc.speed[self.proc_valid].max()

    @property
    def proc_temp_max(self):
        return self.proc.temp[self.proc_valid].max()

    @property
    def proc_sal_max(self):
        return self.proc.sal[self.proc_valid].max()

    @property
    def proc_depth_median(self):
        w = self.calc_weights(self.proc.depth[self.proc_valid])
        return self.weighted_median(self.proc.depth[self.proc_valid], w)

    @property
    def proc_speed_median(self):
        w = self.calc_weights(self.proc.speed[self.proc_valid])
        return self.weighted_median(self.proc.speed[self.proc_valid], w)

    @property
    def proc_temp_median(self):
        w = self.calc_weights(self.proc.temp[self.proc_valid])
        return self.weighted_median(self.proc.temp[self.proc_valid], w)

    @property
    def proc_sal_median(self):
        w = self.calc_weights(self.proc.sal[self.proc_valid])
        return self.weighted_median(self.proc.sal[self.proc_valid], w)

    @property
    def proc_depth_mean(self):
        w = self.calc_weights(self.proc.depth[self.proc_valid])
        return np.average(self.proc.depth[self.proc_valid], weights=w)

    @property
    def proc_speed_mean(self):
        return self.weighted_harmonic_mean()

    @property
    def proc_temp_mean(self):
        w = self.calc_weights(self.proc.temp[self.proc_valid])
        return np.average(self.proc.temp[self.proc_valid], weights=w)

    @property
    def proc_sal_mean(self):
        w = self.calc_weights(self.proc.sal[self.proc_valid])
        return np.average(self.proc.sal[self.proc_valid], weights=w)

    @property
    def proc_depth_std(self):
        w = self.calc_weights(self.proc.depth[self.proc_valid])
        return self.weighted_arithmetic_std(self.proc.depth[self.proc_valid], w)

    @property
    def proc_speed_std(self):
        return self.weighted_harmonic_std()

    @property
    def proc_temp_std(self):
        w = self.calc_weights(self.proc.temp[self.proc_valid])
        return self.weighted_arithmetic_std(self.proc.temp[self.proc_valid], w)

    @property
    def proc_sal_std(self):
        w = self.calc_weights(self.proc.sal[self.proc_valid])
        return self.weighted_arithmetic_std(self.proc.sal[self.proc_valid], w)

    def _calc_water_salinity_threshold(self):
        """Determine salinity threshold from min/max values to help determine where instrument entered water"""
        sal_min = self.proc.sal[self.proc_valid].min()
        sal_max = self.proc.sal[self.proc_valid].max()

        sal_thresh = sal_min + 0.1 * (sal_max - sal_min)  # '10% between extremes
        if sal_thresh < 0.03:
            sal_thresh = 0.03
        elif sal_thresh > 3:
            sal_thresh = 3.0

        return sal_thresh

    def _calc_air_water_index(self):
        """Use the salinity threshold to determine where instrument first entered water."""
        sal_thresh = self._calc_water_salinity_threshold()
        try:
            water_i = np.argwhere(self.proc.sal[self.proc_valid] >= sal_thresh)[0][0]
        except IndexError:  # never passed threshold
            water_i = len(self.proc.sal[self.proc_valid]) - 1
        logger.debug("water index: %d (using salinity threshold: %.3f)" % (water_i, sal_thresh))
        return water_i

    def remove_pre_water_entry(self):
        """Look for data that is likely out of the water by searching for very low salinity levels"""

        if not self.proc.sal.any():
            logger.debug("all salinity values are zero -> skipping pre-water entry removal")
            return

        if self.nr_valid_proc_samples == 0:
            logger.debug("not valid processing samples")
            return

        # remove initial samples out of water using salinity
        water_i = self._calc_air_water_index()
        in_air_ii = np.arange(0, len(self.proc_valid)) < water_i
        valid_and_in_air_ii = np.logical_and(self.proc_valid, in_air_ii)
        self.proc.flag[valid_and_in_air_ii] = Dicts.flags['filtered']

        # remove samples out of water within the profile using salinity
        try:
            sal_th = 0.8 * self.proc.sal[self.proc_valid][0]
            in_air_ii = self.proc.sal <= sal_th
            valid_and_in_air_ii = np.logical_and(self.proc_valid, in_air_ii)
            self.proc.flag[valid_and_in_air_ii] = Dicts.flags['filtered']
        except IndexError:
            logger.warning("issue with removing samples out of the water using salinity")

        # remove samples out of water within the profile using pressure
        try:
            press_th = -0.001
            in_air_ii = self.proc.pressure <= press_th
            valid_and_in_air_ii = np.logical_and(self.proc_valid, in_air_ii)
            self.proc.flag[valid_and_in_air_ii] = Dicts.flags['filtered']
        except IndexError:
            logger.warning("issue with removing samples out of the water using salinity")

    def statistical_filter(self):

        speed = self.proc.speed[self.proc_valid]
        depth = self.proc.depth[self.proc_valid]

        sigma = speed * 0.0
        speed_mean = speed * 0.0

        nr_samples = len(speed)
        sigma_min_th = 0.2  # Minimum standard deviation allowed.
        logger.debug("applying statistical filter at %d valid samples" % nr_samples)

        # Calculate local mean and std dev for each sample, use 2 neighbors on either sides.
        # Endpoints treated separately. Target: single point fliers
        for i in range(2, nr_samples - 2):
            speed_sum = 0
            speed_sum_sq = 0
            for k in range(-2, 3):
                if k == 0:  # skip itself
                    continue
                speed_sum += speed[i + k]
                speed_sum_sq += speed[i + k] * speed[i + k]

            variance = ((4 * speed_sum_sq) - speed_sum * speed_sum) / (4 * 3)  # unbiased variance
            speed_mean[i] = speed_sum / 4
            if variance < 0:
                variance = 0
            sigma[i] = np.sqrt(variance)  # Local standard deviation
            if sigma[i] < sigma_min_th:
                sigma[i] = sigma_min_th

        # Endpoints (use only three neighboring points). Relax tolerance.
        c_end = 1.3  # Relaxed tolerance factor at endpoints.
        ends_i = [0, 1, nr_samples - 2, nr_samples - 1]
        index = [(1, 2, 3), (0, 2, 3), (nr_samples - 4, nr_samples - 3, nr_samples - 1),
                 (nr_samples - 4, nr_samples - 3, nr_samples - 2)]
        for k in range(4):
            speed_sum = 0
            speed_sum_sq = 0
            i = ends_i[k]  # Point number
            for j in range(3):
                ind_kj = index[k][j]
                speed_sum += speed[ind_kj]
                speed_sum_sq += speed[ind_kj] * speed[ind_kj]

            variance = ((3 * speed_sum_sq) - speed_sum * speed_sum) / (3 * 2)  # unbiased variance
            speed_mean[i] = speed_sum / 3
            if variance < 0:
                variance = 0
            sigma[i] = np.sqrt(variance)
            if sigma[i] < sigma_min_th:
                sigma[i] = sigma_min_th
            sigma[i] *= c_end  # Relax tolerance for end pts

        # identify the sample to filter
        nr_std_dev = 2  # number of standard deviations to use for error band.
        tolerance_factor = 1.3  # Tolerance factor.
        depth_th = 33.0  # Depth at which to relax error band.
        factor = tolerance_factor
        stat_filtered = np.zeros(nr_samples, dtype=bool)
        for i in range(nr_samples):
            if depth[i] > depth_th:
                factor = 1.0
            th = factor * nr_std_dev * sigma[i]
            if np.absolute(speed[i] - speed_mean[i]) > th:
                logger.debug("statistical filtering for sample #%d (%.2f, %.2f, th: %.2f)"
                             % (i, speed[i], speed_mean[i], th))
                stat_filtered[i] = True

        # finally apply the statistical filtering
        filtered_ii = np.zeros(len(self.proc_valid), dtype=bool)
        filtered_ii[self.proc_valid] = stat_filtered
        valid_and_filtered_ii = np.logical_and(self.proc_valid, filtered_ii)
        self.proc.flag[valid_and_filtered_ii] = Dicts.flags['filtered']

    def cosine_smooth(self):
        """Cosine-averaging to smooth the profile data"""

        verbose = False  # set to True for verbose intermediate steps

        valid_and_smoothed = self.proc.source[self.proc_valid] == Dicts.sources['smoothing']
        # noinspection PyUnresolvedReferences
        if (valid_and_smoothed == True).all():
            return
        # logger.debug(valid_and_smoothed)

        # retrieve the depths
        zs = self.proc.depth[self.proc_valid]

        # create a dictionary with data types, not including source and type
        names = ["pressure", "speed", "temp", "conductivity", "sal"]
        records = dict()
        records["pressure"] = self.proc.pressure[self.proc_valid]
        records["speed"] = self.proc.speed[self.proc_valid]
        records["temp"] = self.proc.temp[self.proc_valid]
        records["conductivity"] = self.proc.conductivity[self.proc_valid]
        records["sal"] = self.proc.sal[self.proc_valid]

        # create the window widths
        ww_min = 1.7  # minimum window width for the cos( ) function
        ww_mul = 0.0025  # used to grow the window width (that is, to spread the averaging) as the z gets larger
        window_width = np.maximum(np.absolute(zs * ww_mul), ww_min)
        if verbose:
            logger.debug("cosine avg -> window width: %s" % (window_width,))

        # retrieve the profile's z range
        z_min = zs.min()
        z_max = zs.max()
        if verbose:
            logger.debug("cosine avg -> z range: (%f, %f)" % (z_min, z_max))

        # create a 2D storage array:
        # - [rows -> types]: 2 additional rows (bin values on row #0, weights on row #-1)
        # - [cols -> values]: extra columns (that will be removed at the end) on both sides
        bin_size = 1.0  # size of bin, unit or measure is meter (depth)
        bin_width = 4  # number of bins on both sides of the value
        storage = np.zeros([len(names) + 2, int(2 * (bin_width + 1) + (z_max - z_min) / bin_size)])
        if verbose:
            logger.debug("cosine avg -> storage: rows %s, columns %s" % (storage.shape[0], storage.shape[1]))

        # populate bin values (row #0)
        for i in range(storage.shape[1]):
            storage[0][i] = z_min + (- bin_width + i) * bin_size
        if verbose:
            logger.debug("cosine avg -> storage bin values: %s" % (storage[0],))

        # populate weights
        for i, z in enumerate(zs):

            # calculate the index of the central bin value
            center_idx = int((z - z_min) / bin_size + .5) + bin_width
            # if debug:
            #     logger.debug("cosine avg -> z: %s, center index: %s" % (z, center_idx))

            # calculate the differences from the current z values in the averaging windows
            z_diff = z - storage[0][center_idx - bin_width:center_idx + bin_width + 1]
            # if debug:
            #     logger.debug("cosine avg -> z: %s, z diff: %s" % (z, z_diff))

            # Insure that weight will be .1 at a window width from point I
            bin_weights = 1.0 + np.cos(2.69 * z_diff / window_width[i])
            bin_weights *= np.absolute(z_diff) < window_width[i]  # set to 0 when outside the window width
            # if debug:
            #     logger.debug("cosine avg -> z: %s, bin weights: %s" % (z, bin_weights))

            for j, name in enumerate(names):
                # summing up for all the types, row is j + 1 since the first row is for bin values
                storage[1 + j][center_idx - bin_width:center_idx + bin_width + 1] += records[name][i] * bin_weights

            storage[-1][center_idx - bin_width:center_idx + bin_width + 1] += bin_weights

        if verbose:
            logger.debug("cosine avg -> storage weights: %s" % (storage[-1],))
            for j, name in enumerate(names):
                logger.debug("cosine avg -> storage %s sums: %s" % (name, storage[1 + j],))

        # remove the end stuff for the bin widths
        storage = storage[:, bin_width: -(bin_width + 1)]

        # remove bins that didn't have enough weighting.
        storage = np.compress(storage[-1] > 0.1, storage, axis=1)
        # normalize by using the stored weights
        for i in range(len(names)):
            storage[1 + i] /= storage[-1]

        # calculate the z differences + add 1 value to the outcome (to have the same length as the storage)
        delta_zs = np.hstack(([1.0], np.diff(storage[0])))
        # remove duplicated z values
        storage = np.compress(delta_zs >= .00001, storage, axis=1)

        # logger.debug(self.proc.depth)

        # insert created data into the self.proc arrays
        last_depth = 0.0
        for row in storage.T:

            # index of where the storage record falls
            d_th = float(row[0])
            if d_th < last_depth:
                continue
            last_depth = d_th
            try:
                z_bools = np.logical_and(self.proc_valid, self.proc.depth > d_th)
                i = np.argwhere(z_bools)[0]
            except IndexError:
                i = zs.size

            self.proc.depth = np.insert(self.proc.depth, i, d_th)
            self.proc.source = np.insert(self.proc.source, i, Dicts.sources['smoothing'])
            self.proc.flag = np.insert(self.proc.flag, i, Dicts.flags['valid'])
            for j, name in enumerate(names):
                setattr(self.proc, name, np.insert(getattr(self.proc, name), i, row[j + 1]))

            # logger.debug(self.proc.depth)

        # since we inserted new samples
        self.proc.num_samples = self.proc.depth.size

        # mark previous 'valid' data as 'smoothed'
        self.proc.flag[self.proc.source != Dicts.sources['smoothing']] = Dicts.flags['smoothed']

    def reduce_up_down(self, ssp_direction, use_pressure=False):
        """Reduce the raw data samples based on the passed direction"""
        if self.data.num_samples == 0:  # skipping if there are no data
            return

        # identify max depth
        if use_pressure:
            max_value = self.data.pressure[self.data_valid].max()  # max pressure
            logger.debug("reduce up/down > max pressure: %s" % max_value)

        else:
            max_value = self.data.depth[self.data_valid].max()  # max depth
            logger.debug("reduce up/down > max depth: %s" % max_value)

        # loop through the sample using max depth as turning point
        max_reached = False
        last_value = None
        for i in range(self.data.num_samples):

            if use_pressure:
                value = self.data.pressure[i]
            else:
                value = self.data.depth[i]

            if (ssp_direction == Dicts.ssp_directions['up'] and not max_reached) \
                    or (ssp_direction == Dicts.ssp_directions['down'] and max_reached):
                self.data.flag[i] = Dicts.flags['direction']  # set invalid for direction

            elif ssp_direction == Dicts.ssp_directions['down'] and not max_reached:

                if (i != 0) and (last_value is not None):
                    if value <= last_value:
                        # print(last_value, value)
                        self.data.flag[i] = Dicts.flags['direction']  # set invalid for direction
                    else:
                        last_value = value
                else:
                    last_value = value

            elif ssp_direction == Dicts.ssp_directions['up'] and max_reached:

                if (i != 0) and (last_value is not None):
                    if value >= last_value:
                        self.data.flag[i] = Dicts.flags['direction']  # set invalid for direction
                    else:
                        last_value = value
                else:
                    last_value = value

            if value == max_value:
                max_reached = True
                last_value = value

        if ssp_direction == Dicts.ssp_directions['up']:
            logger.debug("flipping data for up direction")
            self.data.pressure[:] = np.flipud(self.data.pressure)
            self.data.depth[:] = np.flipud(self.data.depth)
            self.data.speed[:] = np.flipud(self.data.speed)
            self.data.temp[:] = np.flipud(self.data.temp)
            self.data.conductivity[:] = np.flipud(self.data.conductivity)
            self.data.sal[:] = np.flipud(self.data.sal)
            self.data.source[:] = np.flipud(self.data.source)
            self.data.flag[:] = np.flipud(self.data.flag)

    def calc_salinity_from_conductivity(self):
        if np.count_nonzero(self.data.pressure):
            pressure = self.data.pressure
        else:
            if not self.meta.latitude:
                latitude = 30.0
                logger.warning("using default latitude: %s" % latitude)
            else:
                latitude = self.meta.latitude
            pressure = Oc.d2p_backup(self.data.depth, latitude)

        self.data.sal = np.zeros_like(self.data.conductivity)
        # convert from S/m to mmho/cm
        # self.data.sal[self.data_valid] = Oc.c2s(self.data.conductivity[self.data_valid] * 10.0,
        #                                  pressure[self.data_valid], self.data.temp[self.data_valid])
        self.data.sal = Oc.c2s(self.data.conductivity * 10.0, pressure,
                               self.data.temp)  # FIXME - what is the standard conductivity unit? S/m or mmho/cm (mS/cm)
        self.modify_proc_info(Dicts.proc_import_infos['CALC_SAL'])

    def calc_salinity(self):
        """Helper method to calculate salinity from depth, sound speed and temperature"""
        # logger.debug("calculate salinity")
        if not self.meta.latitude:
            latitude = 30.0
            logger.warning("using default latitude: %s" % latitude)
        else:
            latitude = self.meta.latitude

        for count in range(self.data.num_samples):
            self.data.sal[count] = Oc.sal(d=self.data.depth[count], speed=self.data.speed[count],
                                          t=self.data.temp[count], lat=latitude)
        self.modify_proc_info(Dicts.proc_import_infos['CALC_SAL'])

    def calc_dyn_height(self):
        """Helper method to calculate the dynamic height"""
        if not self.meta.latitude:
            latitude = 30.0
            logger.warning("using default latitude: %s" % latitude)
        else:
            latitude = self.meta.latitude

        if not self.meta.longitude:
            longitude = -70.0
            logger.warning("using default longitude: %s" % longitude)
        else:
            longitude = self.meta.longitude

        try:
            # print(self.data_valid)
            sa = Oc.sal2sa(sal=self.data.sal[self.data_valid],
                           p=self.data.pressure[self.data_valid],
                           lon=longitude, lat=latitude)
            ct = Oc.t2ct(sa=sa,
                         t=self.data.temp[self.data_valid],
                         p=self.data.pressure[self.data_valid])
            dh = Oc.geo_strf_dyn_height(sa=sa, ct=ct, p=self.data.pressure[self.data_valid], p_ref=0)

            for val in dh:
                if np.isnan(val):
                    raise RuntimeError("nan in geo_strf_dyn_height")

            return dh

        except Exception as e:
            logger.warning("issue: %s" % e)
            return None

    def calc_data_depth(self):
        """Helper method to calculate depth from pressure (in dBar)"""
        dyn_height = self.calc_dyn_height()

        if not self.meta.latitude:
            latitude = 30.0
            logger.warning("using default latitude: %s" % latitude)
        else:
            latitude = self.meta.latitude

        self.data.depth = np.zeros_like(self.data.pressure)
        self.data.depth[self.data_valid] = Oc.p2d(p=self.data.pressure[self.data_valid], lat=latitude,
                                                  dyn_height=dyn_height, debug=True)
        self.modify_proc_info(Dicts.proc_import_infos['CALC_DEP'])

    def calc_dyn_height_with_depth(self):
        """Helper method to calculate the dynamic height"""
        if not self.meta.latitude:
            latitude = 30.0
            logger.warning("using default latitude: %s" % latitude)
        else:
            latitude = self.meta.latitude

        if not self.meta.longitude:
            longitude = -70.0
            logger.warning("using default longitude: %s" % longitude)
        else:
            longitude = self.meta.longitude

        try:
            # print(self.data_valid)
            sa = Oc.sal2sa(sal=self.data.sal[self.data_valid],
                           p=self.data.depth[self.data_valid],
                           lon=longitude, lat=latitude)
            ct = Oc.t2ct(sa=sa,
                         t=self.data.temp[self.data_valid],
                         p=self.data.depth[self.data_valid])
            dh = Oc.geo_strf_dyn_height(sa=sa, ct=ct, p=self.data.depth[self.data_valid], p_ref=0)

            for val in dh:
                if np.isnan(val):
                    raise RuntimeError("nan in geo_strf_dyn_height_with_depth")

            return dh

        except Exception as e:
            logger.warning("issue: %s" % e)
            return None

    def calc_data_pressure(self):
        """Helper method to calculate pressure from depth (in m)"""
        dyn_height = self.calc_dyn_height_with_depth()

        raise RuntimeError("Not implemented")

    def calc_data_speed(self):
        """Helper method to calculate sound speed"""
        # logger.debug("calculate sound speed")
        if not self.meta.latitude:
            latitude = 30.0
            logger.warning("using default latitude: %s" % latitude)
        else:
            latitude = self.meta.latitude

        for count in range(self.data.num_samples):
            self.data.speed[count] = Oc.speed(self.data.depth[count],
                                              self.data.temp[count],
                                              self.data.sal[count],
                                              latitude)
        self.modify_proc_info(Dicts.proc_import_infos['CALC_SPD'])

    def calc_proc_speed(self):
        """Helper method to calculate processed sound speed"""
        # logger.debug("calculate sound speed")
        if not self.meta.latitude:
            latitude = 30.0
            logger.warning("using default latitude: %s" % latitude)
        else:
            latitude = self.meta.latitude

        for count in range(self.proc.num_samples):
            self.proc.speed[count] = Oc.speed(self.proc.depth[count],
                                              self.proc.temp[count],
                                              self.proc.sal[count],
                                              latitude)
        self.modify_proc_info(Dicts.proc_user_infos['RECALC_SPD'])

    def calc_attenuation(self, frequency, ph):
        """Helper method to calculation attenuation [unused]"""
        depth = np.zeros(self.proc.num_samples)
        attenuation = np.zeros(self.proc.num_samples)
        for i in range(self.proc.num_samples):
            depth[i] = self.proc.depth[i]
            attenuation[i] = Oc.a(frequency, self.proc.temp[i], self.proc.sal[i],
                                  self.proc.depth[i], ph)

        return attenuation, depth

    def calc_cumulative_attenuation(self, frequency, ph):
        """Helper method to calculation cumulative attenuation [unused]"""
        attenuation, depth = self.calc_attenuation(frequency, ph)
        cumulative_attenuation = np.zeros(len(attenuation))

        total_loss = 0
        for count in range(len(attenuation) - 1):
            layer_loss = attenuation[count] * (depth[count + 1] - depth[count]) / 1000.0
            total_loss += layer_loss
            cumulative_attenuation[count] = total_loss / (depth[count + 1] / 1000.0)

        cumulative_attenuation[-1] = cumulative_attenuation[-2]

        return cumulative_attenuation, depth

    def insert_proc_speed(self, depth, speed, src=Dicts.sources['user']):
        logger.debug("insert speed to proc data: d:%s, vs:%s" % (depth, speed))

        # we need to take care of valid samples and user-invalidated samples (to avoid to brake in case un-flagged)
        valid = self.proc.flag == Dicts.flags['valid']  # valid samples
        iv = np.indices(self.proc.flag.shape)[0][valid]  # indices of valid samples
        user_invalid = self.proc.flag == Dicts.flags['user']  # user-invalidate samples
        possible = np.logical_or(valid, user_invalid)  # possible samples
        ip = np.indices(self.proc.flag.shape)[0][possible]  # indices of possible samples

        # find depth index both in the valid and in the possible samples
        try:
            # noinspection PyTypeChecker
            v_i = np.argwhere(self.proc.depth[valid] > depth)[0][0]  # the index in the valid array
            i = iv[v_i]  # the corresponding index of the masked index in the full array
        except IndexError:  # in case that there are not
            v_i = self.proc.depth[valid].size - 1
            i = iv[v_i]
        try:
            # noinspection PyTypeChecker
            p_i = np.argwhere(self.proc.depth[possible] > depth)[0][0]  # the index in the possible array
            j = ip[p_i]
        except IndexError:  # in case that there are not
            p_i = self.proc.depth[possible].size - 1
            j = ip[p_i]

        # check if we already have this depth in the masked array
        d_exists = self.proc.depth[valid][v_i] == depth

        # manipulate profile (linear interpolation)
        if d_exists:
            # print('already present')
            self.proc.speed[i] = speed
            self.proc.source[i] = src
            self.proc.flag[i] = Dicts.flags['valid']
        else:
            # print('new depth')
            if depth < self.proc.depth[valid][0]:
                m_ids = [0, 1]
                # print('before beginning: %s' % j)

            elif depth > self.proc.depth[valid][-1]:
                j += 1
                m_ids = [-2, -1]
                # print('after end')

            else:
                if self.proc.depth[valid][v_i] < depth:
                    m_ids = [v_i, v_i + 1]
                else:
                    m_ids = [v_i - 1, v_i]
                    # print('in the middle')

            di = np.array([self.proc.depth[valid][m_ids[0]], self.proc.depth[valid][m_ids[1]]])
            a = np.array([[di[0], 1.], [di[1], 1.]])

            # interpolate for pressure
            pi = np.array([self.proc.pressure[valid][m_ids[0]], self.proc.pressure[valid][m_ids[1]]])
            pm, pc = np.linalg.lstsq(a, pi)[0]
            self.proc.pressure = np.insert(self.proc.pressure, j, pm * depth + pc)
            # print(self.proc.pressure[0], self.proc.pressure.size)

            # interpolate for temp
            ti = np.array([self.proc.temp[valid][m_ids[0]], self.proc.temp[valid][m_ids[1]]])
            tm, tc = np.linalg.lstsq(a, ti)[0]
            self.proc.temp = np.insert(self.proc.temp, j, tm * depth + tc)
            # print(self.proc.temp[0], self.proc.temp.size)

            # interpolate for conductivity
            ci = np.array([self.proc.conductivity[valid][m_ids[0]], self.proc.conductivity[valid][m_ids[1]]])
            cm, cc = np.linalg.lstsq(a, ci)[0]
            self.proc.conductivity = np.insert(self.proc.conductivity, j, cm * depth + cc)
            # print(self.proc.conductivity[0], self.proc.conductivity.size)

            # interpolate for sal
            si = np.array([self.proc.sal[valid][m_ids[0]], self.proc.sal[valid][m_ids[1]]])
            sm, sc = np.linalg.lstsq(a, si)[0]
            self.proc.sal = np.insert(self.proc.sal, j, sm * depth + sc)
            # print(self.proc.sal[0], self.proc.sal.size)

            self.proc.depth = np.insert(self.proc.depth, j, depth)
            self.proc.speed = np.insert(self.proc.speed, j, speed)
            self.proc.source = np.insert(self.proc.source, j, src)
            self.proc.flag = np.insert(self.proc.flag, j, Dicts.flags['valid'])

            self.proc.num_samples += 1

    def insert_sis_speed(self, depth, speed, src=Dicts.sources['user'], temp=None, cond=None, sal=None):
        logger.debug("insert speed to sis data: d:%s, vs:%s" % (depth, speed))

        # we need to take care of valid samples and user-invalidated samples (to avoid to brake in case un-flagged)
        valid = self.sis_thinned  # valid samples
        iv = np.indices(self.sis.flag.shape)[0][valid]  # indices of valid samples
        user_invalid = self.sis.flag == Dicts.flags['user']  # user-invalidate samples
        possible = np.logical_or(valid, user_invalid)  # possible samples
        ip = np.indices(self.sis.flag.shape)[0][possible]  # indices of possible samples

        # find depth index both in the valid and in the possible samples
        try:
            # noinspection PyTypeChecker
            v_i = np.argwhere(self.sis.depth[valid] > depth)[0][0]  # the index in the valid array
            i = iv[v_i]  # the corresponding index of the masked index in the full array
        except IndexError:  # in case that there are not
            v_i = self.sis.depth[valid].size - 1
            i = iv[v_i]
        try:
            # noinspection PyTypeChecker
            p_i = np.argwhere(self.sis.depth[possible] > depth)[0][0]  # the index in the possible array
            j = ip[p_i]
        except IndexError:  # in case that there are not
            p_i = self.sis.depth[possible].size - 1
            j = ip[p_i]

        # check if we already have this depth in the masked array
        d_exists = self.sis.depth[valid][v_i] == depth

        # manipulate profile (linear interpolation)
        if d_exists:
            logger.debug('sample already present with depth: %s -> modifying' % depth)
            self.sis.speed[i] = speed
            self.sis.source[i] = src
            self.sis.flag[i] = Dicts.flags['thin']

            if temp is not None:
                self.sis.temp[i] = temp
            if cond is not None:
                self.sis.conductivity[i] = cond
            if sal is not None:
                self.sis.sal[i] = sal

        else:
            logger.debug("added new sample at depth: %s" % depth)
            if depth < self.sis.depth[valid][0]:
                m_ids = [0, 1]
                # print('before beginning: %s' % j)

            elif depth > self.sis.depth[valid][-1]:
                j += 1
                m_ids = [-2, -1]
                # print('after end')

            else:
                if self.sis.depth[valid][v_i] < depth:
                    m_ids = [v_i, v_i + 1]
                else:
                    m_ids = [v_i - 1, v_i]
                    # print('in the middle')

            di = np.array([self.sis.depth[valid][m_ids[0]], self.sis.depth[valid][m_ids[1]]])
            a = np.array([[di[0], 1.], [di[1], 1.]])

            # interpolate for pressure
            pi = np.array([self.sis.pressure[valid][m_ids[0]], self.sis.pressure[valid][m_ids[1]]])
            pm, pc = np.linalg.lstsq(a, pi, rcond=None)[0]
            self.sis.pressure = np.insert(self.sis.pressure, j, pm * depth + pc)
            # print(self.sis.pressure[0], self.sis.pressure.size)

            # interpolate for temp
            if temp is None:
                ti = np.array([self.sis.temp[valid][m_ids[0]], self.sis.temp[valid][m_ids[1]]])
                tm, tc = np.linalg.lstsq(a, ti, rcond=None)[0]
                self.sis.temp = np.insert(self.sis.temp, j, tm * depth + tc)
            else:
                self.sis.temp = np.insert(self.sis.temp, j, temp)
            # logger.debug("added temperature: %s" % self.sis.temp[j])

            # interpolate for conductivity
            if cond is None:
                ci = np.array([self.sis.conductivity[valid][m_ids[0]], self.sis.conductivity[valid][m_ids[1]]])
                cm, cc = np.linalg.lstsq(a, ci, rcond=None)[0]
                self.sis.conductivity = np.insert(self.sis.conductivity, j, cm * depth + cc)
            else:
                self.sis.conductivity = np.insert(self.sis.conductivity, j, cond)
            # logger.debug("added conductivity: %s" % self.sis.conductivity[j])

            # interpolate for sal
            if sal is None:
                si = np.array([self.sis.sal[valid][m_ids[0]], self.sis.sal[valid][m_ids[1]]])
                sm, sc = np.linalg.lstsq(a, si, rcond=None)[0]
                self.sis.sal = np.insert(self.sis.sal, j, sm * depth + sc)
            else:
                self.sis.sal = np.insert(self.sis.sal, j, sal)
            # logger.debug("added salinity: %s" % self.sis.sal[j])

            self.sis.depth = np.insert(self.sis.depth, j, depth)
            self.sis.speed = np.insert(self.sis.speed, j, speed)
            self.sis.source = np.insert(self.sis.source, j, src)
            # we flag it as thin since the user most likely wants to have this value in the export
            self.sis.flag = np.insert(self.sis.flag, j, Dicts.flags['thin'])

            self.sis.num_samples += 1

    def insert_proc_temp_sal(self, depth, temp, sal):
        logger.debug("insert temp, sal to proc data: d:%s, t:%s, s:%s" % (depth, temp, sal))

        speed = Oc.speed(d=depth, t=temp, s=sal, lat=self.meta.latitude)

        # we need to take care of valid samples and user-invalidated samples (to avoid to brake in case un-flagged)
        valid = self.proc.flag == Dicts.flags['valid']  # valid samples
        iv = np.indices(self.proc.flag.shape)[0][valid]  # indices of valid samples
        user_invalid = self.proc.flag == Dicts.flags['user']  # user-invalidate samples
        possible = np.logical_or(valid, user_invalid)  # possible samples
        ip = np.indices(self.proc.flag.shape)[0][possible]  # indices of possible samples

        # find depth index both in the valid and in the possible samples
        try:
            # noinspection PyTypeChecker
            v_i = np.argwhere(self.proc.depth[valid] > depth)[0][0]  # the index in the valid array
            i = iv[v_i]  # the corresponding index of the masked index in the full array
        except IndexError:  # in case that there are not
            v_i = self.proc.depth[valid].size - 1
            i = iv[v_i]
        try:
            # noinspection PyTypeChecker
            p_i = np.argwhere(self.proc.depth[possible] > depth)[0][0]  # the index in the possible array
            j = ip[p_i]
        except IndexError:  # in case that there are not
            p_i = self.proc.depth[possible].size - 1
            j = ip[p_i]

        # check if we already have this depth in the masked array
        d_exists = self.proc.depth[valid][v_i] == depth

        # manipulate profile (linear interpolation)
        if d_exists:
            # print('already present')
            self.proc.temp[i] = temp
            self.proc.sal[i] = sal
            self.proc.speed[i] = speed
            self.proc.source[i] = Dicts.sources['user']
            self.proc.flag[i] = Dicts.flags['valid']
        else:
            # print('new depth')
            if depth < self.proc.depth[valid][0]:
                m_ids = [0, 1]
                # print('before beginning: %s' % j)

            elif depth > self.proc.depth[valid][-1]:
                j += 1
                m_ids = [-2, -1]
                # print('after end')

            else:
                if self.proc.depth[valid][v_i] < depth:
                    m_ids = [v_i, v_i + 1]
                else:
                    m_ids = [v_i - 1, v_i]
                    # print('in the middle')

            di = np.array([self.proc.depth[valid][m_ids[0]], self.proc.depth[valid][m_ids[1]]])
            a = np.array([[di[0], 1.], [di[1], 1.]])

            # interpolate for pressure
            pi = np.array([self.proc.pressure[valid][m_ids[0]], self.proc.pressure[valid][m_ids[1]]])
            pm, pc = np.linalg.lstsq(a, pi)[0]
            self.proc.pressure = np.insert(self.proc.pressure, j, pm * depth + pc)
            # print(self.proc.pressure[0], self.proc.pressure.size)

            # interpolate for conductivity
            ci = np.array([self.proc.conductivity[valid][m_ids[0]], self.proc.conductivity[valid][m_ids[1]]])
            cm, cc = np.linalg.lstsq(a, ci)[0]
            self.proc.conductivity = np.insert(self.proc.conductivity, j, cm * depth + cc)
            # print(self.proc.conductivity[0], self.proc.conductivity.size)

            self.proc.depth = np.insert(self.proc.depth, j, depth)
            self.proc.speed = np.insert(self.proc.speed, j, speed)
            self.proc.temp = np.insert(self.proc.temp, j, temp)
            self.proc.sal = np.insert(self.proc.sal, j, sal)
            self.proc.source = np.insert(self.proc.source, j, Dicts.sources['user'])
            self.proc.flag = np.insert(self.proc.flag, j, Dicts.flags['valid'])

            self.proc.num_samples += 1

    def extend_profile(self, extender, ext_type):
        """ Use the extender samples to extend the profile """
        logger.debug("extension source type: %s" % Dicts.first_match(Dicts.sources, ext_type))
        try:
            extender.cur.proc.source[:] = ext_type
        except AttributeError:
            return False

        # find the max valid depth in the current profile
        if self.proc.num_samples > 0:
            vi = self.proc_valid
            ivs = np.indices(self.proc.flag.shape)[0][vi]  # indices of valid samples
            max_depth = self.proc.depth[vi].max()  # this is the max of the valid samples
            # noinspection PyTypeChecker
            vi_idx = np.argwhere(self.proc.depth[vi] >= max_depth)[0][0]  # index of the max depth
            max_idx = ivs[vi_idx]  # index of the max depth in the original array
        else:
            max_depth = 0
            max_idx = 0
        # logger.debug("orig.max depth: %s[%s]" % (max_depth, max_idx))

        # find the depth values in the extender that are deeper than the current (valid) max depth
        ext_vi = extender.cur.proc_valid
        try:
            # noinspection PyTypeChecker
            ind2 = np.argwhere(extender.cur.proc.depth[ext_vi][:] > max_depth)[0][0]
            if ind2 <= 0:
                logger.info("nothing to extend with")
                return True
                # logger.debug("ext.max depth: [%s]" % ind2)
        except IndexError as e:
            logger.warning("too short to extend with: %s" % e)
            return True

        # stack the extending samples after the last valid (max depth) index
        self.proc.pressure = np.hstack([self.proc.depth[:max_idx],
                                        np.zeros_like(extender.cur.proc.depth[ext_vi][ind2:])])
        self.proc.depth = np.hstack([self.proc.depth[:max_idx],
                                     extender.cur.proc.depth[ext_vi][ind2:]])
        self.proc.speed = np.hstack([self.proc.speed[:max_idx],
                                     extender.cur.proc.speed[ext_vi][ind2:]])
        self.proc.temp = np.hstack([self.proc.temp[:max_idx],
                                    extender.cur.proc.temp[ext_vi][ind2:]])
        self.proc.conductivity = np.hstack([self.proc.sal[:max_idx],
                                            np.zeros_like(extender.cur.proc.sal[ext_vi][ind2:])])
        self.proc.sal = np.hstack([self.proc.sal[:max_idx],
                                   extender.cur.proc.sal[ext_vi][ind2:]])
        self.proc.source = np.hstack([self.proc.source[:max_idx],
                                      extender.cur.proc.source[ext_vi][ind2:]])
        self.proc.flag = np.hstack([self.proc.flag[:max_idx],
                                    extender.cur.proc.flag[ext_vi][ind2:]])
        self.proc.num_samples = self.proc.depth.size

        # update processing info
        if ext_type == Dicts.sources['ref_ext']:
            self.modify_proc_info(Dicts.proc_user_infos['EXT_REF'])

        elif ext_type == Dicts.sources['rtofs_ext']:
            self.modify_proc_info(Dicts.proc_user_infos['EXT_RTOFS'])

        elif ext_type == Dicts.sources['woa09_ext']:
            self.modify_proc_info(Dicts.proc_user_infos['EXT_WOA09'])

        elif ext_type == Dicts.sources['woa13_ext']:
            self.modify_proc_info(Dicts.proc_user_infos['EXT_WOA13'])

        else:
            logger.warning("unknown atlases: %s" % ext_type)
            return False

        return True

    def modify_proc_info(self, info):

        if info not in Dicts.proc_user_infos.values():
            if info not in Dicts.proc_import_infos.values():
                raise RuntimeError("invalid processing info: %s" % info)

        # if empty, add the info
        if not self.meta.proc_info:
            self.meta.proc_info = info
            return

        # check if it is already present
        tokens = self.meta.proc_info.split(';')
        if info not in tokens:
            self.meta.proc_info += ';%s' % info

    def remove_user_proc_info(self):

        # if empty, nothing to do
        if not self.meta.proc_info:
            return

        # check if it is already present
        tokens = self.meta.proc_info.split(';')
        self.meta.proc_info = None
        for i, token in enumerate(tokens):

            if token in Dicts.proc_import_infos.values():

                if self.meta.proc_info is None:
                    self.meta.proc_info = '%s' % token

                else:
                    self.meta.proc_info += ';%s' % token

    def clone_data_to_proc(self):
        """Clone the raw data samples into proc samples

        The operation eliminates the direction-flagged samples
        """
        logger.info("cloning raw data to proc samples")

        if self.data.num_samples == 0:
            return

        vi = self.data_valid  # invalid samples (no direction-flagged)

        self.init_proc(np.sum(vi))
        self.proc.pressure[:] = self.data.pressure[vi]
        self.proc.depth[:] = self.data.depth[vi]
        self.proc.speed[:] = self.data.speed[vi]
        self.proc.temp[:] = self.data.temp[vi]
        self.proc.conductivity[:] = self.data.conductivity[vi]
        self.proc.sal[:] = self.data.sal[vi]
        self.proc.source[:] = self.data.source[vi]
        self.proc.flag[:] = self.data.flag[vi]

        self.update_proc_time()

    def clone_proc_to_sis(self):
        """Clone the processed data samples into sis samples"""
        logger.info("cloning proc data to sis samples")

        if self.proc.num_samples == 0:
            return

        self.init_sis(self.proc.depth.size)
        self.sis.pressure[:] = self.proc.pressure
        self.sis.depth[:] = self.proc.depth
        self.sis.speed[:] = self.proc.speed
        self.sis.temp[:] = self.proc.temp
        self.sis.conductivity[:] = self.proc.conductivity
        self.sis.sal[:] = self.proc.sal
        self.sis.source[:] = self.proc.source
        self.sis.flag[:] = self.proc.flag

    def update_proc_time(self):
        self.meta.update_proc_time()

    def replace_proc_sal(self, source):  # unused
        try:
            self.proc.sal = np.interp(self.proc.depth[:], source.cur.proc.depth[:], source.cur.proc.sal[:])
        except Exception as e:
            logger.warning("in replace salinity, %s" % e)
            return False
        return True

    def replace_proc_temp_sal(self, source):  # unused
        try:
            self.proc.temp = np.interp(self.proc.depth[:], source.cur.proc.depth[:], source.cur.proc.temp[:])
            self.proc.sal = np.interp(self.proc.depth[:], source.cur.proc.depth[:], source.cur.proc.sal[:])
        except Exception as e:
            logger.warning("in replace temp/sal, %s" % e)
            return False
        return True

    # - thinning

    def thin(self, tolerance):
        """Thin the sis data"""
        logger.info("thinning the sis samples")

        # if the profile is too short, we just pass it back
        if self.sis.depth[self.sis_valid].size < 100:
            self.sis.flag[self.sis_valid] = Dicts.flags['thin']
            logger.debug("skipping thinning for short profile (%d samples)" % self.sis.depth[self.sis_valid].size)
            return True

        # - 1000 points for: EM2040, EM710, EM302 and EM122;
        # - 570 points for: EM3000, EM3002, EM1002, EM300, EM120
        flagged = self.sis.flag[self.sis_valid][:]
        idx_start = 0
        idx_end = self.sis.depth[self.sis_valid].size - 1
        # logger.debug('first: %s, last: %s[%s]'
        #              % (self.sis.depth[self.sis_valid][idx_start],
        #                 self.sis.depth[self.sis_valid][idx_end],
        #                 self.sis.flag[self.sis_valid][idx_end]))
        self.douglas_peucker_1d(idx_start, idx_end, tolerance=tolerance, data=flagged)
        self.sis.flag[self.sis_valid] = flagged[:]

        # logger.info("thinned: %s" % self.sis.flag[self.sis_thinned].size)
        return True

    def douglas_peucker_1d(self, start, end, tolerance, data):
        """ Recursive implementation """
        # logger.debug("dp: %s, %s" % (start, end))

        # We always keep end points
        data[start] = Dicts.flags['thin']
        data[end] = Dicts.flags['thin']

        slope = (self.sis.speed[self.sis_valid][end] - self.sis.speed[self.sis_valid][start]) / \
                (self.sis.depth[self.sis_valid][end] - self.sis.depth[self.sis_valid][start])

        max_dist = 0
        max_ind = 0
        for ind in range(start + 1, end):
            dist = abs(self.sis.speed[self.sis_valid][start] +
                       slope * (self.sis.depth[self.sis_valid][ind] - self.sis.depth[self.sis_valid][start]) -
                       self.sis.speed[self.sis_valid][ind])

            if dist > max_dist:
                max_dist = dist
                max_ind = ind

        if max_dist <= tolerance:
            return

        else:
            data[max_ind] = Dicts.flags['thin']
            # print(max_ind, max_dist, data[max_ind])
            self.douglas_peucker_1d(start, max_ind, tolerance, data=data)
            self.douglas_peucker_1d(max_ind, end, tolerance, data=data)
            return

    # - debugging

    def data_debug_plot(self, more=False):
        """Create a debug plot with the data, optionally with the extra data if available"""
        if self.data.depth is None:
            return
        else:
            self._plot(samples=self.data, more=more, kind='data')

    def proc_debug_plot(self, more=False):
        """Create a debug plot with the processed data, optionally with the extra data if available"""
        if self.proc.depth is None:
            return
        else:
            self._plot(samples=self.proc, more=more, kind='proc')

    def sis_debug_plot(self, more=False):
        """Create a debug plot with the sis-targeted data, optionally with the extra data if available"""
        if self.sis.depth is None:
            return
        else:
            self._plot(samples=self.sis, more=more, kind='sis')

    def _plot(self, samples, more, kind):
        from matplotlib import pyplot as plt
        plt.figure("[%s] %s" % (self.meta.original_path, kind), dpi=120)

        if samples.speed is not None:
            plt.subplot(231)  # speed
            plt.plot(samples.speed, samples.depth)
            plt.gca().invert_yaxis()
            plt.grid(True)
            plt.title('speed')

        if samples.temp is not None:
            plt.subplot(232)  # temp
            plt.plot(samples.temp, samples.depth)
            plt.gca().invert_yaxis()
            plt.grid(True)
            plt.title('temp')

        if samples.sal is not None:
            plt.subplot(233)  # sal
            plt.plot(samples.sal, samples.depth)
            plt.gca().invert_yaxis()
            plt.grid(True)
            plt.title('sal')

        if samples.flag is not None:
            plt.subplot(234)  # source
            plt.plot(samples.source, samples.depth)
            plt.gca().invert_yaxis()
            plt.grid(True)
            plt.title('source')

        if samples.flag is not None:
            plt.subplot(235)  # flag
            plt.plot(samples.flag, samples.depth)
            plt.gca().invert_yaxis()
            plt.grid(True)
            plt.title('flag')

        plt.subplot(236)  # meta
        fs = 8  # font size
        plt.title('meta[%s]' % kind)
        plt.axis('off')
        plt.text(0.1, 0.25, self.meta.debug_info(), fontsize=fs)
        plt.show(block=False)

        if more:
            self.more.debug_plot()

    def interpolate_proc_speed_at_depth(self, depth, points=3):
        """ Return speed difference at the passed depth"""

        # identify start/end of profile data to be used for interpolation
        idx = np.searchsorted(self.proc.depth[self.proc_dqa_valid], depth)
        start = (idx - points) if (idx - points >= 0) else 0
        end = idx + points

        # calculate coefficients and interpolated speed
        coefficients = np.polyfit(self.proc.depth[self.proc_dqa_valid][start:end],
                                  self.proc.speed[self.proc_dqa_valid][start:end], 2)
        cast_speed = np.poly1d(coefficients)(depth)

        return cast_speed

    def compute_ray_paths(self, draft, thetas_deg, travel_times=None, res=.005, b_project=False):
        """Returns a RayPath object for each launch angle."""
        if not draft or draft == 'Unknown':
            draft = 0.0
        else:
            draft = float(draft)

        depths = self.proc.depth[self.proc_dqa_valid] - draft
        speeds = self.proc.speed[self.proc_dqa_valid]

        ray_paths = []
        for launch in thetas_deg:

            params = RayTracing.get_svp_layer_parameters(np.deg2rad(launch), depths, speeds)
            if travel_times is None:
                tt = np.arange(res, params[-2][-1], res)  # make travel_times to reach end of profile
            else:
                tt = np.array(travel_times)

            rays = RayTracing.ray_trace(tt, depths, speeds, params, b_project=b_project)
            rays[:, 0] += draft

            ray_paths.append(RayPath(np.vstack((tt, rays.transpose())).transpose()))

        return ray_paths

    def compare_profile(self, profile, angle):

        dep_max = min(self.proc.depth[self.proc_dqa_valid].max(), profile.proc.depth[profile.proc_dqa_valid].max())
        if dep_max <= 400:
            tt_inc = 0.002  # Travel time increment in seconds.
        elif dep_max <= 800:
            tt_inc = 0.005
        else:
            tt_inc = 0.01

        draft1 = 0.0  # TODO
        draft2 = 0.0  # TODO
        draft = max(draft1, draft2)

        # Generate the travel time table for the two profiles.
        ray1 = self.compute_ray_paths(draft, [angle], res=tt_inc)[0]
        ray2 = profile.compute_ray_paths(draft, [angle], res=tt_inc)[0]

        nr_points = min(len(ray1.data), len(ray2.data))
        if nr_points == 0:
            raise RuntimeError("One of the two profiles is too shallow!")

        depth1 = ray1.data[:nr_points, 1]
        depth2 = ray2.data[:nr_points, 1]
        delta_depth = depth2 - depth1
        larger_depths = np.maximum(depth1, depth2)
        pct_diff = np.absolute(delta_depth / larger_depths) * 100.0
        # noinspection PyUnresolvedReferences
        max_diff_index = pct_diff.argmax()
        # noinspection PyUnresolvedReferences
        max_diff = pct_diff[max_diff_index]
        max_diff_depth = larger_depths[max_diff_index]

        # create output message

        p1 = "<pre style='margin:1px;'>"
        p2 = "</pre>"

        self_path = self.meta.original_path
        self_path = self_path if os.path.exists(self_path) else os.path.basename(self_path)
        profile_path = profile.meta.original_path
        profile_path = profile_path if os.path.exists(profile_path) else os.path.basename(profile_path)

        msg = "%s<b>SUMMARY OF RESULTS - COMPARE 2 CASTS</b>%s<br>" % (p1, p2)

        msg += "%s<b>Sound Speed library</b>:                 %s%s" % (p1, soundspeed_version, p2)
        msg += "%s<b>Reference profile</b>:                   %s%s" % (p1, self_path, p2)
        msg += "%s<b>Comparison profile</b>:                  %s%s" % (p1, profile_path, p2)
        msg += "%s<b>Reference instrument</b>:                sensor-%s, probe-%s%s%s" \
               % (p1, self.meta.sensor, self.meta.probe, ", sn-%s" % self.meta.sn if self.meta.sn else "", p2)
        msg += "%s<b>Comparison instrument</b>:               sensor-%s, probe-%s%s%s<br>" \
               % (p1, profile.meta.sensor, profile.meta.probe, ", sn-%s" % profile.meta.sn if profile.meta.sn else "",
                  p2)

        msg += "%s<b>Draft</b>:                               %.2f m%s" % (p1, draft, p2)
        msg += "%s<b>Maximum Common Depth</b>:                %.2f m%s" % (p1, dep_max, p2)
        msg += "%s<b>Maximum Depth Percentage Difference</b>: %.2f%%%s" % (p1, max_diff, p2)
        msg += "%s<b>Maximum Percentage Difference at</b>:    %.2f m%s<br>" % (p1, max_diff_depth, p2)

        msg += "%s<b>Max percentage diff. line and last line of travel time table</b>:%s" % (p1, p2)

        msg += "%sTravel time, Avg Depth, Depth Diff, Pct Depth Diff, Avg Crosstrack, Crosstrack Diff, " \
               "Pct Crosstrack Diff%s" % (p1, p2)
        for ni in (max_diff_index, nr_points - 1):
            msg += "%s%9.2f s,%8.2f m,%9.2f m,%14.2f%%,%13.2f m,%14.2f m,%19.2f%%%s" \
                   % (
                       p1,
                       ray1.data[ni, 0],  # travel time
                       np.average([ray1.data[ni, 1], ray2.data[ni, 1]]),  # avg. depth
                       np.absolute(delta_depth[ni]),  # depth diff.
                       pct_diff[ni],  # pct. depth diff.
                       np.average([ray1.data[ni, 2], ray2.data[ni, 2]]),  # avg. cross-track
                       np.absolute(ray1.data[ni, 2] - ray2.data[ni, 2]),  # cross-track diff.
                       100.0 * np.absolute(ray1.data[ni, 2] - ray2.data[ni, 2]) /
                       max(ray1.data[ni, 2], ray2.data[ni, 2]),  # pct. cross-track diff.
                       p2
                   )

        msg += '<br>%s%s%s<br>' % (p1, time.ctime(), p2)

        if max_diff > 0.25:
            msg += "%s<b>RESULTS INDICATE PROBLEM.</b>%s" % (p1, p2)
            msg += "%sThe absolute value of percent depth difference exceeds the recommended amount (.25).%s" % (p1, p2)
            msg += "%sIf test was conducted to compare 2 casts for possible grouping into one representative%s" \
                   % (p1, p2)
            msg += "%scast, then the 2 casts should NOT be grouped.%s" % (p1, p2)
            msg += "%sIf test was run as part of a Data Quality Assurance for 2 simultaneous casts, then one%s" \
                   % (p1, p2)
            msg += "%sor both of the instruments used is functioning improperly. Investigate further by%s" % (p1, p2)
            msg += "%sperforming simultaneous casts of each of the instruments with a third instrument.%s" % (p1, p2)
            msg += "%sThen rerun this procedure with the 2 new pairs of casts to determine which one of%s" % (p1, p2)
            msg += "%sthe instruments is not functioning properly.%s" % (p1, p2)
            msg += "%sIf the test was run to compare an XBT cast with the last CTD cast, then it is time%s" % (p1, p2)
            msg += "%sto take a new CTD cast.%s<br>" % (p1, p2)

            msg += "%s<b>RESULTS</b>: PERCENT DEPTH DIFFERENCE TOO LARGE%s" % (p1, p2)

        else:
            msg += "%s<b>RESULTS OK.</b>%s" % (p1, p2)
            msg += "%sPercent depth difference is within recommended bounds.%s<br>" % (p1, p2)

            msg += "%s<b>RESULTS</b>: PERCENT DEPTH DIFFERENCE OK%s" % (p1, p2)

        return msg
