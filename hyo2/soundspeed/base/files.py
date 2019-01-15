import os
import logging
from typing import IO
# To use a consistent encoding
from codecs import open

logger = logging.getLogger(__name__)


class FileInfo:
    """A class that collects information on a passed file"""

    def __init__(self, data_path: str):
        self._path = os.path.abspath(data_path)
        self._basename = str(os.path.basename(self._path).split('.')[0])
        self._ext = str(os.path.basename(self._path).split('.')[-1])
        self._io = None

    @property
    def path(self) -> str:
        return self._path

    @property
    def basename(self) -> str:
        return self._basename

    @property
    def ext(self) -> str:
        return self._ext

    @property
    def io(self) -> IO:
        return self._io

    @io.setter
    def io(self, value: IO):
        self._io = value

    def __repr__(self):
        msg = "<%s:%s:%s>" % (self.__class__.__name__, self._basename, self._ext)

        return msg


class FileManager(FileInfo):
    def __init__(self, data_path: str, mode: str, encoding: str = 'utf-8'):
        """Open the passed file and store related info"""
        if (not os.path.exists(data_path)) and ((mode == 'r') or (mode == 'rb')):
            raise RuntimeError('the passed file does not exist: %s' % data_path)
        super(FileManager, self).__init__(data_path=data_path)
        self._append_exists = False
        if mode == 'a':
            self._append_exists = os.path.exists(data_path)
        self._io = open(self.path, mode=mode, encoding=encoding)

    @property
    def append_exists(self) -> bool:
        """Return if the file was existing before the appending operation"""
        return self._append_exists

    def close(self) -> None:
        if self._io is not None:
            self._io.close()
