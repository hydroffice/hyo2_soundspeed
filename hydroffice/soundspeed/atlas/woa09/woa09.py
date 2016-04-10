from __future__ import absolute_import, division, print_function, unicode_literals

import os
import shutil
import logging

logger = logging.getLogger(__name__)

from ..abstract import AbstractAtlas
from ..ftp import Ftp


class Woa09(AbstractAtlas):
    """WOA09 atlas"""

    def __init__(self, data_folder):
        super(Woa09, self).__init__(data_folder)
        self.name = self.__class__.__name__
        self.desc = "WOA09"

    def is_present(self):
        """check the presence of one of the dataset file"""
        check_woa09_file = os.path.join(self.folder, 'landsea.msk')
        if not os.path.exists(check_woa09_file):
            return False
        return True

    def download_db(self, qprogressbar=None):
        """try to download the data set"""
        logger.debug('downloading WOA9 atlas')

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
            data_zip_src = "fromccom/hydroffice/woa09.zip"
            data_zip_dst = os.path.join(self.data_folder, "woa09.zip")
            ftp.get_file(data_zip_src, data_zip_dst, unzip_it=True)
            return self.is_present()

        except Exception as e:
            logger.error('during WOA09 download and unzip: %s' % e)
            return False

    def __repr__(self):
        msg = "%s" % super(Woa09, self).__repr__()
        return msg