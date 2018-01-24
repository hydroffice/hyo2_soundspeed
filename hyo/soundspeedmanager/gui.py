import sys
from PySide import QtGui, QtCore

import logging

logger = logging.getLogger(__name__)

from hyo.soundspeedmanager import mainwin
from hyo.soundspeedmanager.stylesheet import stylesheet


def qt_custom_handler(error_type, error_context):
    logger.info("Qt error: %s [%s]" % (str(error_type), str(error_context)))


QtCore.qInstallMsgHandler(qt_custom_handler)


def gui():
    """Create the application and show the Sound Speed Manager gui"""

    app = QtGui.QApplication(sys.argv)
    app.setStyleSheet(stylesheet.load(pyside=True))

    main = mainwin.MainWin()
    main.show()

    # uncomment for execute helper function (development-mode only!)
    # main.do()

    sys.exit(app.exec_())
