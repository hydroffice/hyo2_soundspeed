import logging
import os
import sys
import traceback

if os.environ.get("SSM_DEBUG"):
    # noinspection PyUnresolvedReferences
    from hyo2.abc2.lib.debug_import import DebugImport
    DebugImport(numpy=True, pyproj=True, gdal=True, qt=True, matplotlib=True, cartopy=True)

from PySide6 import QtCore, QtWidgets, QtGui

from hyo2.abc2.app.app_style.app_style import AppStyle
from hyo2.abc2.lib.gdal_aux import GdalAux
from hyo2.abc2.lib.logging import set_logging
from hyo2.abc2.lib.package.pkg_helper import PkgHelper
from hyo2.ssm2.app.gui.soundspeedmanager import app_info

set_logging(ns_list=["hyo2.abc2", "hyo2.ssm2", "hyo2.sdm3"])
logger = logging.getLogger(__name__)


def qt_custom_handler(error_type: QtCore.QtMsgType, error_context: QtCore.QMessageLogContext, message: str):
    if "Cannot read property 'id' of null" in message:
        return
    if "GLImplementation: desktop" in message:
        return
    logger.info("Qt error: %s [%s] -> %s" % (error_type, error_context, message))

    for line in traceback.format_stack():
        logger.debug("- %s" % line.strip())


QtCore.qInstallMessageHandler(qt_custom_handler)


def gui(use_sdm4: bool = False):
    """Create the application and show the Sound Speed Manager gui"""
    os.environ.get("SSM_DEBUG") and logger.debug("Init gui ...")
    from hyo2.ssm2.app.gui.soundspeedmanager.mainwin import MainWin

    os.environ.get("SSM_DEBUG") and logger.debug("Init app ...")
    app = QtWidgets.QApplication(sys.argv)
    AppStyle.apply(app=app)

    if PkgHelper.is_script_already_running():
        txt = "The app is already running!"
        logger.warning(txt)
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle("Multiple Instances of Sound Speed Manager")
        msg_box.setIconPixmap(QtGui.QPixmap(app_info.app_icon_path).scaled(QtCore.QSize(36, 36)))
        msg_box.setText('%s\n\nDo you want to continue? This might create issues.' % txt)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
        reply = msg_box.exec()
        if reply == QtWidgets.QMessageBox.StandardButton.No:
            sys.exit(app.exit())

    os.environ.get("SSM_DEBUG") and logger.debug("Init gdal aux ...")
    GdalAux.check_proj4_data(verbose=True)
    GdalAux.check_gdal_data(verbose=True)

    main_win = MainWin(use_sdm4=use_sdm4)
    sys.excepthook = main_win.exception_hook  # install the pkg_exception hook
    main_win.show()
    main_win.do()

    sys.exit(app.exec())
