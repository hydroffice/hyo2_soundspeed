import sys
from PySide import QtGui
from multiprocessing import freeze_support

import logging
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)

from hyo.sis import mainwin


def sis_gui():
    """create the main windows and the event loop"""

    app = QtGui.QApplication(sys.argv)

    main = mainwin.MainWin()
    main.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    freeze_support()
    sis_gui()
