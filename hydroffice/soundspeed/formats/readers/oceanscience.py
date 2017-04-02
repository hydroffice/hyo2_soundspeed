import datetime
import logging
import re

import numpy

logger = logging.getLogger(__name__)

from hydroffice.soundspeed.formats.readers.abstract import AbstractTextReader
from hydroffice.soundspeed.profile.dicts import Dicts
from hydroffice.soundspeed.base.callbacks.cli_callbacks import CliCallbacks
from hydroffice.soundspeed.temp import coordinates

from hydroffice.soundspeed.temp.regex_helpers import Profile, parseNumbers, getMetaFromTimeRE, getMetaFromCoord


class OceanScience(AbstractTextReader):
    """Ocean Science "ASC" reader -> CTD style
    """

    def __init__(self):
        super(OceanScience, self).__init__()
        self.desc = "OceanScience"
        self._ext.add('asc')

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

        self.fix()
        self.finalize()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _parse_header(self):
        '''For old data columns were not listed in the header and had a fixed format.  Okeanos Explorer downloaded a new
        driver which changed the format.  It now lists fields in the header and since I don't know if they are user configurable
        will load them dynamically similar to the Seacat data
        '''
        meta = {}
        s = "\n".join(self.lines)
        # lines = filedata.splitlines()[1:] #skip the header which is bad (is the download date or process date?)
        latm = re.search(r'/*\*Lat (?P<lat>[\d/]+)', s)
        lonm = re.search(r'/*\*Lon (?P<lon>[\d/]+)', s)

        try:
            location = coordinates.Coordinate(latm.group('lat'), lonm.group('lon'))
            location.lon = -location.lon  # force to West since it doesn't specify east/west in it's sample
            meta.update(getMetaFromCoord(location))
        except:
            pass  # newer format? -- or lat/lon is blank

        mDT = re.search(r'/*\*DeviceType=\s*(?P<TYPE>\w+)', s)
        mSN = re.search(r'/*\*SerialNumber=\s*(?P<SN>\w+)', s)
        if mSN and mDT:
            meta['SerialNum'] = mSN.group('SN')
            meta['Instrument'] = mDT.group('TYPE') + ' (SN:' + mSN.group('SN') + ')'
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
        meta['filename'] = self.fid._path
        self.rawmeta = meta

    def _parse_body(self):
        '''OceanScience format from Nancy Foster example data.
        metadata lines start with an asterisk.

        *scan# C[S/m]  T[degC]  P[dbar]
        1  0.00000 20.948    0.031
        2  0.00000 20.952    0.031
        3  0.00000 20.958    0.031
        '''

        meta = self.rawmeta

        profile_data = parseNumbers(self.lines,
                                    [('index', numpy.int32), ('conductivity', numpy.float32), ('temperature', numpy.float32), ('pressure', numpy.float32)],
                                    r"[\s,]+", pre=r'^\s*', post=r'\s*$')
        profile_data = numpy.compress(profile_data['temperature'] >= 0.0, profile_data)  # remove temperatures that make SV equation fail (t<0)
        profile_data = numpy.compress(profile_data['conductivity'] >= 0.0, profile_data)  # remove temperatures that make SV equation fail (t<0)
        # clear some of the surface noise when first entering water
        profile_data = numpy.compress(profile_data['pressure'] >= 0.2, profile_data)  # remove temperatures that make SV equation fail (t<0)
        # lat = cnv_data.metadata['location'].lat
        p = Profile(profile_data, ymetric="depth", attribute="soundspeed", metadata=meta)

        self.ssp.append_profile(p.ConvertToSoundSpeedProfile())
