from __future__ import absolute_import, division, print_function, unicode_literals

import logging

logger = logging.getLogger(__name__)

from .base.baseproject import BaseProject
from .base.settings import Settings


class Project(BaseProject):
    """Sound Speed project"""

    def __init__(self, data_folder=None):
        """Initialization for the library"""
        super(Project, self).__init__(data_folder=data_folder)
        self.setup = Settings(data_folder=self.data_folder)

    # --- repr

    def __repr__(self):
        msg = "%s" % super(Project, self).__repr__()
        msg += "%s\n" % self.setup
        return msg
