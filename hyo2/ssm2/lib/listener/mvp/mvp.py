import logging
from threading import Event
from typing import TYPE_CHECKING

from hyo2.ssm2.lib.listener.abstract import AbstractListener
from hyo2.ssm2.lib.formats.readers import mvp
if TYPE_CHECKING:
    from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary

logger = logging.getLogger(__name__)


class Mvp(AbstractListener):

    def __init__(self, port: int, prj: 'SoundSpeedLibrary', timeout: int = 1,
                 ip: str = "0.0.0.0", target: object | None = None, name: str | None = "Km",
                 debug: bool = False) -> None:
        super(Mvp, self).__init__(port=port, ip=ip, timeout=timeout,
                                  target=target, name=name, debug=debug)
        self.desc = "MVP"
        self.prj = prj

        self.new_ssp = Event()

        try:
            self.protocol = mvp.Mvp.protocols[prj.setup.mvp_transmission_protocol]
        except KeyError:
            raise RuntimeError("passed unknown protocol: %s" % prj.setup.mvp_transmission_protocol)
        try:
            self.format = mvp.Mvp.formats[prj.setup.mvp_format]
        except KeyError:
            raise RuntimeError("passed unknown format: %s" % prj.setup.mvp_format)

        self.header: bytes = bytes()
        self.has_header = False
        self.data_blocks: list[bytes] = list()
        self.has_data = False
        self.footer: bytes = bytes()
        self.has_footer = False

    def _clear_data(self) -> None:
        self.header = bytes()
        self.has_header = False
        self.data_blocks = list()
        self.has_data = False
        self.footer = bytes()
        self.has_footer = False

    def __repr__(self) -> str:
        msg = "%s" % super(Mvp, self).__repr__()
        return msg

    def parse(self) -> None:
        if self.debug:
            logger.info("Parsing data of length %s using protocol %s" % (len(self.data), self.protocol))

        rdr = mvp.Mvp()

        if self.protocol == mvp.Mvp.protocols["NAVO_ISS60"]:

            if len(self.data) == 536:
                if self.debug:
                    logger.info("Got header")
                self._clear_data()
                self.header = self.data
                self.has_header = True
                return

            if len(self.data) == 20032:
                if self.debug:
                    logger.info("Got data block")
                self.data_blocks.append(self.data)
                self.has_data = True
                return

            if len(self.data) == 8:
                if self.debug:
                    logger.info("Got footer")
                self.footer = self.data
                self.has_footer = True

            if self.has_header and self.has_data and self.has_footer:
                logger.info("Assembling the cast: %d + (%d x %d) + %d" %
                            (len(self.header), len(self.data_blocks), len(self.data_blocks[0]), len(self.footer)))

                rdr.init_from_listener(header=self.header, data_blocks=self.data_blocks, footer=self.footer,
                                       protocol=self.protocol, fmt=self.format, settings=self.prj.setup,
                                       callbacks=self.prj.cb)
            else:
                logger.error("Footer received without header or data")
                self._clear_data()
                return

        elif self.protocol == mvp.Mvp.protocols["UNDEFINED"]:
            logger.info("Parsing with UNDEFINED protocol: %s" % self.data)
            self.data_blocks.append(self.data)
            rdr.init_from_listener(header=self.header, data_blocks=self.data_blocks, footer=self.footer,
                                   protocol=self.protocol, fmt=self.format, settings=self.prj.setup,
                                   callbacks=self.prj.cb)

        else:
            raise RuntimeError("Unsupported protocol: %s" % self.protocol)

        self.prj.ssp = rdr.ssp
        self._clear_data()
        self.prj.ssp.cur.listener_completed = True

        # retrieve atlases data for each retrieved profile
        if self.prj.use_woa09() and self.prj.has_woa09():
            self.prj.ssp.cur.woa09 = self.prj.atlases.woa09.query(lat=self.prj.ssp.cur.meta.latitude,
                                                                  lon=self.prj.ssp.cur.meta.longitude,
                                                                  dtstamp=self.prj.ssp.cur.meta.utc_time)
            logger.debug("added WOA09")

        if self.prj.use_woa13() and self.prj.has_woa13():
            self.prj.ssp.cur.woa13 = self.prj.atlases.woa13.query(lat=self.prj.ssp.cur.meta.latitude,
                                                                  lon=self.prj.ssp.cur.meta.longitude,
                                                                  dtstamp=self.prj.ssp.cur.meta.utc_time)
            logger.debug("added WOA13")

        if self.prj.use_woa18() and self.prj.has_woa18():
            self.prj.ssp.cur.woa18 = self.prj.atlases.woa18.query(lat=self.prj.ssp.cur.meta.latitude,
                                                                  lon=self.prj.ssp.cur.meta.longitude,
                                                                  dtstamp=self.prj.ssp.cur.meta.utc_time)
            logger.debug("added WOA18")

        if self.prj.use_woa23() and self.prj.has_woa23():
            self.prj.ssp.cur.woa23 = self.prj.atlases.woa23.query(lat=self.prj.ssp.cur.meta.latitude,
                                                                  lon=self.prj.ssp.cur.meta.longitude,
                                                                  dtstamp=self.prj.ssp.cur.meta.utc_time)
            logger.debug("added WOA23")

        if self.prj.use_rtofs():
            try:
                self.prj.ssp.cur.rtofs = self.prj.atlases.rtofs.query(lat=self.prj.ssp.cur.meta.latitude,
                                                                      lon=self.prj.ssp.cur.meta.longitude,
                                                                      dtstamp=self.prj.ssp.cur.meta.utc_time)
                logger.debug("added RTOFS")

            except RuntimeError:
                self.prj.ssp.cur.rtofs = None
                logger.warning("unable to retrieve RTOFS data")

        self.data = None
        self.new_ssp.set()
