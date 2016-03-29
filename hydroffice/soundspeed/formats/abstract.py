from __future__ import absolute_import, division, print_function, unicode_literals

from abc import ABCMeta, abstractmethod, abstractproperty
import logging

logger = logging.getLogger(__name__)

from ..helper import FileInfo


class AbstractFormat(object):
    """ Common abstract data format """

    __metaclass__ = ABCMeta

    def __init__(self):
        self.name = self.__class__.__name__
        self.version = "0.1.0"
        self._data = None

    @property
    def data(self):
        return self._data


class AbstractReader(AbstractFormat):
    """ Abstract data reader """

    __metaclass__ = ABCMeta

    def __init__(self):
        super(AbstractReader, self).__init__()
        self.fid = None

    def __repr__(self):
        return "<%s:reader:%s>" % (self.name, self.version)

    def _read_asci(self, data_path):
        self.fid = FileInfo(data_path, 'r')

    def _read_binary(self, data_path):
        self.fid = FileInfo(data_path, 'rb')


class AbstractWriter(AbstractFormat):
    """ Abstract data writer """

    __metaclass__ = ABCMeta

    def __repr__(self):
        return "<%s:writer:%s>" % (self.name, self.version)

    def __init__(self):
        super(AbstractWriter, self).__init__()
        self.fod = None

    def _write_asci(self, data_path):
        self.fod = FileInfo(data_path, 'w')

    def _write_binary(self, data_path):
        self.fod = FileInfo(data_path, 'wb')
