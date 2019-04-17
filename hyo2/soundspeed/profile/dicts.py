from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


class Dicts:

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
        ('SIS', 4),
        ('GoMOFS', 5),  # since DB v.3
        ('CBOFS', 6),  # since DB v.3
        ('DBOFS', 7),  # since DB v.3
        ('NYOFS', 8),  # since DB v.3
        ('SJROFS', 9),  # since DB v.3
        ('NGOFS', 10),  # since DB v.3
        ('TBOFS', 11),  # since DB v.3
        ('LEOFS', 12),  # since DB v.3
        ('LHOFS', 13),  # since DB v.3
        ('LMOFS', 14),  # since DB v.3
        ('LOOFS', 15),  # since DB v.3
        ('LSOFS', 16),  # since DB v.3
        ('CREOFS', 17),  # since DB v.3
        ('SFBOFS', 18),  # since DB v.3

        ('SVP', 101),
        ('Castaway', 102),
        ('Idronaut', 103),
        ('S2', 104),
        ('SBE', 105),
        ('XBT', 106),
        ('MVP', 107),
        ('Sonardyne', 108),
        ('ELAC', 109),
        ('ISS', 110),
        ('DigibarPro', 111),
        ('DigibarS', 112),
        ('ASVP', 113),
        ('CARIS', 114),
        ('Simrad', 115),
        ('OceanScience', 116),
        ('AML', 117),
        ('SeaAndSun', 118),

        ('Deep Blue', 200),
        ('T-10', 201),
        ('T-11 (Fine Structure)', 202),
        ('T-4', 203),
        ('T-5', 204),
        ('T-5/20', 205),
        ('T-7', 206),
        ('XSV-01', 207),
        ('XSV-02', 208),
        ('XCTD-1', 209),
        ('XCTD-2', 210),
        ('Fast Deep', 211),
        ('T-5_20', 212),

        ('MONITOR SVP 500', 300),
        ('MIDAS SVP 6000', 301),
        ('MIDAS SVX2 100', 302),
        ('MIDAS SVX2 500', 303),
        ('MIDAS SVX2 1000', 304),
        ('MIDAS SVX2 3000', 305),
        ('MIDAS SVX2 6000', 306),
        ('MiniSVP', 307),
        ('RapidSVT', 308),
        ('SWiFT', 309),

        ('Future', 999),

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

        ('Future', 999),

    ])

    ssp_directions = OrderedDict([

        ('up', 0),
        ('down', 1)

    ])

    flags = OrderedDict([

        ('valid', 0),
        ('direction', 1),
        ('user', 2),
        ('thin', 3),
        ('sis', 4),
        ('filtered', 5),  # since DB v.2
        ('smoothed', 6),  # since DB v.2

    ])

    sources = OrderedDict([

        ('raw', 0),
        ('user', 1),
        ('tss', 2),
        ('woa09_ext', 3),
        ('woa13_ext', 4),
        ('rtofs_ext', 5),
        ('ref_ext', 6),
        ('interp', 7),
        ('sis', 8),
        ('smoothing', 9),  # since DB v.2
        ('gomofs_ext', 10),  # since DB v.3
        ('woa18_ext', 11),  # since DB v.3

    ])

    booleans = OrderedDict([

        (True, 0),
        (False, 1)

    ])

    clients = OrderedDict([

        ("SIS", 0),
        ("HYPACK", 1),
        ("PDS2000", 2),
        ("QINSY", 3),
        ("KCTRL", 4),
    ])

    atlases = OrderedDict([

        ("WOA09", 0),
        ("WOA13", 1),
        ("RTOFS", 2),
        ("ref", 3),
        ("GoMOFS", 4),  # since DB v.3

    ])

    server_sources = OrderedDict([

        ("WOA09", 0),
        ("WOA13", 1),
        ("RTOFS", 2),
        ("GoMOFS", 3),  # since DB v.3

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

    kng_formats = OrderedDict([

        ('ASVP', 0),
        ('S00', 1),
        ('S01', 2),
        ('S10', 3),
        ('S11', 4),
        ('S02', 5),
        ('S12', 6),
        ('S22', 7),

    ])

    uom_symbols = OrderedDict([

        ('unknown', 'NA'),
        ('decibar', 'dbar'),
        ('meter', 'm'),

    ])

    proc_import_infos = OrderedDict([

        ('CALC_SAL', 'calc.salinity'),
        ('CALC_DEP', 'calc.depth'),
        ('CALC_SPD', 'calc.speed'),

    ])

    proc_user_infos = OrderedDict([

        ('EXT_WOA09', 'ext.from WOA09'),
        ('EXT_WOA13', 'ext.from WOA13'),
        ('EXT_RTOFS', 'ext.from RTOFS'),
        ('EXT_GoMOFS', 'ext.from GoMOFS'),  # since DB v.3
        ('EXT_REF', 'ext.from ref'),

        ('REP_SAL_WOA09', 'sal.from WOA09'),
        ('REP_SAL_WOA13', 'sal.from WOA13'),
        ('REP_SAL_RTOFS', 'sal.from RTOFS'),
        ('REP_SAL_GoMOFS', 'sal.from GoMOFS'),  # since DB v.3
        ('REP_SAL_REF', 'sal.from ref'),

        ('REP_TEMP_SAL_WOA09', 'temp./sal.from WOA09'),
        ('REP_TEMP_SAL_WOA13', 'temp./sal.from WOA13'),
        ('REP_TEMP_SAL_RTOFS', 'temp./sal.from RTOFS'),
        ('REP_TEMP_SAL_GoMOFS', 'temp./sal.from GoMOFS'),  # since DB v.3
        ('REP_TEMP_SAL_REF', 'temp./sal.from ref'),

        ('RECALC_SPD', 'recalc.speed'),
        ('ADD_TSS', 'added tss'),

        ('PLOTTED', 'plotted'),

    ])
