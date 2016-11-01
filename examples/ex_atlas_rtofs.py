from __future__ import absolute_import, division, print_function, unicode_literals

from PySide import QtGui
from datetime import datetime as dt, timedelta

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
from hydroffice.soundspeedmanager.qtcallbacks import QtCallbacks


def main():
    app = QtGui.QApplication([])  # PySide stuff (start)
    mw = QtGui.QMainWindow()
    mw.show()

    prj = Project(qt_progress=QtGui.QProgressDialog)
    prj.set_callbacks(QtCallbacks(mw))

    tests = [
        (43.026480, -70.318824, dt.utcnow()),  # offshore Portsmouth
        (-19.1, 74.16, dt.utcnow()),  # Indian Ocean
        (18.2648113, 16.1761115, dt.utcnow()),  # in land -> middle of Africa
    ]

    if not prj.has_rtofs():
        prj.download_rtofs()
    logger.info("has rtofs: %s" % prj.has_rtofs())

    temp_url, sal_url = prj.atlases.rtofs._build_check_urls(dt.utcnow())
    logger.info("urls:\n%s [%s]\n%s [%s]"
                % (temp_url, prj.atlases.rtofs._check_url(temp_url), sal_url, prj.atlases.rtofs._check_url(sal_url)))
    temp_url, sal_url = prj.atlases.rtofs._build_check_urls(dt.utcnow() - timedelta(days=1))
    logger.info("urls:\n%s [%s]\n%s [%s]"
                % (temp_url, prj.atlases.rtofs._check_url(temp_url), sal_url, prj.atlases.rtofs._check_url(sal_url)))

    for test in tests:
        logger.info("rtofs profile:\n%s" % prj.atlases.rtofs.query(lat=test[0], lon=test[1], datestamp=test[2]))

    prj.retrieve_rtofs()
    logger.info("lib retrieve rtofs: %s" % prj.ssp)

    app.exec_()  # PySide stuff (end)

if __name__ == "__main__":
    main()
