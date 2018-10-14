from PySide import QtCore, QtGui
from typing import Optional
import logging

logger = logging.getLogger(__name__)

from hyo.soundspeed.base.progress.abstract_progress import AbstractProgress


class QtProgress(AbstractProgress):
    """Command-line interface implementation of a progress bar"""

    def __init__(self, parent: QtCore.QObject):
        super(QtProgress, self).__init__()
        self._parent = parent
        self._qt_app = QtGui.QApplication
        self._progress = None

    @property
    def canceled(self) -> bool:
        """Currently, always false"""
        if self._progress is not None:
            self._is_canceled = self._progress.wasCanceled()
        return self._is_canceled

    def start(self, title: str="Processing", text: str="Ongoing processing. Please wait!",
              min_value: float=0.0, max_value: float=100.0,
              has_abortion=False, is_disabled=False) -> None:

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
        self._value = 0

        self._is_canceled = False
        if self._progress is None:
            self._progress = QtGui.QProgressDialog(self._parent)
        self._progress.setWindowTitle(title)
        self._progress.setWindowModality(QtCore.Qt.WindowModal)
        if not has_abortion:
            self._progress.setCancelButton(None)
        self._progress.setMinimumDuration(1000)

        self._display()
        self._progress.setVisible(True)

    def update(self, value: Optional[float]=None, text: Optional[str]=None) -> None:
        if self._is_disabled:
            return

        if value is not None:
            new_percentage = ((value - self._min) / self._range) * 100
            if new_percentage < self._value:
                raise RuntimeError('attempt to update current progress value (%d) with a smaller value (%d)'
                                   % (self._value, new_percentage))
            if (value < self._min) or (value > self._max):
                raise RuntimeError('attempt to update current progress value (%d) outside valid range(%s %s)'
                                   % (value, self._min, self._max))
            self._value = new_percentage

        if text is not None:
            self._text = text

        self._display()

    def add(self, quantum: float, text: Optional[str]=None) -> None:
        if self._is_disabled:
            return

        old_value = ((self._value / 100) * self._range) + self._min
        tmp_value = old_value + quantum

        if tmp_value < self._value:
            raise RuntimeError('attempt to update current progress value (%d) with a smaller value (%d)'
                               % (self._value, tmp_value))
        if (tmp_value < self._min) or (tmp_value > self._max):
            raise RuntimeError('attempt to update current progress value (%d) outside valid range(%s %s)'
                               % (tmp_value, self._min, self._max))

        self._value = ((tmp_value - self._min) / self._range) * 100
        if text is not None:
            self._text = text

        self._display()

    def end(self, text: Optional[str]=None) -> None:
        self._value = self._max
        if text is None:
            self._text = 'Done!'
        else:
            self._text = text

        self._display()
        self._progress.setHidden(True)

    def _display(self) -> None:

        self._progress.setLabelText(self._text)
        self._progress.forceShow()
        self._progress.setValue(self._value)

        # noinspection PyArgumentList
        self._qt_app.processEvents()
