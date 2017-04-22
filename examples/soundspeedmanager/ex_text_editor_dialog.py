from PySide import QtGui

from hyo.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

from hyo.soundspeedmanager.dialogs.text_editor_dialog import TextEditorDialog
from hyo.soundspeed.soundspeed import SoundSpeedLibrary


def main():
    app = QtGui.QApplication([])
    # noinspection PyArgumentList
    app.setApplicationName('test')
    app.setOrganizationName("HydrOffice")
    app.setOrganizationDomain("hyo.org")

    mw = QtGui.QMainWindow()
    mw.show()

    lib = SoundSpeedLibrary()

    body = "<pre style='margin:3px;'><b>Test!</b>   #001:            OK</pre>" \
           "<pre style='margin:3px;'><b>Test!</b>   #002:            KO</pre>"

    dlg = TextEditorDialog(title="Text", basename="test", body=body, main_win=mw, lib=lib, parent=None)
    dlg.exec_()

    # app.exec_()

if __name__ == "__main__":
    main()
