from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
import logging

logger = logging.getLogger(__name__)


class More(object):
    def __init__(self):
        self.sa = None

    def init_struct_array(self, num_samples, fields):
        """Initialize the stuctured array using the passed num_samples and the len of 'fields' list

        The 'fields' must have as first field the depth
        """
        if len(fields) == 0:
            return
        dt = [(fld.encode('ASCII'), b'f4') for fld in fields]
        self.sa = np.zeros((num_samples, len(fields)), dtype=dt)

    def __repr__(self):
        msg = "  <More>\n"
        if self.sa is not None:
            msg += "    <shape:(%s,%s)>\n" % self.sa.shape
            for fn in self.sa.dtype.names:
                if len(self.sa[fn]) > 2:
                    msg += "    <%s sz:%s min:%.3f max:%.3f>\n" \
                           % (fn, self.sa[fn].shape[0], self.sa[fn].min(), self.sa[fn].max())
        return msg

    def resize(self, count):
        """Resize the arrays (if present) to the new given number of elements"""
        if self.sa is None:
            return

        if self.sa.shape[0] == count:
            return

        self.sa.resize((count, self.sa.shape[1]))

    def debug_plot(self):
        """Create a debug plot with the data, optionally with the extra data if available"""
        if self.sa is None:
            return

        import matplotlib.pyplot as plt
        nr_fields = self.sa.shape[1] - 1
        nr_figures = (nr_fields // 4) + 1

        logger.info("plotting additional %s fields on %s figures" % (nr_fields, nr_figures))

        count = 0  # 0 is depth
        names = self.sa.dtype.names
        for i in range(nr_figures):  # figure

            if count >= nr_fields:
                break

            plt.figure(dpi=100)

            for j in range(6):  # subplots for figure

                if count >= nr_fields:
                    break

                if j == 0:
                    plt.subplot(231)
                elif j == 1:
                    plt.subplot(232)
                elif j == 2:
                    plt.subplot(233)
                elif j == 3:
                    plt.subplot(234)
                elif j == 4:
                    plt.subplot(235)
                elif j == 5:
                    plt.subplot(236)

                plt.title("%s" % names[count + 1])
                plt.plot(self.sa[names[count + 1]], self.sa[names[0]])
                plt.gca().invert_yaxis()
                plt.grid(True)
                count += 1

            plt.show(block=False)
