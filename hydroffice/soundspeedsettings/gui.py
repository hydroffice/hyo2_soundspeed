from __future__ import absolute_import, division, print_function, unicode_literals

import sys
from PySide import QtGui

import logging

log = logging.getLogger(__name__)

from . import mainwin
from hydroffice.soundspeed.soundspeed import SoundSpeedLibrary


def gui():
    """Run the Sound Speed Settings gui"""

    app = QtGui.QApplication(sys.argv)

    lib = SoundSpeedLibrary()
    main = mainwin.MainWin(lib=lib)
    main.show()

    sys.exit(app.exec_())
