import time

from hydroffice.soundspeed.logging import test_logging

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

