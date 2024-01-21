import logging
from abc import ABCMeta, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)


class Nmea0183NavAbstract(metaclass=ABCMeta):

    def __init__(self, data: str) -> None:
        self.data = data
        self.msg = None  # type: Optional[list[str]]

        self._latitude = None  # type: Optional[float]
        self._longitude = None  # type: Optional[float]

        self.msg = self.data.split(',')

        self._parse()

    @abstractmethod
    def _parse(self) -> None:
        pass

    @property
    def latitude(self) -> Optional[float]:
        return self._latitude

    @property
    def longitude(self) -> Optional[float]:
        return self._longitude

    def __str__(self) -> str:
        return "Latitude: %s, longitude: %s" % (self._latitude, self._longitude)
