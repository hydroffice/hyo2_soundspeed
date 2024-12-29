import logging
import os
from typing import TYPE_CHECKING

from PySide6 import QtWidgets

from hyo2.abc2.app.qt_progress import QtProgress
from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary

if TYPE_CHECKING:
    from hyo2.ssm2.app.gui.soundspeedmanager.mainwin import MainWin

logger = logging.getLogger(__name__)


class AbstractWidget(QtWidgets.QMainWindow):
    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.abspath(os.path.join(here, os.pardir, 'media')).replace("\\", "/")

    def __init__(self, main_win: 'MainWin', lib: SoundSpeedLibrary) -> None:
        QtWidgets.QMainWindow.__init__(self)
        self.main_win = main_win
        self.lib = lib

        self.setContentsMargins(0, 0, 0, 0)

        # add a frame
        self.frame = QtWidgets.QFrame()
        self.setCentralWidget(self.frame)

        # progress dialog
        self.progress = QtProgress(parent=self)

    def data_cleared(self):
        pass

    def data_imported(self):
        pass

    def data_stored(self):
        pass

    def data_removed(self):
        pass

    def server_started(self):
        pass

    def server_stopped(self):
        pass
