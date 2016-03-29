from __future__ import absolute_import, division, print_function, unicode_literals

from abc import ABCMeta, abstractmethod, abstractproperty
import logging

logger = logging.getLogger(__name__)

from ..helper import FileManager
from ..profile.profile import Profile


class AbstractFormat(object):
    """ Common abstract data format """

    __metaclass__ = ABCMeta

    def __init__(self):
        self.name = self.__class__.__name__
        self.version = "0.1.0"
        self._data = None
        self._ext = set()

    @property
    def ssp(self):
        return self._ssp

    @property
    def driver(self):
        return "%s.%s" % (self.name, self.version)

    def init_data(self):
        """Create a new empty profile"""
        self._ssp = Profile()


class AbstractReader(AbstractFormat):
    """ Abstract data reader """

    __metaclass__ = ABCMeta

    def __init__(self):
        super(AbstractReader, self).__init__()
        self.fid = None

    def __repr__(self):
        return "<%s:reader:%s:%s>" % (self.name, self.version, ",".join(self._ext))

    @abstractmethod
    def read(self, data_path):
        pass

    @abstractmethod
    def _parse_header(self):
        pass

    @abstractmethod
    def _parse_body(self):
        pass


class AbstractTextReader(AbstractReader):
    """ Abstract text data reader """

    __metaclass__ = ABCMeta

    def __init__(self):
        super(AbstractTextReader, self).__init__()
        self.lines = []
        self.lines_offset = None

    def _read(self, data_path):
        self.fid = FileManager(data_path, 'r')
        self.lines = self.fid.io.readlines()
        self.samples_offset = 0
        self.field_index = dict()
        self.more_fields = list()


class AbstractBinaryReader(AbstractReader):
    """ Abstract binary data reader """

    __metaclass__ = ABCMeta

    def __init__(self):
        super(AbstractBinaryReader, self).__init__()

    def _read(self, data_path):
        self.fid = FileManager(data_path, 'rb')


class AbstractWriter(AbstractFormat):
    """ Abstract data writer """

    __metaclass__ = ABCMeta

    def __repr__(self):
        return "<%s:writer:%s:%s>" % (self.name, self.version, ",".join(self._ext))

    def __init__(self):
        super(AbstractWriter, self).__init__()
        self.fod = None

    def _write_text(self, data_path):
        self.fod = FileManager(data_path, 'w')

    def _write_binary(self, data_path):
        self.fod = FileManager(data_path, 'wb')
