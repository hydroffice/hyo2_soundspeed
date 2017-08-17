# logging settings
import logging
import os
import sys

from PySide import QtCore
from PySide import QtGui

logger = logging.getLogger(__name__)

from hyo.sis import __doc__ as sis_name
from hyo.sis import __version__ as sis_version
from hyo.sis.gui import controlpanel


class MainWin(QtGui.QMainWindow):

    here = os.path.abspath(os.path.dirname(__file__))
    media = os.path.join(here, "media")

    def __init__(self):
        super().__init__()

        self.name = sis_name
        self.version = sis_version

        # setup default project folder
        self.projects_folder = self.here

        self.setWindowTitle('%s v.%s' % (self.name, self.version))
        # noinspection PyArgumentList
        _app = QtCore.QCoreApplication.instance()
        _app.setApplicationName('%s' % self.name)
        _app.setOrganizationName("HydrOffice")
        _app.setOrganizationDomain("hydroffice.org")

        # set icons
        icon_info = QtCore.QFileInfo(os.path.join(self.here, 'media', 'favicon.png'))
        self.setWindowIcon(QtGui.QIcon(icon_info.absoluteFilePath()))
        if (sys.platform == 'win32') or (os.name is "nt"):

            try:
                # This is needed to display the app icon on the taskbar on Windows 7
                import ctypes
                app_id = '%s v.%s' % (self.name, self.version)
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

            except AttributeError as e:
                logger.debug("Unable to change app icon: %s" % e)

        self.panel = controlpanel.ControlPanel()
        self.setCentralWidget(self.panel)

    def _do_you_really_want(self, title="Quit", text="quit"):
        """helper function that show to the user a message windows asking to confirm an action"""
        msg_box = QtGui.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setIconPixmap(QtGui.QPixmap(os.path.join(self.media, 'favicon.png')).scaled(QtCore.QSize(36, 36)))
        msg_box.setText('Do you really want to %s?' % text)
        msg_box.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        msg_box.setDefaultButton(QtGui.QMessageBox.No)
        return msg_box.exec_()

    def closeEvent(self, event):
        """ actions to be done before close the app """
        reply = self._do_you_really_want("Quit", "quit %s" % self.name)

        if reply == QtGui.QMessageBox.Yes:

            event.accept()
            self.panel.stop_emulation()
            super().closeEvent(event)

        else:
            event.ignore()
