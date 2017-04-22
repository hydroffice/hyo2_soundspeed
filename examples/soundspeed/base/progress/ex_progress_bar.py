from time import sleep
from PySide import QtGui

from hyo.soundspeed.logging import test_logging

from hyo.soundspeed.soundspeed import SoundSpeedLibrary


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