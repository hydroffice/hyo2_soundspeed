from __future__ import absolute_import, division, print_function, unicode_literals

from PySide import QtGui

# logging settings
import logging
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)

from hydroffice.soundspeedmanager.dialogs.text_editor_dialog import TextEditorDialog
from hydroffice.soundspeed.soundspeed import SoundSpeedLibrary


def main():
    app = QtGui.QApplication([])
    # noinspection PyArgumentList
    app.setApplicationName('test')
    app.setOrganizationName("HydrOffice")
    app.setOrganizationDomain("hydroffice.org")

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
