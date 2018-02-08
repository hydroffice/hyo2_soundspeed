import datetime as dt
import logging

logger = logging.getLogger(__name__)

from hyo.soundspeed.formats.readers.abstract import AbstractTextReader
from hyo.soundspeed.profile.dicts import Dicts
from hyo.soundspeed.base.callbacks.cli_callbacks import CliCallbacks


class Iss(AbstractTextReader):
    """Leidos ISS reader"""

    def __init__(self):
        super(Iss, self).__init__()
        self.desc = "ISS"
        self._ext.add('v*')
        self._ext.add('d*')
        self._ext.add('svp')

        self.is_v = False
        self.is_d = False

    def read(self, data_path, settings, callbacks=CliCallbacks(), progress=None):
        logger.debug('*** %s ***: start' % self.driver)

        self.s = settings
        self.cb = callbacks

        self.init_data()  # create a new empty profile list
        self.ssp.append()  # append a new profile

        # initialize probe/sensor type
        self.ssp.cur.meta.probe_type = Dicts.probe_types['ISS']
        self.ssp.cur.meta.sensor_type = Dicts.sensor_types['SVP']

        self._read(data_path=data_path)
        self._parse_header()
        self._parse_body()

        self.fix()
        # self.ssp.cur.calc_data_depth()
        self.finalize()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _parse_header(self):
        """Parsing header: field header"""
        logger.debug('parsing header')

        # identify format
        mvp_token_header = "$MVS"
        first_line = self.lines[0].strip()
        mid_line = self.lines[int(len(self.lines) / 2)].strip()
        comma_tokens = mid_line.split(',')
        space_tokens = mid_line.split()

        if first_line[:len(mvp_token_header)] == mvp_token_header:
            logger.info("identified as .v* format")
            self._parse_header_v()
            self.is_v = True

        elif len(comma_tokens) > 1:
            logger.info("identified as .d* format")
            self._parse_header_d()
            self.is_d = True

        elif len(space_tokens) > 1:
            logger.info("identified as .svp format")
            self._parse_header_svp()

        else:
            raise RuntimeError('Unable to identify the input file format')

    def _parse_header_v(self):
        logger.info("reading > v header")

        token_header = "$MVS"
        header = self.lines[0]

        if header[:len(token_header)] != token_header:
            logger.warning("unknown Leidos v* format with header starting with: %s" % header[:len(token_header)])

        else:
            hdr_tokens = header.split(',')

            try:
                if len(hdr_tokens) == 9:
                    self.ssp.cur.meta.utc_time = dt.datetime(int(hdr_tokens[8]), int(hdr_tokens[7]), int(hdr_tokens[6]),
                                                             int(hdr_tokens[3]), int(hdr_tokens[4]), int(hdr_tokens[5]))
                    logger.info("date: %s" % self.ssp.cur.meta.utc_time)

            except ValueError:
                logger.error("unable to parse date and time from: %s" % header)

        if not self.ssp.cur.meta.original_path:
            self.ssp.cur.meta.original_path = self.fid.path

        # initialize data sample fields
        self.ssp.cur.init_data(len(self.lines))

    def _parse_header_d(self):
        logger.info("reading > d header")

        self.num_samples = len(self.lines)
        logger.info("max number of samples: %s" % self.num_samples)

        if not self.ssp.cur.meta.original_path:
            self.ssp.cur.meta.original_path = self.fid.path

        # initialize data sample fields
        self.ssp.cur.init_data(len(self.lines))

    def _parse_header_svp(self):
        logger.info("reading > svp header")

        token_header = "000"
        header = self.lines[0]

        if header[:len(token_header)] != token_header:
            logger.warning("unknown Leidos ISS svp format with header starting with: %s" % header[:len(token_header)])

        else:
            hdr_tokens = header.split()
            # logger.info("tokens: %s" % (hdr_tokens, ))

            try:
                if len(hdr_tokens) not in [11, 12]:
                    raise RuntimeError("invalid number of tokens (%d) in: %s" % (len(hdr_tokens), header))

                # cast date-time
                token_dt = hdr_tokens[5] + " " + hdr_tokens[4]
                self.ssp.cur.meta.utc_time = dt.datetime.strptime(token_dt, '%y%j %H%M%S')
                logger.info("date: %s" % self.ssp.cur.meta.utc_time)

            except ValueError:
                logger.error("unable to parse date and time from: %s" % header)

            try:
                if len(hdr_tokens) not in [11, 12]:
                    raise RuntimeError("invalid number of tokens (%d) in: %s" % (len(hdr_tokens), header))

                # latitude
                latitude = float(hdr_tokens[2])
                if latitude != 0.0:  # assumed empty fields?
                    self.ssp.cur.meta.latitude = latitude

                # longitude
                longitude = float(hdr_tokens[3])
                if longitude != 0.0:  # assumed empty fields?
                    self.ssp.cur.meta.longitude = longitude

                logger.info("(lat, lon): %s, %s" % (self.ssp.cur.meta.latitude, self.ssp.cur.meta.longitude))

            except ValueError:
                logger.error("unable to parse position from: %s" % header)

        if not self.ssp.cur.meta.original_path:
            self.ssp.cur.meta.original_path = self.fid.path

        # initialize data sample fields
        self.ssp.cur.init_data(len(self.lines))

    def _parse_body(self):
        """Parsing samples: depth, speed, temp, sal"""
        logger.debug('parsing body')

        if self.is_v:
            self._parse_body_v()

        elif self.is_d:
            self._parse_body_d()

        else:
            self._parse_body_svp()

    def _parse_body_v(self):
        logger.info("reading > v body")

        samples = 0
        for i, line in enumerate(self.lines):

            # Skip over the header
            if i == 0:
                continue

            # remove leading 0s
            line = line.strip()

            # In case an incomplete file comes through
            try:
                dpt, spd = line.split(',')

                if spd == 0.0:
                    logger.info("skipping 0-speed row at line %d: %s" % (i, line))
                    continue

                self.ssp.cur.data.depth[samples] = float(dpt)
                self.ssp.cur.data.speed[samples] = float(spd)
                logger.info("%d %7.1f %7.1f"
                            % (samples, self.ssp.cur.data.depth[samples], self.ssp.cur.data.speed[samples]))

            except ValueError:
                logger.error("skipping line %s" % i)
                continue

            samples += 1

        logger.info("good samples: %s" % samples)

        self.ssp.cur.data_resize(samples)

    def _parse_body_d(self):
        logger.info("reading > d body")

        initial_comments_reading = True

        samples = 0
        for i, line in enumerate(self.lines):

            # remove leading 0s
            line = line.strip()

            # Skip over the header
            if initial_comments_reading:

                if line[0] == '#':
                    logger.info("skipping initial comment at line #%d" % i)
                    continue

                else:
                    initial_comments_reading = False
                    logger.info("reading header")

                    hdr_tokens = line.split(' ')

                    try:
                        if len(hdr_tokens) == 8:

                            # cast date-time
                            token_dt = hdr_tokens[0] + " " + hdr_tokens[1]
                            self.ssp.cur.meta.utc_time = dt.datetime.strptime(token_dt, '%Y/%j %H:%M:%S.%f')
                            logger.info("date: %s" % self.ssp.cur.meta.utc_time)

                            # latitude
                            latitude = float(hdr_tokens[2]) + float(hdr_tokens[3]) / 60.0
                            if hdr_tokens[4] == 'S':
                                self.ssp.cur.meta.latitude = -latitude
                            else:
                                self.ssp.cur.meta.latitude = latitude

                            # longitude
                            longitude = float(hdr_tokens[5]) + float(hdr_tokens[6]) / 60.0
                            if hdr_tokens[7] == 'W':
                                self.ssp.cur.meta.longitude = -longitude
                            else:
                                self.ssp.cur.meta.longitude = longitude

                    except ValueError:
                        logger.error("unable to parse date, time, and position from: %s" % line)

                    continue

            # In case an incomplete file comes through
            try:
                dpt, spd = line.split(',')

                if spd == 0.0:
                    logger.info("skipping 0-speed row at line %d: %s" % (i, line))
                    continue

                self.ssp.cur.data.depth[samples] = float(dpt)
                self.ssp.cur.data.speed[samples] = float(spd)
                logger.info("%d %7.1f %7.1f"
                            % (samples, self.ssp.cur.data.depth[samples], self.ssp.cur.data.speed[samples]))

            except ValueError:
                logger.error("skipping line %s" % i)
                continue

            samples += 1

        logger.info("good samples: %s" % samples)

        self.ssp.cur.data_resize(samples)

    def _parse_body_svp(self):
        logger.info("reading > svp body")

        samples = 0
        for i, line in enumerate(self.lines):

            # Skip over the header
            if i == 0:
                continue

            # remove leading 0s
            line = line.strip()

            # In case an incomplete file comes through
            try:
                tokens = line.split()
                if len(tokens) not in [2, 4]:
                    logger.info("skipping row at line %d for invalid number of fields: %s" % (i, line))
                    continue

                dpt = float(tokens[0])
                spd = float(tokens[1])

                if spd == 0.0:
                    logger.info("skipping 0-speed row at line %d: %s" % (i, line))
                    continue

                self.ssp.cur.data.depth[samples] = dpt
                self.ssp.cur.data.speed[samples] = spd
                # logger.info("%d %7.1f %7.1f"
                #             % (samples, self.ssp.cur.data.depth[samples], self.ssp.cur.data.speed[samples]))

            except ValueError:
                logger.error("skipping line %s" % i)
                continue

            samples += 1

        logger.info("good samples: %s" % samples)

        self.ssp.cur.data_resize(samples)
