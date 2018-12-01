from PySide2 import QtCore, QtGui, QtWidgets

import logging

logger = logging.getLogger(__name__)


class InfoViewerDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("SIS I/O Info")
        self.setContentsMargins(0, 0, 0, 0)

        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)
        vbox.setContentsMargins(5, 5, 5, 5)

        self.viewer = QtWidgets.QTextBrowser()
        self.viewer.resize(QtCore.QSize(280, 40))
        self.viewer.setTextColor(QtGui.QColor("#4682b4"))
        self.viewer.ensureCursorVisible()
        # create a monospace font
        font = QtGui.QFont("Courier New")
        font.setStyleHint(QtGui.QFont.TypeWriter)
        font.setFixedPitch(True)
        font.setPointSize(9)
        self.viewer.document().setDefaultFont(font)
        # set the tab size
        metrics = QtGui.QFontMetrics(font)
        self.viewer.setTabStopWidth(3 * metrics.width(' '))
        self.viewer.setReadOnly(True)
        vbox.addWidget(self.viewer)

    def append(self, text):

        try:
            self.viewer.append(text)
            self.viewer.moveCursor(QtGui.QTextCursor.End)

        except RuntimeError:
            logger.info("latest message: %s" % text)