from datetime import datetime as dt
import math
import logging

logger = logging.getLogger(__name__)

from hyo2.soundspeed.formats.readers.abstract import AbstractTextReader
from hyo2.soundspeed.profile.dicts import Dicts
from hyo2.soundspeed.base.callbacks.cli_callbacks import CliCallbacks


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
        self._temp_token = "Temperature (C)"
        self._sal_token = "Salinity (PSU)"
        self._speed_token = "SV (m/s)"
        self._speed2_token = "Calc. SV (m/s)"

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
        lat = None
        lon = None

        for row_nr, line in enumerate(self.lines):

            tokens = line.split("=")

            if len(tokens) != 2:
                continue

            try:

                if (tokens[0].lower() == self._date_token) and (date is None):
                    try:
                        date = dt.strptime(tokens[1].strip(), "%m/%d/%y")
                        continue
                    except ValueError:
                        date = dt.strptime(tokens[1].strip(), "%Y-%m-%d")
                        continue

                if (tokens[0].lower() == self._time_token) and (time is None):
                    time = dt.strptime(tokens[1].strip(), "%H:%M:%S")
                    continue

                if (tokens[0].lower() == self._lat_token) and (lat is None):
                    lat = float(tokens[1])
                    continue

                if (tokens[0].lower() == self._long_token) and (lon is None):
                    lon = float(tokens[1])
                    continue

                if (lat is not None) and (lon is not None) and \
                        (self.ssp.cur.meta.latitude is None) and (self.ssp.cur.meta.longitude is None):
                    if math.isclose(lat, 0.0) and math.isclose(lon, 0.0):
                        lat = None
                        lon = None
                        logger.info("skipped (0.0, 0.0) location as invalid")
                    else:
                        self.ssp.cur.meta.latitude = lat
                        self.ssp.cur.meta.longitude = lon
                        logger.debug("retrieved location: (%s, %s)" %
                                     (self.ssp.cur.meta.longitude, self.ssp.cur.meta.latitude))

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

        if not self.ssp.cur.meta.original_path:
            self.ssp.cur.meta.original_path = self.fid.path

    def _parse_body(self):
        logger.debug('parsing body')

        count = 0
        read_samples = False
        has_depth_and_speed = False
        has_calc_speed = False
        has_temp = False
        has_sal = False
        depth_idx = None
        temp_idx = None
        sal_idx = None
        speed_idx = None

        self.ssp.cur.init_data(len(self.lines))

        data_row = 0

        for row_nr, line in enumerate(self.lines):

            # logger.debug("%d : %s" % (row_nr, line))

            # first look for [data]
            if not read_samples:

                tokens = line.split()

                if len(tokens) == 0:
                    continue

                if tokens[0].lower() == self._data_token:
                    read_samples = True
                    data_row = row_nr
                    logger.debug("found data token: %s at row: %d" % (self._data_token, data_row))
                    continue

                continue

            # then look for depth and speed indices
            if not has_depth_and_speed:

                tokens = line.split(",")
                for idx, token in enumerate(tokens):

                    if token == self._depth_token:
                        depth_idx = idx
                        logger.debug("found depth index: %s" % depth_idx)

                    elif token == self._temp_token:
                        temp_idx = idx
                        has_temp = True
                        logger.debug("found temp index: %s" % temp_idx)

                    elif token == self._sal_token:
                        sal_idx = idx
                        has_sal = True
                        logger.debug("found sal index: %s" % sal_idx)

                    elif token == self._speed_token:
                        speed_idx = idx
                        logger.debug("found sound speed index: %s" % speed_idx)

                    elif (token == self._speed2_token) and (speed_idx is None):
                        speed_idx = idx
                        has_calc_speed = True
                        logger.debug("found sound speed index [2]: %s" % speed_idx)

                    continue

                # set flag to true
                if (depth_idx is not None) and (speed_idx is not None):

                    has_depth_and_speed = True
                    if has_temp:

                        if not has_sal:

                            if has_calc_speed:  # special case: we treat is as XBT
                                self.ssp.cur.meta.sensor_type = Dicts.sensor_types['XBT']
                                logger.debug("detected sensor type: XBT")

                            else:
                                self.ssp.cur.meta.sensor_type = Dicts.sensor_types['SVPT']
                                logger.debug("detected sensor type: SVPT")

                        else:
                            self.ssp.cur.meta.sensor_type = Dicts.sensor_types['CTD']
                            logger.debug("detected sensor type: CTD")
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

                    elif idx == speed_idx:
                        self.ssp.cur.data.speed[count] = float(tokens[speed_idx])
                        if speed_idx > depth_idx:
                            count += 1
                        continue

                    elif idx == temp_idx:
                        self.ssp.cur.data.temp[count] = float(tokens[temp_idx])
                        continue

                    elif idx == sal_idx:
                        self.ssp.cur.data.sal[count] = float(tokens[sal_idx])
                        continue

                    else:  # not parsed value
                        continue

                except ValueError:
                    logger.warning("invalid conversion parsing of line #%s" % row_nr)
                    continue
                except IndexError:
                    logger.warning("invalid index parsing of line #%s" % row_nr)
                    continue

        if read_samples is False:
            raise RuntimeError("Issue in finding data token: %s" % self._data_token)

        if not has_depth_and_speed:
            # try to guess the sound speed token at index 2
            speed_idx = 2
            depth_idx = 3

            for row_nr, line in enumerate(self.lines):
                # finally the data
                tokens = line.split(",")
                if len(tokens) < 4:
                    continue

                try:

                    depth = float(tokens[depth_idx])
                    speed = float(tokens[speed_idx])

                    if depth < 0.01:
                        logger.warning("skipping sample at row #%d -> depth value: %s" % (row_nr, depth))
                        continue
                    if (speed < 1200.0) or (speed > 1700):
                        logger.warning("skipping sample at row #%d -> speed value: %s" % (row_nr, speed))
                        continue

                    self.ssp.cur.data.depth[count] = depth
                    self.ssp.cur.data.speed[count] = speed
                    count += 1

                except ValueError:
                    logger.warning("invalid conversion parsing of line #%s" % row_nr)
                    continue
                except IndexError:
                    logger.warning("invalid index parsing of line #%s" % row_nr)
                    continue

            # it should already be set as a SVP type
            self.ssp.cur.meta.sensor_type = Dicts.sensor_types['SVP']

        if count == 0:
            raise RuntimeError("unable to find depth and sound speed indices!")

        logger.debug("retrieved %d samples" % count)
        self.ssp.cur.data_resize(count)
