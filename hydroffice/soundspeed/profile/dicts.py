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
        ('RTOFS', 1),
        ('WOA09', 2),
        ('WOA13', 3),
        ('SVP', 4),
        ('Castaway', 5),
        ('Idronaut', 6),
        ('S2', 7),
        ('SBE', 8),
        ('XBT', 9),
        ('Deep Blue', 10),
        ('T-10', 11),
        ('T-11 (Fine Structure)', 12),
        ('T-4', 13),
        ('T-5', 14),
        ('T-5/20', 15),
        ('T-7', 16),
        ('XSV-01', 17),
        ('XSV-02', 18),
        ('XCTD-1', 19),
        ('XCTD-2', 20),
        ('MONITOR SVP 500', 21),
        ('MIDAS SVP 6000', 22),
        ('MIDAS SVX2 1000', 23),
        ('MIDAS SVX2 3000', 24),
        ('MiniSVP', 25),
        ('MVP', 26),
        ('Sonardyne', 27),
        ('Elac', 28),
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

    flags = OrderedDict([
        ('valid', 0),
        ('direction', 1),
        ('user', 2),
    ])

    sources = OrderedDict([
        ('raw', 0),
        ('user', 1),
        # 'Atlas': 2,
        # 'Interp': 3,
        # 'SurfaceSensor': 4,
        # 'Woa09Extend': 5,
        # 'Woa13Extend': 6,
        # 'RtofsExtend': 7,
        # 'UserRefExtend': 8,
    ])

    booleans = OrderedDict([
        (True, 0),
        (False, 1)
    ])

    clients = OrderedDict([
        ("SIS", 0),
        ("HYPACK", 1),
        ("PDS2000", 2),
        ("QINSY", 3)
    ])

    atlases = OrderedDict([
        ("WOA09", 0),
        ("WOA13", 1),
        ("RTOFS", 2)
    ])

    mvp_protocols = OrderedDict([
        ("NAVO_ISS60", 0),
        ("UNDEFINED", 1),
    ])

    mvp_formats = OrderedDict([
        ("S12", 0),
        ("CALC", 1),
        ("ASVP", 2)
    ])

    mvp_instruments = OrderedDict([
        ("AML_uSVP", 0),
        ("AML_uSVPT", 1),
        ("AML_Smart_SVP", 2),
        ("AML_uCTD", 3),
        ("AML_uCTD+", 4),
        ("Valeport_SVPT", 5),
        ("SBE_911+", 6),
        ("SBE_49", 7),
    ])

