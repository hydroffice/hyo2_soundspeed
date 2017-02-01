from __future__ import absolute_import, division, print_function, unicode_literals

from time import sleep
from PySide import QtGui

from hydroffice.soundspeed.logging import test_logging

from hydroffice.soundspeed.soundspeed import SoundSpeedLibrary


def main():
    app = QtGui.QApplication([])
    lib = SoundSpeedLibrary()
    lib.progress.start("TEST")
    sleep(0.5)
    lib.progress.update(30)
    sleep(0.5)
    lib.progress.update(60)
    sleep(0.5)
    lib.progress.end()
    app.exec_()

if __name__ == "__main__":
    main()