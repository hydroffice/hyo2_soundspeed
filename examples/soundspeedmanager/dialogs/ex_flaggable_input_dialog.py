from PySide import QtGui

from hyo.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

from hyo.soundspeedmanager.dialogs.flaggable_input_dialog import FlaggableInputDialog


def main():
    _ = QtGui.QApplication([])
    print(FlaggableInputDialog.get_text_with_flag(None))


if __name__ == "__main__":
    main()
