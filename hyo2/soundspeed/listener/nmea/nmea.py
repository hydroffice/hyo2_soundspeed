import logging
from datetime import datetime
from typing import Optional, Union

from hyo2.soundspeed.listener.abstract import AbstractListener
from hyo2.soundspeed.formats import nmea0183

logger = logging.getLogger(__name__)


class Nmea(AbstractListener):
    """NMEA listener"""

    def __init__(self, port: int, timeout: int = 1, ip: str = "0.0.0.0",
                 target: Optional[object] = None, name: str = "NMEA", debug: bool = False) -> None:
        super(Nmea, self).__init__(port=port, ip=ip, timeout=timeout, target=target, name=name, debug=debug)
        self.desc = name

        self.nav = None            # type: Union[nmea0183.Nmea0183GGA, nmea0183.Nmea0183GLL, None]
        self.nav_last_time = None  # type: Optional[datetime]
        
    @property
    def nav_latitude(self) -> Optional[float]:
        if self.nav is None:
            return None
        return self.nav.latitude

    @property
    def nav_longitude(self) -> Optional[float]:
        if self.nav is None:
            return None
        return self.nav.longitude            

    def parse(self) -> None:
        this_data = self.data[:].decode("utf-8")
        if self.debug:
            logger.debug("Received: %s)" % (this_data))

        sentence_type = this_data[3:6]

        if sentence_type == 'GGA':
            self.nav = nmea0183.Nmea0183GGA(this_data)
            self.nav_last_time = datetime.utcnow()

        elif sentence_type == 'GLL':
            self.nav = nmea0183.Nmea0183GLL(this_data)
            self.nav_last_time = datetime.utcnow()
        
    def __repr__(self):
        msg = "%s" % super(Nmea, self).__repr__()
        # msg += "  <has data loaded: %s>\n" % self.has_data_loaded
        return msg
