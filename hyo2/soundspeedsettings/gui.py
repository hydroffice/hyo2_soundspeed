import sys
import traceback
import logging

from PySide2 import QtCore, QtWidgets

from hyo2.abc.app.app_style import AppStyle
from hyo2.soundspeedsettings.mainwin import MainWin
from hyo2.soundspeed.soundspeed import SoundSpeedLibrary

logger = logging.getLogger(__name__)


def qt_custom_handler(error_type, error_context):
    logger.info("Qt error: %s [%s]" % (str(error_type), str(error_context)))

    for line in traceback.format_stack():
        logger.debug("- %s" % line.strip())


QtCore.qInstallMessageHandler(qt_custom_handler)


def gui():
    """Run the Sound Speed Settings gui"""

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(AppStyle.load_stylesheet())

    lib = SoundSpeedLibrary()
    main = MainWin(lib=lib)
    main.show()

    sys.exit(app.exec_())
