from PySide2 import QtWidgets

import logging

from hyo2.soundspeedmanager.dialogs.text_editor_dialog import TextEditorDialog
from hyo2.soundspeed.soundspeed import SoundSpeedLibrary
from hyo2.abc.lib.logging import set_logging

ns_list = ["hyo2.soundspeed", "hyo2.soundspeedmanager", "hyo2.soundspeedsettings"]
set_logging(ns_list=ns_list)

logger = logging.getLogger(__name__)


app = QtWidgets.QApplication([])
# noinspection PyArgumentList
app.setApplicationName('test')
app.setOrganizationName("HydrOffice")
app.setOrganizationDomain("hydroffice.org")

mw = QtWidgets.QMainWindow()
mw.show()

lib = SoundSpeedLibrary()

body = "<pre style='margin:3px;'><b>Test!</b>   #001:            OK</pre>" \
       "<pre style='margin:3px;'><b>Test!</b>   #002:            KO</pre>"

dlg = TextEditorDialog(title="Text", basename="test", body=body, main_win=mw, lib=lib, parent=None)
dlg.exec_()

# app.exec_()
