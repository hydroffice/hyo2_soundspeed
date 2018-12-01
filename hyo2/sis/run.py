import logging
import sys
from multiprocessing import freeze_support

from PySide import QtGui

logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)

from hyo2.sis.gui import mainwin


def sis_gui():
    """create the main windows and the event loop"""

    app = QtWidgets.QApplication(sys.argv)

    main = mainwin.MainWin()
    main.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    freeze_support()
    sis_gui()
