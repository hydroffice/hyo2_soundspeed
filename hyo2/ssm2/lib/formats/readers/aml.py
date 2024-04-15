import traceback
from datetime import datetime as dt
import logging
import math
import os
from typing import Optional, TYPE_CHECKING

from hyo2.ssm2.lib.formats.readers.abstract import AbstractTextReader
from hyo2.ssm2.lib.profile.dicts import Dicts
from hyo2.ssm2.lib.base.callbacks.cli_callbacks import CliCallbacks

if TYPE_CHECKING:
    from hyo2.abc2.lib.progress.abstract_progress import AbstractProgress
    from hyo2.ssm2.lib.base.callbacks.abstract_callbacks import AbstractCallbacks
    from hyo2.ssm2.lib.base.setup import Setup

logger = logging.getLogger(__name__)


class Aml(AbstractTextReader):
    """AML SeaCast "CSV" reader -> SVP style"""

    def __init__(self):
        super().__init__()
        self.desc = "AML"
        self._ext.add('csv')
        self._ext.add('aml')

        class CsvTokens:
            def __init__(self):
                self.date = "date"
                self.time = "time"
                self.lat = "latitude"
                self.long = "longitude"

                self.data = "[data]"
                self.depth = "Depth (m)"
                self.pressure = "Pressure (dBar)"
                self.temp = "Temperature (C)"
                self.sal = "Salinity (PSU)"
                self.speed = "SV (m/s)"
                self.speed2 = "Calc. SV (m/s)"

        self._csv = CsvTokens()

        class AmlTokens:
            def __init__(self):
                self.header = "[header]"
                self.date = "date"
                self.time = "time"
                self.lat = "gpslatitude"
                self.long = "gpslongitude"
                self.lat2 = "latitude"
                self.long2 = "longitude"
                self.serial = "serialnumber"
                self.serial2 = "sn"

                self.metadata = "[measurementmetadata]"
                self.columns = "columns"
                self.units = "units"
                self.pressure = "pressure"
                self.depth = "depth"
                self.temp = "temp"
                self.temp2 = "tempct"
                self.temp3 = "tempsv"
                self.cond = "cond"
                self.cond_multi = 1.0
                self.sal = "salinity"
                self.speed = "sv"
                self.speed2 = "calcsv"

                self.data = "[measurementdata]"

        self._aml = AmlTokens()

        self._path_ext = None  # type: Optional[str]
        self.field_units = dict()

    def read(self, data_path: str, settings: 'Setup', callbacks: 'AbstractCallbacks' = CliCallbacks(),
             progress: Optional['AbstractProgress'] = None):
        logger.debug('*** %s ***: start' % self.driver)

        self.s = settings
        self.cb = callbacks

        self.init_data()  # create a new empty profile list
        self.ssp.append()  # append a new profile

        # initialize probe/sensor type
        self.ssp.cur.meta.probe_type = Dicts.probe_types['AML']

        self._read(data_path=data_path)
        self._path_ext = os.path.splitext(self.fid.path)[-1]
        self._parse_header()
        self._parse_body()

        self.fix()
        self.finalize()

        logger.debug('*** %s ***: done' % self.driver)
        return True

    def _parse_header(self):
        if self._path_ext in [".csv"]:
            self._csv_header()
        elif self._path_ext in [".aml"]:
            self._aml_header()
        else:
            raise RuntimeError('Unsupported extension> %s' % self._path_ext)

    def _csv_header(self):
        logger.debug('parsing CSV header')

        date = None
        time = None
        lat = None
        lon = None

        for row_nr, line in enumerate(self.lines):

            tokens = line.split("=")

            if len(tokens) != 2:
                continue

            try:

                if (tokens[0].lower() == self._csv.date) and (date is None):
                    try:
                        date = dt.strptime(tokens[1].strip(), "%m/%d/%y")
                        continue
                    except ValueError:
                        date = dt.strptime(tokens[1].strip(), "%Y-%m-%d")
                        continue

                if (tokens[0].lower() == self._csv.time) and (time is None):
                    try:
                        time = dt.strptime(tokens[1].strip(), "%H:%M:%S")
                        continue
                    except ValueError:
                        time = dt.strptime(tokens[1].strip(), "%H:%M:%S.%f")
                        continue

                if tokens[0].lower() == self._csv.lat:
                    try:
                        lat = float(tokens[1])
                    except ValueError:  # it may be no-lock
                        lat = None
                    continue

                if tokens[0].lower() == self._csv.long:
                    try:
                        lon = float(tokens[1])
                    except ValueError:  # it may be no-lock
                        lon = None
                    continue
                
                if tokens[0].lower() == self._aml.serial2:
                    if tokens[1]:
                        self.ssp.cur.meta.sn = tokens[1].strip()
                    continue

            except ValueError:
                logger.warning("invalid conversion parsing of line #%s: %s" % (row_nr, tokens[1]))
                continue
            except IndexError:
                logger.warning("invalid index parsing of line #%s: %s" % row_nr, tokens[1])
                continue

            continue

        if (lat is not None) and (lon is not None) and \
                (self.ssp.cur.meta.latitude is None) and (self.ssp.cur.meta.longitude is None):
            if math.isclose(lat, 0.0) and math.isclose(lon, 0.0):
                logger.info("skipped (0.0, 0.0) location as invalid")
            else:
                self.ssp.cur.meta.latitude = lat
                self.ssp.cur.meta.longitude = lon
                logger.debug("retrieved location: (%s, %s)" % (self.ssp.cur.meta.longitude, self.ssp.cur.meta.latitude))

        if (date is not None) and (time is not None):
            self.ssp.cur.meta.utc_time = dt(year=date.year, month=date.month, day=date.day,
                                            hour=time.hour, minute=time.minute, second=time.second)
            logger.debug("retrieved timestamp: %s" % self.ssp.cur.meta.utc_time)

        if not self.ssp.cur.meta.original_path:
            self.ssp.cur.meta.original_path = self.fid.path

        self.ssp.cur.meta.sensor_type = Dicts.sensor_types['SVP']

    def _aml_header(self):
        logger.debug('parsing AML header')

        read_header = False
        read_metadata = False
        read_data = False

        date = None
        time = None
        lat = None
        lon = None
        lat2 = None
        lon2 = None

        for row_nr, line in enumerate(self.lines):

            try:
                if line.lower() == self._aml.header:
                    read_header = True
                    continue

                if line.lower() == self._aml.metadata:
                    read_header = False
                    read_metadata = True
                    continue

                if line.lower() == self._aml.data:
                    read_metadata = False
                    read_data = True
                    logger.debug("found [DATA]")
                    self.samples_offset = row_nr
                    break

                tokens = line.split("=")

                if len(tokens) != 2:
                    continue

                if read_header:
                    if (tokens[0].lower() == self._aml.date) and (date is None):
                        try:
                            date = dt.strptime(tokens[1].strip(), "%m/%d/%y")
                            continue
                        except ValueError:
                            date = dt.strptime(tokens[1].strip(), "%Y-%m-%d")
                            continue

                    if (tokens[0].lower() == self._aml.time) and (time is None):
                        try:
                            time = dt.strptime(tokens[1].strip(), "%H:%M:%S")
                            continue
                        except ValueError:
                            time = dt.strptime(tokens[1].strip(), "%H:%M:%S.%f")
                            continue

                    if tokens[0].lower() == self._aml.lat:
                        try:
                            if not math.isclose(float(tokens[1]), 0.0):
                                lat = float(tokens[1])
                            else:
                                lat = None
                        except ValueError:  # it may be no-lock
                            lat = None
                        continue

                    if tokens[0].lower() == self._aml.long:
                        try:
                            if not math.isclose(float(tokens[1]), 0.0):
                                lon = float(tokens[1])
                            else:
                                lon = None
                        except ValueError:  # it may be no-lock
                            lon = None
                        continue

                    if tokens[0].lower() == self._aml.lat2:
                        try:
                            if not math.isclose(float(tokens[1]), 0.0):
                                lat2 = float(tokens[1])
                            else:
                                lat2 = None
                        except ValueError:  # it may be no-lock
                            lat2 = None
                        continue

                    if tokens[0].lower() == self._aml.long2:
                        try:
                            if not math.isclose(float(tokens[1]), 0.0):
                                lon2 = float(tokens[1])
                            else:
                                lon2 = None
                        except ValueError:  # it may be no-lock
                            lon2 = None
                        continue

                    if tokens[0].lower() == self._aml.serial:
                        if tokens[1]:
                            self.ssp.cur.meta.sn = tokens[1]
                        continue

                if read_metadata:
                    if tokens[0].lower() == self._aml.columns:
                        fields = tokens[1].split(',')
                        for field_idx, field in enumerate(fields):
                            self.field_index[field.lower()] = field_idx

                    if tokens[0].lower() == self._aml.units:
                        units = tokens[1].split(',')
                        for unit_idx, unit in enumerate(units):
                            self.field_units[unit_idx] = unit.lower()

            except ValueError:
                traceback.print_exc()
                logger.warning("invalid conversion parsing of line #%s: %s" % (row_nr, line))
                continue
            except IndexError:
                logger.warning("invalid index parsing of line #%s: %s" % row_nr, line)
                continue

            continue

        if not read_data:
            raise RuntimeError('Invalid file structure -> header: %s, metadata: %s, data: %s'
                               % (read_header, read_metadata, read_data))

        if (lat is not None) and (lon is not None) and \
                (self.ssp.cur.meta.latitude is None) and (self.ssp.cur.meta.longitude is None):
            self.ssp.cur.meta.latitude = lat
            self.ssp.cur.meta.longitude = lon
            logger.debug("retrieved GPS location: (%s, %s)" % (self.ssp.cur.meta.longitude, self.ssp.cur.meta.latitude))

        elif (lat2 is not None) and (lon2 is not None) and \
                (self.ssp.cur.meta.latitude is None) and (self.ssp.cur.meta.longitude is None):
            self.ssp.cur.meta.latitude = lat2
            self.ssp.cur.meta.longitude = lon2
            logger.debug("retrieved location: (%s, %s)" % (self.ssp.cur.meta.longitude, self.ssp.cur.meta.latitude))

        if (date is not None) and (time is not None):
            self.ssp.cur.meta.utc_time = dt(year=date.year, month=date.month, day=date.day,
                                            hour=time.hour, minute=time.minute, second=time.second)
            logger.debug("retrieved timestamp: %s" % self.ssp.cur.meta.utc_time)

        if not self.ssp.cur.meta.original_path:
            self.ssp.cur.meta.original_path = self.fid.path

        has_temp = (self._aml.temp in self.field_index) or (self._aml.temp2 in self.field_index) or \
                   (self._aml.temp3 in self.field_index)

        if self._aml.pressure in self.field_units:
            if self.field_units[self._aml.pressure] != "dbar":
                logger.warning('unsupported UoM for pressure: %s' % self.field_units[self._aml.pressure])
                del self.field_index[self._aml.pressure]
        if self._aml.depth in self.field_units:
            if self.field_units[self._aml.depth] != "m":
                logger.warning('unsupported UoM for depth: %s' % self.field_units[self._aml.depth])
                del self.field_index[self._aml.depth]
        if self._aml.cond in self.field_units:
            if self.field_units[self._aml.cond] == "mS/cm":
                self._aml.cond_multi = 0.1
            elif self.field_units[self._aml.cond] == "S/m":
                logger.warning('unsupported UoM for conductivity: %s' % self.field_units[self._aml.cond])
                del self.field_index[self._aml.cond]
        if self._aml.sal in self.field_units:
            if self.field_units[self._aml.sal] != "PSU":
                logger.warning('unsupported UoM for salinity: %s' % self.field_units[self._aml.sal])
                del self.field_index[self._aml.sal]
        if self._aml.temp in self.field_units:
            if self.field_units[self._aml.temp] != "C":
                logger.warning('unsupported UoM for temperature: %s' % self.field_units[self._aml.temp])
                del self.field_index[self._aml.temp]
        if self._aml.temp2 in self.field_units:
            if self.field_units[self._aml.temp2] != "C":
                logger.warning('unsupported UoM for temperature: %s' % self.field_units[self._aml.temp2])
                del self.field_index[self._aml.temp2]
        if self._aml.temp3 in self.field_units:
            if self.field_units[self._aml.temp3] != "C":
                logger.warning('unsupported UoM for temperature: %s' % self.field_units[self._aml.temp3])
                del self.field_index[self._aml.temp3]
        if self._aml.speed in self.field_units:
            if self.field_units[self._aml.speed] != "m/s":
                logger.warning('unsupported UoM for sound speed: %s' % self.field_units[self._aml.speed])
                del self.field_index[self._aml.speed]
        if self._aml.speed2 in self.field_units:
            if self.field_units[self._aml.speed2] != "m/s":
                logger.warning('unsupported UoM for sound speed: %s' % self.field_units[self._aml.speed2])
                del self.field_index[self._aml.speed2]

        if (self._aml.pressure not in self.field_index) and (self._aml.depth not in self.field_index):
            raise RuntimeError('Unable to locate valid depth or pressure column')

        # logger.info(self.field_index)
        if self._aml.speed2 in self.field_index:  # CalcSV -> CTD
            self.ssp.cur.meta.sensor_type = Dicts.sensor_types['CTD']            
        elif self._aml.speed in self.field_index:  # SV -> SV or SVT
            if has_temp:
                self.ssp.cur.meta.sensor_type = Dicts.sensor_types['SVPT']
            else:
                self.ssp.cur.meta.sensor_type = Dicts.sensor_types['SVP']
        else:  # missing sound speed
            if has_temp:
                self.ssp.cur.meta.sensor_type = Dicts.sensor_types['XBT']
            else:  # missing temperature
                raise RuntimeError("Unable to locate depth or sound speed column")

    def _parse_body(self):
        if self._path_ext in [".csv"]:
            self._csv_body()
        elif self._path_ext in [".aml"]:
            self._aml_body()
        else:
            raise RuntimeError('Unsupported extension> %s' % self._path_ext)

    def _csv_body(self):
        logger.debug('parsing CSV body')

        count = 0
        read_samples = False
        has_depth_and_speed = False
        has_pressure_and_speed = False
        has_calc_speed = False
        has_temp = False
        has_sal = False
        depth_idx = None
        pressure_idx = None
        temp_idx = None
        sal_idx = None
        speed_idx = None

        self.ssp.cur.init_data(len(self.lines))

        for row_nr, line in enumerate(self.lines):

            # logger.debug("%d : %s" % (row_nr, line))

            # first look for [data]
            if not read_samples:

                tokens = line.split()

                if len(tokens) == 0:
                    continue

                if tokens[0].lower() == self._csv.data:
                    read_samples = True
                    data_row = row_nr
                    logger.debug("found data token: %s at row: %d" % (self._csv.data, data_row))
                    continue

                continue

            # then look for depth and speed indices
            if not (has_depth_and_speed or has_pressure_and_speed):

                tokens = line.split(",")
                for idx, token in enumerate(tokens):

                    if token == self._csv.depth:
                        depth_idx = idx
                        logger.debug("found depth index: %s" % depth_idx)

                    elif token == self._csv.pressure:
                        pressure_idx = idx
                        logger.debug("found pressure index: %s" % pressure_idx)

                    elif token == self._csv.temp:
                        temp_idx = idx
                        has_temp = True
                        logger.debug("found temp index: %s" % temp_idx)

                    elif token == self._csv.sal:
                        sal_idx = idx
                        has_sal = True
                        logger.debug("found sal index: %s" % sal_idx)

                    elif token == self._csv.speed:
                        speed_idx = idx
                        logger.debug("found sound speed index: %s" % speed_idx)

                    elif (token == self._csv.speed2) and (speed_idx is None):
                        speed_idx = idx
                        has_calc_speed = True
                        logger.debug("found sound speed index [2]: %s" % speed_idx)

                    continue

                # set flag to true
                if (depth_idx is not None) and (speed_idx is not None):
                    has_depth_and_speed = True

                elif (pressure_idx is not None) and (speed_idx is not None):
                    has_pressure_and_speed = True

                if has_pressure_and_speed or has_depth_and_speed:

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
                        if has_depth_and_speed:
                            if speed_idx < depth_idx:
                                count += 1
                        continue

                    elif idx == pressure_idx:
                        self.ssp.cur.data.pressure[count] = float(tokens[pressure_idx])
                        if has_pressure_and_speed:
                            if speed_idx < pressure_idx:
                                count += 1
                        continue

                    elif idx == speed_idx:
                        self.ssp.cur.data.speed[count] = float(tokens[speed_idx])
                        if has_depth_and_speed:
                            if speed_idx > depth_idx:
                                count += 1
                        elif has_pressure_and_speed:
                            if speed_idx > pressure_idx:
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
            raise RuntimeError("Issue in finding data token: %s" % self._csv.data)

        if not (has_depth_and_speed or has_pressure_and_speed):

            read_samples = False
            first_row_done = False

            for row_nr, line in enumerate(self.lines):

                # first look for [data]
                if not read_samples:

                    tokens = line.split()

                    if len(tokens) == 0:
                        continue

                    if tokens[0].lower() == self._csv.data:
                        read_samples = True
                        data_row = row_nr
                        logger.debug("found data token: %s at row: %d" % (self._csv.data, data_row))
                        continue

                    continue

                # finally the data
                tokens = line.split(",")
                if len(tokens) < 4:
                    continue

                if len(tokens) == 9:  # TODO: currently assuming Base-X2 with CT Xchange and P Xchange installed
                    conductivity_idx = 2
                    temp_idx = 3
                    pressure_idx = 4
                    sal_idx = 6
                    speed_idx = 8

                    if not first_row_done:
                        first_row_done = True
                        # it should already be set as a SVP type
                        self.ssp.cur.meta.sensor_type = Dicts.sensor_types['CTD']
                        logger.debug("guessing: C: %d, T: %d, P: %d, sal: %d, SS: %d"
                                     % (conductivity_idx, temp_idx, pressure_idx, sal_idx, speed_idx))

                    try:
                        conductivity = float(tokens[conductivity_idx])
                        temp = float(tokens[temp_idx])
                        pressure = float(tokens[pressure_idx])
                        sal = float(tokens[sal_idx])
                        speed = float(tokens[speed_idx])

                        if pressure < 0.01:
                            logger.warning("skipping sample at row #%d -> pressure value: %s" % (row_nr, pressure))
                            continue
                        if (speed < 1200.0) or (speed > 1700):
                            logger.warning("skipping sample at row #%d -> speed value: %s" % (row_nr, speed))
                            continue

                        self.ssp.cur.data.conductivity[count] = conductivity
                        self.ssp.cur.data.temp[count] = temp
                        self.ssp.cur.data.pressure[count] = pressure
                        self.ssp.cur.data.sal[count] = sal
                        self.ssp.cur.data.speed[count] = speed
                        count += 1

                    except ValueError:
                        logger.warning("invalid conversion parsing of line #%s" % row_nr)
                        continue
                    except IndexError:
                        logger.warning("invalid index parsing of line #%s" % row_nr)
                        continue

                else:  # token != 9 -> just attempting for depth and sound speed
                    depth_idx = 3
                    speed_idx = 2
                    if not first_row_done:
                        first_row_done = True
                        # it should already be set as a SVP type
                        self.ssp.cur.meta.sensor_type = Dicts.sensor_types['SVP']
                        logger.debug("guessing: d: %s, SS: %s" % (depth_idx, speed_idx))

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

        if count == 0:
            raise RuntimeError("unable to find depth and sound speed indices!")

        logger.debug("retrieved %d samples" % count)
        self.ssp.cur.data_resize(count)

    def _aml_body(self):
        logger.debug('parsing AML body')

        self.ssp.cur.init_data(len(self.lines) - self.samples_offset)

        count = 0
        for line_idx, line in enumerate(self.lines[self.samples_offset:len(self.lines)]):

            data = line.split(',')
            # logger.debug(data)

            # skip empty lines
            if len(data) == 1:
                continue

            # pressure
            try:
                if self._aml.pressure in self.field_index:
                    # logger.debug(self.field_index[self._aml.pressure])
                    self.ssp.cur.data.pressure[count] = float(data[self.field_index[self._aml.pressure]])
            except ValueError:
                logger.warning("invalid conversion parsing of line #%s" % (self.samples_offset + line_idx))
                continue
            except IndexError:
                logger.warning("invalid index parsing of line #%s" % (self.samples_offset + line_idx))
                continue

            # depth
            try:
                if self._aml.depth in self.field_index:
                    # logger.debug(self.field_index[self._aml.depth])
                    self.ssp.cur.data.depth[count] = float(data[self.field_index[self._aml.depth]])
            except ValueError:
                logger.warning("invalid conversion parsing of line #%s" % (self.samples_offset + line_idx))
                continue
            except IndexError:
                logger.warning("invalid index parsing of line #%s" % (self.samples_offset + line_idx))
                continue

            # temperature
            try:
                if self._aml.temp in self.field_index:
                    self.ssp.cur.data.temp[count] = float(data[self.field_index[self._aml.temp]])
                elif self._aml.temp2 in self.field_index:
                    self.ssp.cur.data.temp[count] = float(data[self.field_index[self._aml.temp2]])
                elif self._aml.temp3 in self.field_index:
                    self.ssp.cur.data.temp[count] = float(data[self.field_index[self._aml.temp3]])
            except ValueError:
                logger.warning("invalid conversion parsing of line #%s" % (self.samples_offset + line_idx))
                continue
            except IndexError:
                logger.warning("invalid index parsing of line #%s" % (self.samples_offset + line_idx))
                continue

            # conductivity
            try:
                if self._aml.cond in self.field_index:
                    self.ssp.cur.data.conductivity[count] = float(data[self.field_index[self._aml.cond]]) * \
                                                            self._aml.cond_multi
            except ValueError:
                logger.warning("invalid conversion parsing of line #%s" % (self.samples_offset + line_idx))
                continue
            except IndexError:
                logger.warning("invalid index parsing of line #%s" % (self.samples_offset + line_idx))
                continue

            # salinity
            try:
                if self._aml.sal in self.field_index:
                    self.ssp.cur.data.sal[count] = float(data[self.field_index[self._aml.sal]])
            except ValueError:
                logger.warning("invalid conversion parsing of line #%s" % (self.samples_offset + line_idx))
                continue
            except IndexError:
                logger.warning("invalid index parsing of line #%s" % (self.samples_offset + line_idx))
                continue

            # sound speed
            try:
                if self._aml.speed2 in self.field_index:
                    self.ssp.cur.data.speed[count] = float(data[self.field_index[self._aml.speed2]])
                elif self._aml.speed in self.field_index:
                    self.ssp.cur.data.speed[count] = float(data[self.field_index[self._aml.speed]])
            except ValueError:
                logger.warning("invalid conversion parsing of line #%s" % (self.samples_offset + line_idx))
                continue
            except IndexError:
                logger.warning("invalid index parsing of line #%s" % (self.samples_offset + line_idx))
                continue

            count += 1

        self.ssp.cur.data_resize(count)
