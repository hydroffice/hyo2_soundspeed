from datetime import datetime as dt
import logging

logger = logging.getLogger(__name__)

from hydroffice.soundspeed.formats.readers.abstract import AbstractTextReader
from hydroffice.soundspeed.profile.dicts import Dicts
from hydroffice.soundspeed.base.callbacks.cli_callbacks import CliCallbacks


class Caris(AbstractTextReader):
    """CARIS svp reader"""

    def __init__(self):
        super(Caris, self).__init__()
        self.desc = "CARIS"
        self._ext.add('svp')

        self.common_path = None
        self.cur_row_idx = None
        self.max_nr_lines = None
        self.section_token = "Section"

    def read(self, data_path, settings, callbacks=CliCallbacks(), progress=None):
        logger.debug('*** %s ***: start' % self.driver)

        self.s = settings
        self.cb = callbacks

        self.init_data()  # create a new empty profile list

        self._read(data_path=data_path)
        self._parse_header()
        self._parse_body()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _parse_header(self):
        """Parsing top header: common path"""
        logger.debug('parsing header')

        self.max_nr_lines = len(self.lines)
        if self.max_nr_lines < 4:
            raise RuntimeError("The input file is only %d-line long" % len(self.lines))

        try:

            self.cur_row_idx = 0
            first_line = self.lines[self.cur_row_idx]
            first_token = "[SVP_VERSION_2]"
            if first_token not in first_line:
                raise RuntimeError("Unknown start of file: it should be %s, but it is %s" % (first_token, first_line))

            self.cur_row_idx += 1
            if self.lines[self.cur_row_idx][:len(self.section_token)] != self.section_token:
                self.common_path = self.lines[self.cur_row_idx].strip()
                self.cur_row_idx += 1
                logger.debug("common path: %s" % self.common_path)

        except Exception as e:
            raise RuntimeError("While parsing header, %s" % e)

    def _parse_body(self):
        """Parsing all the section"""
        logger.debug('parsing body')

        while self.cur_row_idx < self.max_nr_lines:

            # skip empty lines
            if len(self.lines[self.cur_row_idx]) == 0:
                continue

            # new profile
            if self.lines[self.cur_row_idx][:len(self.section_token)] == self.section_token:
                logger.info("new profile")
                self.ssp.append()  # append a new profile

                # initialize probe/sensor type
                self.ssp.cur.meta.sensor_type = Dicts.sensor_types['SVP']
                self.ssp.cur.meta.probe_type = Dicts.probe_types['CARIS']
                self.ssp.cur.meta.original_path = self.common_path

                self._parse_section_header()
                self._parse_section_body()

                continue

            # this point should be never reached.. unless troubles
            logger.debug("skipping line #%03d" % self.cur_row_idx)
            self.cur_row_idx += 1

        self.fix()
        self.finalize()

        logger.debug("read %d profiles" % self.ssp.nr_profiles)

    def _parse_section_header(self):
        """Parsing header: time, latitude, longitude"""
        logger.debug('parsing section #%d header' % self.ssp.nr_profiles)

        tokens = self.lines[self.cur_row_idx].strip().split()
        if len(tokens) < 5:
            logger.warning("skipping section header for invalid number of tokens: %s " % self.lines[self.cur_row_idx])
            return

        time_fields = "%s %s" % (tokens[1], tokens[2])
        try:
            self.ssp.cur.meta.utc_time = dt.strptime(time_fields, "%Y-%j %H:%M:%S")

        except Exception as e:
            logger.warning("unable to interpret the timestamp: %s" % time_fields)

        try:
            self.ssp.cur.meta.latitude = self._interpret_caris_coord(tokens[3])

        except Exception as e:
            logger.warning("unable to interpret the latitude: %s, %s" % (tokens[3], e))

        try:
            self.ssp.cur.meta.longitude = self._interpret_caris_coord(tokens[4])

        except Exception as e:
            logger.warning("unable to interpret the longitude: %s, %s" % (tokens[4], e))

        # initialize data sample fields
        self.ssp.cur.init_data(self.max_nr_lines - self.cur_row_idx)

        self.cur_row_idx += 1

    @classmethod
    def _interpret_caris_coord(cls, value):

        tokens = value.strip().split(':')
        if len(tokens) != 3:
            raise RuntimeError("invalid number of tokens for %s" % value)

        is_negative = False
        deg = float(tokens[0])
        if deg < 0:
            is_negative = True
            deg = abs(deg)
        min = float(tokens[1]) / 60.0
        sec = float(tokens[2]) / 3600.0

        coord = deg + min + sec
        if is_negative:
            coord = -coord

        return coord

    def _parse_section_body(self):
        """Parsing samples: depth, speed"""
        logger.debug('parsing section #%d body' % self.ssp.nr_profiles)

        # valid samples counter
        count = 0

        while self.cur_row_idx < self.max_nr_lines:

            # A new section is coming
            if self.lines[self.cur_row_idx][:len(self.section_token)] == self.section_token:
                return

            # skip empty lines
            if len(self.lines[self.cur_row_idx]) == 0:
                continue

            tokens = self.lines[self.cur_row_idx].strip().split()
            if len(tokens) != 2:
                logger.warning("skipping line for invalid number of tokens: %s " % self.lines[self.cur_row_idx])
                continue

            try:
                self.ssp.cur.data.depth[count] = float(tokens[0])
                self.ssp.cur.data.speed[count] = float(tokens[1])

            except ValueError:
                logger.warning("invalid conversion parsing of line #%03d" % (self.cur_row_idx, ))
                continue

            except IndexError:
                logger.warning("invalid index parsing of line #%03d" % (self.cur_row_idx, ))
                continue

            count += 1
            self.cur_row_idx += 1

        self.ssp.cur.data_resize(count)
