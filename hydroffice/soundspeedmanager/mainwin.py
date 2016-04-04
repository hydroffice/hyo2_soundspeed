from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys

from PySide import QtGui
from PySide import QtCore

import logging
logger = logging.getLogger(__name__)

from . import __version__ as ssm_version
from hydroffice.soundspeed.project import Project
from .callbacks import Callbacks


class MainWin(QtGui.QMainWindow):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        # create the project
        self.prj = Project()
        self.prj.set_callbacks(Callbacks(self))  # set the PySide callbacks

        # set the application name
        self.name = "Sound Speed Manager"
        self.version = ssm_version
        self.setWindowTitle('%s v.%s' % (self.name, self.version))
        self.setMinimumSize(800, 600)
        _app = QtCore.QCoreApplication.instance()
        _app.setApplicationName('Hush v.%s' % self.version)
        _app = QtCore.QCoreApplication.instance()
        _app.setOrganizationName("CCOMJHC")
        _app.setOrganizationDomain("ccom.unh.edu")

        # set icons
        icon_info = QtCore.QFileInfo(os.path.join(self.here, 'media', 'favicon.png'))
        self.setWindowIcon(QtGui.QIcon(icon_info.absoluteFilePath()))
        if (sys.platform == 'win32') or (os.name is "nt"):  # is_windows()
            try:
                # This is needed to display the app icon on the taskbar on Windows 7
                import ctypes
                app_id = '%s v.%s' % (self.name, self.version)
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
            except AttributeError as e:
                logger.debug("Unable to change app icon: %s" % e)

        # set palette
        style_info = QtCore.QFileInfo(os.path.join(self.here, 'styles', 'main.stylesheet'))
        style_content = open(style_info.filePath()).read()
        self.setStyleSheet(style_content)

