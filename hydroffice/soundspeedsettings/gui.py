from __future__ import absolute_import, division, print_function, unicode_literals

import sys
from PySide import QtGui

import logging

log = logging.getLogger(__name__)

from . import mainwin
from hydroffice.soundspeed.project import Project


def gui():
    """Run the Sound Speed Settings gui"""

    app = QtGui.QApplication(sys.argv)

    prj = Project()
    main = mainwin.MainWin(prj=prj)
    main.show()

    sys.exit(app.exec_())
