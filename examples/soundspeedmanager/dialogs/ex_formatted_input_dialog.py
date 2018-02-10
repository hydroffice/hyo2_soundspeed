from PySide import QtGui

from hyo.soundspeed.logging import test_logging

import logging
logger = logging.getLogger()

from hyo.soundspeedmanager.dialogs.formatted_input_dialog import FormattedInputDialog


def main():
    _ = QtGui.QApplication([])
    print(FormattedInputDialog.get_format_text(None))


if __name__ == "__main__":
    main()
