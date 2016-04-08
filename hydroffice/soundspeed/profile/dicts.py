from __future__ import absolute_import, division, print_function, unicode_literals

from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


class Dicts(object):

    @classmethod
    def first_match(cls, dct, val):
        # print(dct, val)
        values = [key for key, value in dct.items() if value == val]
        if len(values) != 0:
            return values[0]
        else:
            raise RuntimeError("unknown value %s in dict: %s" % (val, dct))

    probe_types = OrderedDict([
        ('Unknown', 0),
        ('Synthetic', 1),
        ('SVP', 2),
        ('Castaway', 3),
        ('Idronaut', 4),
        ('S2', 5),
        ('SBE', 6),
        ('XBT', 7),
        ('Deep Blue', 8),
        ('T-10', 9),
        ('T-11 (Fine Structure)', 10),
        ('T-4', 11),
        ('T-5', 12),
        ('T-5/20', 13),
        ('T-7', 14),
        ('XSV-01', 15),
        ('XSV-02', 16),
        ('XCTD-1', 17),
        ('XCTD-2', 18),
        ('MONITOR SVP 500', 19),
        ('MIDAS SVP 6000', 20),
        ('MIDAS SVX2 1000', 21),
        ('MIDAS SVX2 3000', 22),
        ('MiniSVP', 23),
        ('MVP', 24),
        ('Sonardyne', 25),
        ('Elac', 26),
    ])

    sensor_types = OrderedDict([
        ('Unknown', 0),
        ('Synthetic', 1),
        ('SVP', 2),
        ('CTD', 3),
        ('XBT', 4),
        ('XSV', 5),
        ('XCTD', 6),
        ('SVPT', 7),
        ('MVP', 8),
    ])

    ssp_directions = OrderedDict([
        ('up', 0),
        ('down', 1)
    ])

