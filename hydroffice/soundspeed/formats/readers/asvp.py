from datetime import datetime as dt
import logging

logger = logging.getLogger(__name__)

from hydroffice.soundspeed.formats.readers.abstract import AbstractTextReader
from hydroffice.soundspeed.profile.dicts import Dicts
from hydroffice.soundspeed.base.callbacks.cli_callbacks import CliCallbacks


class Asvp(AbstractTextReader):
    """Kongsberg asvp reader"""

    def __init__(self):
        super(Asvp, self).__init__()
        self.desc = "Konsgberg"
        self._ext.add('asvp')

        # header token
        self.tk_header = "("

    def read(self, data_path, settings, callbacks=CliCallbacks(), progress=None):
        logger.debug('*** %s ***: start' % self.driver)

        self.s = settings
        self.cb = callbacks

        self.init_data()  # create a new empty profile list
        self.ssp.append()  # append a new profile

        # initialize probe/sensor type
        self.ssp.cur.meta.sensor_type = Dicts.sensor_types['SVP']
        self.ssp.cur.meta.probe_type = Dicts.probe_types['ASVP']

        self._read(data_path=data_path)
        self._parse_header()
        self._parse_body()

        self.fix()
        self.finalize()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _parse_header(self):
        """Parsing header: time, latitude, longitude"""
        logger.debug('parsing header')

        has_header = False

        for line in self.lines:

            if not line:  # skip empty lines
                continue

            if line[0] == self.tk_header:  # header's token
                try:
                    for idx, field in enumerate(line.split()):
                        # print(idx, field)
                        if idx == 4:  # time
                            self.ssp.cur.meta.utc_time = dt.strptime(field, "%Y%m%d%H%M")
                        elif idx == 5:  # latitude
                            self.ssp.cur.meta.latitude = float(field)
                        elif idx == 6:  # longitude
                            self.ssp.cur.meta.longitude = float(field)
                    logger.debug("samples offset: %s" % self.samples_offset)

                except Exception as e:
                    logger.warning("unable to fully parse the header: %s" % e)
                has_header = True
                self.samples_offset += 1
                break

            self.samples_offset += 1

        if not has_header:
            raise RuntimeError("Missing header field: %s" % self.tk_header)
        if not self.ssp.cur.meta.original_path:
            self.ssp.cur.meta.original_path = self.fid.path

        # initialize data sample fields
        self.ssp.cur.init_data(len(self.lines) - self.samples_offset)

    def _parse_body(self):
        """Parsing samples: depth, speed"""
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

            except ValueError:
                logger.warning("invalid conversion parsing of line #%s" % (self.samples_offset + count))
                continue
            except IndexError:
                logger.warning("invalid index parsing of line #%s" % (self.samples_offset + count))
                continue

            count += 1

        self.ssp.cur.data_resize(count)
