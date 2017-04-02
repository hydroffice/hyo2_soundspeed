import logging
import re

import numpy

logger = logging.getLogger(__name__)

from hydroffice.soundspeed.formats.readers.abstract import AbstractTextReader
from hydroffice.soundspeed.profile.dicts import Dicts
from hydroffice.soundspeed.base.callbacks.cli_callbacks import CliCallbacks
from hydroffice.soundspeed.temp import coordinates

from hydroffice.soundspeed.temp.regex_helpers import Profile, parseNumbers, getMetaFromTimeRE

# Identifier Input data    Data to be used                     Comment
ssp_fmts_doc = '''
        S00 D,c           D,c
        S01 D,c,T,S       D,c,a(D,T,S,L)                      Same as S12, but used immediately.
        S02 D,T,S         D,c(D,T,S,L),a(D,T,S,L)             Same as S22, but used immediately.
        S03 D,T,C         D,c(D,T,C,L),a(D,T,S,L)             Same as S32,but used immediately.
        S04 P,T,S         D(P,T,S,L),c(P,T,S,L),a(P,T,S,L)    Same as S42,but used immediately.
        S05 P,T,C         D(P,T,C,L),c(P,T,C,L),a(P,T,C,L)    Same as S52,but used immediately.
        S06 D,c,a         D,c,a                               Same as S11,but used immediately.
        S10 D,c           D,c
        S11 D,c,a         D,c,a
        S12 D,c,T,S       D,c,a(D,T,S,L)
        S13 D,c,a,f       D,c,a                               Frequency dependent
        S20 D,T,S         D,c(D,T,S,L)
        S21 D,T,S,a       D,c(D,T,S,L),a
        S22 D,T,S         D,c(D,T,S,L),a(D,T,S,L)
        S23 D,T,S,a,f     D,c(D,T,S,L),a                      Frequency dependent
        S30 D,T,C         D,c(D,T,S,L)
        S31 D,T,C,a       D,c(D,T,S,L),a
        S32 D,T,C         D,c(D,T,S,L),a(D,T,S,L)
        S33 D,T,C,a,f     D,c(D,T,S,L),a                      Frequency dependent
        S40 P,T,S         D(P,T,S,L),c(P,T,S,L)
        S41 P,T,S,a       D(P,T,S,L),c(P,T,S,L),a
        S42 P,T,S         D(P,T,S,L),c(P,T,S,L),a(P,T,S,L)
        S43 P,T,S,a,f     D(P,T,S,L),c(P,T,S,L),a             Frequency dependent
        S50 P,T,C         D(P,T,C,L),c(P,T,C,L)
        S51 P,T,C,a       D(P,T,C,L),c(P,T,C,L),a
        S52 P,T,C         D(P,T,C,L),c(P,T,C,L),a(P,T,C,L)
        S53 P,T,C,a,f     D(P,T,C,L),c(P,T,C,L),a             Frequency dependent
'''

SSP_Formats = {}
for fmt in ssp_fmts_doc.splitlines():
    m = re.match(r'\s*(?P<fmt>S\d\d)\s*(?P<fields>[\w,]*)\s', fmt)
    if m:
        SSP_Formats[m.group('fmt')] = [t.replace('a', 'absorption').replace('c', 'soundspeed').replace('f', 'frequency').replace('D', 'depth').replace('T', 'temperature').replace('S', 'salinity') for t in m.group('fields').split(',')]


