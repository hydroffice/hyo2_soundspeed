from __future__ import absolute_import, division, print_function, unicode_literals

import os
import shutil
import logging

logger = logging.getLogger(__name__)

from ..abstract import AbstractAtlas
from ..ftp import Ftp
from ...profile.profile import Profile


class Woa13(AbstractAtlas):
    """WOA13 atlas"""

    def __init__(self, data_folder, prj):
        super(Woa13, self).__init__(data_folder=data_folder, prj=prj)
        self.name = self.__class__.__name__
        self.desc = "WOA13"

    def is_present(self):
        """check the presence of one of the dataset file"""
        check_woa13_file = os.path.join(self.folder, 'tmp', 'woa13_decav_t00_01v2.nc')
        if not os.path.exists(check_woa13_file):
            return False
        check_woa13_file = os.path.join(self.folder, 'sal', 'woa13_decav_s00_01v2.nc')
        if not os.path.exists(check_woa13_file):
            return False
        return True

    def download_db(self, qprogressbar=None):
        """try to download the data set"""
        logger.debug('downloading WOA13 atlas')

        try:
            # remove all the content
            for root, dirs, files in os.walk(self.folder, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
        except Exception as e:
            logger.error('during cleaning target folder: %s' % e)
            return False

        try:
            ftp = Ftp("ftp.ccom.unh.edu", show_progress=True, debug_mode=False,
                      qprogressbar=qprogressbar)
            data_zip_src = "fromccom/hydroffice/woa13_tmp.zip"
            data_zip_dst = os.path.join(self.data_folder, "woa13_tmp.zip")
            ftp.get_file(data_zip_src, data_zip_dst, unzip_it=True)

            ftp = Ftp("ftp.ccom.unh.edu", show_progress=True, debug_mode=False,
                      qprogressbar=qprogressbar)
            data_zip_src = "fromccom/hydroffice/woa13_sal.zip"
            data_zip_dst = os.path.join(self.data_folder, "woa13_sal.zip")
            ftp.get_file(data_zip_src, data_zip_dst, unzip_it=True)

            return self.is_present()

        except Exception as e:
            logger.error('during WOA13 download and unzip: %s' % e)
            return False

    def query(self, lat, lon, datestamp):
        ssp = Profile()
        return ssp

    def __repr__(self):
        msg = "%s" % super(Woa13, self).__repr__()
        return msg
