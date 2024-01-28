import logging
import os

from hyo2.ssm2 import pkg_info

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

app_path = os.path.abspath(os.path.dirname(__file__))
app_media_path = os.path.join(app_path, "media")
app_info = pkg_info.app_info(
    app_name = "Sound Speed Manager",
    app_license_path = os.path.join(app_media_path, "LICENSE"),
    app_icon_path = os.path.join(app_media_path, "app_icon.png")
)
