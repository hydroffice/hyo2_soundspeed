import socket
import operator
import logging
import functools
import time
from threading import Thread, Event

logger = logging.getLogger(__name__)

from hyo.soundspeed.listener.abstract import AbstractListener
from hyo.soundspeed.formats.readers import mvp


class Mvp(AbstractListener):
    """MVP listener"""

    def __init__(self, port, prj, timeout=1, ip="0.0.0.0", target=None, name="Km"):
        super(Mvp, self).__init__(port=port, ip=ip, timeout=timeout,
                                  target=target, name=name)
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

        self.header = str()
        self.footer = str()
        self.data_blocks = []

        self.num_data_blocks = 0

        self.got_header = False
        self.got_data = False
        self.got_footer = False

        self.ssp = None

    def __repr__(self):
        msg = "%s" % super(Mvp, self).__repr__()
        # msg += "  <has data loaded: %s>\n" % self.has_data_loaded
        return msg

    def parse(self):
        logger.info("Going to parse data of length %s using protocol %s" % (len(self.data), self.protocol))

        if self.protocol == mvp.Mvp.protocols["NAVO_ISS60"]:

            if len(self.data) == 536:
                logger.info("got header")
                self.header = self.data
                self.got_header = True
                self.got_footer = False
                self.got_data = False
                self.num_data_blocks = 0

            elif len(self.data) == 20032:
                logger.info(" got data block")
                self.got_data = True
                self.data_blocks.append(self.data)
                self.num_data_blocks += 1

            elif len(self.data) == 8:
                logger.info("got footer")
                self.footer = self.data
                self.got_footer = True

            if self.got_header and self.got_data and self.got_footer:
                logger.info("Assembling the cast!")
                logger.info("- lengths: %s %s %s"
                         % (len(self.header), len(self.data_blocks), len(self.footer)))
                logger.info("- nr. of data blocks: %s" % self.num_data_blocks)

                rdr = mvp.Mvp()
                rdr.init_from_listener(self.header, self.data_blocks, self.footer, self.protocol, self.format)
                self.prj.ssp = rdr.ssp

                self.got_header = False
                self.header = None
                self.got_data = False
                self.data_blocks = []
                self.num_data_blocks = 0
                self.got_footer = False
                self.footer = None

                # retrieve atlases data for each retrieved profile
                if self.prj.use_woa09() and self.prj.has_woa09():
                    self.prj.ssp.cur.woa09 = self.prj.atlases.woa09.query(lat=self.prj.ssp.cur.meta.latitude,
                                                                          lon=self.prj.ssp.cur.meta.longitude,
                                                                          datestamp=self.prj.ssp.cur.meta.utc_time)
                    logger.debug("added WOA09")

                if self.prj.use_woa13() and self.prj.has_woa13():
                    self.prj.ssp.cur.woa13 = self.prj.atlases.woa13.query(lat=self.prj.ssp.cur.meta.latitude,
                                                                          lon=self.prj.ssp.cur.meta.longitude,
                                                                          datestamp=self.prj.ssp.cur.meta.utc_time)
                    logger.debug("added WOA13")

                if self.prj.use_rtofs():
                    try:
                        self.prj.ssp.cur.rtofs = self.prj.atlases.rtofs.query(lat=self.prj.ssp.cur.meta.latitude,
                                                                              lon=self.prj.ssp.cur.meta.longitude,
                                                                              datestamp=self.prj.ssp.cur.meta.utc_time)
                        logger.debug("added RTOFS")

                    except RuntimeError:
                        self.prj.ssp.cur.rtofs = None
                        logger.warning("unable to retrieve RTOFS data")

                self.prj.ssp.cur.listener_completed = True

        elif self.protocol == mvp.Mvp.protocols["UNDEFINED"]:

            logger.info("going to parse with UNDEFINED protocol!!")
            logger.info("the data is %s" % self.data)
            self.data_blocks.append(self.data)
            self.num_data_blocks += 1
            rdr = mvp.Mvp()
            rdr.init_from_listener(self.header, self.data_blocks, self.footer, self.protocol, self.format)
            self.prj.ssp = rdr.ssp

            # retrieve atlases data for each retrieved profile
            if self.prj.use_woa09() and self.prj.has_woa09():
                self.prj.ssp.cur.woa09 = self.prj.atlases.woa09.query(lat=self.prj.ssp.cur.meta.latitude,
                                                                      lon=self.prj.ssp.cur.meta.longitude,
                                                                      datestamp=self.prj.ssp.cur.meta.utc_time)

            if self.prj.use_woa13() and self.prj.has_woa13():
                self.prj.ssp.cur.woa13 = self.prj.atlases.woa13.query(lat=self.prj.ssp.cur.meta.latitude,
                                                                      lon=self.prj.ssp.cur.meta.longitude,
                                                                      datestamp=self.prj.ssp.cur.meta.utc_time)

            if self.prj.use_rtofs():
                try:
                    self.prj.ssp.cur.rtofs = self.prj.atlases.rtofs.query(lat=self.prj.ssp.cur.meta.latitude,
                                                                          lon=self.prj.ssp.cur.meta.longitude,
                                                                          datestamp=self.prj.ssp.cur.meta.utc_time)
                except RuntimeError:
                    self.prj.ssp.cur.rtofs = None
                    logger.warning("unable to retrieve RTOFS data")

            self.prj.ssp.cur.listener_completed = True

        self.data = None
        self.new_ssp.set()
