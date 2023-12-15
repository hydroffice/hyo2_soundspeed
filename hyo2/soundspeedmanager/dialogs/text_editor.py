import logging
from PySide6 import QtGui, QtWidgets

logger = logging.getLogger(__name__)


class TextEditor(QtWidgets.QTextEdit):

    def __init__(self):
        super(TextEditor, self).__init__()

        self._dirty = False
        self._first_save = True
        self._original = None
        self._basename = None
        self._is_raw = True

        # noinspection PyUnresolvedReferences
        self.textChanged.connect(self._none)

        self.setReadOnly(True)

        # create a mono-space font
        font = QtGui.QFont()
        font.setFamily("Courier")
        font.setStyleHint(QtGui.QFont.Monospace)
        font.setFixedPitch(True)
        font.setPointSize(9)
        self.setFont(font)
        # set the tab size
        metrics = QtGui.QFontMetrics(font)
        # noinspection PyArgumentList
        self.setTabStopWidth(3 * metrics.width(' '))

    @property
    def dirty(self):
        return self._dirty or self._first_save

    @property
    def current_row(self):
        return self.textCursor().blockNumber() + 1

    @property
    def current_col(self):
        return self.textCursor().columnNumber() + 1

    def set_read_only(self, value):
        self.setReadOnly(value)

    def view_raw_text(self):
        # noinspection PyUnresolvedReferences
        self.textChanged.disconnect()
        # noinspection PyUnresolvedReferences
        self.textChanged.connect(self._none)

        self._is_raw = True
        self.setPlainText(self.toHtml())

    def view_html_text(self):
        # noinspection PyUnresolvedReferences
        self.textChanged.disconnect()
        # noinspection PyUnresolvedReferences
        self.textChanged.connect(self._text_changed)

        self._is_raw = False
        self.setHtml(self.toPlainText())

    def set_html_text(self, body):
        self.setHtml(body)
        self._original = [s.strip() for s in self.toPlainText().splitlines() if s.strip()]
        self._dirty = True
        self._is_raw = False
        self._first_save = True

        # noinspection PyUnresolvedReferences
        self.textChanged.disconnect()
        # noinspection PyUnresolvedReferences
        self.textChanged.connect(self._text_changed)

    def save_txt(self, file_path, append):

        if append:
            fid = open(file_path, 'a')
            fid.write('\n\n---\n')

        else:
            fid = open(file_path, 'w')

        fid.write(self.toPlainText())
        self._original = [s.strip() for s in self.toPlainText().splitlines() if s.strip()]
        self._dirty = False
        if self._first_save:
            self._first_save = False

    def _text_changed(self):

        if not self._is_raw:
            self._dirty = self._original != [s.strip() for s in self.toPlainText().splitlines() if s.strip()]

    def _none(self):
        pass
