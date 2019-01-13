import logging
import sys
from multiprocessing import freeze_support

from PySide2 import QtWidgets

from hyo2.sis.app.mainwin import MainWin


def set_logging(default_logging=logging.WARNING, hyo2_logging=logging.INFO, abc_logging=logging.DEBUG):
    logging.basicConfig(
        level=default_logging,
        format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s"
    )
    logging.getLogger("hyo2").setLevel(hyo2_logging)
    logging.getLogger("hyo2.sis").setLevel(abc_logging)


set_logging()


def sis_gui():
    """create the main windows and the event loop"""

    app = QtWidgets.QApplication(sys.argv)

    main = MainWin()
    main.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    freeze_support()
    sis_gui()
