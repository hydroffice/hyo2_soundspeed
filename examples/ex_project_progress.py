from __future__ import absolute_import, division, print_function, unicode_literals

from time import sleep
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

from hydroffice.soundspeed.project import Project


def main():
    app = QtGui.QApplication([])
    prj = Project(qprogress=QtGui.QProgressDialog)
    prj.progress.start("TEST")
    sleep(2)
    prj.progress.update(30)
    sleep(2)
    prj.progress.update(60)
    sleep(1)
    prj.progress.end()
    app.exec_()

if __name__ == "__main__":
    main()