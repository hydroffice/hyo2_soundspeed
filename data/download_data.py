import logging
import os.path
import shutil
from hyo2.abc2.lib.ftp import Ftp

logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
logger = logging.getLogger(__name__)

clear_download_folder = False

# list of files to download from https://nomads.ncep.noaa.gov/pub/data/nccf/com/rtofs/prod/
data_files = [
    "rtofs_glo_3dz_f024_daily_3zsio.nc",
    "rtofs_glo_3dz_f024_daily_3ztio.nc"
]

# create an empty `download` folder
download_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "download")
if not os.path.exists(download_folder):
    os.makedirs(download_folder)
elif clear_download_folder:
    shutil.rmtree(download_folder)
    os.makedirs(download_folder)
rtofs_folder = os.path.join(download_folder, "rtofs")
if not os.path.exists(rtofs_folder):
    os.makedirs(rtofs_folder)
elif clear_download_folder:
    shutil.rmtree(rtofs_folder)
    os.makedirs(rtofs_folder)

# actually downloading the file with wget
for fid in data_files:

    data_src = os.path.join("fromccom/hydroffice/smartmap", fid)
    data_dst = os.path.abspath(os.path.join(rtofs_folder, fid))
    print("> downloading %s to %s" % (data_src, data_dst))

    try:
        ftp = Ftp("ftp.ccom.unh.edu", show_progress=True, debug_mode=False)
        ftp.get_file(data_src, data_dst, unzip_it=False)
        ftp.disconnect()

    except Exception as e:
        logger.error('while downloading %s: %s' % (fid, e))
