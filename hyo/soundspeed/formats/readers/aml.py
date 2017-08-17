from datetime import datetime as dt
import logging

logger = logging.getLogger(__name__)

from hyo.soundspeed.formats.readers.abstract import AbstractTextReader
from hyo.soundspeed.profile.dicts import Dicts
from hyo.soundspeed.base.callbacks.cli_callbacks import CliCallbacks


class Aml(AbstractTextReader):
    """AML SeaCast "CSV" reader -> SVP style"""

    def __init__(self):
        super(Aml, self).__init__()
        self.desc = "AML"
        self._ext.add('csv')

        self._date_token = "date"
        self._time_token = "time"
        self._lat_token = "latitude"
        self._long_token = "longitude"

        self._data_token = "[data]"
        self._depth_token = "Depth (m)"
        self._speed_token = "SV (m/s)"

    def read(self, data_path, settings, callbacks=CliCallbacks(), progress=None):
        logger.debug('*** %s ***: start' % self.driver)

        self.s = settings
        self.cb = callbacks

        self.init_data()  # create a new empty profile list
        self.ssp.append()  # append a new profile

        # initialize probe/sensor type
        self.ssp.cur.meta.sensor_type = Dicts.sensor_types['SVP']
        self.ssp.cur.meta.probe_type = Dicts.probe_types['AML']

        self._read(data_path=data_path)
        self._parse_header()
        self._parse_body()

        self.fix()
        self.finalize()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _parse_header(self):
        """
        """
        logger.debug('parsing header')

        date = None
        time = None

        for row_nr, line in enumerate(self.lines):

            tokens = line.split("=")

            if len(tokens) != 2:
                continue

            try:

                if tokens[0] == self._date_token:
                    date = dt.strptime(tokens[1].strip(), "%m/%d/%y")
                    continue

                if tokens[0] == self._time_token:
                    time = dt.strptime(tokens[1].strip(), "%H:%M:%S")
                    continue

                if tokens[0] == self._lat_token:
                    self.ssp.cur.meta.latitude = float(tokens[1])
                    continue

                if tokens[0] == self._long_token:
                    self.ssp.cur.meta.longitude = float(tokens[1])
                    continue

            except ValueError:
                logger.warning("invalid conversion parsing of line #%s: %s" % (row_nr, tokens[1]))
                continue
            except IndexError:
                logger.warning("invalid index parsing of line #%s: %s" % row_nr, tokens[1])
                continue

            continue

        if (date is not None) and (time is not None):
            self.ssp.cur.meta.utc_time = dt(year=date.year, month=date.month, day=date.day,
                                            hour=time.hour, minute=time.minute, second=time.second)
            logger.debug("retrieved timestamp: %s" % self.ssp.cur.meta.utc_time)

    def _parse_body(self):
        logger.debug('parsing body')

        count = 0
        read_samples = False
        has_depth_and_speed = False
        depth_idx = None
        speed_idx = None

        self.ssp.cur.init_data(len(self.lines))

        for row_nr, line in enumerate(self.lines):

            # logger.debug("%d : %s" % (row_nr, line))

            # first look for [data]
            if not read_samples:

                tokens = line.split()

                if len(tokens) == 0:
                    continue

                if tokens[0] == self._data_token:
                    read_samples = True
                    logger.debug("found data token: %s" % self._data_token)
                    continue

                continue

            # then look for depth and speed indices
            if not has_depth_and_speed:

                tokens = line.split(",")
                for idx, token in enumerate(tokens):

                    if token == self._depth_token:
                        depth_idx = idx
                        if speed_idx is not None:
                            has_depth_and_speed = True
                        logger.debug("found depth index: %s" % depth_idx)
                        continue

                    if token == self._speed_token:
                        speed_idx = idx
                        if depth_idx is not None:
                            has_depth_and_speed = True
                        logger.debug("found sound speed index: %s" % speed_idx)
                        continue

                    continue

                continue

            # finally the data
            tokens = line.split(",")
            if len(tokens) == 0:
                continue

            for idx, token in enumerate(tokens):

                try:

                    if idx == depth_idx:
                        self.ssp.cur.data.depth[count] = float(tokens[depth_idx])
                        if speed_idx < depth_idx:
                            count += 1
                        continue

                    if idx == speed_idx:
                        self.ssp.cur.data.speed[count] = float(tokens[speed_idx])
                        if speed_idx > depth_idx:
                            count += 1
                        continue

                except ValueError:
                    logger.warning("invalid conversion parsing of line #%s" % row_nr)
                    continue
                except IndexError:
                    logger.warning("invalid index parsing of line #%s" % row_nr)
                    continue

                continue

        if read_samples is False:
            raise RuntimeError("Issue in finding data token: %s" % self._data_token)

        if has_depth_and_speed is False:
            raise RuntimeError("Issue in identifying indices for depth and speed")

        logger.debug("retrieved %d samples" % count)
        self.ssp.cur.data_resize(count)
