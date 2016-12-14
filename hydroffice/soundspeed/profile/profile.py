from __future__ import absolute_import, division, print_function, unicode_literals

import time
import numpy as np
import logging

logger = logging.getLogger(__name__)

from hydroffice.soundspeed import __version__ as ssp_version
from hydroffice.soundspeed.profile.metadata import Metadata
from hydroffice.soundspeed.profile.samples import Samples
from hydroffice.soundspeed.profile.more import More
from hydroffice.soundspeed.profile.dicts import Dicts
from hydroffice.soundspeed.profile.oceanography import Oceanography as Oc
from hydroffice.soundspeed.profile import geostrophic_48
from hydroffice.soundspeed.profile.svequations import SVEquations
from hydroffice.soundspeed.profile.raypath import Raypath


class Profile(object):
    """"A sound speed profile with 3 sections: metadata, data specific to the task, and additional data"""

    def __init__(self):
        self.meta = Metadata()  # metadata
        self.data = Samples()   # raw data
        self.proc = Samples()   # processed data
        self.sis = Samples()    # sis data
        self.more = More()      # additional fields

        self.woa09 = None
        self.woa13 = None
        self.rtofs = None

    def __repr__(self):
        msg = "<Profile>\n"
        msg += "%s" % self.meta
        msg += "%s" % self.data
        msg += "%s" % self.more
        return msg

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

    def reduce_up_down(self, ssp_direction):
        """Reduce the raw data samples based on the passed direction"""
        if self.data.num_samples == 0:  # skipping if there are no data
            return

        # identify max depth
        max_depth = self.data.depth[self.data_valid].max()  # max depth
        logger.debug("reduce up/down > max depth: %s" % max_depth)

        # loop through the sample using max depth as turning point
        max_depth_reached = False
        for i in range(self.data.num_samples):

            if (ssp_direction == Dicts.ssp_directions['up'] and not max_depth_reached) \
                    or (ssp_direction == Dicts.ssp_directions['down'] and max_depth_reached):
                self.data.flag[i] = Dicts.flags['direction']  # set invalid for direction

            if self.data.depth[i] == max_depth:
                max_depth_reached = True

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
        self.modify_proc_info('calc.salinity')

    def calc_data_depth(self):
        """Helper method to calculate depth from pressure (in dBar)"""
        # logger.debug("calculate depth from pressure")
        geostrophic_48.d_from_p(self)
