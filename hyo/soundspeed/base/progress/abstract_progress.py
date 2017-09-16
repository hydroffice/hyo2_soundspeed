from abc import ABCMeta, abstractmethod, abstractproperty
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
    def value(self):
        return self._value

    @property
    def min(self):
        return self._min

    @property
    def max(self):
        return self._max

    @property
    def range(self):
        self._range = self._max - self._min
        return self._range

    @property
    @abstractmethod
    def canceled(self):
        pass

    @abstractmethod
    def start(self, title="Progress", text="Processing", min_value=0, max_value=100,
              has_abortion=False, is_disabled=False):
        pass

    @abstractmethod
    def update(self, value=None, text=None):
        pass

    @abstractmethod
    def add(self, quantum, text=None):
        pass

    @abstractmethod
    def end(self):
        pass
