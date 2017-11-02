import time
from PySide import QtGui

from hyo.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

from hyo.soundspeedmanager.dialogs.multi_selection_dialog import MultiSelectionDialog

app = QtGui.QApplication([])

profiles = ["prof 1", "prof 2", "prof 3", "prof 4"]
ms_dlg = MultiSelectionDialog(title="Sea-Bird Seacat profiles", message="Select profiles:", items=profiles)
ret = ms_dlg.exec_()
if ret == QtGui.QDialog.Accepted:
    print(ms_dlg.selected_items())

# app.exec_()