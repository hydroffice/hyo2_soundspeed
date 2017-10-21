import sys
from PySide import QtGui

import logging

logger = logging.getLogger(__name__)

from hyo.soundspeedmanager import mainwin
from hyo.soundspeedmanager.stylesheet import stylesheet


def gui():
    """Create the application and show the Sound Speed Manager gui"""

    app = QtGui.QApplication(sys.argv)
    app.setStyleSheet(stylesheet.load(pyside=True))

    main = mainwin.MainWin()
    main.show()

    # uncomment for execute helper function (development-mode only!)
    # main.do()

    sys.exit(app.exec_())
