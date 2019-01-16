import time
from datetime import datetime as dt, timedelta
import logging

from PySide2 import QtWidgets

from hyo2.abc.app.qt_progress import QtProgress
from hyo2.soundspeedmanager import app_info
from hyo2.soundspeed.soundspeed import SoundSpeedLibrary
from hyo2.soundspeedmanager.qt_callbacks import QtCallbacks


logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
logger = logging.getLogger(__name__)

switch = "GoMOFS"  # WOA09 or WOA13 or RTOFS or GoMOFS

app = QtWidgets.QApplication([])  # PySide stuff (start)
mw = QtWidgets.QMainWindow()
mw.show()

lib = SoundSpeedLibrary(progress=QtProgress(parent=mw), callbacks=QtCallbacks(parent=mw))

tests = [
    (43.026480, -70.318824, dt.utcnow()),  # offshore Portsmouth
    # (-19.1, 74.16, dt.utcnow()),  # Indian Ocean
    # (18.2648113, 16.1761115, dt.utcnow()),  # in land -> middle of Africa
]

if switch == "WOA09":

    # download the woa09 if not present
    if not lib.has_woa09():
        success = lib.download_woa09()
        if not success:
            raise RuntimeError("unable to download")
    logger.info("has WOA09: %s" % lib.has_woa09())

elif switch == "WOA13":

    # download the woa13 if not present
    if not lib.has_woa13():
        success = lib.download_woa13()
        if not success:
            raise RuntimeError("unable to download")
    logger.info("has WOA13: %s" % lib.has_woa13())

elif switch == "RTOFS":

    # download the current-time rtofs
    if not lib.has_rtofs():
        lib.download_rtofs()
    logger.info("has RTOFS: %s" % lib.has_rtofs())

elif switch == "GoMOFS":

    # download the current-time rtofs
    if not lib.has_gomofs():
        lib.download_gomofs()
    logger.info("has GoMOFS: %s" % lib.has_gomofs())

else:
    raise RuntimeError("invalid switch value: %s" % switch)

# # more stuff
# if switch == "RTOFS":
#
#     # test today urls
#     # noinspection PyProtectedMember
#     temp_url, sal_url = lib.atlases.rtofs._build_check_urls(dt.utcnow())
#     # noinspection PyProtectedMember
#     logger.info("urls:\n- %s [%s]\n%s [%s]"
#                 % (temp_url, lib.atlases.rtofs._check_url(temp_url), sal_url, lib.atlases.rtofs._check_url(sal_url)))
#     # test yesterday urls
#     # noinspection PyProtectedMember
#     temp_url, sal_url = lib.atlases.rtofs._build_check_urls(dt.utcnow() - timedelta(days=1))
#     # noinspection PyProtectedMember
#     logger.info("urls:\n- %s [%s]\n%s [%s]"
#                 % (temp_url, lib.atlases.rtofs._check_url(temp_url), sal_url, lib.atlases.rtofs._check_url(sal_url)))
#
# elif switch == "GoMOFS":
#
#     # test today urls
#     # noinspection PyProtectedMember
#     url = lib.atlases.gomofs._build_check_url(dt.utcnow())
#     # noinspection PyProtectedMember
#     logger.info("url:\n- %s [%s]"
#                 % (url, lib.atlases.gomofs._check_url(url)))
#     # test yesterday urls
#     # noinspection PyProtectedMember
#     url = lib.atlases.gomofs._build_check_url(dt.utcnow() - timedelta(days=1))
#     # noinspection PyProtectedMember
#     logger.info("url:\n- %s [%s]"
#                 % (url, lib.atlases.gomofs._check_url(url)))


# test for a few locations
for test in tests:

    start_time = time.time()
    # just the ssp (there are also ssp_min and ssp_max)
    if switch == "WOA09":
        logger.info("WOA09 profiles:\n%s" % lib.atlases.woa09.query(lat=test[0], lon=test[1], datestamp=test[2]))
    elif switch == "WOA13":
        logger.info("WOA13 profiles:\n%s" % lib.atlases.woa13.query(lat=test[0], lon=test[1], datestamp=test[2]))
    elif switch == "RTOFS":
        logger.info("RTOFS profiles:\n%s" % lib.atlases.rtofs.query(lat=test[0], lon=test[1], datestamp=test[2]))
    elif switch == "GoMOFS":
        logger.info("GoMOFS profiles:\n%s" % lib.atlases.gomofs.query(lat=test[0], lon=test[1], datestamp=test[2]))
    else:
        raise RuntimeError("invalid switch value: %s" % switch)
    logger.info("execution time: %.3f s" % (time.time() - start_time))

# app.exec_()  # no need to actually run the message loop
