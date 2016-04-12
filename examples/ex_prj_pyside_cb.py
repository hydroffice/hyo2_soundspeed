from __future__ import absolute_import, division, print_function, unicode_literals

from PySide import QtGui

# logging settings
import logging
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)

from hydroffice.soundspeedmanager.mainwin import MainWin


def main():
    app = QtGui.QApplication([])
    mw = MainWin()
    mw.show()
    logger.info(mw.prj)
    print(mw.prj.cb.ask_location())
    print(mw.prj.cb.ask_date())
    app.exec_()

if __name__ == "__main__":
    main()
