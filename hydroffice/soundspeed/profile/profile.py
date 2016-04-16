from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
import logging
import os

logger = logging.getLogger(__name__)

from .metadata import Metadata
from .samples import Samples
from .more import More
from .dicts import Dicts
from .oceanography import Oceanography as Oc


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
        self.data.init_depth()
        self.data.init_speed()
        self.data.init_temp()
        self.data.init_sal()
        self.data.init_source()
        self.data.init_flag()

    def init_proc(self, num_samples):
        if num_samples == 0:
            return

        self.proc.num_samples = num_samples
        self.proc.init_depth()
        self.proc.init_speed()
        self.proc.init_temp()
        self.proc.init_sal()
        self.proc.init_source()
        self.proc.init_flag()

    def init_sis(self, num_samples):
        if num_samples == 0:
            return

        self.sis.num_samples = num_samples
        self.sis.init_depth()
        self.sis.init_speed()
        self.sis.init_temp()
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
        """Return indices of valid data"""
        return np.equal(self.proc.flag, Dicts.flags['valid'])

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
            if self.data.depth[i] == max_depth:
                max_depth_reached = True

            if (ssp_direction == Dicts.ssp_directions['up'] and not max_depth_reached) \
                    or (ssp_direction == Dicts.ssp_directions['down'] and max_depth_reached):
                self.data.flag[i] = Dicts.flags['direction']  # set invalid for direction

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

    def calc_depth(self):
        """Helper method to calculate depth from pressure (in dBar)"""
        # logger.debug("calculate depth from pressure")
        if not self.meta.latitude:
            latitude = 30.0
            logger.warning("using default latitude: %s" % latitude)
        else:
            latitude = self.meta.latitude

        for count in range(self.data.num_samples):
            self.data.depth[count] = Oc.p2d(p=self.data.depth[count], lat=latitude)

        self.modify_proc_info('calc.depth')

    def calc_speed(self):
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

    def insert_proc_speed(self, depth, speed):
        logger.debug("insert speed to proc data: d:%s, vs:%s" % (depth, speed))

        # we need to take care of valid samples and user-invalidated samples (to avoid to brake in case un-flagged)
        valid = self.proc.flag == Dicts.flags['valid']  # valid samples
        iv = np.indices(self.proc.flag.shape)[0][valid]  # indices of valid samples
        user_invalid = self.proc.flag == Dicts.flags['user']  # user-invalidate samples
        possible = np.logical_or(valid, user_invalid)  # possible samples
        ip = np.indices(self.proc.flag.shape)[0][possible]  # indices of possible samples

        # find depth index both in the valid and in the possible samples
        try:
            v_i = np.argwhere(self.proc.depth[valid] > depth)[0][0]  # the index in the valid array
            i = iv[v_i]  # the corresponding index of the masked index in the full array
        except IndexError:  # in case that there are not
            v_i = self.proc.depth[valid].size - 1
            i = iv[v_i]
        try:
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

            # interpolate for temp
            di = np.array([self.proc.depth[valid][m_ids[0]], self.proc.depth[valid][m_ids[1]]])
            a = np.array([[di[0], 1.], [di[1], 1.]])
            ti = np.array([self.proc.temp[valid][m_ids[0]], self.proc.temp[valid][m_ids[1]]])
            tm, tc = np.linalg.lstsq(a, ti)[0]
            self.proc.temp = np.insert(self.proc.temp, j, tm * depth + tc)
            # print(self.proc.temp[0], self.proc.temp.size)

            # interpolate for sal
            si = np.array([self.proc.sal[valid][m_ids[0]], self.proc.sal[valid][m_ids[1]]])
            sm, sc = np.linalg.lstsq(a, si)[0]
            self.proc.sal = np.insert(self.proc.sal, j, sm * depth + sc)
            # print(self.proc.sal[0], self.proc.sal.size)

            self.proc.depth = np.insert(self.proc.depth, j, depth)
            self.proc.speed = np.insert(self.proc.speed, j, speed)
            self.proc.source = np.insert(self.proc.source, j, Dicts.sources['user'])
            self.proc.flag = np.insert(self.proc.flag, j, Dicts.flags['valid'])

            self.proc.num_samples += 1

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
            v_i = np.argwhere(self.proc.depth[valid] > depth)[0][0]  # the index in the valid array
            i = iv[v_i]  # the corresponding index of the masked index in the full array
        except IndexError:  # in case that there are not
            v_i = self.proc.depth[valid].size - 1
            i = iv[v_i]
        try:
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
            if depth > self.proc.depth[valid][-1]:
                j += 1
            #     print('after end')
            # elif depth < self.proc.depth[valid][0]:
            #     print('before beginning: %s' % j)
            # else:
            #     print('in the middle')

            self.proc.depth = np.insert(self.proc.depth, j, depth)
            self.proc.speed = np.insert(self.proc.speed, j, speed)
            self.proc.temp = np.insert(self.proc.temp, j, temp)
            self.proc.sal = np.insert(self.proc.sal, j, sal)
            self.proc.source = np.insert(self.proc.source, j, Dicts.sources['user'])
            self.proc.flag = np.insert(self.proc.flag, j, Dicts.flags['valid'])

            self.proc.num_samples += 1

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

        vi = self.data.flag == Dicts.flags['valid']  # invalid samples (no direction-flagged)

        self.init_proc(np.sum(vi))
        self.proc.depth[:] = self.data.depth[vi]
        self.proc.speed[:] = self.data.speed[vi]
        self.proc.temp[:] = self.data.temp[vi]
        self.proc.sal[:] = self.data.sal[vi]
        self.proc.source[:] = self.data.source[vi]
        self.proc.flag[:] = self.data.flag[vi]

        self.update_proc_time()

    def update_proc_time(self):
        self.meta.update_proc_time()

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
