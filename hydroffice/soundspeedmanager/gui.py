import sys
from PySide import QtGui

import logging

logger = logging.getLogger(__name__)

from . import mainwin


def gui():
    """Create the application and show the Sound Speed Manager gui"""

    app = QtGui.QApplication(sys.argv)

    main = mainwin.MainWin()
    main.show()

    # uncomment for execute helper function (development-mode only!)
    # main.do()

    sys.exit(app.exec_())
