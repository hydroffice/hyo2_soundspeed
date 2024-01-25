import datetime
import logging
import re

import numpy

logger = logging.getLogger(__name__)

from hyo2.ssm2.lib.formats.readers.abstract import AbstractTextReader
from hyo2.ssm2.lib.profile.dicts import Dicts
from hyo2.ssm2.lib.base.callbacks.cli_callbacks import CliCallbacks
from hyo2.ssm2.lib.temp import coordinates

from hyo2.ssm2.lib.temp.regex_helpers import Profile, parseNumbers, getMetaFromTimeRE, getMetaFromCoord


class OceanScience(AbstractTextReader):
    """Ocean Science "ASC" reader -> CTD style
    """

    def __init__(self):
        super(OceanScience, self).__init__()
        self.desc = "OceanScience"
        self._ext.add('asc')
        self.raw_meta = None

    def read(self, data_path, settings, callbacks=CliCallbacks(), progress=None):
        logger.debug('*** %s ***: start' % self.driver)

        self.s = settings
        self.cb = callbacks

        self.init_data()  # create a new empty profile list

        self._read(data_path=data_path)
        self._parse_header()
        self._parse_body()

        # initialize probe/sensor type
        self.ssp.cur.meta.sensor_type = Dicts.sensor_types['CTD']
        self.ssp.cur.meta.probe_type = Dicts.probe_types['OceanScience']

        # fix issue with lat and lon not being well defined (after email exchange with Teledyn OceanScience)
        # logger.debug("initial lat: %s, lon: %s" % (self.ssp.cur.meta.latitude, self.ssp.cur.meta.longitude))
        self.ssp.cur.meta.latitude, self.ssp.cur.meta.longitude = self.cb.ask_location(
            default_lat=self.ssp.cur.meta.latitude, default_lon=self.ssp.cur.meta.longitude)
        if (self.ssp.cur.meta.latitude is None) or (self.ssp.cur.meta.longitude is None):
            self.ssp.clear()
            raise RuntimeError("missing geographic location required for database lookup")

        self.fix()
        self.finalize()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _parse_header(self):
        """ 
        For old data, columns were not listed in the header and had a fixed format.  
        Okeanos Explorer downloaded a new driver which changed the format. It now lists fields in the header, but since 
        we don't know if they are user configurable, they are loaded them dynamically (similar to the Seacat data).
        """
        meta = dict()

        s = "\n".join(self.lines)
        lat_meta = re.search(r'/*\*Lat (?P<lat>[\d/]+)', s)
        lon_meta = re.search(r'/*\*Lon (?P<lon>[\d/]+)', s)

        if (lat_meta is None) or (lon_meta is None):
            lat_meta = re.search(r'/*\*Lat (?P<lat>[\d.-]+)', s)
            lon_meta = re.search(r'/*\*Lon (?P<lon>[\d.-]+)', s)
            # logger.debug("lat: %s" % lat_meta.group('lat'))

        try:
            location = coordinates.Coordinate(lat_meta.group('lat'), lon_meta.group('lon'))
            meta.update(getMetaFromCoord(location))

        except Exception as e:
            logger.warning("unable to retrieve cast location: %s" % e)

        device_meta = re.search(r'/*\*DeviceType=\s*(?P<TYPE>\w+)', s)
        sn_meta = re.search(r'/*\*SerialNumber=\s*(?P<SN>\w+)', s)
        if sn_meta and device_meta:
            meta['SerialNum'] = sn_meta.group('SN')
            meta['Instrument'] = device_meta.group('TYPE') + ' (SN:' + sn_meta.group('SN') + ')'
        else:
            meta['Instrument'] = "Unknown"  # new format isn't necessarily filling out serial number

        m = re.search(r'''Cast\s+\d+\s+(?P<DATE>\d+\s+\w+\s+\d+\s+\d+:\d+:\d+)''', s, re.VERBOSE | re.DOTALL)
        if m:
            # grab the date from the cast metadata and convert to datetime object
            dt = datetime.datetime.strptime(m.group('DATE'), "%d %b %Y %H:%M:%S")
            # turn the datetime into a string
            tm = dt.strftime("%Y %m %d %H %M")
            # turn the string into a regex grouping/match object to pass into the standard date handler
            m = re.search("(?P<yr>\d+)\s+(?P<mon>\d+)\s+(?P<day>\d+)\s+(?P<hour>\d+)\s+(?P<minute>\d+)", tm)
            # update the profile metadata with the interpreted time data
            meta.update(getMetaFromTimeRE(m))

        meta['filename'] = self.fid.path

        self.raw_meta = meta

    def _parse_body(self):
        """
        OceanScience format from Nancy Foster example data.
        metadata lines start with an asterisk.

        *scan# C[S/m]  T[degC]  P[dbar]
        1  0.00000 20.948    0.031
        2  0.00000 20.952    0.031
        3  0.00000 20.958    0.031
        """

        meta = self.raw_meta

        profile_data = parseNumbers(self.lines,
                                    [('index', numpy.int32), ('conductivity', numpy.float32),
                                     ('temperature', numpy.float32), ('pressure', numpy.float32)],
                                    r"[\s,]+", pre=r'^\s*', post=r'\s*$')

        # clear profile (e.g., when first entering water)
        profile_data = numpy.compress(profile_data['temperature'] >= -10.0, profile_data)  # remove t < -10
        profile_data = numpy.compress(profile_data['conductivity'] >= 0.0, profile_data)  # remove C < 0
        profile_data = numpy.compress(profile_data['conductivity'] < 13.0, profile_data)  # remove C => 13
        profile_data = numpy.compress(profile_data['pressure'] >= 0.2, profile_data)  # remove p < 0.2

        p = Profile(profile_data, ymetric="depth", attribute="soundspeed", metadata=meta)
        self.ssp.append_profile(p.ConvertToSoundSpeedProfile())
