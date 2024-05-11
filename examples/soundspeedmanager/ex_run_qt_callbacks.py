from PySide6 import QtWidgets

import logging

from hyo2.ssm2.app.gui.soundspeedmanager.mainwin import MainWin
from hyo2.abc.lib.logging import set_logging

ns_list = ["hyo2.ssm2"]
set_logging(ns_list=ns_list)

logger = logging.getLogger(__name__)


app = QtWidgets.QApplication([])
mw = MainWin()
mw.show()
logger.info(mw.lib)
# print(mw.lib.cb.ask_location())
# print(mw.lib.cb.ask_date())
print(mw.lib.cb.ask_text_with_flag())
app.exec()
