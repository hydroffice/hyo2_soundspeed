import logging
from PySide2 import QtWidgets

from hyo2.soundspeedmanager.dialogs.flaggable_input_dialog import FlaggableInputDialog

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


_ = QtWidgets.QApplication([])
print(FlaggableInputDialog.get_text_with_flag(None))
