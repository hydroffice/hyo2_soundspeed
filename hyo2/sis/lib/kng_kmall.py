import enum
import struct
from typing.io import BinaryIO


class KngKmall:
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

    def read(self, datagram: BinaryIO, file_size:int) -> Flags:
        """populate header data"""

        chunk = datagram[0:20]
        hdr_data = struct.unpack("<I4BBBHII", chunk)
        self.length = hdr_data[0]

        return self.Flags.VALID
