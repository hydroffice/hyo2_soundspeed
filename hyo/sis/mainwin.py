import os, sys
from PySide import QtGui
from PySide import QtCore

# logging settings
import logging
logger = logging.getLogger(__name__)

from hyo.sis import __doc__ as sis_name
from hyo.sis import __version__ as sis_version
from hyo.sis import controlpanel


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
