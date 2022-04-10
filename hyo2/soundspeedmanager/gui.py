import sys
import traceback
import logging

from PySide2 import QtCore, QtWidgets, QtGui

from hyo2.abc.lib.helper import Helper
from hyo2.abc.lib.logging import set_logging
from hyo2.abc.app.app_style import AppStyle
from hyo2.soundspeedmanager import app_info

set_logging(ns_list=["hyo2.abc", "hyo2.soundspeed", "hyo2.soundspeedmanager", "hyo2.soundspeedsettings",
                     "hyo2.surveydatamonitor"])
logger = logging.getLogger(__name__)


def qt_custom_handler(error_type: QtCore.QtMsgType, error_context: QtCore.QMessageLogContext, message: str):

    logger.info("Qt error: %s [%s, %s:%s:%d, v.%s] -> %s"
                % (error_type, error_context.category, error_context.file, error_context.function,
                   error_context.line, error_context.version, message))

    for line in traceback.format_stack():
        logger.debug("- %s" % line.strip())


QtCore.qInstallMessageHandler(qt_custom_handler)

app = None


def gui():
    """Create the application and show the Sound Speed Manager gui"""
    from hyo2.soundspeedmanager.mainwin import MainWin
    global app
    app = QtWidgets.QApplication([])
    app.setStyleSheet(AppStyle.load_stylesheet())

    if Helper.is_script_already_running():
        txt = "The app is already running!"
        logger.warning(txt)
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle("Multiple Instances of Sound Speed Manager")
        msg_box.setIconPixmap(QtGui.QPixmap(app_info.app_icon_path).scaled(QtCore.QSize(36, 36)))
        msg_box.setText('%s\n\nDo you want to continue? This might create issues.' % txt)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msg_box.setDefaultButton(QtWidgets.QMessageBox.No)
        reply = msg_box.exec_()
        if reply == QtWidgets.QMessageBox.No:
            sys.exit(app.exit())

    main_win = MainWin()
    sys.excepthook = main_win.exception_hook  # install the exception hook
    main_win.show()
    main_win.do()

    sys.exit(app.exec_())
