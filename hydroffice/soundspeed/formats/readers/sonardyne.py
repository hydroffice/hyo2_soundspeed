from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime as dt
import logging

logger = logging.getLogger(__name__)


from .abstract import AbstractTextReader
from ...profile.dicts import Dicts
from ...base.callbacks import Callbacks


class Sonardyne(AbstractTextReader):
    """Sonardyne reader -> CTD style

    Info: http://www.sonardyne.com/products/positioning.html
    """

    def __init__(self):
        super(Sonardyne, self).__init__()
        self.ext.add('pro')

    def read(self, data_path, settings, callbacks=Callbacks()):
        logger.debug('*** %s ***: start' % self.driver)

        self.s = settings
        self.cb = callbacks

        self.init_data()  # create a new empty profile list
        self.ssp.append()  # append a new profile

        # initialize probe/sensor type
        self.ssp.cur.meta.sensor_type = Dicts.sensor_types['XBT']
        self.ssp.cur.meta.probe_type = Dicts.probe_types['Sonardyne']

        self._read(data_path=data_path)
        self._parse_header()
        self._parse_body()

        self.finalize()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _parse_header(self):
        """Parsing header: field header, time, latitude, longitude"""
        logger.debug('parsing header')

        try:
            self.samples_offset = 1
            date = dt.strptime(self.lines[self.samples_offset].strip(), "%d/%m/%Y")  # date
            self.samples_offset = 2
            time = dt.strptime(self.lines[self.samples_offset].strip(), "%H:%M:%S")  # time
            self.ssp.cur.meta.utc_time = dt(year=date.year, month=date.month, day=date.day,
                                            hour=time.hour, minute=time.minute, second=time.second)
        except ValueError as e:
            logger.info("unable to parse date and time from line #%s: %s" % (self.samples_offset, e))

        self.samples_offset = 5  # start of data samples

        if not self.ssp.cur.meta.original_path:
            self.ssp.cur.meta.original_path = self.fid.path

        # initialize data sample structures
        self.ssp.cur.init_data(len(self.lines) - self.samples_offset)
        # initialize additional fields
        self.ssp.cur.init_more(self.more_fields)

    def _parse_body(self):
        """Parsing samples: depth, speed, temp, sal"""
        logger.debug('parsing body')

        count = 0
        for line in self.lines[self.samples_offset:len(self.lines)]:

            # skip empty lines
            if len(line.split()) == 0:
                continue

            data = line.split()
            # first required data fields
            try:
                self.ssp.cur.data.depth[count] = float(data[0])
                self.ssp.cur.data.speed[count] = float(data[1])
                try:
                    self.ssp.cur.data.sal[count] = float(data[2])
                except Exception:
                    pass
                try:
                    self.ssp.cur.data.temp[count] = float(data[3])
                except Exception:
                    pass

            except ValueError:
                logger.warning("invalid conversion parsing of line #%s" % (self.samples_offset + count))
                continue
            except IndexError:
                logger.warning("invalid index parsing of line #%s" % (self.samples_offset + count))
                continue

            count += 1

        self.ssp.cur.data_resize(count)
