import logging

from PySide2 import QtWidgets

from hyo2.soundspeedmanager.dialogs.multi_selection_dialog import MultiSelectionDialog
from hyo2.abc.lib.logging import set_logging

ns_list = ["hyo2.soundspeed", "hyo2.soundspeedmanager", "hyo2.soundspeedsettings"]
set_logging(ns_list=ns_list)

logger = logging.getLogger(__name__)

app = QtWidgets.QApplication([])

profiles = ["prof 1", "prof 2", "prof 3", "prof 4"]
ms_dlg = MultiSelectionDialog(title="Sea-Bird Seacat profiles", message="Select profiles:", items=profiles)
ret = ms_dlg.exec_()
if ret == QtWidgets.QDialog.Accepted:
    print(ms_dlg.selected_items())

# app.exec_()
