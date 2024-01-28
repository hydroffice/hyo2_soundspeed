import logging
import os

from hyo2.ssm2 import pkg_info

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

app_path = os.path.abspath(os.path.dirname(__file__))
app_media_path = os.path.join(app_path, "media")

app_info = pkg_info.app_info(
    app_name="SSM-SIS",
    app_version="1.2.0",
    app_beta=True,
    app_url="https://www.hydroffice.org/ssm_sis/",
    app_latest_url="https://www.hydroffice.org/latest/ssm_sis.txt",
    app_path=app_path,
    app_media_path=app_media_path,
    app_license_path=os.path.join(app_media_path, "LICENSE"),
    app_icon_path=os.path.join(app_media_path, "ssm_sis.png")
)
