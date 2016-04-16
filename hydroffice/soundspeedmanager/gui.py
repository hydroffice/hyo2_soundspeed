from __future__ import absolute_import, division, print_function, unicode_literals

import sys
from PySide import QtGui

import logging

log = logging.getLogger(__name__)

from . import mainwin


def gui():
    """Run the Sound Speed Manager gui"""

    app = QtGui.QApplication(sys.argv)

    main = mainwin.MainWin()
    main.show()
    main.do()

    sys.exit(app.exec_())
