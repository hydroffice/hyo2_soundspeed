from __future__ import absolute_import, division, print_function, unicode_literals

import logging

logger = logging.getLogger(__name__)

from .metadata import Metadata
from .samples import Samples
from .more import More


class Profile(object):
    """"A sound speed profile with 3 sections: metadata, data specific to the task, and additional data"""

    def __init__(self):
        self.meta = Metadata()
        self.data = Samples()
        self.more = More()

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

    def init_more(self, more_fields):
        self.more.init_struct_array(self.data.num_samples, more_fields)

    def resize(self, count):
        self.data.resize(count)
        self.more.resize(count)

    def debug_plot(self, more=False):
        """Create a debug plot with the data, optionally with the extra data if available"""
        import matplotlib.pyplot as plt
        plt.figure(self.meta.original_path, dpi=100)

        plt.subplot(141)  # speed
        plt.plot(self.data.speed, self.data.depth)
        plt.gca().invert_yaxis()
        plt.grid(True)
        plt.title('speed')

        plt.subplot(142)  # temp
        plt.plot(self.data.temp, self.data.depth)
        plt.gca().invert_yaxis()
        plt.grid(True)
        plt.title('temp')

        plt.subplot(143)  # sal
        plt.plot(self.data.sal, self.data.depth)
        plt.gca().invert_yaxis()
        plt.grid(True)
        plt.title('sal')

        plt.subplot(144)  # meta
        fs = 9  # font size
        plt.title('meta')
        plt.axis('off')
        plt.text(0.1, 0.5, self.meta.debug_info(), fontsize=fs)
        plt.show(block=False)

        if more:
            self.more.debug_plot()
