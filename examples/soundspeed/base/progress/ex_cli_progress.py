from __future__ import absolute_import, division, print_function, unicode_literals

import time

# logging settings
import logging
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)

from hydroffice.soundspeed.base.progress.cli_progress import CliProgress

progress = CliProgress()

progress.start(title='Test Bar', text='Doing stuff', min_value=100, max_value=300)

time.sleep(1.)

progress.update(value=135, text='Updating')

time.sleep(1.)

progress.add(quantum=33, text='Updating')

time.sleep(1.)

print("canceled? %s" % progress.canceled)

progress.end()

