from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

logger = logging.getLogger(__name__)


class Progress(object):

    def __init__(self, qprogress=None):
        if qprogress:
            self.qt = True
            self._prog = qprogress()
        else:
            self.qt = False
            self._prog = None

    def start(self, text="Processing", abortion=False):
        if self.qt:
            self._prog.reset()
            if not abortion:
                self._prog.setCancelButton(None)
            self._prog.setMinimumDuration(1000)
            self._prog.setLabelText(text)
            self._prog.forceShow()
            self._prog.setValue(10)

    def update(self, value, text=None):
        if self.qt:
            self._prog.setValue(value)
            if text:
                self._prog.setLabelText(text)

    def end(self):
        if self.qt:
            self._prog.setValue(100)

    def was_canceled(self):
        if self.qt:
            return self._prog.wasCanceled()
        return False
