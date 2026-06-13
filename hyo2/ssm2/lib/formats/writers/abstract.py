import logging
import os
from abc import ABCMeta, abstractmethod

# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.base.files import FileManager
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.formats.abstract import AbstractFormat
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.profile.profilelist import ProfileList

logger = logging.getLogger(__name__)


class AbstractWriter(AbstractFormat, metaclass=ABCMeta):
    """ Abstract data writer """

    def __repr__(self) -> str:
        return "<%s:writer:%s:%s>" % (self.name, self.version, ",".join(self._ext))

    def __init__(self) -> None:
        super(AbstractWriter, self).__init__()
        self.fod: FileManager | None = None

    @abstractmethod
    def write(self, ssp: ProfileList, data_path: str, data_file: str | None = None, project: str = '') -> bool:
        pass

    @abstractmethod
    def _write_header(self) -> str:
        pass

    @abstractmethod
    def _write_body(self) -> None:
        pass

    def finalize(self) -> None:
        if self.fod:
            if not self.fod.io.closed:
                self.fod.io.close()


class AbstractTextWriter(AbstractWriter, metaclass=ABCMeta):
    """ Abstract text data writer """

    def __init__(self) -> None:
        super(AbstractTextWriter, self).__init__()

    def _write(self, data_path: str, data_file: str | None, encoding='utf8', append=False, binary=False):
        """Helper function to write the raw file"""

        if not os.path.exists(data_path):
            os.makedirs(data_path)

        if data_file is not None:

            if len(data_file.split('.')) == 1:
                data_file += (".%s" % (list(self.ext)[0],))

            file_path = os.path.join(data_path, data_file)

        else:
            ssp = self.ssp
            if ssp is None:
                raise RuntimeError('Profile not set')
            if ssp.cur.meta.original_path:
                data_file: str = "%s.%s" % (os.path.basename(ssp.cur.meta.original_path), list(self.ext)[0])
            else:
                data_file: str = 'output.%s' % (list(self.ext)[0],)

            file_path: str = str(os.path.join(data_path, data_file))

        logger.info("output file: %s" % file_path)

        if append:
            mode = 'a'
        else:
            mode = 'w'
        if binary:
            mode = '%sb' % mode
        self.fod = FileManager(data_path=file_path, mode=mode, encoding=encoding)
