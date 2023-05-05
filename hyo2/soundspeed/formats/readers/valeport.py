import datetime as dt
import logging
import os

from hyo2.soundspeed.formats.readers.abstract import AbstractTextReader
from hyo2.soundspeed.profile.dicts import Dicts
from hyo2.soundspeed.base.callbacks.cli_callbacks import CliCallbacks

logger = logging.getLogger(__name__)


class Valeport(AbstractTextReader):
    """Valeport reader"""

    # A dictionary to resolve sensor type from probe type
    sensor_dict = {
        Dicts.probe_types['MIDAS SVP']: Dicts.sensor_types["SVPT"],
        Dicts.probe_types['MIDAS SVP 6000']: Dicts.sensor_types["SVPT"],
        Dicts.probe_types['MIDAS SVX2']: Dicts.sensor_types["SVPT"],
        Dicts.probe_types['MIDAS SVX2 100']: Dicts.sensor_types["SVPT"],
        Dicts.probe_types['MIDAS SVX2 500']: Dicts.sensor_types["SVPT"],
        Dicts.probe_types['MIDAS SVX2 1000']: Dicts.sensor_types["SVPT"],
        Dicts.probe_types['MIDAS SVX2 3000']: Dicts.sensor_types["SVPT"],
        Dicts.probe_types['MIDAS SVX2 6000']: Dicts.sensor_types["SVPT"],
        Dicts.probe_types['MiniSVP']: Dicts.sensor_types["SVPT"],
        Dicts.probe_types['MONITOR CTD']: Dicts.sensor_types["CTD"],
        Dicts.probe_types['MONITOR SVP 500']: Dicts.sensor_types["SVPT"],
        Dicts.probe_types['RapidSV']: Dicts.sensor_types["SVP"],
        Dicts.probe_types['RapidSVT']: Dicts.sensor_types["SVPT"],
        Dicts.probe_types['SWiFT']: Dicts.sensor_types["SVPT"],
        Dicts.probe_types['SWiFT CTD']: Dicts.sensor_types["CTD"],
        Dicts.probe_types['Unknown']: Dicts.sensor_types["Unknown"]
    }

    def __init__(self):
        super(Valeport, self).__init__()
        self.desc = "Valeport"  # Monitor/Midas/MiniSVP/RapidSVT
        self._ext.add('000')
        self._ext.add('txt')
        self._ext.add('vpd')
        self._ext.add('vp2')

        self.tk_start_data = ""
        self.tk_time = ""
        self.tk_latitude = 'Latitude'
        self.tk_probe_type = ""

        # flag used to remember if the pressure in in meter (we check that: 'Pressure units: m'), thus depth
        self.minisvp_has_depth = False

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
        logger.debug('parsing header')

        if os.path.splitext(self.fid.path)[-1] in [".vpd", ".vp2"]:
            self._vp2_header()

        elif self.lines[0][:3] == 'Now':  # MiniSVP
            self._mini_header()

        else:  # MIDAS or Monitor
            self._midas_header()

    def _vp2_header(self):
        logger.debug("VPD/VP2 format: header")

        has_header = False

        for idx, line in enumerate(self.lines):

            line = line.strip().upper()

            if not has_header:
                # check valid format
                if line == "[HEADER]":
                    has_header = True
                continue

            if line == "[DATA]":
                logger.debug("found [DATA]")
                self.samples_offset = idx
                break

            tokens = line.split('=')
            if len(tokens) != 2:
                continue

            if tokens[0] == "INSTRUMENT":
                if tokens[1] == "SWIFT SVP":
                    self.ssp.cur.meta.probe_type = Dicts.probe_types['SWiFT']
                    self.ssp.cur.meta.sensor_type = self.sensor_dict[self.ssp.cur.meta.probe_type]
                    continue
                elif tokens[1] == "SWIFT CTD":
                    self.ssp.cur.meta.probe_type = Dicts.probe_types['SWiFT CTD']
                    self.ssp.cur.meta.sensor_type = self.sensor_dict[self.ssp.cur.meta.probe_type]
                    continue
                elif tokens[1] == "MONITOR CTD":
                    self.ssp.cur.meta.probe_type = Dicts.probe_types['MONITOR CTD']
                    self.ssp.cur.meta.sensor_type = self.sensor_dict[self.ssp.cur.meta.probe_type]
                    continue
                elif tokens[1] == "MIDAS SVX2":
                    self.ssp.cur.meta.probe_type = Dicts.probe_types['MIDAS SVX2']
                    self.ssp.cur.meta.sensor_type = self.sensor_dict[self.ssp.cur.meta.probe_type]
                    continue
                elif tokens[1] == "MIDAS SVP":
                    self.ssp.cur.meta.probe_type = Dicts.probe_types['MIDAS SVP']
                    self.ssp.cur.meta.sensor_type = self.sensor_dict[self.ssp.cur.meta.probe_type]
                    continue
                else:
                    raise RuntimeError("Unknown/unsupported instrument: %s" % line)

            if tokens[0] in ["INSTRUMENTCODE", "SERIAL_NUMBER"]:
                try:
                    self.ssp.cur.meta.sn = tokens[1]
                    continue
                except ValueError:
                    logger.warning("unable to parse instrument code/serial number: %s" % line)

            if tokens[0] == "LATITUDE":
                try:
                    self.ssp.cur.meta.latitude = float(tokens[1])
                    continue
                except ValueError:
                    logger.warning("unable to parse latitude: %s" % line)

            if tokens[0] == "LONGITUDE":
                try:
                    self.ssp.cur.meta.longitude = float(tokens[1])
                    continue
                except ValueError:
                    logger.warning("unable to parse longitude: %s" % line)

            if tokens[0] == "DATASTARTTIME":
                try:
                    self.ssp.cur.meta.utc_time = dt.datetime.strptime(tokens[1], "%Y/%m/%d %H:%M:%S")
                except ValueError:
                    logger.warning("unable to parse date and time: %s" % line)

            if tokens[0] == "DATESTARTTIME":
                try:
                    self.ssp.cur.meta.utc_time = dt.datetime.strptime(tokens[1], "%Y/%m/%d %H:%M:%S")
                except ValueError:
                    logger.warning("unable to parse date and time: %s" % line)

            if tokens[0] == "TIME_STAMP":
                try:
                    self.ssp.cur.meta.utc_time = dt.datetime.strptime(tokens[1], "%Y/%m/%d %H:%M:%S.%f")
                except ValueError:
                    try:
                        self.ssp.cur.meta.utc_time = dt.datetime.strptime(tokens[1], "%Y.%m.%d %H:%M:%S.%f")
                    except ValueError:
                        logger.warning("unable to parse date and time: %s" % line)

        if not has_header:
            raise RuntimeError('Invalid format! Unable to locate the [HEADER] row')

        if not self.ssp.cur.meta.original_path:
            self.ssp.cur.meta.original_path = self.fid.path

        # initialize data sample fields
        self.ssp.cur.init_data(len(self.lines) - self.samples_offset)
        # initialize additional fields
        self.ssp.cur.init_more(self.more_fields)

    def _mini_header(self):
        self.tk_start_data = 'Pressure units:'
        self.tk_time = 'Now'
        self.tk_sn = 'S/N'

        for line in self.lines:
            if line[:len(self.tk_start_data)] == self.tk_start_data:
                self.samples_offset += 1
                if ' m' in line[len(self.tk_start_data):]:
                    self.minisvp_has_depth = True
                    self.ssp.cur.meta.depth_uom = Dicts.uom_symbols['meter']
                else:
                    if ' dBar' in line[len(self.tk_start_data):]:
                        self.ssp.cur.meta.pressure_uom = Dicts.uom_symbols['decibar']
                    self.minisvp_has_depth = False
                logger.info("MiniSVP/RapidSVT has depth: %s" % self.minisvp_has_depth)
                break

            elif line[:len(self.tk_time)] == self.tk_time:
                try:
                    date_string = line.split()[1]
                    time_string = line.split()[2]
                    month = int(date_string.split('/')[1])
                    day = int(date_string.split('/')[0])
                    year = int(date_string.split('/')[2])
                    hour = int(time_string.split(':')[0])
                    minute = int(time_string.split(':')[1])
                    second = int(time_string.split(':')[2])
                    if (year is not None) and (hour is not None):
                        self.ssp.cur.meta.utc_time = dt.datetime(year, month, day, hour, minute, second)
                except ValueError:
                    logger.warning("unable to parse date and time from line #%s" % self.samples_offset)

            elif line[:len(self.tk_latitude)] == self.tk_latitude:
                try:
                    self.ssp.cur.meta.latitude = float(line.split(':')[-1])
                except ValueError:
                    logger.warning("unable to parse latitude from line #%s" % self.samples_offset)

            elif line[:len('MiniSVP:')] == 'MiniSVP:':
                self.ssp.cur.meta.probe_type = Dicts.probe_types['MiniSVP']
                try:
                    self.ssp.cur.meta.sensor_type = self.sensor_dict[self.ssp.cur.meta.probe_type]
                except KeyError:
                    logger.warning("unable to recognize probe type from line #%s" % self.samples_offset)
                    self.ssp.cur.meta.sensor_type = Dicts.sensor_types['Unknown']
                    
                if self.tk_sn in line[len('MiniSVP:'):]:
                    try:
                        self.ssp.cur.meta.sn = line[len('MiniSVP:'):].split()[1]
                    except IndexError:
                        logger.warning("unable to parse instrument serial number from line: %s" % line)

            elif line[:len('RapidSVT:')] == 'RapidSVT:':
                self.ssp.cur.meta.probe_type = Dicts.probe_types['RapidSVT']
                try:
                    self.ssp.cur.meta.sensor_type = self.sensor_dict[self.ssp.cur.meta.probe_type]
                except KeyError:
                    logger.warning("unable to recognize probe type from line #%s" % self.samples_offset)
                    self.ssp.cur.meta.sensor_type = Dicts.sensor_types['Unknown']

            elif line[:len('RapidSV:')] == 'RapidSV:':
                self.ssp.cur.meta.probe_type = Dicts.probe_types['RapidSV']
                try:
                    self.ssp.cur.meta.sensor_type = self.sensor_dict[self.ssp.cur.meta.probe_type]
                except KeyError:
                    logger.warning("unable to recognize probe type from line #%s" % self.samples_offset)
                    self.ssp.cur.meta.sensor_type = Dicts.sensor_types['Unknown']

            self.samples_offset += 1

        if not self.ssp.cur.meta.original_path:
            self.ssp.cur.meta.original_path = self.fid.path

        # initialize data sample fields
        self.ssp.cur.init_data(len(self.lines) - self.samples_offset)
        # initialize additional fields
        self.ssp.cur.init_more(self.more_fields)

    def _midas_header(self):
        # check valid format
        first_row = self.lines[0]
        first_row = first_row.split('\t')
        if not first_row[0].strip().upper() == 'PREVIOUS FILE LOCATION :':
            raise RuntimeError('Invalid first row: %s' % first_row)

        logger.debug('Midas format: header')

        for idx, line in enumerate(self.lines):

            line = line.strip().upper()

            tokens = line.split('\t')
            if len(tokens) == 1:
                continue

            if len(tokens) > 2 and (tokens[0] == 'DATE / TIME'):
                logger.debug('found data header list')
                self.samples_offset = idx
                break

            if tokens[0] == 'TIME STAMP :':
                try:
                    date_time = tokens[1]
                    date_string = date_time.split(' ')[0]
                    time_string = date_time.split(' ')[1]
                    day, month, year = [int(i) for i in date_string.split('/')]
                    hour, minute, second = [int(i) for i in time_string.split(':')]
                    self.ssp.cur.meta.utc_time = dt.datetime(year, month, day, hour, minute, second)
                except ValueError:
                    logger.warning("Unable to parse time from line #%d" % idx)
                continue

            if tokens[0] == 'MODEL NAME :':
                try:
                    self.ssp.cur.meta.probe_type = Dicts.probe_types[tokens[1]]
                except (ValueError, KeyError):
                    logger.warning("unable to parse probe type from line #%d" % idx)
                    self.ssp.cur.meta.probe_type = Dicts.probe_types['Unknown']
                try:
                    self.ssp.cur.meta.sensor_type = self.sensor_dict[self.ssp.cur.meta.probe_type]
                except KeyError:
                    logger.warning("unable to find sensor type from line #%d" % idx)
                    self.ssp.cur.meta.sensor_type = Dicts.sensor_types['Unknown']
                continue

            if tokens[0] == 'SERIAL NO. :':
                try:
                    self.ssp.cur.meta.sn = tokens[1]
                except ValueError:
                    logger.warning('Unable to parse serial number on line: #%d' % idx)
                continue

        if (self.ssp.cur.meta.probe_type == Dicts.probe_types['MIDAS SVX2 1000']) or \
                (self.ssp.cur.meta.probe_type == Dicts.probe_types['MIDAS SVX2 3000']):
            self.more_fields.append('Pressure')
            self.more_fields.append('Conductivity')
        if not self.ssp.cur.meta.original_path:
            self.ssp.cur.meta.original_path = self.fid.path

        # initialize data sample fields
        self.ssp.cur.init_data(len(self.lines) - self.samples_offset)
        # initialize additional fields
        self.ssp.cur.init_more(self.more_fields)

    def _parse_body(self):
        logger.debug('parsing body')

        if os.path.splitext(self.fid.path)[-1] in [".vpd", ".vp2"]:
            self._vp2_body()

        elif self.lines[0][:3] == 'Now':  # MiniSVP
            self._mini_body()

        else:  # MIDAS or Monitor
            self._midas_body()

    def _vp2_body(self):
        # check valid format
        first_data_row = self.lines[self.samples_offset]
        if not first_data_row.strip().upper() == "[DATA]":
            raise RuntimeError("Invalid first data row: %s" % first_data_row)

        logger.debug("VPD/VP2 format: body")

        depth_idx = None
        pressure_idx = None
        speed_idx = None
        temp_idx = None
        sal_idx = None

        count = 0
        for idx, line in enumerate(self.lines[self.samples_offset:]):

            if idx == 0:
                continue

            if idx == 1:
                line = line.strip().upper()
                tokens = line.split('\t')
                # logger.debug("data header: %s" % line)
                if len(tokens) < 4:
                    raise RuntimeError("Invalid number of data columns: %s" % line)

                for idx_token, token in enumerate(tokens):
                    if token == "DEPTH":
                        depth_idx = idx_token
                    if token == "PRESSURE":
                        pressure_idx = idx_token
                    elif token == "SOUND VELOCITY":
                        speed_idx = idx_token
                    elif token == "TEMPERATURE":
                        temp_idx = idx_token
                    elif token == "SALINITY":
                        sal_idx = idx_token

                continue

            if idx == 2:
                continue

            if depth_idx is None:
                raise RuntimeError("Unable to identify depth column")

            data_tokens = line.split('\t')
            if len(data_tokens) < 4:
                continue

            try:
                depth = float(data_tokens[depth_idx])
                pressure = float(data_tokens[pressure_idx])
                speed = float(data_tokens[speed_idx])
                temp = float(data_tokens[temp_idx])
                sal = float(data_tokens[sal_idx])

                if pressure < 0.0:  # pressure
                    logger.info("skipping for invalid pressure: %s" % line)
                    continue
                if speed < 0.0:  # sound speed
                    logger.info("skipping for invalid sound speed: %s" % line)
                    continue
                if (temp < -10.0) or (temp > 100):  # temp
                    logger.info("skipping for invalid temp: %s" % line)
                    continue
                if sal < 0.0:  # salinity
                    logger.info("skipping for invalid salinity: %s" % line)
                    continue

            except ValueError:
                logger.error("unable to parse line: %s" % line)
                continue

            self.ssp.cur.data.depth[count] = depth
            self.ssp.cur.data.pressure[count] = pressure
            self.ssp.cur.data.speed[count] = speed
            self.ssp.cur.data.temp[count] = temp
            self.ssp.cur.data.sal[count] = sal

            count += 1

        self.ssp.cur.data_resize(count)

    def _mini_body(self):
        count = 0
        for line in self.lines[self.samples_offset:len(self.lines)]:

            data = line.split()

            if self.ssp.cur.meta.probe_type == Dicts.probe_types['RapidSV']:  # 2-column data
                if len(data) != 2:
                    logger.warning("unexpected number of fields: %d" % len(data))
                    continue

                try:
                    z = float(data[0])
                    speed = float(data[1])
                except ValueError:
                    logger.error("unable to parse line: %s" % line)
                    continue

                # Skipping invalid data (above water, negative temperature or crazy sound speed)
                if (z < 0.0) or (speed < 1400.0) or (speed > 1650.0):
                    logger.warning("skipping invalid values: %.1f %.1f" % (z, speed))
                    continue

                if self.minisvp_has_depth:
                    self.ssp.cur.data.depth[count] = z
                else:
                    self.ssp.cur.data.pressure[count] = z
                self.ssp.cur.data.speed[count] = speed

            else:
                if len(data) != 3:
                    logger.warning("unexpected number of fields: %d" % len(data))
                    continue

                try:
                    z = float(data[0])
                    temp = float(data[1])
                    speed = float(data[2])
                except ValueError:
                    logger.error("unable to parse line: %s" % line)
                    continue

                # Skipping invalid data (above water, negative temperature or crazy sound speed)
                if (z < 0.0) or (temp < -2.0) or (temp > 100.0) or (speed < 1400.0) \
                        or (speed > 1650.0):
                    logger.warning("skipping invalid values: %.1f %.1f %.1f" % (z, temp, speed))
                    continue

                if self.minisvp_has_depth:
                    self.ssp.cur.data.depth[count] = z
                else:
                    self.ssp.cur.data.pressure[count] = z
                self.ssp.cur.data.temp[count] = temp
                self.ssp.cur.data.speed[count] = speed

            count += 1

        self.ssp.cur.data_resize(count)

    def _midas_body(self):
        # check valid format
        first_row = self.lines[self.samples_offset]
        first_row = first_row.split('\t')
        if not first_row[0].strip().upper() == 'DATE / TIME':
            raise RuntimeError('Invalid first data row: %s' % first_row)

        logger.debug('midas format: body')

        pressure_idx = None     # Pressure, Speed, and Temperature in all probe types
        speed_idx = None
        temp_idx = None
        sal_idx = None
        cond_idx = None

        count = 0
        for idx, line in enumerate(self.lines[self.samples_offset:]):

            if idx == 0:
                line = line.strip().upper()
                tokens = line.split('\t')
                if len(tokens) < 2:
                    raise RuntimeError('Invalid number of data columns: %s' % line)

                for idx_token, token in enumerate(tokens):
                    token = token.split(';')
                    if token[0] == "PRESSURE":
                        pressure_idx = idx_token
                    elif token[0] == "SOUND VELOCITY":
                        speed_idx = idx_token
                    elif token[0] == "TEMPERATURE":
                        temp_idx = idx_token
                    elif token[0] == "CALC. SALINITY":
                        sal_idx = idx_token
                    elif token[0] == "CONDUCTIVITY":
                        cond_idx = idx_token

                if (pressure_idx is None) or (temp_idx is None) or (speed_idx is None):
                    raise RuntimeError('Unable to identify required datafield (PRESSURE/ SOUNDSPEED/ TEMPERATURE)'
                                       ' in line: %s' % line)

                continue

            data_tokens = line.split('\t')

            try:
                # Required tokens
                pressure = float(data_tokens[pressure_idx])
                if pressure < 0.0:
                    logger.info("skipping for invalid pressure (%s): %s" % (pressure, line))
                    continue
                speed = float(data_tokens[speed_idx])
                if speed < 0.0:
                    logger.info("skipping for invalid sound speed (%s): %s" % (speed, line))
                    continue
                temp = float(data_tokens[temp_idx])
                if (temp < -10.0) or (temp > 100):
                    logger.info("skipping for invalid temp (%s): %s" % (temp, line))
                    continue

                # Optional tokens
                sal = None
                if sal_idx is not None:
                    sal = float(data_tokens[sal_idx])
                    if sal < 0.0:  # salinity
                        logger.info("skipping for invalid salinity (%s): %s" % (sal, line))
                        continue
                cond = None
                if cond_idx is not None:
                    cond = float(data_tokens[cond_idx])
                    if cond < 0.0:
                        logger.info("skipping for invalid conductivity (%s): %s" % (cond, line))

                # Storing the retrieved valid values
                self.ssp.cur.data.pressure[count] = pressure
                self.ssp.cur.data.speed[count] = speed
                self.ssp.cur.data.temp[count] = temp
                if sal_idx is not None:
                    self.ssp.cur.data.sal[count] = sal
                if cond_idx is not None:
                    self.ssp.cur.data.conductivity[count] = cond

            except ValueError:
                logger.error('Unable to parse line: %s' % line)
                continue

            count += 1

        self.ssp.cur.data_resize(count)
