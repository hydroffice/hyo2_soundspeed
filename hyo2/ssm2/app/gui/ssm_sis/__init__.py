import logging
import os

from hyo2.abc2.app.app_info import AppInfo
from hyo2.abc2.lib.lib_info import LibInfo


name = "SSM-SIS"
__version__ = "1.2.0"

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

app_info = AppInfo()

app_info.app_name = name
app_info.app_version = __version__
app_info.app_url = "https://www.hydroffice.org/ssm_sis/"
app_info.app_latest_url = "https://www.hydroffice.org/latest/ssm_sis.txt"
app_info.app_path = os.path.abspath(os.path.dirname(__file__))
app_info.app_media_path = os.path.join(app_info.app_path, "media")
app_info.app_icon_path = os.path.join(app_info.app_media_path, "ssm_sis.png")
