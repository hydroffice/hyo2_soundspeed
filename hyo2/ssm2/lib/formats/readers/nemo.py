import datetime as dt
import logging
import math

from hyo2.ssm2.lib.base.callbacks.cli_callbacks import CliCallbacks
from hyo2.ssm2.lib.formats.readers.abstract import AbstractTextReader
from hyo2.ssm2.lib.profile.dicts import Dicts

logger = logging.getLogger(__name__)


class NEMO(AbstractTextReader):
    """NEMO CTD reader -> CTD style"""

    def __init__(self):
        super().__init__()
        self.desc = "NEMO"
        self.ext.add("csv")

        # body tokens
        self.tk_pressure = "depth (dbar)"  # Despite the name, these are pressure values.
        self.tk_temp = "temperature (°C)"
        self.tk_sal = "salinity (PSU)"
        self.tk_speed = "sound speed (m/s)"
        self.tk_density = "density (kg/m³)"
        self.tk_timestamp = "timestamp"

    def read(self, data_path, settings, callbacks=CliCallbacks(), progress=None):
        logger.debug("*** %s ***: start", self.driver)

        self.s = settings
        self.cb = callbacks

        self.init_data()  # create a new empty profile list
        self.ssp.append()  # append a new profile

        self.ssp.cur.meta.sensor_type = Dicts.sensor_types["CTD"]
        self.ssp.cur.meta.probe_type = Dicts.probe_types['NEMO']

        self._read(data_path=data_path)
        self._parse_header()
        self._parse_body()

        self.fix()
        self.finalize()

        logger.debug("*** %s ***: done", self.driver)
        return True

    @staticmethod
    def _utc_datetime(value):
        parsed = dt.datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("NEMO timestamps must include a UTC offset")
        return parsed.astimezone(dt.timezone.utc).replace(tzinfo=None)

    def _parse_header(self):
        """Parsing header: field header, serial number, timestamp, latitude, longitude"""
        logger.debug("parsing  header")

        metadata = {}
        self.samples_offset = 0

        required = (self.tk_pressure, self.tk_temp, self.tk_sal, self.tk_speed)
        for index, raw_line in enumerate(self.lines):
            line = raw_line.strip().lstrip("\ufeff")
            if not line: # skip empty lines
                continue

            if line.startswith("#"):
                if ":" in line:
                    key, value = line[1:].split(":", 1)
                    metadata[key.strip().lower()] = value.strip()
                continue

            fields = [field.strip() for field in line.split(",")]
            self.field_index = {field: col for col, field in enumerate(fields)}
            missing = [field for field in required if field not in self.field_index]
            if missing:
                raise RuntimeError("Missing NEMO CSV fields: %s" % ", ".join(missing))
            self.samples_offset = index + 1
            break
        else:
            raise RuntimeError("Missing NEMO CSV column header")

        self.ssp.cur.meta.sn = metadata.get("serial number", "")
        if "timestamp" in metadata:
            self.ssp.cur.meta.utc_time = self._utc_datetime(metadata["timestamp"])
        if "latitude" in metadata:
            self.ssp.cur.meta.latitude = float(metadata["latitude"])
        if "longitude" in metadata:
            self.ssp.cur.meta.longitude = float(metadata["longitude"])
        if not self.ssp.cur.meta.original_path:
            self.ssp.cur.meta.original_path = self.fid.path

        # Keep density as an additional numeric field; row timestamps are not numeric.
        self.more_fields = [self.tk_density] if self.tk_density in self.field_index else []
        self.ssp.cur.init_data(len(self.lines) - self.samples_offset)
        self.ssp.cur.init_more(self.more_fields)

    def _parse_body(self):
        """Parsing samples: pressure, temp, salinity, density, speed"""
        logger.debug('parsing body')

        count = 0
        for line_number, raw_line in enumerate(self.lines[self.samples_offset:], self.samples_offset + 1):
            line = raw_line.strip()
            # skip empty lines
            if not line or line.startswith("#"):
                continue

            data = [field.strip() for field in line.split(",")]
            # first required data fields
            try:
                pressure = float(data[self.field_index[self.tk_pressure]])
                temp = float(data[self.field_index[self.tk_temp]])
                sal = float(data[self.field_index[self.tk_sal]])
                speed = float(data[self.field_index[self.tk_speed]])
                if not all(map(math.isfinite, (pressure, temp, sal, speed))):
                    raise ValueError("non-finite sample")
            except (ValueError, IndexError) as exc:
                logger.warning("invalid NEMO sample on line %s: %s", line_number, exc)
                continue

            self.ssp.cur.data.pressure[count] = pressure
            self.ssp.cur.data.temp[count] = temp
            self.ssp.cur.data.sal[count] = sal
            self.ssp.cur.data.speed[count] = speed

            if self.more_fields:
                try:
                    self.ssp.cur.more.sa[self.tk_density][count] = float(data[self.field_index[self.tk_density]])
                except (ValueError, IndexError):
                    logger.debug("invalid NEMO density on line %s", line_number)
            count += 1

        if count == 0:
            raise RuntimeError("No valid NEMO samples found")

        if count < self.ssp.cur.data.num_samples:
            self.ssp.cur.data_resize(count)
