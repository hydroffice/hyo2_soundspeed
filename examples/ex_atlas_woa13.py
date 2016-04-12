from __future__ import absolute_import, division, print_function, unicode_literals

from PySide import QtGui
from datetime import datetime as dt, timedelta
import os

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
    app = QtGui.QApplication([])  # PySide stuff (start)
    mw = QtGui.QMainWindow()
    mw.show()

    prj = Project(qprogress=QtGui.QProgressDialog)

    tests = [
        (43.026480, -70.318824, dt.utcnow()),  # offshore Portsmouth
        (-19.1, 74.16, dt.utcnow()),  # Indian Ocean
        (18.2648113, 16.1761115, dt.utcnow()),  # in land -> middle of Africa
    ]

    if not prj.has_woa13():
        success = prj.download_woa13()
        if not success:
            raise RuntimeError("unable to download")
    logger.info("has woa09: %s" % prj.has_woa13())

    logger.info("load woa13: %s" % prj.atlases.woa13.load_grids())

    for test in tests:
        # just the ssp (there are also ssp_min and ssp_max)
        logger.info("woa13 profile:\n%s" % prj.atlases.woa13.query(lat=test[0], lon=test[1], datestamp=test[2])[0])

    app.exec_()  # PySide stuff (end)

if __name__ == "__main__":
    main()
