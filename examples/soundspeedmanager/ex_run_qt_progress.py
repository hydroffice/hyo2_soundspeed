import time
from PySide import QtGui

from hydroffice.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

from hydroffice.soundspeedmanager.qt_progress import QtProgress

app = QtGui.QApplication([])

widget = QtGui.QWidget()
widget.show()

progress = QtProgress(parent=widget)

progress.start(title='Test Bar', text='Doing stuff')

time.sleep(1.)

progress.update(value=30, text='Updating')

time.sleep(1.)

print("canceled? %s" % progress.canceled)

progress.end()

# app.exec_()
