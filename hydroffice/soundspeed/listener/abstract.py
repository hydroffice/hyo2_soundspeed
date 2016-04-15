from __future__ import absolute_import, division, print_function, unicode_literals

from abc import ABCMeta, abstractmethod, abstractproperty
import os
import logging

logger = logging.getLogger(__name__)


class AbstractListener(object):
    """Common abstract listener"""

    __metaclass__ = ABCMeta

    def __init__(self, prj):
        self.name = self.__class__.__name__
        self.desc = "Abstract listener"  # a human-readable description
        self.prj = prj

    # @abstractmethod
    # def is_present(self):
    #     pass

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__
        msg += "  <desc: %s>\n" % self.desc
        return msg
