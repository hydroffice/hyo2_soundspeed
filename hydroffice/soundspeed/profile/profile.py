from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
import logging
import os

logger = logging.getLogger(__name__)

from .metadata import Metadata
from .samples import Samples
from .more import More
from .dicts import Dicts
from .oceanography import Oceanography

class Profile(object):
    """"A sound speed profile with 3 sections: metadata, data specific to the task, and additional data"""

    def __init__(self):
        self.meta = Metadata()  # metadata
        self.data = Samples()   # raw data
        self.proc = Samples()   # processed data
        self.sis = Samples()    # sis data
        self.more = More()      # additional fields

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
        return np.equal(self.proc.flag, Dicts.flags['direction'])

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

    def clone_data_to_proc(self):
        """Clone the raw data samples into proc samples"""
        logger.info("cloning raw data to proc samples")

        self.init_proc(self.data.num_samples)
        self.proc.depth[:] = self.data.depth
        self.proc.speed[:] = self.data.speed
        self.proc.temp[:] = self.data.temp
        self.proc.sal[:] = self.data.sal
        self.proc.source[:] = self.data.source
        self.proc.flag[:] = self.data.flag

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
