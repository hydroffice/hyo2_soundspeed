from PySide import QtGui

from hyo.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

from hyo.soundspeedmanager.mainwin import MainWin


def main():
    app = QtGui.QApplication([])
    mw = MainWin()
    mw.show()
    logger.info(mw.lib)
    # print(mw.lib.cb.ask_location())
    # print(mw.lib.cb.ask_date())
    print(mw.lib.cb.ask_text_with_flag())
    app.exec_()


if __name__ == "__main__":
    main()
