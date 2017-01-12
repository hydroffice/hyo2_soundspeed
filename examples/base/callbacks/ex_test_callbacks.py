from __future__ import absolute_import, division, print_function, unicode_literals

# logging settings
import logging
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)


from hydroffice.soundspeed.base.callbacks.test_callbacks import TestCallbacks

cb = TestCallbacks()

logger.debug("ask number: %s" % cb.ask_number())
logger.debug("ask text: %s" % cb.ask_text())
logger.debug("ask date: %s" % cb.ask_date())
logger.debug("ask location: %s %s" % cb.ask_location())
logger.debug("ask filename: %s" % cb.ask_filename())
logger.debug("ask directory: %s" % cb.ask_directory())
logger.debug("ask location from SIS: %s" % cb.ask_location_from_sis())
logger.debug("ask tss: %s" % cb.ask_tss())
logger.debug("ask draft: %s" % cb.ask_draft())
logger.debug("ask directory: %s" % cb.ask_directory())
