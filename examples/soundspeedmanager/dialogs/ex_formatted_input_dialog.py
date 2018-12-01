from PySide2 import QtWidgets

import logging

from hyo2.soundspeedmanager.dialogs.formatted_input_dialog import FormattedInputDialog


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

_ = QtWidgets.QApplication([])
print(FormattedInputDialog.get_format_text(None))
