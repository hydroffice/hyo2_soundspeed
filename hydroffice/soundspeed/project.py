from __future__ import absolute_import, division, print_function, unicode_literals

import logging

logger = logging.getLogger(__name__)

from .base.baseproject import BaseProject
from .base.settings import Settings
from .base.callbacks import Callbacks, AbstractCallbacks
from . import formats


class Project(BaseProject):
    """Sound Speed project"""

    def __init__(self, data_folder=None):
        """Initialization for the library"""
        super(Project, self).__init__(data_folder=data_folder)
        self.setup = Settings(data_folder=self.data_folder)
        self.cb = Callbacks()

    # --- callbacks

    def set_callbacks(self, cb):
        if not issubclass(type(cb), AbstractCallbacks):
            raise RuntimeError("invalid callbacks object")
        self.cb = cb

    # --- readers/writers
    @property
    def readers(self):
        return formats.readers

    @property
    def writers(self):
        return formats.writers

    # --- repr

    def __repr__(self):
        msg = "%s" % super(Project, self).__repr__()
        msg += "%s\n" % self.setup
        return msg
