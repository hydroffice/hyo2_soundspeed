from __future__ import absolute_import, division, print_function, unicode_literals

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

    if not prj.has_woa09():
        prj.download_woa09()
    logger.info("has woa09: %s" % prj.has_woa09())

    if not prj.has_woa13():
        prj.download_woa13()
    logger.info("has woa13: %s" % prj.has_woa13())


if __name__ == "__main__":
    main()
