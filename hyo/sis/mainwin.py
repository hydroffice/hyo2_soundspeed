import os, sys
from PySide import QtGui
from PySide import QtCore

# logging settings
import logging
logger = logging.getLogger(__name__)

from . import __doc__ as lib_name
from . import __version__ as lib_version
from . import controlpanel


class MainWin(QtGui.QMainWindow):
    """Main window"""

    here = os.path.abspath(os.path.dirname(__file__))
    media = os.path.join(here, "media")

    def __init__(self):
        super(MainWin, self).__init__()
        logger.debug("init")

        self.name = lib_name
        self.version = lib_version

        # setup default project folder
        self.projects_folder = self.here

        self.setWindowTitle('%s v.%s' % (self.name, self.version))
        app = QtCore.QCoreApplication.instance()
        app.setOrganizationName("CCOMJHC")
        app.setOrganizationDomain("ccom.unh.edu")
        app.setApplicationName('%s %s' % (self.name, self.version))

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
