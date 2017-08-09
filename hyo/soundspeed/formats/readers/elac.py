import logging

logger = logging.getLogger(__name__)

from hyo.soundspeed.formats.readers.abstract import AbstractTextReader
from hyo.soundspeed.profile.dicts import Dicts
from hyo.soundspeed.base.callbacks.cli_callbacks import CliCallbacks


class Elac(AbstractTextReader):
    """ELAC reader"""

    def __init__(self):
        super(Elac, self).__init__()
        self.desc = "ELAC"
        self._ext.add('sva')

        # header tokens
        self.tk_start_data = '.profile'
        self.tk_start_header = '# depth'

        # body tokens
        self.tk_depth = 'depth'
        self.tk_sal = 'salin.'
        self.tk_temp = 'temp.'
        self.tk_speed = 'veloc.'

    def read(self, data_path, settings, callbacks=CliCallbacks(), progress=None):
        logger.debug('*** %s ***: start' % self.driver)

        self.s = settings
        self.cb = callbacks

        self.version = None

        self.init_data()  # create a new empty profile list
        self.ssp.append()  # append a new profile

        # initialize probe/sensor type
        self.ssp.cur.meta.sensor_type = Dicts.sensor_types['XBT']  # faking XBT
        self.ssp.cur.meta.probe_type = Dicts.probe_types['ELAC']

        self._read(data_path=data_path)
        self._parse_header()
        self._parse_body()

        self.fix()
        self.finalize()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _parse_header(self):
        logger.debug('parsing header')

        # control flags
        has_depth = False
        has_speed = False
        has_temp = False
        has_sal = False

        for line in self.lines:

            if not line:  # skip empty lines
                self.samples_offset += 1
                continue

            if line[:len(self.tk_start_data)] == self.tk_start_data:  # start data
                self.samples_offset += 1
                logger.debug("samples offset: %s" % self.samples_offset)
                break

            elif line[:len(self.tk_start_header)] == self.tk_start_header:  # start header
                col = 0  # field column
                for field in line.split():
                    if field == "#":  # skip the header token
                        continue
                    self.field_index[field] = col
                    if field == self.tk_depth:
                        has_depth = True
                        self.more_fields.insert(0, field)  # prepend depth to additional fields
                    elif field == self.tk_speed:
                        has_speed = True
                    elif field == self.tk_temp:
                        has_temp = True
                    elif field == self.tk_sal:
                        has_sal = True
                    else:
                        self.more_fields.append(field)
                    col += 1

            self.samples_offset += 1

        # sample fields checks
        if not has_depth:
            raise RuntimeError("Missing depth field: %s" % self.tk_depth)
        if not has_speed:
            raise RuntimeError("Missing sound speed field: %s" % self.tk_speed)
        if not has_temp:
            raise RuntimeError("Missing temperature field: %s" % self.tk_temp)
        if not has_sal:
            raise RuntimeError("Missing salinity field: %s" % self.tk_sal)
        if not self.ssp.cur.meta.original_path:
            self.ssp.cur.meta.original_path = self.fid.path

        # initialize data sample fields
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

                self.ssp.cur.data.temp[count] = float(data[2])
                self.ssp.cur.data.sal[count] = float(data[3])

            except ValueError:
                logger.warning("invalid conversion parsing of line #%s" % (self.samples_offset + count))
                continue
            except IndexError:
                logger.warning("invalid index parsing of line #%s" % (self.samples_offset + count))
                continue

            # additional data field
            try:
                for mf in self.more_fields:
                    self.ssp.cur.more.sa[mf][count] = float(data[self.field_index[mf]])
            except Exception as e:
                logger.debug("issue in reading additional data fields: %s -> skipping" % e)

            count += 1

        self.ssp.cur.data_resize(count)
