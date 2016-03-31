from __future__ import absolute_import, division, print_function, unicode_literals

from abc import ABCMeta, abstractmethod, abstractproperty
import os
import logging

logger = logging.getLogger(__name__)

from ..helper import FileManager
from ..profile.profilelist import ProfileList


class AbstractFormat(object):
    """ Common abstract data format """

    __metaclass__ = ABCMeta

    def __init__(self):
        self.name = self.__class__.__name__
        self.version = "0.1.0"
        self._ssp = None  # profile list
        self._ext = set()

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


class AbstractReader(AbstractFormat):
    """ Abstract data reader """

    __metaclass__ = ABCMeta

    def __init__(self):
        super(AbstractReader, self).__init__()
        self.fid = None

    def __repr__(self):
        return "<%s:reader:%s:%s>" % (self.name, self.version, ",".join(self.ext))

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

    def _read(self, data_path, encoding='utf8'):
        """Helper function to read the raw file"""
        self.fid = FileManager(data_path, mode='r', encoding=encoding)
        try:
            self.lines = self.fid.io.readlines()
        except UnicodeDecodeError as e:
            if encoding == 'utf8':
                logger.info("changing encoding to latin: %s" % e)
                self.fid = FileManager(data_path, mode='r', encoding='latin')
                self.lines = self.fid.io.readlines()
            elif encoding == 'latin':
                logger.info("changing encoding to utf8: %s" % e)
                self.fid = FileManager(data_path, mode='r', encoding='utf8')
                self.lines = self.fid.io.readlines()
            else:
                raise e
        self.samples_offset = 0
        self.field_index = dict()
        self.more_fields = list()


class AbstractBinaryReader(AbstractReader):
    """ Abstract binary data reader """

    __metaclass__ = ABCMeta

    def __init__(self):
        super(AbstractBinaryReader, self).__init__()

    def _read(self, data_path):
        """Helper function to read the raw file"""
        self.fid = FileManager(data_path, mode='rb')


class AbstractWriter(AbstractFormat):
    """ Abstract data writer """

    __metaclass__ = ABCMeta

    def __repr__(self):
        return "<%s:writer:%s:%s>" % (self.name, self.version, ",".join(self._ext))

    def __init__(self):
        super(AbstractWriter, self).__init__()
        self.fod = None

    @abstractmethod
    def write(self, ssp, data_path, data_file=None):
        pass

    @abstractmethod
    def _write_header(self):
        pass

    @abstractmethod
    def _write_body(self):
        pass


class AbstractTextWriter(AbstractWriter):
    """ Abstract text data writer """

    __metaclass__ = ABCMeta

    def __init__(self):
        super(AbstractTextWriter, self).__init__()

    def _write(self, data_path, data_file, encoding='utf8'):
        """Helper function to write the raw file"""
        if data_file:
            file_path = os.path.join(data_path, data_file)
        else:
            if self.ssp.cur.meta.original_path:
                data_file = os.path.basename(self.ssp.cur.meta.original_path) + '.' + list(self.ext)[0]
            else:
                data_file = 'output.' + list(self.ext)[0]
            data_path = os.path.join(data_path, self.name.lower())
            if not os.path.exists(data_path):
                os.makedirs(data_path)
            file_path = os.path.join(data_path, data_file)
        logger.info("output file: %s" % file_path)
        self.fod = FileManager(file_path, mode='w', encoding=encoding)
