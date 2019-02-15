import enum
import logging
import struct
from typing.io import BinaryIO

logger = logging.getLogger(__name__)


class KngAll:
    class Flags(enum.Enum):
        VALID = 0
        MISSING_FIRST_STX = 1
        CORRUPTED_START_DATAGRAM = 2
        UNEXPECTED_EOF = 3
        CORRUPTED_END_DATAGRAM = 4

    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose
        self.length = None
        self.stx = None
        self.id = None
        self.model = None
        self.date = None
        self.time = None

        self.etx = None
        self.checksum = None

    def read(self, file_input: BinaryIO, file_size: int) -> Flags:
        """populate header data"""

        first_dg = (file_input.tell() == 0)
        chunk = file_input.read(16)
        hdr_data = struct.unpack("<IBBHII", chunk)

        self.length = hdr_data[0]
        self.stx = hdr_data[1]
        self.id = hdr_data[2]
        self.model = hdr_data[3]
        self.date = hdr_data[4]
        self.time = hdr_data[5]

        if first_dg and self.stx != 2:
            if self.verbose:
                logger.warning("invalid Kongberg file > STX: %s" % self.stx)
            return self.Flags.MISSING_FIRST_STX

        if (self.stx != 2) or (self.id == 0):
            if self.verbose:
                logger.warning("corrupted datagram")
            return self.Flags.CORRUPTED_START_DATAGRAM

        # try to read ETX

        # Make sure we don't try to read beyond the EOF (-13 since 16 for header and 3 for ender)
        if (file_input.tell() + (self.length - 13)) >= file_size:
            if self.verbose:
                logger.warning("unexpected EOF > current pos: %s, datagram length: %s, file size: %s"
                               % (file_input.tell(), self.length, file_size))
            return self.Flags.UNEXPECTED_EOF

        # move file cursor to the end of the datagram
        file_input.seek(self.length - 15, 1)

        chunk = file_input.read(3)
        footer_data = struct.unpack("<BH", chunk)
        self.etx = footer_data[0]
        self.checksum = footer_data[1]

        if self.etx != 3:
            # print 'ETX not found, trying next datagram at position',file.tell()-(length+3)

            return self.Flags.CORRUPTED_END_DATAGRAM

        return self.Flags.VALID
