import logging

from PySide6 import QtWidgets

from hyo2.abc2.app.qt_progress import QtProgress
from hyo2.ssm2.lib.base.setup_db import SetupDb

logger = logging.getLogger(__name__)


class AbstractWidget(QtWidgets.QMainWindow):

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
