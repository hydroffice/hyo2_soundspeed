from __future__ import absolute_import, division, print_function, unicode_literals

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
    # create a project
    prj = Project()
    logger.info(prj)
    logger.info(prj.atlases)

    lat = 43.026480
    lon = -70.318824
    # split case
    # lat = -19.1
    # lon = 74.16
    timestamp = dt.utcnow()

    # woa13
    if not prj.has_woa09():
        prj.download_woa09()
    logger.info("has woa09: %s" % prj.has_woa09())

    # woa09
    if not prj.has_woa13():
        prj.download_woa13()
    logger.info("has woa13: %s" % prj.has_woa13())

    # rtofs
    if not prj.has_rtofs():
        prj.download_rtofs()
    logger.info("has rtofs: %s" % prj.has_rtofs())

    temp_url, sal_url = prj.atlases.rtofs.build_check_urls(dt.utcnow())
    logger.info("urls:\n%s\n%s" % (temp_url, sal_url))
    logger.info("valid:%s" % prj.atlases.rtofs.check_url(temp_url))
    temp_url, sal_url = prj.atlases.rtofs.build_check_urls(dt.utcnow() - timedelta(days=1))
    logger.info("urls:\n%s\n%s" % (temp_url, sal_url))
    logger.info("valid:%s" % prj.atlases.rtofs.check_url(temp_url))

    logger.info("rtofs profile:\n%s" % prj.atlases.rtofs.query(lat=lat, lon=lon, datestamp=timestamp))

if __name__ == "__main__":
    main()
