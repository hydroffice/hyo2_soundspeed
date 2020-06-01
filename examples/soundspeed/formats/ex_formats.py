import logging

from hyo2.soundspeed.formats import readers, writers
from hyo2.abc.lib.logging import set_logging

ns_list = ["hyo2.soundspeed", "hyo2.soundspeedmanager", "hyo2.soundspeedsettings"]
set_logging(ns_list=ns_list)

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