#         if not self.meta.latitude:
#             latitude = 30.0
#             logger.warning("using default latitude: %s" % latitude)
#         else:
#             latitude = self.meta.latitude
# 
#         self.data.depth = self.data.pressure.copy()
#         for count in range(self.data.num_samples):
#             self.data.depth[count] = Oc.p2d(p=self.data.pressure[count], lat=latitude, prof=self)

        self.modify_proc_info('calc.depth')

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
        self.modify_proc_info("calc.speed")

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
        self.modify_proc_info("calc.speed")

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

    def insert_sis_speed(self, depth, speed, src=Dicts.sources['user']):
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
            # print('already present')
            self.sis.speed[i] = speed
            self.sis.source[i] = src
            self.sis.flag[i] = Dicts.flags['thin']
        else:
            # print('new depth')
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
            pm, pc = np.linalg.lstsq(a, pi)[0]
            self.sis.pressure = np.insert(self.sis.pressure, j, pm * depth + pc)
            # print(self.sis.pressure[0], self.sis.pressure.size)

            # interpolate for temp
            ti = np.array([self.sis.temp[valid][m_ids[0]], self.sis.temp[valid][m_ids[1]]])
            tm, tc = np.linalg.lstsq(a, ti)[0]
            self.sis.temp = np.insert(self.sis.temp, j, tm * depth + tc)
            # print(self.sis.temp[0], self.sis.temp.size)

            # interpolate for conductivity
            ci = np.array([self.sis.conductivity[valid][m_ids[0]], self.sis.conductivity[valid][m_ids[1]]])
            cm, cc = np.linalg.lstsq(a, ci)[0]
            self.sis.conductivity = np.insert(self.sis.conductivity, j, cm * depth + cc)
            # print(self.proc.conductivity[0], self.proc.conductivity.size)

            # interpolate for sal
            si = np.array([self.sis.sal[valid][m_ids[0]], self.sis.sal[valid][m_ids[1]]])
            sm, sc = np.linalg.lstsq(a, si)[0]
            self.sis.sal = np.insert(self.sis.sal, j, sm * depth + sc)
            # print(self.proc.sal[0], self.proc.sal.size)

            self.sis.depth = np.insert(self.sis.depth, j, depth)
            self.sis.speed = np.insert(self.sis.speed, j, speed)
            self.sis.source = np.insert(self.sis.source, j, src)
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
        extender.cur.proc.source[:] = ext_type

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

        return True

    def modify_proc_info(self, info):
        # if empty, add the info
        if not self.meta.proc_info:
            self.meta.proc_info = info
            return
        # check if it is already present
        tokens = self.meta.proc_info.split(';')
        if info not in tokens:
            self.meta.proc_info += ';%s' % info

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

        # - 1000 points for: EM2040, EM710, EM302 and EM122;
        # - 570 points for: EM3000, EM3002, EM1002, EM300, EM120
        # TODO: the resulting profile must be less than 30kB
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
        import matplotlib.pyplot as plt
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

    def fit_parab(self, Yin, NSpread=3, ymetric='depth', xattr='speed'):
        ''' NOTE! pass in a Y value and recieve an interpolated X, a bit backwards from normal naming 
        Yin is the ymetric (depth/pressure) to get a fitted approximate value at.  
        NSpread is how many points to use around the desired dept/pressure to use in polyfit 
        ymetric and xattr will default the the profile.ymetric and profile.attribute if left as None.
        Should add the ability to spline the data instead/in addition
        http://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html
        '''
        layers = self._no_dupes_goodflags()
        layers.sort(order=[ymetric]) 
        y = layers[ymetric]
        x = layers[xattr]
        index = np.searchsorted(y, Yin)
        I1 = index - NSpread if index - NSpread >= 0 else 0
        I2 = index + NSpread # too large of index doesn't matter in python
        y = y[I1:I2]
        x = x[I1:I2]
        return np.poly1d(np.polyfit(y, x, 2))(Yin)

    def DQA_surface(self, x, y, SN='Unknown'):
        ''' DQA Test using a given depth (pressure) and SV
        x is the xattr quantity (normally sound speed)
        y is the ymetric (normally depth or pressure)
        SN is the serial number of the instrument that measured the passed in x,y
        '''
        x_cast = self.fit_parab(y)
        DiffSV = np.absolute(x_cast - x)
        DQAResults= '\n' + time.ctime()
        DQAResults += "DAILY DQA - SURFACE SOUND SPEED COMPARISON\n\n" # Start building the Public result message
        if DiffSV > 2:
            DQAResults += " - TEST FAILED - Diff in sound speed > 2 m/sec\n"
        else:
            DQAResults += " - TEST PASSED - Diff in sound speed <= 2 m/sec\n"

        # Record DQA results
        DQAResults += '\n'
        DQAResults += "Surface sound speed instrument Serial Number: %s\n" % SN
        DQAResults += "Surface sound speed instrument depth (m): %.1f\n" % y
        DQAResults += "Surface sound speed Instrument reading (m/sec): %.2f\n" % x
        DQAResults += "Full sound speed profile: %s\n" % self.meta.original_path
        DQAResults += "   Instrument: sensor-%s, probe-%s, sn-%s\n" % (self.meta.sensor, self.meta.probe, self.meta.sn)
        DQAResults += "Profile sound speed at same depth (m/sec): %.1f\n" % x_cast
        DQAResults += "Difference in sound speed (m/sec): %.2f\n" % DiffSV
        return DQAResults, DiffSV

    def _no_dupes_goodflags(self, spacing = 0.1):
        '''Returns a new array with 'flag' values !=0 and the depths sorted and spaced by at least the spacing value
        '''
        #layers = copy.deepcopy(self.ssp) 
        dtype = [(b'depth', '<f8'), (b'speed', '<f8')]
        data = []
        for count in range(self.proc.num_samples):
            if self.proc.source[count] == Dicts.sources['raw'] and self.proc.flag[count] == Dicts.flags['valid']:
                data.append((self.proc.depth[count], self.proc.speed[count]))
        layers = np.array(data, dtype=dtype)
        #if 'flag' in self.dtype.names:
        #    layers=scipy.compress(layers['flag']>=0, d)
        layers.sort(order=['depth']) #must sort before taking the differences
        depths = layers['depth']
        #TODO: should we use QC( ) here or just the first sample that passes the spacing check?  Depends on if averaging the other data fields is ok.
        ilist = [0]
        for i in range(len(layers)):
            if depths[i]-depths[ilist[-1]] >= spacing:
                ilist.append(i)
        layers = layers.take(ilist)
        #delta_depth = scipy.hstack(([spacing*2],scipy.diff(layers['depth']))) #add a true value for the first difference that
        #layers = scipy.compress(delta_depth>=spacing, layers) #make sure duplicate depths not written
        return layers

    def compute_raypaths(self, draft, thetas_deg, traveltimes=None, res=.005, bProject=False):
        '''Performs a multiple raytraces.  
        Returns a RayPath object for each launch angle (thetas_deg).
        Will return points within the RayPath at each traveltime specified or 
          will compute traveltimes needed to reach the end of the profile at each launch angle
        Draft will be used as the starting point within the profile and be added to depths 
        '''
        if not draft or draft == 'Unknown':
            draft = 0.0
        else:
            draft = float(draft)
        layers = self._no_dupes_goodflags() #Get the data so we can sort and remove stuff
        layers['depth'] -= draft
        zero_ind = layers['depth'].searchsorted(0.0, side='right')
        if zero_ind > 0:
            layers['depth'][zero_ind - 1] = 0.0 #set the depth for the first layer to zero (so it doesn't get cut off).  
            #i.e. first layer goes from 0 to 5, draft ==2, that changes first layer to -2 to 3 which needs to be 0.0 to 3 so we don't cut off the sound velocity for the layer.
        layers = layers.compress(layers['depth'] >= 0)
        raypaths = []
        for launch in thetas_deg:
            params = SVEquations.GetSVPLayerParameters(np.deg2rad(launch), layers)
            if traveltimes is None:
                tt = np.arange(res, params[-2][-1], res) #make traveltimes to reach end of profile
            else:
                tt = np.array(traveltimes)
            rays = SVEquations.RayTraceUsingParameters(tt, layers, params, bProject=bProject)
            rays[:,0] += draft
            raypaths.append(Raypath(np.vstack((tt, rays.transpose())).transpose()))
        return raypaths

    def DQA_compare(self, prof, angle):
        DepMax = min(self.proc.depth.max(), prof.proc.depth.max())
        # Generate the travel time table for the two profiles.
        if DepMax < 30:  # Modify time increment for shallow casts 02/14/00
            TTInc = 0.002
        elif DepMax <= 400:
            TTInc = 0.002  # Travel time increment in seconds.
        elif DepMax <= 800:
            TTInc = 0.005
        else:
            TTInc = 0.01

        draft1 = 0.0 # TODO
        draft2 = 0.0 # TODO

        draft = max(draft1, draft2)
        ray1 = self.compute_raypaths(draft, [angle], res=TTInc)[0]
        ray2 = prof.compute_raypaths(draft, [angle], res=TTInc)[0]
        
        npts = min(len(ray1.data), len(ray2.data))
        depth1 = ray1.data[:npts, 1]
        depth2 = ray2.data[:npts, 1]
        delta_depth = depth2 - depth1
        larger_depths = np.maximum(depth1, depth2)
        perc_diff = np.absolute(delta_depth / larger_depths) * 100.0
        max_diff_index = perc_diff.argmax()
        max_diff = perc_diff[max_diff_index]
        max_diff_depth = larger_depths[max_diff_index]
        
        
        details  = "SUMMARY OF RESULTS - COMPARE 2 CASTS   " 
        details += "SSManager, Version     %s\n\n" % ssp_version
        details += "REFERENCE PROFILE:     %s\n" % self.meta.original_path
        details += "COMPARISON PROFILE:    %s\n\n" % prof.meta.original_path
        details += "REFERENCE INSTRUMENT:  sensor-%s, probe-%s, sn-%s\n" % (self.meta.sensor, self.meta.probe, self.meta.sn)
        details += "COMPARISON INSTRUMENT: sensor-%s, probe-%s, sn-%s\n\n" % (prof.meta.sensor, prof.meta.probe, prof.meta.sn)
        #Space(10) & "SYSTEM: %s\n" & UserSystem & CRLF
        details += "DRAFT                               = %.2fm\n" % draft
        details += "MAXIMUM COMMON DEPTH                = %.2f\n" % DepMax 
        details += "MAXIMUM DEPTH PERCENTAGE DIFFERENCE = %.2f%%\n" % max_diff
        details += "MAXIMUM PERCENTAGE DIFFERENCE AT    = %.2fm\n" % max_diff_depth
        details += "Max percentage diff line and last line of travel time table:\n"
        details += "Travel time, Avg Depth, Depth Diff, Pct Depth Diff, Avg Crosstrack, Crosstrack Diff, Pct Crosstrack Diff\n"
        for ni in (max_diff_index, npts-1):
            diff_data = (ray1.data[ni,0], 
                         np.average([ray1.data[ni,1], ray2.data[ni,1]]), np.absolute(delta_depth[ni]), perc_diff[ni], 
                         np.average([ray1.data[ni,2], ray2.data[ni,2]]), np.absolute(ray1.data[ni,2]-ray2.data[ni,2]), 100.0*np.absolute(ray1.data[ni,2]-ray2.data[ni,2])/max(ray1.data[ni,2],ray2.data[ni,2]))
            details += "    %5.2fs ,   %6.2fm,   %5.2fm  ,     %5.2f%%    ,      %6.2fm  ,      %5.2fm    ,         %5.2f%%\n" % diff_data
 
        DQAResults = '\n' + time.ctime() + '\n'
        if max_diff > 0.25:
            message  = "RESULTS INDICATE PROBLEM.\n\n"
            message += "The absolute value of percent depth difference exceeds the recommended amount (.25).\n\n"
            message += "If test was conducted to compare 2 casts for possible\n"
            message += "grouping into one representative cast, then\n"
            message += "the 2 casts should NOT be grouped.\n\n"
            message += "If test was run as part of a Data Quality Assurance for\n"
            message += "2 simultaneous casts, then one or both of the instruments\n"
            message += "used is functioning improperly.  Investigate further by\n"
            message += "performing simultaneous casts of each of the instruments\n"
            message += "with a third instrument.  Then rerun this procedure with\n"
            message += "the 2 new pairs of casts to determine which one of the\n"
            message += "instruments is not functioning properly.\n\n"
            message += "If the test was run to compare an XBT cast with\n"
            message += "the last CTD cast, then it is time to take a new CTD cast."
            DQAResults += "COMPARE 2 FILES\n  RESULTS: PERCENT DEPTH DIFFERENCE TOO LARGE\n"
        else:
            message  = "RESULTS OK.\n\n"
            message += "Percent depth difference is within recommended bounds."
            DQAResults += "COMPARE 2 FILES\n  RESULTS: PERCENT DEPTH DIFFERENCE OK\n"
        return DQAResults, message, details, (max_diff, max_diff_depth), prof.meta.utc_time.strftime('%Y%m%d%H%M%S')

