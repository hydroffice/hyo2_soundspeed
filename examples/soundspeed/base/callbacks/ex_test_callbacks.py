import logging

from hyo2.soundspeed.base.callbacks.fake_callbacks import FakeCallbacks
from hyo2.abc.lib.logging import set_logging

ns_list = ["hyo2.soundspeed", "hyo2.soundspeedmanager", "hyo2.soundspeedsettings"]
set_logging(ns_list=ns_list)

logger = logging.getLogger(__name__)

cb = FakeCallbacks()

logger.debug("ask number: %s" % cb.ask_number())
logger.debug("ask text: %s" % cb.ask_text())
logger.debug("ask text with flag: %s, %r" % cb.ask_text_with_flag())
logger.debug("ask date: %s" % cb.ask_date())
logger.debug("ask location: %s, %s" % cb.ask_location())
logger.debug("ask filename: %s" % cb.ask_filename())
logger.debug("ask directory: %s" % cb.ask_directory())
logger.debug("ask location from SIS: %s" % cb.ask_location_from_sis())
logger.debug("ask tss: %s" % cb.ask_tss())
logger.debug("ask draft: %s" % cb.ask_draft())
logger.debug("ask directory: %s" % cb.ask_directory())
