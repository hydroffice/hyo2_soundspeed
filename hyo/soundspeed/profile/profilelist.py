import logging

logger = logging.getLogger(__name__)

from hyo.soundspeed.profile.profile import Profile


class ProfileList:
    """"A thin wrapper around a list for sound speed profiles"""

    def __init__(self):
        self._list = list()
        self._current_index = None

        # True only if loaded from a project db
        # The current use of this flag is in the app to change the behavior of the metadata dialog
        self.loaded_from_db = False

    @property
    def l(self):
        return self._list

    @l.setter
    def l(self, value):
        if type(value) != Profile:
            raise RuntimeError("profile list received a %s type" % type(value))
        self._list = value

    @property
    def nr_profiles(self):
        return len(self._list)

    @property
    def cur(self):
        if self._current_index is None:
            raise RuntimeError("current index is None")
        return self.l[self._current_index]

    @property
    def current_index(self):
        if self._current_index is None:
            raise RuntimeError("current index is None")
        return self._current_index

    @current_index.setter
    def current_index(self, value):
        if (value >= len(self.l)) or (value < 0):
            raise RuntimeError("unable to set the current profile at index: %s (list sz: %s)" % (value, len(self.l)))
        self._current_index = value

    def clear(self):
        del self._list[:]
        self._list = list()
        self._current_index = None

    def append(self):
        self._list.append(Profile())
        self.current_index = len(self._list) - 1

    def append_profile(self, profile):
        self._list.append(profile)
        self.current_index = len(self._list) - 1

    def debug_plot(self, more=False):
        """Create a debug plot with the data, optionally with the extra data if available"""
        for s in self.l:
            s.data_debug_plot(more=more)
            s.proc_debug_plot(more=more)
            s.sis_debug_plot(more=more)

    def __repr__(self):
        msg = "<ProfileList: %s>\n" % len(self.l)
        for i, p in enumerate(self.l):
            msg += "#%02d%s" % (i, p)
        return msg
