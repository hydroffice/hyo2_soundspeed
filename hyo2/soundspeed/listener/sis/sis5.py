import socket
import operator
import logging
import functools
import time
import struct
from typing import Optional

from hyo2.soundspeed.listener.abstract import AbstractListener
from hyo2.soundspeed.formats import kmall

logger = logging.getLogger(__name__)


class Sis5(AbstractListener):
    """Kongsberg SIS5 listener"""

    def __init__(self, port: int, datagrams: list, timeout: int = 1, ip: str = "0.0.0.0",
                 target: Optional[object] = None, name: Optional[str] = "SIS5") -> None:
        super(Sis5, self).__init__(port=port, datagrams=datagrams, ip=ip, timeout=timeout,
                                   target=target, name=name)
        self.desc = "Kongsberg SIS5"

        # Datagram id
        self.id = None

        # Datagrams
        self.mrz = None
        self.spo = None
        self.svp = None

    def __repr__(self) -> str:
        msg = "%s" % super(Sis5, self).__repr__()
        # msg += "  <has data loaded: %s>\n" % self.has_data_loaded
        return msg

    @classmethod
    def request_cur_profile(cls, ip: str, port: int = 14002) -> None:
        logger.info("Requesting profile from %s:%s" % (ip, port))

        # sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #
        # # We try all of them in the hopes that one works.
        # sensors = ["710", "122", "302", "3020", "2040"]
        # for sensor in sensors:
        #     # talker ID, Roger Davis (HMRG) suggested SM based on something KM told him
        #     output = '$SMR20,EMX=%s,' % sensor
        #
        #     # calculate checksum, XOR of all bytes after the $
        #     checksum = functools.reduce(operator.xor, map(ord, output[1:len(output)]))
        #
        #     # append the checksum and end of datagram identifier
        #     output += "*{0:02x}".format(checksum)
        #     output += "\\\r\n"
        #
        #     sock_out.sendto(output.encode('utf-8'), (ip, port))
        #
        #     # Adding a bit of a pause
        #     time.sleep(0.5)
        #
        # sock_out.close()

        raise RuntimeError("Not implemented")

    def parse(self) -> None:
        self._parse_sis_5()

    def _parse_sis_5(self) -> None:
        this_data = self.data[:]
        # logger.debug("SIS 5: %s" % this_data)

        self.id = b''.join(struct.unpack("<I4c", this_data[:8])[1:5])
        try:
            name = kmall.Kmall.datagrams[self.id]
        except KeyError:
            name = "Unknown name"

        if self.id not in self.datagrams:
            return

        logger.info("%s > DG %s [%s] > sz: %.2f KB"
                    % (self.sender, self.id, name, len(this_data) / 1024))

        if self.id == b'#MRZ':
            self.mrz = kmall.KmallMRZ(this_data)

        elif self.id == b'#SPO':
            self.spo = kmall.KmallSPO(this_data)

        elif self.id == b'#SVP':
            self.svp = kmall.KmallSVP(this_data)

        else:
            logger.error("Missing parser for datagram type: %s" % self.id)
