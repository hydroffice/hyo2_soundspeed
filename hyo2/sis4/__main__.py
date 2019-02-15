import logging
import sys
from multiprocessing import freeze_support
from PySide2 import QtWidgets
from hyo2.sis4.app import mainwin

logging.basicConfig(level=logging.WARNING, format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s")
logging.getLogger("hyo2").setLevel(logging.INFO)
logging.getLogger("hyo2.sis4").setLevel(logging.DEBUG)

def sis_gui():
    """create the main windows and the event loop"""

    app = QtWidgets.QApplication(sys.argv)

    main = mainwin.MainWin()
    main.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    freeze_support()
    sis_gui()
