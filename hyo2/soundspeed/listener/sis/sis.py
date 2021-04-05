import logging
import struct
from typing import Optional

from hyo2.soundspeed.listener.abstract import AbstractListener
from hyo2.soundspeed.formats import km, kmall

logger = logging.getLogger(__name__)


class Sis(AbstractListener):
    """Kongsberg SIS listener"""

    class Sis4:
        def __init__(self):
            self.datagrams = [0x50, 0x52, 0x55, 0x58]
            self.surface_ssp = None  # Type: Optional[km.KmSsp]
            self.surface_ssp_count = 0
            self.nav = None  # Type: Optional[km.KmNav]
            self.nav_count = 0
            self.installation = None  # Type: Optional[km.KmInstallation]
            self.installation_count = 0
            self.runtime = None  # Type: Optional[km.KmRuntime]
            self.runtime_count = 0
            self.ssp = None  # Type: Optional[km.KmSvp]
            self.ssp_count = 0
            self.svp_input = None  # Type: Optional[km.KmSvpInput]
            self.svp_input_count = 0
            self.xyz88 = None  # Type: Optional[km.KmXyz88]
            self.xyz88_count = 0
            self.range_angle78 = None  # Type: Optional[km.KmRangeAngle78]
            self.range_angle78_count = 0
            self.seabed_image89 = None  # Type: Optional[km.KmSeabedImage89]
            self.seabed_image89_count = 0
            self.watercolumn = None  # Type: Optional[km.KmWatercolumn]
            self.watercolumn_count = 0
            self.bist = None  # Type: Optional[km.KmBist]
            self.bist_count = 0

    class Sis5:
        def __init__(self):
            self.datagrams = [b'#MRZ', b'#SPO', b'#SVP']
            self.mrz = None  # Type: Optional[kmall.KmallMRZ]
            self.mrz_count = 0
            self.spo = None  # Type: Optional[kmall.KmallSPO]
            self.spo_count = 0
            self.svp = None  # Type: Optional[kmall.KmallSVP]
            self.svp_count = 0

    def __init__(self, port: int, timeout: int = 1, ip: str = "0.0.0.0",
                 target: Optional[object] = None, name: str = "SIS",
                 use_sis5: bool = False, debug: bool = False):
        super().__init__(port=port, ip=ip, timeout=timeout, target=target, name=name, debug=debug)
        self.use_sis5 = use_sis5
        self.desc = name

        self.sis4 = Sis.Sis4()
        self.sis5 = Sis.Sis5()

        self.cur_id = None

    def parse(self):
        if self.use_sis5:
            self.sis4 = Sis.Sis4()
            self._parse_sis5()
        else:
            self.sis5 = Sis.Sis5()
            self._parse_sis4()

    def _parse_sis4(self) -> None:
        this_data = self.data[:]

        self.cur_id = struct.unpack("<BB", this_data[0:2])[1]
        try:
            name = km.Km.datagrams[self.cur_id]
        except KeyError:
            name = "Unknown name"

        if self.debug:
            logger.debug("Received %s(0x%x/%c/%s)" % (self.cur_id, self.cur_id, self.cur_id, name))

        if self.cur_id not in self.sis4.datagrams:
            if self.debug:
                logger.debug("Ignoring received datagram")
            return

        if self.cur_id == 0x42:
            self.sis4.bist = km.KmBist(this_data)
            self.sis4.bist_count += 1
            if self.debug:
                logger.debug("Parsed")

        elif self.cur_id == 0x47:
            self.sis4.surface_ssp = km.KmSsp(this_data)
            self.sis4.surface_ssp_count += 1
            if self.debug:
                logger.debug("Parsed")

        elif self.cur_id == 0x49:
            self.sis4.installation = km.KmInstallation(this_data)
            self.sis4.installation_count += 1
            if self.debug:
                logger.debug("Parsed")

        elif self.cur_id == 0x4e:
            self.sis4.range_angle78 = km.KmRangeAngle78(this_data)
            self.sis4.range_angle78_count += 1
            if self.debug:
                logger.debug("Parsed")

        elif self.cur_id == 0x50:
            self.sis4.nav = km.KmNav(this_data)
            self.sis4.nav_count += 1
            if self.debug:
                logger.debug("Parsed")

        elif self.cur_id == 0x52:
            self.sis4.runtime = km.KmRuntime(this_data)
            self.sis4.runtime_count += 1
            if self.debug:
                logger.debug("Parsed")

        elif self.cur_id == 0x55:
            self.sis4.ssp = km.KmSvp(this_data)
            self.sis4.ssp_count += 1
            if self.debug:
                logger.debug("Parsed")

        elif self.cur_id == 0x57:
            self.sis4.svp_input = km.KmSvpInput(this_data)
            self.sis4.svp_input_count += 1
            if self.debug:
                logger.debug("Parsed")

        elif self.cur_id == 0x58:
            self.sis4.xyz88 = km.KmXyz88(this_data)
            self.sis4.xyz88_count += 1
            if self.debug:
                logger.debug("Parsed")

        elif self.cur_id == 0x59:
            self.sis4.seabed_image89 = km.KmSeabedImage89(this_data)
            self.sis4.seabed_image89_count += 1
            if self.debug:
                logger.debug("Parsed")

        elif self.cur_id == 0x6b:
            self.sis4.watercolumn = km.KmWatercolumn(this_data)
            self.sis4.watercolumn_count += 1
            if self.debug:
                logger.debug("Parsed")

        else:
            logger.error("Missing parser for datagram type: %s" % self.cur_id)

    def _parse_sis5(self) -> None:
        this_data = self.data[:]

        self.cur_id = b''.join(struct.unpack("<I4c", this_data[:8])[1:5])
        try:
            name = kmall.Kmall.datagrams[self.cur_id]
        except KeyError:
            name = "Unknown name"

        if self.debug:
            logger.debug("Received %s(%s)" % (self.cur_id, name))

        if self.cur_id not in self.sis5.datagrams:
            if self.debug:
                logger.debug("Ignoring received datagram")
            return

        if self.cur_id == b'#MRZ':
            partition = struct.unpack("<2H", this_data[20:24])
            nr_of_datagrams = partition[0]
            datagram_nr = partition[1]
            if datagram_nr == 1:
                self.sis5.mrz = kmall.KmallMRZ(this_data, self.debug)
                self.sis5.mrz_count += 1
                if self.debug:
                    logger.info("%d/%d -> Parsed" % (datagram_nr, nr_of_datagrams))
            else:
                if self.debug:
                    logger.info("%d/%d -> Ignored" % (datagram_nr, nr_of_datagrams))

        elif self.cur_id == b'#SPO':
            self.sis5.spo = kmall.KmallSPO(this_data, self.debug)
            self.sis5.spo_count += 1
            if self.debug:
                logger.debug("Parsed")

        elif self.cur_id == b'#SVP':
            self.sis5.svp = kmall.KmallSVP(this_data, self.debug)
            self.sis5.svp_count += 1
            if self.debug:
                logger.debug("Parsed")

        else:
            logger.error("Missing parser for datagram type: %s" % self.cur_id)

    def info(self) -> str:
        msg = "Received datagrams:\n"
        if self.use_sis5:
            msg += "- MRZ: %d\n" % self.sis5.mrz_count
            msg += "- SPO: %d\n" % self.sis5.spo_count
            msg += "- SVP: %d\n" % self.sis5.svp_count
        else:
            msg += "- Nav: %d\n" % self.sis4.nav_count
            msg += "- Xyz: %d\n" % self.sis4.xyz88_count
            msg += "- Ssp: %d\n" % self.sis4.ssp_count
            msg += "- Runtime: %d\n" % self.sis4.runtime_count
        return msg
