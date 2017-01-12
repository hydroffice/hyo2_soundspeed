from __future__ import absolute_import, division, print_function, unicode_literals

from PySide import QtGui

from hydroffice.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

from hydroffice.soundspeedmanager.mainwin import MainWin


def main():
    app = QtGui.QApplication([])
    mw = MainWin()
    mw.show()
    logger.info(mw.lib)
    print(mw.lib.cb.ask_location())
    print(mw.lib.cb.ask_date())
    app.exec_()

if __name__ == "__main__":
    main()
