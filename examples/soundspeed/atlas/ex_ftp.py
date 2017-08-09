import os
from hyo.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

from hyo.soundspeed.atlas.ftp import Ftp
from hyo.soundspeed.base import testing


def main():

    ftp = Ftp(host="ftp.ccom.unh.edu", password="test@gmail.com", show_progress=True, debug_mode=True)

    ftp.get_file(file_src="fromccom/hydroffice/Caris_Support_Files_5_5.zip",
                 file_dst=os.path.join(testing.output_data_folder(), "test.zip"))


if __name__ == "__main__":
    main()
