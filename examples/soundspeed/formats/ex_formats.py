import logging

from hyo2.soundspeed.formats import readers, writers

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Readers:")
fmts = list()
for rdr in readers:
    logger.debug("> %s" % rdr)
    if len(rdr.ext):
        fmts.append("%s(*.%s)" % (rdr.desc, " *.".join(rdr.ext)))

logger.debug("%s;;All files (*.*)" % ";;".join(fmts))

logger.debug("\nWriters:")
for wtr in writers:
    logger.debug("> %s" % wtr)
