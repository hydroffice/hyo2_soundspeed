from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
import logging

logger = logging.getLogger(__name__)


class More(object):
    def __init__(self):
        self.sa = None

    def init_struct_array(self, num_samples, fields):
        dt = [(fld.encode('ASCII'), b'f4') for fld in fields]
        self.sa = np.zeros((num_samples, len(fields)), dtype=dt)

    def __repr__(self):
        msg = "  <More>\n"
        if self.sa is not None:
            msg += "    <shape:(%s,%s)>\n" % self.sa.shape
            for fn in self.sa.dtype.names:
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
