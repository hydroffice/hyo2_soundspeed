from __future__ import absolute_import, division, print_function, unicode_literals

import time
from PySide import QtGui

# logging settings
import logging
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)

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
