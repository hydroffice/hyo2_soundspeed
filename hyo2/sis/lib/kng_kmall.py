from datetime import datetime, timedelta
import enum
import logging
import struct
from typing.io import BinaryIO

logger = logging.getLogger(__name__)


class KngKmall:
    class Flags(enum.Enum):
        VALID = 0
        UNEXPECTED_EOF = 1
        CORRUPTED_END_DATAGRAM = 2

    kmall_datagrams = {
        b'#IIP': 'Installation parameters and sensor setup',
        b'#IOP': 'Runtime parameters as chosen by operator',
        b'#IBE': 'Built in test (BIST) error report',
        b'#IBR': 'Built in test (BIST) reply',
        b'#IBS': 'Built in test (BIST) short reply',

        b'#MRZ': 'Multibeam (M) raw range (R) and depth(Z) datagram',
        b'#MWC': 'Multibeam (M) water (W) column (C) datagram',

        b'#SPO': 'Sensor (S) data for position (PO)',
        b'#SKM': 'Sensor (S) KM binary sensor format',
        b'#SVP': 'Sensor (S) data from sound velocity (V) profile (P) or CTD',
        b'#SVT': 'Sensor (S) data for sound velocity (V) at transducer (T)',
        b'#SCL': 'Sensor (S) data from clock (CL)',
        b'#SDE': 'Sensor (S) data from depth (DE) sensor',
        b'#SHI': 'Sensor (S) data for height (HI)',

        b'#CPO': 'Compatibility (C) data for position (PO)',
        b'#CHE': 'Compatibility (C) data for heave (HE)',
    }

    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose
        self.length = None
        self.type = None
        self.version = None
        self.system_id = None
        self.sounder_id = None
        self.time_sec = None
        self.time_microsec = None
        self.datetime = None

    def read(self, file_input: BinaryIO, file_size:int) -> Flags:
        """populate header data"""

        first_dg = (file_input.tell() == 0)
        chunk = file_input.read(20)
        hdr_data = struct.unpack("<I4cBBHII", chunk)

        self.length = hdr_data[0]
        # logger.debug('length: %s' % self.length)
        self.type = b''.join(hdr_data[1:5])
        # logger.debug('type: %s -> %s' % (self.type, self.kmall_datagrams[self.type]))
        self.version = hdr_data[5]
        # logger.debug('version: %s' % self.version)
        self.system_id = hdr_data[6]
        # logger.debug('system id: %s' % self.system_id)
        self.sounder_id = hdr_data[7]
        # logger.debug('sounder id: %s' % self.sounder_id)
        self.time_sec = hdr_data[8]
        # logger.debug('time sec: %s' % self.time_sec)
        self.time_microsec = hdr_data[9]
        # logger.debug('time microsec: %s' % self.time_microsec)
        self.datetime = datetime.utcfromtimestamp(
            self.time_sec) + timedelta(microseconds=(self.time_microsec * 10e-3))
        # logger.debug('datetime: %s' % self.datetime.strftime('%Y-%m-%d %H:%M:%S.%f'))

        # Make sure we don't try to read beyond the EOF (-13 since 16 for header and 3 for ender)
        if (file_input.tell() + (self.length - 20)) > file_size:
            if self.verbose:
                logging.warning("unexpected EOF > current pos: %s, datagram length: %s, file size: %s"
                                % (file_input.tell(), self.length, file_size))
            return self.Flags.UNEXPECTED_EOF

        # move file cursor to almost the end of the datagram (just minus the length field)
        file_input.seek(self.length - 24, 1)  # 1 -> current file position

        chunk = file_input.read(4)
        footer_length = struct.unpack("<I", chunk)[0]
        if self.length != footer_length:
            logging.warning("mismatch between initial and end datagram length: %s != %s"
                            % (self.length, footer_length))
            return self.Flags.CORRUPTED_END_DATAGRAM

        return self.Flags.VALID
