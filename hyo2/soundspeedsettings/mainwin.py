import logging
import sys
import traceback

from PySide2 import QtCore, QtGui, QtWidgets

from hyo2.abc.app.dialogs.exception.exception_dialog import ExceptionDialog

from hyo2.soundspeed import lib_info
from hyo2.soundspeedsettings import app_info
from hyo2.soundspeedsettings.widgets.main import Main
from hyo2.soundspeedsettings.widgets.general import General
from hyo2.soundspeedsettings.widgets.input import Input
from hyo2.soundspeedsettings.widgets.output import Output
from hyo2.soundspeedsettings.widgets.listeners import Listeners

from hyo2.soundspeed.soundspeed import SoundSpeedLibrary

logger = logging.getLogger(__name__)


class MainWin(QtWidgets.QMainWindow):

    def __init__(self, lib, main_win=None):
        super().__init__()

        # check passed input parameters
        if not isinstance(lib, SoundSpeedLibrary):
            raise RuntimeError("Invalid type (%s) in place of a Project instance" % type(lib))
        self.lib = lib
        self.db = lib.settings_db()
        self.main_win = main_win

        # set the application name and the version
        self.name = app_info.app_name
        self.version = app_info.app_version
        self.setWindowTitle('%s v.%s' % (self.name, self.version))

        # only called when stand-alone (without Sound Speed Manager)
        # noinspection PyArgumentList
        _app = QtCore.QCoreApplication.instance()
        if _app.applicationName() == 'python':
            _app.setApplicationName('%s v.%s' % (self.name, self.version))
            _app.setOrganizationName("HydrOffice")
            _app.setOrganizationDomain("hydroffice.org")
            logger.debug("set application name: %s" % _app.applicationName())

            # set icons
            self.setWindowIcon(QtGui.QIcon(app_info.app_icon_path))

        # make tabs
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabPosition(QtWidgets.QTabWidget.South)
        self.setCentralWidget(self.tabs)
        self.tabs.setIconSize(QtCore.QSize(45, 45))

        # main
        self.tab_main = Main(db=self.db, main_win=self)
        idx = self.tabs.insertTab(0, self.tab_main, "Main")
        self.tabs.setTabToolTip(idx, "Available setups")
        # general
        self.tab_general = General(db=self.db, main_win=self)
        idx = self.tabs.insertTab(1, self.tab_general, "General")
        self.tabs.setTabToolTip(idx, "General setup")
        # input
        self.tab_input = Input(db=self.db, main_win=self)
        idx = self.tabs.insertTab(2, self.tab_input, "Input")
        self.tabs.setTabToolTip(idx, "Input setup")
        # listeners
        self.tab_listeners = Listeners(db=self.db, main_win=self)
        idx = self.tabs.insertTab(3, self.tab_listeners, "Listeners")
        self.tabs.setTabToolTip(idx, "Listeners setup")
        # output
        self.tab_output = Output(db=self.db, main_win=self)
        idx = self.tabs.insertTab(4, self.tab_output, "Output")
        self.tabs.setTabToolTip(idx, "Output setup")

        self.setup_changed()  # trigger the first update of all the tabs

    def set_editable(self, editable):
        """Helper function to disable/enable all the tabs"""
        if editable:
            self.tab_main.setEnabled(True)
            self.tab_general.setEnabled(True)
            self.tab_input.setEnabled(True)
            self.tab_output.setEnabled(True)
            self.tab_listeners.setEnabled(True)

        else:
            self.tab_main.setDisabled(True)
            self.tab_general.setDisabled(True)
            self.tab_input.setDisabled(True)
            self.tab_output.setDisabled(True)
            self.tab_listeners.setDisabled(True)

    def reload_settings(self):
        logger.debug("reload settings")
        try:
            self.lib.reload_settings_from_db()
        except RuntimeError as e:
            msg = "Issue in reloading settings\n%s" % e
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Settings error", msg, QtWidgets.QMessageBox.Ok)
            return

    def setup_changed(self):
        """Method used to update all the tabs (except the main)"""
        tabs_nr = self.tabs.count()
        for i in range(tabs_nr):
            self.tabs.widget(i).setup_changed()

    def exception_hook(self, ex_type: type, ex_value: BaseException, tb: traceback) -> None:
        sys.__excepthook__(ex_type, ex_value, tb)

        # first manage case of not being an exception (e.g., keyboard interrupts)
        if not issubclass(ex_type, Exception):
            msg = str(ex_value)
            if not msg:
                msg = ex_value.__class__.__name__
            logger.info(msg)
            self.close()
            return

        dlg = ExceptionDialog(app_info=app_info, lib_info=lib_info, ex_type=ex_type, ex_value=ex_value, tb=tb)
        ret = dlg.exec_()
        if ret == QtWidgets.QDialog.Rejected:
            if not dlg.user_triggered:
                self.close()
        else:
            logger.warning("ignored exception")
