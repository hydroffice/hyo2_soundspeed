from __future__ import absolute_import, division, print_function, unicode_literals

import logging

logger = logging.getLogger(__name__)

from hydroffice.soundspeed.base.progress.abstract_progress import AbstractProgress


class CliProgress(AbstractProgress):
    """Command-line interface implementation of a progress bar"""

    def __init__(self):
        super(CliProgress, self).__init__()

    @property
    def canceled(self):
        """Currently, always false"""
        return self._is_canceled

    def start(self, title="Processing", text="Please wait!", min_value=0, max_value=100,
              has_abortion=False, is_disabled=False):
        # has_abortion is not used for CLI implementation

        self._is_disabled = is_disabled
        if self._is_disabled:
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
        self._value = self._min + 0.1 * self._range

        self._is_canceled = False

        self._print()

    def update(self, value, text=None):
        if self._is_disabled:
            return

        if value < self._value:
            raise RuntimeError('attempt to update current progress value (%d) with a smaller value (%d)'
                               % (self._value, value))
        if (value < self._min) or (value >= self._max):
            raise RuntimeError('attempt to update current progress value (%d) outside valid range(%s %s)'
                               % (value, self._min, self._max))
        self._value = value
        if text is not None:
            self._text = text

        self._print()

    def add(self, quantum, text=None):
        if self._is_disabled:
            return

        tmp_value = self._value + quantum

        if tmp_value < self._value:
            raise RuntimeError('attempt to update current progress value (%d) with a smaller value (%d)'
                               % (self._value, tmp_value))
        if (tmp_value < self._min) or (tmp_value >= self._max):
            raise RuntimeError('attempt to update current progress value (%d) outside valid range(%s %s)'
                               % (tmp_value, self._min, self._max))

        self._value = tmp_value
        if text is not None:
            self._text = text

        self._print()

    def end(self):
        if self._is_disabled:
            return

        self._value = self._max
        self._text = 'Done!'

        self._print()

    def _print(self):
        print('[%s] %s: %.1f%%' % (self._title, self._text, (self._value - self._min) / self._range * 100))
