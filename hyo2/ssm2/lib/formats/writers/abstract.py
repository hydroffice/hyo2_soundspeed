from abc import ABCMeta, abstractmethod  # , abstractproperty
import os
import logging

logger = logging.getLogger(__name__)

from hyo2.ssm2.lib.base.files import FileManager
from hyo2.ssm2.lib.formats.abstract import AbstractFormat


class AbstractWriter(AbstractFormat, metaclass=ABCMeta):
    """ Abstract data writer """

    def __repr__(self):
        return "<%s:writer:%s:%s>" % (self.name, self.version, ",".join(self._ext))

    def __init__(self):
        super(AbstractWriter, self).__init__()
        self.fod = None

    @abstractmethod
    def write(self, ssp, data_path, data_file=None, project=''):
        pass

    @abstractmethod
    def _write_header(self):
        pass

    @abstractmethod
    def _write_body(self):
        pass

    def finalize(self):
        if self.fod:
            if not self.fod.io.closed:
                self.fod.io.close()


class AbstractTextWriter(AbstractWriter, metaclass=ABCMeta):
    """ Abstract text data writer """

    def __init__(self):
        super(AbstractTextWriter, self).__init__()

    def _write(self, data_path, data_file, encoding='utf8', append=False, binary=False):
        """Helper function to write the raw file"""

        # data_path = os.path.join(data_path, self.name.lower())  # commented to avoid the creation of sub-folders
        if not os.path.exists(data_path):
            os.makedirs(data_path)

        if data_file:

            if len(data_file.split('.')) == 1:
                data_file += (".%s" % (list(self.ext)[0],))

            file_path = os.path.join(data_path, data_file)

        else:

            if self.ssp.cur.meta.original_path:
                data_file = "%s.%s" % (os.path.basename(self.ssp.cur.meta.original_path), list(self.ext)[0])
            else:
                data_file = 'output.%s' % (list(self.ext)[0],)

            file_path = os.path.join(data_path, data_file)

        logger.info("output file: %s" % file_path)

        if append:
            mode = 'a'
        else:
            mode = 'w'
        if binary:
            mode = '%sb' % mode
        self.fod = FileManager(file_path, mode=mode, encoding=encoding)
