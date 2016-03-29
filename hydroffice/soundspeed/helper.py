from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

logger = logging.getLogger(__name__)

here = os.path.abspath(os.path.dirname(__file__))


def get_testing_data_folder():
    data_folder = os.path.abspath(os.path.join(here, os.pardir, os.pardir, "data", "downloaded"))
    if not os.path.exists(data_folder):
        raise RuntimeError("The testing folder does not exist: %s" % data_folder)
    return data_folder


class FileInfo(object):

    def __init__(self, data_path, mode):

        self._basename = None
        self._ext = None
        self._path = None
        self._io = None

    def __repr__(self):
        msg = "<%s>" % self.__class__.__name__

        return msg
