from __future__ import absolute_import, division, print_function, unicode_literals

from PySide import QtCore, QtGui
import logging

logger = logging.getLogger(__name__)

from hydroffice.soundspeed.base.progress.abstract_progress import AbstractProgress


class QtProgress(AbstractProgress):
    """Command-line interface implementation of a progress bar"""

    def __init__(self, parent):
        super(QtProgress, self).__init__()
        self._parent = parent
        self._qt_app = QtGui.QApplication
        self._progress = None

    @property
    def canceled(self):
        """Currently, always false"""
        if self._progress is not None:
            self._is_canceled = self._progress.wasCanceled()
        return self._is_canceled

    def start(self, title="Processing", text="Ongoing processing. Please wait!", min_value=0, max_value=100,
              has_abortion=False, is_disabled=False):

        self._is_disabled = is_disabled
        if is_disabled:
            return

        if title is not None:
            self._title = title
        if text is not None:
            self._text = text

        # set initial values
        if min_value >= max_value:
            raise RuntimeError("invalid min and max values: min %d, max %d" % (min_value, max_value))
        self._min = min_value
        self._max = max_value
        self._range = self._max - self._min
        self._value = self._min

        self._is_canceled = False

        self._progress = QtGui.QProgressDialog(self._parent)
        self._progress.setWindowTitle(title)
        self._progress.setWindowModality(QtCore.Qt.WindowModal)
        if not has_abortion:
            self._progress.setCancelButton(None)
        self._progress.setMinimumDuration(1000)

        self._display()

    def update(self, value=None, text=None):
        if self._is_disabled:
            return

        if value is not None:
            if value < self._value:
                raise RuntimeError('attempt to update current progress value (%d) with a smaller value (%d)'
                                   % (self._value, value))
            if (value < self._min) or (value > self._max):
                raise RuntimeError('attempt to update current progress value (%d) outside valid range(%s %s)'
                                   % (value, self._min, self._max))
            self._value = value

        if text is not None:
            self._text = text

        self._display()

    def add(self, quantum, text=None):
        if self._is_disabled:
            return

        tmp_value = self._value + quantum

        if tmp_value < self._value:
            raise RuntimeError('attempt to update current progress value (%d) with a smaller value (%d)'
                               % (self._value, tmp_value))
        if (tmp_value < self._min) or (tmp_value > self._max):
            raise RuntimeError('attempt to update current progress value (%d) outside valid range(%s %s)'
                               % (tmp_value, self._min, self._max))

        self._value = tmp_value
        if text is not None:
            self._text = text

        self._display()

    def end(self):
        self._value = self._max
        self._text = 'Done!'

        self._display()
        self._progress.setHidden(True)

    def _display(self):
        # noinspection PyArgumentList
        self._qt_app.processEvents()

        self._progress.setLabelText(self._text)
        self._progress.forceShow()
        self._progress.setValue(self._value)
