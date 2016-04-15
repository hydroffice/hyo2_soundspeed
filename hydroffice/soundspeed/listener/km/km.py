from __future__ import absolute_import, division, print_function, unicode_literals

import logging

logger = logging.getLogger(__name__)

from ..abstract import AbstractListener
# from ...profile.profile import Profile
# from ...profile.profilelist import ProfileList
# from ...profile.dicts import Dicts
# from ...profile.oceanography import Oceanography as Oc


class Km(AbstractListener):
    """Konsberg SIS listener"""

    def __init__(self, prj):
        super(Km, self).__init__(prj=prj)
        self.name = self.__class__.__name__
        self.desc = "Kongsberg SIS"

    def __repr__(self):
        msg = "%s" % super(Km, self).__repr__()
        # msg += "  <has data loaded: %s>\n" % self.has_data_loaded
        return msg

