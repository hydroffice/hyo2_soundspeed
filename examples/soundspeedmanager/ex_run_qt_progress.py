import logging
import time

from PySide2 import QtWidgets

from hyo2.abc.app.qt_progress import QtProgress

app = QtWidgets.QApplication([])

widget = QtWidgets.QWidget()
widget.show()

progress = QtProgress(parent=widget)

progress.start(title='Test Bar', text='Doing stuff')

time.sleep(1.)

progress.update(value=30, text='Updating')

time.sleep(1.)

print("canceled? %s" % progress.canceled)

progress.end()

# app.exec_()
