import platform
import os
import logging

logger = logging.getLogger(__name__)

from hyo.soundspeed.base.helper import is_windows


def load(pyside=True):

    if not pyside:
        raise RuntimeError("unsupported")

    here = os.path.abspath(os.path.dirname(__file__)).replace("\\", "/")
    if is_windows():
        import win32api
        # noinspection PyProtectedMember
        here = win32api.GetLongPathName(here)
    style_path = os.path.join(here, "app.stylesheet")

    # logger.debug(f"here: {here}")
    # logger.debug(f"style path: {style_path}")

    style = str()
    with open(style_path) as fid:
        style = fid.read().replace("LOCAL_PATH", here)

    # print(style)
    if platform.system().lower() == 'darwin':  # see issue #12 on github
        mac_fix = '''
        QDockWidget::title
        {
            background-color: #31363b;
            text-align: center;
            height: 12px;
        }
        '''
        style += mac_fix

    return style
