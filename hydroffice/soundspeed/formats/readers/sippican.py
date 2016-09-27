from __future__ import absolute_import, division, print_function, unicode_literals

import datetime as dt
import logging

logger = logging.getLogger(__name__)


from .abstract import AbstractTextReader
from ...profile.dicts import Dicts
from ...base.callbacks import CliCallbacks


class Sippican(AbstractTextReader):
    """Sippican reader"""

    # A dictionary to resolve sensor type from probe type
    sensor_dict = {
        Dicts.probe_types["Deep Blue"]: Dicts.sensor_types["XBT"],
        Dicts.probe_types["T-10"]: Dicts.sensor_types["XBT"],
        Dicts.probe_types["T-11 (Fine Structure)"]: Dicts.sensor_types["XBT"],
        Dicts.probe_types["T-4"]: Dicts.sensor_types["XBT"],
        Dicts.probe_types["T-5"]: Dicts.sensor_types["XBT"],
        Dicts.probe_types["T-5/20"]: Dicts.sensor_types["XBT"],
        Dicts.probe_types["T-7"]: Dicts.sensor_types["XBT"],
        Dicts.probe_types["XSV-01"]: Dicts.sensor_types["XSV"],
        Dicts.probe_types["XSV-02"]: Dicts.sensor_types["XSV"],
        Dicts.probe_types["XCTD-1"]: Dicts.sensor_types["XCTD"],
        Dicts.probe_types["XCTD-2"]: Dicts.sensor_types["XCTD"]
    }

    def __init__(self):
        super(Sippican, self).__init__()
        self.desc = "Sippican"
        self._ext.add('edf')

        self.is_var_alpha = False
        self.input_salinity = None

        # header tokens
        self.tk_start = 'Depth (m)'
        self.tk_start_alpha = '// Data'  # There's a variant format with this marker
        self.tk_date = 'Date of Launch'
        self.tk_time = 'Time of Launch'
        self.tk_latitude = 'Latitude'
        self.tk_longitude = 'Longitude'
        self.tk_filename = 'Raw Data Filename'
        self.tk_salinity = '// Sound velocity derived with assumed salinity'
        self.tk_salinity_alpha = 'Salinity'
        self.tk_probe = 'Probe Type'
        self.tk_field = 'Field'

    def read(self, data_path, settings, callbacks=CliCallbacks()):
        logger.debug('*** %s ***: start' % self.driver)

        self.s = settings
        self.cb = callbacks

        self.is_var_alpha = False
        self.input_salinity = None

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

        for line in self.lines:

            if not line:  # skip empty lines
                self.samples_offset += 1
                continue

            if line[:len(self.tk_start)] == self.tk_start:  # initial data offset
                self.samples_offset += 1
                logger.debug("samples offset: %s" % self.samples_offset)
                break

            elif (line[:len(self.tk_start_alpha)] == self.tk_start_alpha) \
                    and (len(line) <= (len(self.tk_start_alpha) + 3)):  # variant alpha
                self.is_var_alpha = True
                self.samples_offset += 1
                logger.debug("samples offset(alpha): %s" % self.samples_offset)
                break

            elif line[:len(self.tk_date)] == self.tk_date:  # retrieve date
                date_str = line.split()[-1]
                try:
                    month, day, year = [int(i) for i in date_str.split('/')]
                    self.ssp.cur.meta.utc_time = dt.datetime(year=year, month=1, day=1)
                except ValueError:
                    logger.warning("issue in casting the date format at line #%s" % self.samples_offset)

            elif line[:len(self.tk_time)] == self.tk_time:  # retrieve time
                time_str = line.split()[-1]
                try:
                    hour, minute, second = [int(i) for i in time_str.split(':')]
                    self.ssp.cur.meta.utc_time += dt.timedelta(seconds=second, minutes=minute, hours=hour)
                except ValueError:
                    logger.warning("issue in casting the time format at line #%s" % self.samples_offset)

            elif line[:len(self.tk_latitude)] == self.tk_latitude:  # latitude
                lat_str = line.split(':')[-1].lstrip().strip()
                if len(lat_str) > 0:
                    try:
                        lat_deg = int(line.split()[-2])
                        lat_min = float(line.split()[-1][:-1])
                        lat_dir = line.split()[-1][-1]
                        self.ssp.cur.meta.latitude = lat_deg + lat_min / 60.
                        if lat_dir == 'S':
                            self.ssp.cur.meta.latitude *= -1
                    except ValueError:
                        logger.warning("issue in casting the latitude at line #%s" % self.samples_offset)

            elif line[:len(self.tk_longitude)] == self.tk_longitude:  # longitude
                lon_str = line.split(':')[-1].lstrip().strip()
                if len(lon_str) > 0:
                    try:
                        lon_deg = int(line.split()[-2])
                        lon_min = float(line.split()[-1][:-1])
                        lon_dir = line.split()[-1][-1]
                        self.ssp.cur.meta.longitude = lon_deg + lon_min / 60.
                        if lon_dir == 'W':
                            self.ssp.cur.meta.longitude *= -1
                    except ValueError:
                        logger.warning("issue in casting the longitude at line #%s" % self.samples_offset)

            elif line[:len(self.tk_salinity)] == self.tk_salinity:
                sal_str = line.split()[-2]
                try:
                    self.input_salinity = float(sal_str)
                except ValueError:
                        logger.warning("issue in casting the salinity at line #%s" % self.samples_offset)

            elif line[:len(self.tk_salinity_alpha)] == self.tk_salinity_alpha:
                sal_str = line.split()[-2]
                try:
                    self.input_salinity = float(sal_str)
                except ValueError:
                        logger.warning("issue in casting the salinity (alpha) at line #%s" % self.samples_offset)

            elif line[:len(self.tk_probe)] == self.tk_probe:
                try:
                    self.ssp.cur.meta.probe_type = Dicts.probe_types[line.split(':')[-1].lstrip().strip()]
                    self.ssp.cur.meta.sensor_type = self.sensor_dict[self.ssp.cur.meta.probe_type]

                except (IndexError, KeyError):
                    self.ssp.cur.meta.probe_type = Dicts.probe_types['Unknown']
                    self.ssp.cur.meta.sensor_type = Dicts.sensor_types['Unknown']
                    logger.warning("reverted to unknown probe type at line #%s" % self.samples_offset)

            elif line[:len(self.tk_field)] == self.tk_field:
                column = int(line[5]) - 1  # create the field index
                field_type = line.split()[2]
                self.field_index[field_type] = int(column)
                self.is_var_alpha = True
                # logger.info('is alpha')

            self.samples_offset += 1

        if not self.ssp.cur.meta.original_path:
            self.ssp.cur.meta.original_path = self.fid.path

        # initialize data sample fields
        self.ssp.cur.init_data(len(self.lines) - self.samples_offset)
        # initialize additional fields
        if self.is_var_alpha:
            pass
        else:
            if self.ssp.cur.meta.sensor_type == Dicts.sensor_types["XCTD"]:
                self.more_fields.append('Depth')
                self.more_fields.append('Conductivity')
                self.more_fields.append('Density')
                self.more_fields.append('Status')
        self.ssp.cur.init_more(self.more_fields)

    def _parse_body(self):
        logger.debug('parsing body [alpha: %s]' % self.is_var_alpha)

        if self.ssp.cur.meta.sensor_type == Dicts.sensor_types["XBT"]:
            # logger.info("%s" % self.input_salinity)
            # logger.info("%s" % self.ssp.data.sal)
            if self.input_salinity is not None:
                self.ssp.cur.data.sal[:] = self.input_salinity

        count = 0
        for line in self.lines[self.samples_offset:len(self.lines)]:

            # skip empty lines
            if len(line.split()) == 0:
                continue

            # first required data fields
            try:
                if self.is_var_alpha:
                    self._body_alpha(line, count)
                else:
                    self._body_default(line, count)

            except ValueError:
                logger.warning("invalid conversion parsing of line #%s" % (self.samples_offset + count))
                continue
            except IndexError:
                logger.warning("invalid index parsing of line #%s" % (self.samples_offset + count))
                continue

            count += 1

        self.ssp.cur.data_resize(count)

    def _body_default(self, line, count):

        field_count = 0
        fields = line.split()

        if self.ssp.cur.meta.sensor_type == Dicts.sensor_types["XBT"]:
            if len(fields) < 3:
                logger.warning("too few fields for line #%s" % (self.samples_offset + count))
                return

            # skip 0-speed value
            if float(fields[2]) == 0.0:
                logger.info("skipping 0-speed row")
                return

            for field in fields:
                if field_count == 0:
                    self.ssp.cur.data.depth[count] = field
                elif field_count == 1:
                    self.ssp.cur.data.temp[count] = field
                elif field_count == 2:
                    self.ssp.cur.data.speed[count] = field
                field_count += 1

            return

        elif self.ssp.cur.meta.sensor_type == Dicts.sensor_types["XSV"]:
            if len(fields) < 2:
                logger.warning("too few fields for line #%s" % (self.samples_offset + count))
                return

            # skip 0-speed value
            if float(fields[1]) == 0.0:
                logger.info("skipping 0-speed row")
                return

            for field in fields:
                if field_count == 0:
                    self.ssp.cur.data.depth[count] = field
                elif field_count == 1:
                    self.ssp.cur.data.speed[count] = field
                field_count += 1

            return

        elif self.ssp.cur.meta.sensor_type == Dicts.sensor_types["XCTD"]:
            if len(fields) < 6:
                logger.warning("too few fields for line #%s" % (self.samples_offset + count))
                return

            # skip 0-speed value
            if float(fields[4]) == 0.0:
                logger.info("skipping 0-speed row")
                return

            for field in fields:
                if field_count == 0:
                    self.ssp.cur.data.depth[count] = field
                    self.ssp.cur.more.sa['Depth'][count] = field
                elif field_count == 1:
                    self.ssp.cur.data.temp[count] = field
                elif field_count == 2:
                    self.ssp.cur.more.sa['Conductivity'][count] = field
                elif field_count == 3:
                    self.ssp.cur.data.sal[count] = field
                elif field_count == 4:
                    self.ssp.cur.data.speed[count] = field
                elif field_count == 5:
                    self.ssp.cur.more.sa['Density'][count] = field
                elif field_count == 6:
                    self.ssp.cur.more.sa['Status'][count] = field
                field_count += 1

            return

    def _body_alpha(self, line, count):

        fields = line.split()
        # print(self.field_index)

        if self.ssp.cur.meta.sensor_type == Dicts.sensor_types["XBT"]:
            # skip 0-speed value
            if float(fields[self.field_index["Sound"]]) == 0.0:
                logger.info("skipping 0-speed row")
                return

            self.ssp.cur.data.depth[count] = float(fields[self.field_index["Depth"]])
            self.ssp.cur.data.speed[count] = float(fields[self.field_index["Sound"]])
            self.ssp.cur.data.temp[count] = float(fields[self.field_index["Temperature"]])
            return

        elif self.ssp.cur.meta.sensor_type == Dicts.sensor_types["XSV"]:
            #  skip 0-speed value
            if float(fields[self.field_index["Sound"]]) == 0.0:
                logger.info("skipping 0-speed row")
                return

            self.ssp.cur.data.depth[count] = float(fields[self.field_index["Depth"]])
            self.ssp.cur.data.speed[count] = float(fields[self.field_index["Sound"]])
            return

        elif self.ssp.cur.meta.sensor_type == Dicts.sensor_types["XCTD"]:
            # skip 0-speed value
            if float(fields[self.field_index["Sound"]]) == 0.0:
                logger.info("skipping 0-speed row")
                return

            self.ssp.cur.data.depth[count] = float(fields[self.field_index["Depth"]])
            self.ssp.cur.data.speed[count] = float(fields[self.field_index["Sound"]])
            self.ssp.cur.data.temp[count] = float(fields[self.field_index["Temperature"]])
            self.ssp.cur.data.sal[count] = float(fields[self.field_index["Salinity"]])
            return
