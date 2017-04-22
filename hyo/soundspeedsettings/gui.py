import sys
from PySide import QtGui

import logging

logger = logging.getLogger(__name__)

from . import mainwin
from hyo.soundspeed.soundspeed import SoundSpeedLibrary


def gui():
    """Run the Sound Speed Settings gui"""

    app = QtGui.QApplication(sys.argv)

    lib = SoundSpeedLibrary()
    main = mainwin.MainWin(lib=lib)
    main.show()

    sys.exit(app.exec_())
