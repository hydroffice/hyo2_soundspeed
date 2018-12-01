import logging
import os

from PySide2 import QtWidgets

from hyo2.abc.app.qt_progress import QtProgress
from hyo2.soundspeed.base.setup_db import SetupDb

logger = logging.getLogger(__name__)


class AbstractWidget(QtWidgets.QMainWindow):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded

    def __init__(self, main_win, db):
        super(AbstractWidget, self).__init__()
        if type(db) != SetupDb:
            raise RuntimeError("Passed invalid settings db object: %s" % type(db))
        self.main_win = main_win
        self.db = db

        self.setContentsMargins(0, 0, 0, 0)

        # add a frame
        self.frame = QtWidgets.QFrame()
        self.setCentralWidget(self.frame)

        # progress dialog
        self.progress = QtProgress(parent=self)

    def setup_changed(self):
        pass
