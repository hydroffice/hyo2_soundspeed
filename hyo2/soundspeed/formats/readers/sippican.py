import datetime as dt
import logging

logger = logging.getLogger(__name__)

from hyo2.soundspeed.formats.readers.abstract import AbstractTextReader
from hyo2.soundspeed.profile.dicts import Dicts
from hyo2.soundspeed.base.callbacks.cli_callbacks import CliCallbacks


class Sippican(AbstractTextReader):
    """Sippican reader"""

    # A dictionary to resolve sensor type from probe type
    sensor_dict = {
        Dicts.probe_types["Deep Blue"]: Dicts.sensor_types["XBT"],
        Dicts.probe_types["T-10"]: Dicts.sensor_types["XBT"],
        Dicts.probe_types["T-11 (Fine Structure)"]: Dicts.sensor_types["XBT"],
        Dicts.probe_types["T-4"]: Dicts.sensor_types["XBT"],
        Dicts.probe_types["T-5"]: Dicts.sensor_types["XBT"],
        Dicts.probe_types["T5"]: Dicts.sensor_types["XBT"],
        Dicts.probe_types["T-5/20"]: Dicts.sensor_types["XBT"],
        Dicts.probe_types["T-5_20"]: Dicts.sensor_types["XBT"],
        Dicts.probe_types["T-7"]: Dicts.sensor_types["XBT"],
        Dicts.probe_types["XSV-01"]: Dicts.sensor_types["XSV"],
        Dicts.probe_types["XSV-02"]: Dicts.sensor_types["XSV"],
        Dicts.probe_types["XCTD-01"]: Dicts.sensor_types["XCTD"],
        Dicts.probe_types["XCTD-1"]: Dicts.sensor_types["XCTD"],
        Dicts.probe_types["XCTD-2"]: Dicts.sensor_types["XCTD"],
        Dicts.probe_types["Fast Deep"]: Dicts.sensor_types["XBT"],
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
        self.tk_serial = 'Serial'

    def read(self, data_path, settings, callbacks=CliCallbacks(), progress=None):
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
                    self.ssp.cur.meta.utc_time = dt.datetime(year=year, month=month, day=day)
                except ValueError:
                    logger.warning("issue in casting the date format at line #%s" % self.samples_offset)

            elif line[:len(self.tk_time)] == self.tk_time:  # retrieve time
                time_str = line.split()[-1]
                if self.ssp.cur.meta.utc_time:
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

            elif line[:len(self.tk_serial)] == self.tk_serial:
                self.ssp.cur.meta.sn = line.split(':')[-1].lstrip().strip()
                    
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
        good_data = None
        for line in self.lines[self.samples_offset:len(self.lines)]:

            # skip empty lines
            if len(line.split()) == 0:
                continue

            # first required data fields
            try:
                if self.is_var_alpha:
                    good_data = self._body_alpha(line, count)
                else:
                    good_data = self._body_default(line, count)

            except ValueError:
                logger.warning("invalid conversion parsing of line #%s" % (self.samples_offset + count))
                continue
            except IndexError:
                logger.warning("invalid index parsing of line #%s" % (self.samples_offset + count))
                continue

            if good_data:
                count += 1

        self.ssp.cur.data_resize(count)

    def _body_default(self, line, count):

        field_count = 0
        fields = line.split()

        if self.ssp.cur.meta.sensor_type == Dicts.sensor_types["XBT"]:
            if len(fields) < 3:
                logger.warning("too few fields for line #%s" % (self.samples_offset + count))
                return False

            # skip 0-speed value
            if float(fields[2]) < 1000.0:
                logger.info("skipping low-speed row")
                return False

            for field in fields:
                if field_count == 0:
                    self.ssp.cur.data.depth[count] = field
                elif field_count == 1:
                    self.ssp.cur.data.temp[count] = field
                elif field_count == 2:
                    self.ssp.cur.data.speed[count] = field
                field_count += 1

            return True

        elif self.ssp.cur.meta.sensor_type == Dicts.sensor_types["XSV"]:
            if len(fields) < 2:
                logger.warning("too few fields for line #%s" % (self.samples_offset + count))
                return False

            # skip 0-speed value
            if float(fields[1]) < 1000.0:
                logger.info("skipping low-speed row")
                return False

            for field in fields:
                if field_count == 0:
                    self.ssp.cur.data.depth[count] = field
                elif field_count == 1:
                    self.ssp.cur.data.speed[count] = field
                field_count += 1

            return True

        elif self.ssp.cur.meta.sensor_type == Dicts.sensor_types["XCTD"]:
            if len(fields) < 6:
                logger.warning("too few fields for line #%s" % (self.samples_offset + count))
                return False

            # skip 0-speed value
            if float(fields[4]) < 1000.0:
                logger.info("skipping low-speed row")
                return False

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

            return True

        else:
            logger.warning("unknown/unsupported type: %s" % self.ssp.cur.meta.sensor_type)
            return False

    def _body_alpha(self, line, count):

        fields = line.split()
        # print(self.field_index)

        if self.ssp.cur.meta.sensor_type == Dicts.sensor_types["XBT"]:
            # skip low-speed value
            if float(fields[self.field_index["Sound"]]) < 1000.0:
                logger.info("skipping low-speed #%d row: %f" % (count, float(fields[self.field_index["Sound"]])))
                return False

            self.ssp.cur.data.depth[count] = float(fields[self.field_index["Depth"]])
            self.ssp.cur.data.speed[count] = float(fields[self.field_index["Sound"]])
            self.ssp.cur.data.temp[count] = float(fields[self.field_index["Temperature"]])
            return True

        elif self.ssp.cur.meta.sensor_type == Dicts.sensor_types["XSV"]:
            #  skip low-speed value
            if float(fields[self.field_index["Sound"]]) < 1000.0:
                logger.info("skipping low-speed #%d row: %f" % (count, float(fields[self.field_index["Sound"]])))
                return False

            self.ssp.cur.data.depth[count] = float(fields[self.field_index["Depth"]])
            self.ssp.cur.data.speed[count] = float(fields[self.field_index["Sound"]])
            return True

        elif self.ssp.cur.meta.sensor_type == Dicts.sensor_types["XCTD"]:
            # skip low-speed value
            if float(fields[self.field_index["Sound"]]) < 1000.0:
                logger.info("skipping low-speed #%d row: %f" % (count, float(fields[self.field_index["Sound"]])))
                return False

            self.ssp.cur.data.depth[count] = float(fields[self.field_index["Depth"]])
            self.ssp.cur.data.speed[count] = float(fields[self.field_index["Sound"]])
            self.ssp.cur.data.temp[count] = float(fields[self.field_index["Temperature"]])
            self.ssp.cur.data.sal[count] = float(fields[self.field_index["Salinity"]])
            return True

        else:
            logger.warning("unknown/unsupported type: %s" % self.ssp.cur.meta.sensor_type)
            return False
