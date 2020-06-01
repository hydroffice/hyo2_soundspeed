import logging
from PySide2 import QtWidgets

from hyo2.soundspeedmanager.dialogs.flaggable_input_dialog import FlaggableInputDialog
from hyo2.abc.lib.logging import set_logging

ns_list = ["hyo2.soundspeed", "hyo2.soundspeedmanager", "hyo2.soundspeedsettings"]
set_logging(ns_list=ns_list)

logger = logging.getLogger(__name__)


_ = QtWidgets.QApplication([])
print(FlaggableInputDialog.get_text_with_flag(None))
