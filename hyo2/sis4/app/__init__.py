import os
from hyo2.abc.app.app_info import AppInfo
from hyo2.sis4 import name, __version__

app_info = AppInfo()

app_info.app_name = name
app_info.app_version = __version__
app_info.app_author = "Giuseppe Masetti(UNH,CCOM)"
app_info.app_author_email = "gmasetti@ccom.unh.edu"

app_info.app_license = "LGPLv3"
app_info.app_license_url = "https://www.hydroffice.org/license/"

app_info.app_path = os.path.abspath(os.path.dirname(__file__))

app_info.app_url = "https://www.hydroffice.org/soundspeed/"
app_info.app_manual_url = "https://www.hydroffice.org/manuals/soundspeed/index.html"
app_info.app_support_email = "sis_emulator@hydroffice.org"
app_info.app_latest_url = "https://www.hydroffice.org/latest/soundspeedmanager.txt"

app_info.app_media_path = os.path.join(app_info.app_path, "media")
app_info.app_main_window_object_name = "MainWindow"
app_info.app_license_path = os.path.join(app_info.app_media_path, "LICENSE")
app_info.app_icon_path = os.path.join(app_info.app_media_path, "app_icon.png")
