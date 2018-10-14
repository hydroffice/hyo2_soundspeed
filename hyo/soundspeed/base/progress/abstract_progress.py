from abc import ABCMeta, abstractmethod, abstractproperty
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AbstractProgress(metaclass=ABCMeta):
    """Abstract class for a progress bar"""

    def __init__(self):

        self._title = str()
        self._text = str()

        self._min = 0
        self._max = 100
        self._range = self._max - self._min
        self._value = 0

        self._is_disabled = False
        self._is_canceled = False

    @property
    def value(self) -> float:
        return self._value

    @property
    def min(self) -> float:
        return self._min

    @property
    def max(self) -> float:
        return self._max

    @property
    def range(self) -> float:
        self._range = self._max - self._min
        return self._range

    @property
    @abstractmethod
    def canceled(self) -> bool:
        pass

    @abstractmethod
    def start(self, title: str="Progress", text: str="Processing",
              min_value: float=0.0, max_value: float=100.0,
              has_abortion: bool=False, is_disabled: bool=False) -> None:
        pass

    @abstractmethod
    def update(self, value: Optional[float]=None, text: Optional[str]=None) -> None:
        pass

    @abstractmethod
    def add(self, quantum: float, text: Optional[str]=None) -> None:
        pass

    @abstractmethod
    def end(self, text: Optional[str]=None) -> None:
        pass
