import datetime as dt
import logging

logger = logging.getLogger(__name__)

from hyo2.ssm2.lib.formats.readers.abstract import AbstractTextReader
from hyo2.ssm2.lib.profile.dicts import Dicts
from hyo2.ssm2.lib.base.callbacks.cli_callbacks import CliCallbacks


class TSK(AbstractTextReader):
    """Tsurumi-Seiki reader"""

    def __init__(self):
        super().__init__()
        self.desc = "TSK"
        self._ext.add('xbt')

    def read(self, data_path, settings, callbacks=CliCallbacks(), progress=None):
        logger.debug('*** %s ***: start' % self.driver)

        self.s = settings
        self.cb = callbacks

        self.init_data()  # create a new empty profile list
        self.ssp.append()  # append a new profile

        self._read(data_path=data_path)
        self._parse_header()
        self._parse_body()

        self.fix()
        self.finalize()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _parse_header(self):
        """Parsing header: field header, time, latitude, longitude """
        logger.debug('parsing header')

        header = self.lines[0].strip()
        self.samples_offset = 1
        logger.debug('header: %s' % header)

        tokens = header.split(",")
        nr_tokens = len(tokens)
        if nr_tokens != 14:
            raise RuntimeError("Unexpected header format: %d tokens" % nr_tokens)
        logger.debug('tokens: %d' % nr_tokens)

        for idx, token in enumerate(tokens):
            if idx == 2:  # Date
                try:
                    self.ssp.cur.meta.utc_time = dt.datetime.strptime(token, "%Y%m%d")
                except ValueError:
                    logger.warning("issue in casting the date format: %s" % token)

            elif idx == 3:  # Time
                if self.ssp.cur.meta.utc_time:
                    try:
                        hour, minute, second = int(token[:2]), int(token[2:4]), int(token[4:6])
                        self.ssp.cur.meta.utc_time += dt.timedelta(seconds=second, minutes=minute, hours=hour)
                    except ValueError:
                        logger.warning("issue in casting the time format: %s" % token)

        #     elif line[:len(self.tk_latitude)] == self.tk_latitude:  # latitude
        #         lat_str = line.split(':')[-1].lstrip().strip()
        #         if len(lat_str) > 0:
        #             try:
        #                 lat_deg = int(line.split()[-2])
        #                 lat_min = float(line.split()[-1][:-1])
        #                 lat_dir = line.split()[-1][-1]
        #                 self.ssp.cur.meta.latitude = lat_deg + lat_min / 60.
        #                 if lat_dir == 'S':
        #                     self.ssp.cur.meta.latitude *= -1
        #             except ValueError:
        #                 logger.warning("issue in casting the latitude at line #%s" % self.samples_offset)
        #
        #     elif line[:len(self.tk_longitude)] == self.tk_longitude:  # longitude
        #         lon_str = line.split(':')[-1].lstrip().strip()
        #         if len(lon_str) > 0:
        #             try:
        #                 lon_deg = int(line.split()[-2])
        #                 lon_min = float(line.split()[-1][:-1])
        #                 lon_dir = line.split()[-1][-1]
        #                 self.ssp.cur.meta.longitude = lon_deg + lon_min / 60.
        #                 if lon_dir == 'W':
        #                     self.ssp.cur.meta.longitude *= -1
        #             except ValueError:
        #                 logger.warning("issue in casting the longitude at line #%s" % self.samples_offset)
        #
        #     elif line[:len(self.tk_salinity)] == self.tk_salinity:
        #         sal_str = line.split()[-2]
        #         try:
        #             self.input_salinity = float(sal_str)
        #         except ValueError:
        #             logger.warning("issue in casting the salinity at line #%s" % self.samples_offset)
        #
        #     elif line[:len(self.tk_salinity_alpha)] == self.tk_salinity_alpha:
        #         sal_str = line.split()[-2]
        #         try:
        #             self.input_salinity = float(sal_str)
        #         except ValueError:
        #             logger.warning("issue in casting the salinity (alpha) at line #%s" % self.samples_offset)
        #
        #     elif line[:len(self.tk_probe)] == self.tk_probe:
        #         try:
        #             self.ssp.cur.meta.probe_type = Dicts.probe_types[line.split(':')[-1].lstrip().strip()]
        #             self.ssp.cur.meta.sensor_type = self.sensor_dict[self.ssp.cur.meta.probe_type]
        #
        #         except (IndexError, KeyError):
        #             self.ssp.cur.meta.probe_type = Dicts.probe_types['Unknown']
        #             self.ssp.cur.meta.sensor_type = Dicts.sensor_types['Unknown']
        #             logger.warning("reverted to unknown probe type at line #%s" % self.samples_offset)
        #
        #     elif line[:len(self.tk_serial)] == self.tk_serial:
        #         self.ssp.cur.meta.sn = line.split(':')[-1].strip()
        #
        #     elif line[:len(self.tk_field)] == self.tk_field:
        #         column = int(line[5]) - 1  # create the field index
        #         field_type = line.split()[2]
        #         self.field_index[field_type] = int(column)
        #         self.is_var_alpha = True
        #         # logger.info('is alpha')
        #
        #     self.samples_offset += 1

        if not self.ssp.cur.meta.original_path:
            self.ssp.cur.meta.original_path = self.fid.path

        # # initialize data sample fields
        self.ssp.cur.init_data(len(self.lines) - self.samples_offset)

    def _parse_body(self):
        logger.debug('parsing body')

        count = 0
        for idx, line in enumerate(self.lines[self.samples_offset:]):

            # skip empty lines
            if len(line.split()) == 0:
                continue

            # first required data fields
            try:
                good_data = self._body_default(line, count)

            except ValueError:
                logger.warning("invalid conversion parsing of line #%s: %s" % (self.samples_offset + idx, line))
                continue
            except IndexError:
                logger.warning("invalid index parsing of line #%s: %s" % (self.samples_offset + idx, line))
                continue

            if good_data:
                count += 1

        self.ssp.cur.data_resize(count)

    def _body_default(self, line, count):

        fields = line.split(",")

        if len(fields) < 3:
            logger.warning("too few fields for: %s" % line)
            return False

        if len(fields) > 3:
            logger.warning("too main fields for: %s" % line)
            return False

        for jdx, field in enumerate(fields):
            if jdx == 0:
                self.ssp.cur.data.depth[count] = float(field)
            elif jdx == 1:
                self.ssp.cur.data.temp[count] = float(field)
            else:
                continue

        return True
