import datetime as dt
import logging

logger = logging.getLogger(__name__)

# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.readers.abstract import AbstractTextReader
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.profile.dicts import Dicts
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.base.callbacks.cli_callbacks import CliCallbacks


class TSK(AbstractTextReader):
    """Tsurumi-Seiki reader"""

    supported_xbt_probes = (
        Dicts.probe_types["T-5"],
        Dicts.probe_types["T-6"],
        Dicts.probe_types["T-7"],
        Dicts.probe_types["T-10"],
    )

    supported_xctd_probes = (
        Dicts.probe_types["XCTD-1"],
        Dicts.probe_types["XCTD-3"],
        Dicts.probe_types["XCTD-4"],
    )

    supported_axctd_probes = (
        Dicts.probe_types["AXCTD-1"],
    )

    probe_type_dict = {
        "T05": Dicts.probe_types["T-5"],
        "T06": Dicts.probe_types["T-6"],
        "T07": Dicts.probe_types["T-7"],
        "T10": Dicts.probe_types["T-10"],
        "CT1": Dicts.probe_types["XCTD-1"],
        "CT3": Dicts.probe_types["XCTD-3"],
        "CT4": Dicts.probe_types["XCTD-4"],
        "AC1": Dicts.probe_types["AXCTD-1"],
    }

    sensor_type_dict = {
        "T05": Dicts.sensor_types["XBT"],
        "T06": Dicts.sensor_types["XBT"],
        "T07": Dicts.sensor_types["XBT"],
        "T10": Dicts.sensor_types["XBT"],
        "CT1": Dicts.sensor_types["XCTD"],
        "CT3": Dicts.sensor_types["XCTD"],
        "CT4": Dicts.sensor_types["XCTD"],
        "AC1": Dicts.sensor_types["XCTD"],
    }

    def __init__(self):
        super().__init__()
        self.desc = "TSK"
        self._ext.add('xbt')
        self._ext.add('xctd')
        self._ext.add('xctp')
        self.version = "0.2.0"

    def read(self, data_path, settings, callbacks=CliCallbacks(), progress=None):
        logger.debug('*** %s ***: start' % self.driver)

        self.s = settings
        self.cb = callbacks

        self.init_data_and_append()  # create a new empty profile list and append a new profile

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
        self.samples_offset: int = 1
        logger.debug('header: %s' % header)

        tokens = header.split(",")
        nr_tokens = len(tokens)
        if nr_tokens != 14:
            raise RuntimeError("Unexpected header format: %d tokens" % nr_tokens)
        logger.debug('tokens: %d' % nr_tokens)

        ssp = self.ssp
        if ssp is None:
            raise RuntimeError("unset profile list")
        cur = ssp.cur
        if cur is None:
            raise RuntimeError("unset current profile")

        nr_samples = len(self.lines) - 1

        for idx, token in enumerate(tokens):
            token = token.strip()
            if len(token) == 0:
                logger.debug(f"skip empty field @{idx}")
                continue

            if idx == 0:  # Serial Number
                try:
                    cur.meta.sn = token
                except ValueError:
                    logger.warning("issue in casting the serial number: %s" % token)

            elif idx == 1:  # Data Number
                logger.debug(f"skip unused Data Number field @{idx}")

            elif idx == 2:  # Date
                try:
                    cur.meta.utc_time = dt.datetime.strptime(token, "%Y%m%d")
                except ValueError:
                    logger.warning("issue in retrieving the date format: %s" % token)

            elif idx == 3:  # Time
                if cur.meta.utc_time:
                    try:
                        hour, minute, second = int(token[:2]), int(token[2:4]), int(token[4:6])
                        cur.meta.utc_time += dt.timedelta(seconds=second, minutes=minute, hours=hour)
                    except ValueError:
                        logger.warning("issue in retrieving the time format: %s" % token)

            elif idx == 4:  # Latitude
                try:
                    lat_deg = int(token[0:2])
                    lat_min = float(token[3:10])
                    cur.meta.latitude = lat_deg + lat_min / 60.
                    lat_dir = token[10]
                    if lat_dir == 'S':
                        cur.meta.latitude *= -1
                except ValueError:
                    logger.warning("issue in retrieving the latitude: %s" % token)

            elif idx == 5:  # Longitude
                try:
                    lat_deg = int(token[0:3])
                    lat_min = float(token[4:11])
                    cur.meta.longitude = lat_deg + lat_min / 60.
                    lat_dir = token[11]
                    if lat_dir == 'W':
                        cur.meta.longitude *= -1
                except ValueError:
                    logger.warning("issue in retrieving the longitude: %s" % token)

            elif idx == 6:  # Probe Type
                try:
                    cur.meta.probe_type = self.probe_type_dict[token]
                    cur.meta.sensor_type = self.sensor_type_dict[token]
                except (IndexError, KeyError):
                    cur.meta.probe_type = Dicts.probe_types['Unknown']
                    cur.meta.sensor_type = Dicts.sensor_types['Unknown']
                    logger.warning(f"issue in retrieving probe type @{idx}: {token}")

            elif idx == 7:  # Count of Data
                try:
                    nr_samples = int(token)
                    logger.debug(f"count of data: {nr_samples}")
                except ValueError:
                    logger.warning(f"issue in retrieving count of data @{idx}: {token}")

            elif idx > 7:
                break

        if not cur.meta.original_path and self.fid:
            cur.meta.original_path = self.fid.path

        # # initialize data sample fields
        cur.init_data(nr_samples)

    def _parse_body(self):
        logger.debug('parsing body')

        ssp = self.ssp
        if ssp is None:
            raise RuntimeError('no ssp found')
        cur = ssp.cur
        if cur is None:
            raise RuntimeError('no cur ssp found')

        count = 0
        for idx, line in enumerate(self.lines[self.samples_offset:]):

            # skip empty lines
            if len(line.split()) == 0:
                continue

            # first required data fields
            try:
                if cur.meta.probe_type in self.supported_xbt_probes:
                    good_data = self._body_xbt(line, count)
                elif cur.meta.probe_type in self.supported_xctd_probes:
                    good_data = self._body_xctd(line, count)
                elif cur.meta.probe_type in self.supported_axctd_probes:
                    good_data = self._body_axctd(line, count)
                else:
                    raise RuntimeError(f"unsupported probe type: {cur.meta.probe_type}")

            except ValueError:
                logger.warning("invalid conversion parsing of line #%s: %s" % (self.samples_offset + idx, line))
                continue
            except IndexError:
                logger.warning("invalid index parsing of line #%s: %s" % (self.samples_offset + idx, line))
                continue

            if good_data:
                count += 1

        logger.debug(f"good data samples: {count}")
        cur.data_resize(count)

    def _body_xbt(self, line: str, count: int) -> bool:

        fields = line.split(",")

        if len(fields) < 3:
            logger.warning("too few fields for: %s" % line)
            return False

        if len(fields) > 3:
            logger.warning("too main fields for: %s" % line)
            return False

        ssp = self.ssp
        if ssp is None:
            raise RuntimeError('no ssp found')
        cur = ssp.cur
        if cur is None:
            raise RuntimeError('no cur ssp found')

        for jdx, field in enumerate(fields):
            if jdx == 0:
                cur.data.depth[count] = float(field)
            elif jdx == 1:
                cur.data.temp[count] = float(field)
            else:
                continue

        return True

    def _body_xctd(self, line: str, count: int) -> bool:

        fields = line.split(",")

        if len(fields) < 7:
            logger.warning("too few fields for: %s" % line)
            return False

        if len(fields) > 7:
            logger.warning("too main fields for: %s" % line)
            return False

        ssp = self.ssp
        if ssp is None:
            raise RuntimeError('no ssp found')
        cur = ssp.cur
        if cur is None:
            raise RuntimeError('no cur ssp found')

        for jdx, field in enumerate(fields):
            if jdx == 0:
                cur.data.depth[count] = float(field)
            elif jdx == 1:
                cur.data.temp[count] = float(field)
            elif jdx == 2:
                cur.data.conductivity[count] = float(field) * 0.1
            elif jdx == 3:
                cur.data.sal[count] = float(field)
            elif jdx == 4:
                cur.data.speed[count] = float(field)
            else:
                continue

        return True

    def _body_axctd(self, line: str, count: int) -> bool:

        fields = line.split(",")

        if len(fields) < 7:
            logger.warning("too few fields for: %s" % line)
            return False

        if len(fields) > 7:
            logger.warning("too main fields for: %s" % line)
            return False

        ssp = self.ssp
        if ssp is None:
            raise RuntimeError('no ssp found')
        cur = ssp.cur
        if cur is None:
            raise RuntimeError('no cur ssp found')

        for jdx, field in enumerate(fields):
            field = field.strip()
            if jdx == 0:
                cur.data.depth[count] = float(field)
            elif jdx == 1:
                cur.data.temp[count] = float(field)
            elif jdx == 2:
                cur.data.conductivity[count] = float(field) * 0.1
            elif jdx == 3:
                cur.data.sal[count] = float(field)
            elif jdx == 4:
                cur.data.speed[count] = float(field)
            elif jdx == 6:
                cur.data.pressure[count] = float(field)
            else:
                continue

        return True
