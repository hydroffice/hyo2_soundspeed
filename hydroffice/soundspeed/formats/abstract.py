from __future__ import absolute_import, division, print_function, unicode_literals

from abc import ABCMeta, abstractmethod, abstractproperty
import logging

logger = logging.getLogger(__name__)

from ..profile.profilelist import ProfileList


class AbstractFormat(object):
    """ Common abstract data format """

    __metaclass__ = ABCMeta

    def __init__(self):
        self.name = self.__class__.__name__
        self.desc = "Abstract Format"  # a human-readable description
        self.version = "0.1.0"
        self._ssp = None  # profile list
        self._ext = set()
        self.multicast_support = False

        self.s = None  # settings
        self.cb = None  # callbacks

    @property
    def ssp(self):
        return self._ssp

    @ssp.setter
    def ssp(self, value):
        self._ssp = value

    @property
    def ext(self):
        return self._ext

    @property
    def driver(self):
        return "%s.%s" % (self.name, self.version)

    def init_data(self):
        """Create a new empty profile list"""
        self._ssp = ProfileList()
