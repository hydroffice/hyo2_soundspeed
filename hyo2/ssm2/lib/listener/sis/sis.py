import functools
import logging
import operator
import socket
import struct
import time
import traceback
from datetime import datetime
from typing import Optional, Union

from hyo2.ssm2.lib.listener.abstract import AbstractListener
from hyo2.ssm2.lib.formats import km, kmall
from hyo2.ssm2.lib.profile.profilelist import ProfileList
from hyo2.ssm2.lib.profile.dicts import Dicts
from hyo2.ssm2.lib.formats.writers.asvp import Asvp


logger = logging.getLogger(__name__)


class Sis(AbstractListener):
    """Kongsberg SIS listener"""

    class Sis4:
        def __init__(self):
            self.datagrams = [0x50, 0x52, 0x55, 0x58]
            self.surface_ssp = None  # type: Optional[km.KmSsp]
            self.surface_ssp_count = 0
            self.nav = None  # type: Optional[km.KmNav]
            self.nav_count = 0
            self.installation = None  # type: Optional[km.KmInstallation]
            self.installation_count = 0
            self.runtime = None  # type: Optional[km.KmRuntime]
            self.runtime_count = 0
            self.ssp = None  # type: Optional[km.KmSvp]
            self.ssp_count = 0
            self.svp_input = None  # type: Optional[km.KmSvpInput]
            self.svp_input_count = 0
            self.xyz88 = None  # type: Optional[km.KmXyz88]
            self.xyz88_count = 0
            self.range_angle78 = None  # type: Optional[km.KmRangeAngle78]
            self.range_angle78_count = 0
            self.seabed_image89 = None  # type: Optional[km.KmSeabedImage89]
            self.seabed_image89_count = 0
            self.watercolumn = None  # type: Optional[km.KmWatercolumn]
            self.watercolumn_count = 0
            self.bist = None  # type: Optional[km.KmBist]
            self.bist_count = 0

            self.r20_count = 0
            self.s01_count = 0

    class Sis5:
        def __init__(self):
            self.datagrams = [b'#SSM', b'#MRZ', b'#SPO', b'#SVP']
            self.ssm = None  # type: Optional[kmall.KmallSSM]
            self.ssm_count = 0
            self.mrz = None  # type: Optional[kmall.KmallMRZ]
            self.mrz_count = 0
            self.spo = None  # type: Optional[kmall.KmallSPO]
            self.spo_count = 0
            self.svp = None  # type: Optional[kmall.KmallSVP]
            self.svp_count = 0

            self.k454_count = 0
            self.s01_count = 0

    def __init__(self, port: int, timeout: int = 1, ip: str = "0.0.0.0",
                 target: Optional[object] = None, name: str = "SIS",
                 use_sis5: bool = False, debug: bool = False) -> None:
        super().__init__(port=port, ip=ip, timeout=timeout, target=target, name=name, debug=debug)
        self.use_sis5 = use_sis5
        self.desc = name

        self.sis4 = Sis.Sis4()
        self.sis5 = Sis.Sis5()

        self.cur_id = None
        self.nav_last_time = None  # type: Optional[datetime]
        self.xyz_last_time = None  # type: Optional[datetime]

    @property
    def ssp(self) -> Union[km.KmSvp, kmall.KmallSVP, None]:
        if self.use_sis5:
            return self.sis5.svp
        else:
            return self.sis4.ssp

    @ssp.setter
    def ssp(self, value: Union[km.KmSvp, kmall.KmallSVP, None]) -> None:
        if self.use_sis5:
            self.sis5.svp = value
        else:
            self.sis4.ssp = value

    def clear_ssp(self) -> None:
        if self.use_sis5:
            self.sis5.svp = None
        else:
            self.sis4.ssp = None

    @property
    def nav(self) -> Union[km.KmNav, kmall.KmallSPO, kmall.KmallSSM]:
        if self.use_sis5:
            if self.sis5.ssm:
                return self.sis5.ssm
            return self.sis5.spo
        else:
            return self.sis4.nav

    def clear_nav(self) -> None:
        if self.use_sis5:
            self.sis5.ssm = None
            self.sis5.spo = None
        else:
            self.sis4.nav = None

    @property
    def xyz(self) -> Union[km.KmXyz88, kmall.KmallMRZ, kmall.KmallSSM]:
        if self.use_sis5:
            if self.sis5.ssm:
                return self.sis5.ssm
            return self.sis5.mrz
        else:
            return self.sis4.xyz88

    def clear_xyz(self) -> None:
        if self.use_sis5:
            self.sis5.ssm = None
            self.sis5.mrz = None
        else:
            self.sis4.xyz88 = None

    @property
    def xyz_transducer_depth(self) -> Optional[float]:
        if self.use_sis5:

            if self.sis5.ssm:
                return self.sis5.ssm.transducer_depth

            if self.sis5.mrz is None:
                return None
            return self.sis5.mrz.transducer_depth

        else:

            if self.sis4.xyz88 is None:
                return None
            return self.sis4.xyz88.transducer_draft

    @property
    def xyz_transducer_sound_speed(self) -> Optional[float]:
        if self.use_sis5:

            if self.sis5.ssm:
                return self.sis5.ssm.tss

            if self.sis5.mrz is None:
                return None
            return self.sis5.mrz.tss

        else:

            if self.sis4.xyz88 is None:
                return None
            return self.sis4.xyz88.sound_speed

    @property
    def xyz_mean_depth(self) -> float:
        if self.use_sis5:

            if self.sis5.ssm:
                return self.sis5.ssm.mean_depth

            return self.sis5.mrz.mean_depth

        else:
            return self.sis4.xyz88.mean_depth

    @property
    def nav_latitude(self) -> Optional[float]:
        if self.use_sis5:

            if self.sis5.ssm:
                return self.sis5.ssm.latitude

            if self.sis5.spo is None:
                return None
            return self.sis5.spo.latitude

        else:

            if self.sis4.nav is None:
                return None
            return self.sis4.nav.latitude

    @property
    def nav_longitude(self) -> Optional[float]:
        if self.use_sis5:

            if self.sis5.ssm:
                return self.sis5.ssm.longitude

            if self.sis5.spo is None:
                return None
            return self.sis5.spo.longitude

        else:

            if self.sis4.nav is None:
                return None
            return self.sis4.nav.longitude

    @property
    def nav_timestamp(self) -> Optional[float]:
        if self.use_sis5:

            if self.sis5.ssm:
                return self.sis5.ssm.dg_time

            if self.sis5.spo is None:
                return None
            return self.sis5.spo.dg_time

        else:

            if self.sis4.nav is None:
                return None
            return self.sis4.nav.dg_time

    def parse(self) -> None:
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
            self.nav_last_time = datetime.utcnow()
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
            self.xyz_last_time = datetime.utcnow()
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
                logger.debug("%s: Ignoring received datagram" % self.cur_id)
            return

        if self.cur_id == b'#SSM':
            ssm = kmall.KmallSSM(this_data, self.debug)
            if ssm.invalid_data or ssm.inactive_navigation:
                return
            self.sis5.ssm = ssm
            self.sis5.ssm_count += 1
            self.nav_last_time = datetime.utcnow()
            if not ssm.inactive_pinging:
                self.xyz_last_time = datetime.utcnow()
            if self.debug:
                logger.debug("%s: Parsed" % self.cur_id)

        elif self.cur_id == b'#MRZ':
            partition = struct.unpack("<2H", this_data[20:24])
            nr_of_datagrams = partition[0]
            datagram_nr = partition[1]
            if datagram_nr == 1:
                self.sis5.mrz = kmall.KmallMRZ(this_data, self.debug)
                self.sis5.mrz_count += 1
                self.xyz_last_time = datetime.utcnow()
                if self.debug:
                    logger.info("%s: %d/%d -> Parsed" % (self.cur_id, datagram_nr, nr_of_datagrams))
            else:
                if self.debug:
                    logger.info("%s: %d/%d -> Ignored" % (self.cur_id, datagram_nr, nr_of_datagrams))

        elif self.cur_id == b'#SPO':
            spo = kmall.KmallSPO(this_data, self.debug)
            if spo.invalid_data or spo.inactive_sensor:
                return
            self.sis5.spo = spo
            self.sis5.spo_count += 1
            self.nav_last_time = datetime.utcnow()
            if self.debug:
                logger.debug("%s: Parsed" % self.cur_id)

        elif self.cur_id == b'#SVP':
            self.sis5.svp = kmall.KmallSVP(this_data, self.debug)
            self.sis5.svp_count += 1
            if self.debug:
                logger.debug("%s: Parsed" % self.cur_id)

        else:
            logger.error("Missing parser for datagram type: %s" % self.cur_id)

    def request_cur_profile(self, ip: str, port: int) -> None:
        if self.use_sis5:
            self._request_cur_sis5_profile(ip=ip, port=port)
        else:
            self._request_cur_sis4_profile(ip=ip, port=port)

    def _request_cur_sis5_profile(self, ip: str, port: int) -> None:
        logger.info("Requesting profile from %s:%s" % (ip, port))

        if self.sis5.mrz:
            echo_id = "%d_%d" % (self.sis5.mrz.sounder_id, self.sis5.mrz.system_id)
        elif self.sis5.ssm:
            echo_id = "%d_%d" % (self.sis5.ssm.sounder_id, self.sis5.ssm.system_id)
        elif self.sis5.spo:
            echo_id = "%d_%d" % (self.sis5.spo.sounder_id, self.sis5.spo.system_id)
        else:
            logger.warning("unable to retrieve a valid echo sounder ID")
            return

        output = "$KSSIS,454,EM%s\n\r" % echo_id

        sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_out.sendto(output.encode('utf-8'), (ip, port))
        if self.debug:
            logger.debug("tx -> '%s'" % (output, ))
        self.sis5.k454_count += 1
        sock_out.close()

    def _request_cur_sis4_profile(self, ip: str, port: int) -> None:
        logger.info("Requesting profile from %s:%s" % (ip, port))

        sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # We try all of them in the hopes that one works.
        sensors = ["710", "122", "302", "3020",  # legacy
                   "0124", "0304", "0712", "2040", "2045"]
        for idx, sensor in enumerate(sensors):
            # talker ID, Roger Davis (HMRG) suggested SM based on something KM told him
            output = '$SMR20,EMX=%s,' % sensor

            # calculate checksum, XOR of all bytes after the $
            checksum = functools.reduce(operator.xor, map(ord, output[1:len(output)]))

            # append the checksum and end of datagram identifier
            output += "*{0:02x}".format(checksum)
            output += "\\\r\n"

            sock_out.sendto(output.encode('utf-8'), (ip, port))
            if self.debug:
                logger.debug("%s: tx -> %s" % (idx, output))
            self.sis4.r20_count += 1

            # Adding a bit of a pause
            time.sleep(0.5)

        sock_out.close()

    def send_profile(self, ssp: ProfileList, ip: str, port: int) -> None:
        tx_data = Asvp().convert(ssp, fmt=Dicts.kng_formats['S01'])
        if self.debug:
            logger.debug('sending:\n%s' % tx_data)
        sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock_out.sendto(tx_data.encode('utf-8'), (ip, port))
            if self.use_sis5:
                self.sis5.s01_count += 1
            else:
                self.sis4.s01_count += 1
        except socket.error as e:
            traceback.print_exc()
            logger.warning("socket issue: %s" % e)
        sock_out.close()

    def info(self) -> str:
        msg = "Received datagrams:\n"
        if self.use_sis5:
            msg += "- SSM: %d\n" % self.sis5.ssm_count
            msg += "- MRZ: %d\n" % self.sis5.mrz_count
            msg += "- SPO: %d\n" % self.sis5.spo_count
            msg += "- SVP: %d\n" % self.sis5.svp_count
        else:
            msg += "- Nav: %d\n" % self.sis4.nav_count
            msg += "- Xyz: %d\n" % self.sis4.xyz88_count
            msg += "- Ssp: %d\n" % self.sis4.ssp_count
            msg += "- Runtime: %d\n" % self.sis4.runtime_count
        msg += "Transmitted datagrams:\n"
        if self.use_sis5:
            msg += "- K454: %d\n" % self.sis5.k454_count
            msg += "- S01: %d\n" % self.sis5.s01_count
        else:
            msg += "- R20: %d\n" % self.sis4.r20_count
            msg += "- S01: %d\n" % self.sis4.s01_count
        return msg
