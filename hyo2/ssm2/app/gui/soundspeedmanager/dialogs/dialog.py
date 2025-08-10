import logging
import os
from typing import TYPE_CHECKING

from PySide6 import QtWidgets

from hyo2.abc2.app.qt_progress import QtProgress
if TYPE_CHECKING:
    from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary


logger = logging.getLogger(__name__)


class AbstractDialog(QtWidgets.QDialog):
    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.abspath(os.path.join(here, os.pardir, "media"))

    def __init__(self, main_win, lib: 'SoundSpeedLibrary', parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.main_win = main_win
        self.lib = lib

        self.setWindowFlags(self.windowFlags())

        # progress dialog
        self.progress = QtProgress(parent=self)
