from __future__ import absolute_import, division, print_function, unicode_literals

from copy import deepcopy
import numpy
from numpy import ndarray, array, empty
from numpy.ma import MaskedArray
import logging

logger = logging.getLogger(__name__)


class RayPath(object):
    """Represents the path of a SONAR wave through the water column. Basically
       this is just an n by 3 array (travel time, depth, across track).
    """

    def __init__(self, data):
        """data should be an n by 3 numpy.array (travel time, depth, across track)"""
        if type(data) == ndarray:
            pass
        elif type(data) != ndarray and type(data) == list:
            data = array(data)
        else:
            raise TypeError("Raypath data must be a list of some type (python list or numpy.ndarray")

        if data.shape[1] != 3:
            raise TypeError(
                "A ray path must be a list of 3-tuples... the shape of this array is '%s' when it should be '([len], 3)'" % str(
                    data.shape))

        self.data = data

    def getTimes(self):
        return self.data[:, 0]

    def getDepths(self):
        return self.data[:, 1]

    def getAcrossTracks(self):
        return self.data[:, 2]

    def __add__(self, other):
        """Adds (and subtracting) one raypath to/from another.
           At each mutual travel time, return z+-z (depth) and x+-x (across track)
           This is most useful for creating an uncertainty wedge
        """
        a = self.data
        b = other.data
        minlength = min(a.shape[0], b.shape[0])  # dimension 1 should _always_ be 3
        assert (a[:minlength, 0] == b[:minlength,
                                    0]).all()  # == returns a list of bools and .all() asks whether they are "all" True
        newtimes = a[:minlength, 0]
        newdepths = a[:minlength, 1]
        newxt = a[:minlength, 2]
        dz = a[:minlength, 1] + b[:minlength, 1]
        dx = a[:minlength, 2] + b[:minlength, 2]

        # Need to return t, z, h, dz, dh
        c = array([newtimes, newdepths, newxt, dz, dx]).transpose()
        return c

    def __sub__(self, other):
        return self.__add__(-other)

    def __neg__(self):
        r = deepcopy(self)
        r.data[:, 1:] *= -1
        return r

    def __len__(self):
        return int(self.data.shape[0])

    @staticmethod
    def mean_and_stdev(raypaths):
        minlen = min(map(len, raypaths))
        maxlen = max(map(len, raypaths))

        # newtimes  = empty(maxlen)
        meandepth = empty(maxlen)
        meanxt = empty(maxlen)

        depths = MaskedArray(empty((len(raypaths), maxlen)), mask=numpy.zeros((len(raypaths), maxlen), dtype=bool))
        xts = MaskedArray(empty((len(raypaths), maxlen)), mask=numpy.zeros((len(raypaths), maxlen), dtype=bool))
        times = MaskedArray(empty((len(raypaths), maxlen)), mask=numpy.zeros((len(raypaths), maxlen), dtype=bool))

        # Build up some numpy arrays
        for i, r in enumerate(raypaths):
            # Set the used values
            depths[i, :len(r)] = r.getDepths()
            xts[i, :len(r)] = r.getAcrossTracks()
            times[i, :len(r)] = r.getTimes()

            # For the longest row, save the times to be our return value
            if len(r) == maxlen: newtimes = r.getTimes()

            # Mask out the unused valuse
            mask = [[True for _ in range(maxlen - len(r))]]
            depths.mask[i, len(r):] = deepcopy(mask)
            xts.mask[i, len(r):] = deepcopy(mask)
            times.mask[i, len(r):] = deepcopy(mask)

        # Calculate the stats
        mean_depths = depths.mean(axis=0)  # depths.filled(0).sum(axis=0) / depths.count(axis=0)
        mean_xts = xts.mean(axis=0)  # xts.filled(0).sum(axis=0) / xts.count(axis=0)
        stdev_depths = [depths[:, i].compressed().std() for i in range(maxlen)]
        stdev_xts = [xts[:, i].compressed().std() for i in range(maxlen)]

        return array([newtimes, mean_depths, mean_xts, stdev_depths, stdev_xts]).transpose()
