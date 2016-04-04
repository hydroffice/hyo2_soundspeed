from __future__ import absolute_import, division, print_function, unicode_literals

from abc import ABCMeta, abstractmethod, abstractproperty
import os
import logging

logger = logging.getLogger(__name__)

from ...base.helper import FileManager
from ...profile.dicts import Dicts
from ..abstract import AbstractFormat


class AbstractReader(AbstractFormat):
    """ Abstract data reader """

    __metaclass__ = ABCMeta

    def __init__(self):
        super(AbstractReader, self).__init__()
        self.fid = None
        self.up_or_down = None

    def __repr__(self):
        return "<%s:reader:%s:%s>" % (self.name, self.version, ",".join(self.ext))

    @abstractmethod
    def read(self, data_path, up_or_down=Dicts.ssp_directions['down']):
        """Common read function signature

        The up_or_down is used to select the samples related to only the down- or up- cast.
        """
        pass

    @abstractmethod
    def _parse_header(self):
        pass

    @abstractmethod
    def _parse_body(self):
        pass

    def finalize(self):
        """Function called after the parsing is done, to finalize the reading"""
        self.ssp.cur.clone_data_to_proc()


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
