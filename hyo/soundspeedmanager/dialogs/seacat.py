import os
import logging
import traceback
import datetime
import shutil
try:
    # TODO: winreg is windows-only, use QSettings instead
    import winreg  # python 3+
except:
    pass

from PySide import QtGui, QtCore
from PySide.QtGui import QMessageBox
from hyo.soundspeed.listener.seacat import sbe_serialcomms

logger = logging.getLogger(__name__)

from hyo.soundspeedmanager.widgets.widget import AbstractWidget


def add_btn(name, func, tooltip, layout):
    btn = QtGui.QPushButton(name)
    # noinspection PyUnresolvedReferences
    btn.clicked.connect(func)
    btn.setToolTip(tooltip)
    layout.addWidget(btn)
    return btn


def get_setting_string(keyname, default=None):
    settings = QtCore.QSettings()
    val = settings.value(keyname)
    if val is not None:
        val = str(val)
    else:
        val = default
    return val


def get_setting_float(keyname, default=None):
    settings = QtCore.QSettings()
    try:
        return float(settings.value(keyname, default))
    except TypeError:
        return default


def set_setting(keyname, val):
    settings = QtCore.QSettings()
    settings.setValue(keyname, val)


def set_setting_string(keyname, val):
    set_setting(keyname, val)


def set_setting_float(keyname, val):
    set_setting(keyname, val)


SEACAT_REGKEY = 'SEACAT'
COMPORT_SUBKEY = SEACAT_REGKEY + '\\COMPORTS'
COMPORT_NAME = 'COMPORT'


class SelectCastsDlg(QtGui.QDialog):

    def __init__(self, items, parent=None):
        super(SelectCastsDlg, self).__init__(parent)
        self.setWindowTitle("Seacat Download")
        layout = QtGui.QVBoxLayout()

        label = QtGui.QLabel("Select the casts to download")
        layout.addWidget(label)

        listWidget = self.listWidget = QtGui.QListWidget(self)
        for item in items:
            newItem = QtGui.QListWidgetItem("", listWidget)
            cb = QtGui.QCheckBox(item)
            listWidget.setItemWidget(newItem, cb)
        layout.addWidget(listWidget)

        self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        # noinspection PyUnresolvedReferences
        self.buttonBox.accepted.connect(self.accept)
        # noinspection PyUnresolvedReferences
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.setCenterButtons(True)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def get_selected(self):
        checked_items = []
        for index in range(self.listWidget.count()):
            w = self.listWidget.itemWidget(self.listWidget.item(index))
            if w.isChecked():
                checked_items.append(index)
                # print(index, w.text(), w.isChecked())
        return checked_items


class AutoSeacat:
    def __init__(self, port=None, progbar=None):
        self.progbar = progbar
        if progbar:
            progbar.start(title="Seacat", text="Waking up Seacat")
        self.sbe = open_seacat(port, progbar)

    def __enter__(self):
        return self.sbe

    def __exit__(self, *args, **kyargs):
        self.sbe.close()
        if self.progbar:
            self.progbar.end()


def open_seacat(port=None, progbar=None):
    # check for the last time this com port was opened
    if not port:
        port = get_last_comport()
    # portstr = sbe_serialcomms.SeacatComms.portstr(port)
    dbaud = int(get_setting_float("\\".join([COMPORT_SUBKEY, port, 'BAUD']), 0))
    dbits = int(get_setting_float("\\".join([COMPORT_SUBKEY, port, 'BITS']), 0))
    dparity = get_setting_string("\\".join([COMPORT_SUBKEY, port, 'PARITY']), '')
    sbe = sbe_serialcomms.SeacatComms.open_seacat(port, dbaud, dbits, dparity, progbar=progbar)
    if sbe.isOpen():
        set_setting("\\".join([COMPORT_SUBKEY, port, 'BAUD']), sbe.comlink.baudrate)
        set_setting("\\".join([COMPORT_SUBKEY, port, 'BITS']), sbe.comlink.bytesize)
        set_setting("\\".join([COMPORT_SUBKEY, port, 'PARITY']), sbe.comlink.parity)
    return sbe


def save_last_comport(comport):
    """integer part of COMxx port to be saved"""
    set_setting_string(COMPORT_SUBKEY + "\\" + COMPORT_NAME, comport)


def get_last_comport():
    comport = get_setting_string(COMPORT_SUBKEY + "\\" + COMPORT_NAME, "COM1")
    return comport
