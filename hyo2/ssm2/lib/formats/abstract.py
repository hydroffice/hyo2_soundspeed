import logging
from abc import ABCMeta
from typing import Optional, Set, TYPE_CHECKING

from hyo2.ssm2.lib.profile.profilelist import ProfileList

if TYPE_CHECKING:
    from hyo2.ssm2.lib.base.callbacks.abstract_callbacks import AbstractCallbacks
    from hyo2.ssm2.lib.base.setup import Setup

logger = logging.getLogger(__name__)


class AbstractFormat(metaclass=ABCMeta):
    """ Common abstract data format """

    def __init__(self):
        self.name = self.__class__.__name__.lower()
        self.desc = "Abstract Format"  # a human-readable description
        self.version = "0.1.0"
        self._ssp: ProfileList | None = None
        self._ext = set()
        self._project = str()
        self.multicast_support = False

        self.s: Setup | None = None
        self.cb: AbstractCallbacks | None = None

    @property
    def ssp(self) -> Optional[ProfileList]:
        return self._ssp

    @ssp.setter
    def ssp(self, value: ProfileList):
        self._ssp = value

    @property
    def ext(self) -> Set[str]:
        return self._ext

    @property
    def driver(self) -> str:
        return "%s.%s" % (self.name, self.version)

    def init_data(self) -> None:
        """Create a new empty profile list"""
        self._ssp = ProfileList()