class Simrad(AbstractTextReader):
    """Simrad reader -> CTD style
    """

    def __init__(self):
        super(Simrad, self).__init__()
        self.desc = "Simrad"
        self._ext.add('ssp')
        self._ext.add('s??')

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
        self.ssp.cur.meta.probe_type = Dicts.probe_types['Simrad']

        self.fix()
        self.finalize()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _parse_header(self):
        meta = {}
        m = re.search(r'''\$[A-Z][A-Z](?P<fmt>S\d\d),  #fmt is between 00 and 53
                      (?P<id>\d+),
                      (?P<nmeasure>\d+),
                      (?P<hour>\d\d)(?P<minute>\d\d)(?P<second>\d\d),
                      (?P<day>\d\d),
                      (?P<mon>\d\d),
                      (?P<yr>\d+),
                    ''', self.lines[0], re.VERBOSE)  # ignoring the optional fields of first line
        if m:
            meta.update(getMetaFromTimeRE(m))
            meta['DataSetID'] = m.group('id')
            meta['Format'] = "SSP " + m.group('fmt')
            meta['fmt'] = m.group('fmt')
            m = re.search(r'''(?P<lat>[\d.]+,[NS]),
                              (?P<lon>[\d.]+,[EW]),
                            ''', self.lines[1], re.VERBOSE)  # try the optional second line
            if not m:
                m = re.search(r'''(?P<lat>[\d.]+,[NS]),
                                  (?P<lon>[\d.]+,[EW]),
                                ''', self.lines[-1], re.VERBOSE)  # try at the end of file
            if m:
                location = coordinates.Coordinate(m.group('lat'), m.group('lon'))
                meta.update(Profile.getMetaFromCoord(location))
        meta['filename'] = self.fid._path
        self.rawmeta = meta

    def _parse_body(self):
        """
        ' Simrad SSP format (See EM Series 1002 Operator Manual for details):

        ' Start ID,                                      $              item 1
        ' Talker ID                                      AA
        ' Datagram ID,                                   S10,
        ' Data Set ID,                                   xxxxx,         item 2
        ' Number of measurements,                        xxxx,          item 3
        ' UTC time of data acquisition,                  hhmmss,        item 4
        ' Day of data acquisition,                       xx,            item 5
        ' Month of data acquisition,                     xx,            item 6
        ' Year of data acquisition,                      xxxx,          item 7
        ' First good depth in m                          x.x,
        ' Corresponding Sound Velocity in m/s,           x.x,
        ' Skip temp, sal, absorption coeff fields        ,,,
        ' End of line                                    CRLF
        ' Then, repeat good depth, sv,,,,CRLF until all NPTS are listed.

        From the Simrad Datagrams docs:
        Data Description Format Length Valid range Note
        Start identifier = $ Always 24h 1
        Talker identifier aa 2 Capital letters
        Datagram identifier Always Sxx, 4 S00to S53 1,2
        Data set identifier xxxxx, 6 00000 to 65535
        Number of measurements = N xxxx, 5 0001 to 9999 9
        UTC time of data acquisition hhmmss, 7 000000 to 235959 3
        Day of data acquisition xx, 3 00 to 31 3
        Month of data acquisition xx, 3 00 to 12 3
        Year of data acquisition xxxx, 5 0000 to 9999 3
        N entries of the next 5 fields  See note 4
         Depth in m fromwater level or
        Pressure in MPa
        x.x, 2  0 to 12000.00 0 to
        1.0000
        4
         Sound velocity in m/s x.x, 1  1400 to 1700.00
         Temperature in _C x.x, 1  5 to 45.00
         Salinity in parts per thousand or
        Conductivity in S/m
        x.x, 1  0 to 45.00 0 to 7.000
        Absorption coefficient in dB/km x.x 0 0 to 200.00 5
        Data set delimiter CRLF 2 0Dh 0Ah
        End of repeat cycle
        Latitude in degrees and minutes, plus
        optional decimal minutes
        llll.ll, Variable 5 0000 to 9000.0... 6
        Latitude  N/S a, 2 N or S 6
        Longitude in degrees and minutes, plus
        optional decimal minutes
        yyyyy.yy, Variable 6 00000 to 18000.0... 6
        Longitude  E/W a, 2 Eor W 6
        Atmospheric pressure in MPa x.x, 1 0 to 1.0000 6
        Frequency in Hz xxxxxx, Variable  7
        User given comments c c Variable  6
        Optional checksum *hh   8
        End of datagram delimiter = \CRLF 5Ch 0Dh 0Ah 3

        Note:
        1 The datagram identifier identifies what type of data is
        included. This is shown in the following table where D is
        depth, P is pressure, S is salinity, C is conductivity, c is
        soundspeed, 'a' is absorption coefficient, f is frequency and
        L is latitude. The notation c(T,S) indicates for example that
        the soundspeed is to be calculated from the temperature and
        salinity input data. When pressure is used, the atmospheric
        pressure must be given if the pressure is absolute, otherwise
        the pressure must be given re the sea level and the
        atmospheric pressure must be zero.

        See top of module ssp_fmts_doc for format specifiers.
        """
        metadata = self.rawmeta
        # read any of the above formats
        profile_data = parseNumbers(self.lines,
                                    [(n, numpy.float32) for n in SSP_Formats[metadata['fmt']]],
                                    r"\s*,\s*", pre=r'^\s*', post=r'[,.\s\d]*$', ftype='SSP')
        p = Profile(profile_data, ymetric="depth", attribute="soundspeed", metadata=metadata)

        self.ssp.append_profile(p.ConvertToSoundSpeedProfile())
