import logging
from datetime import datetime, timezone

from hyo2.ssm2.lib.profile.profile import Profile
from hyo2.ssm2.lib.profile.dicts import Dicts

logger = logging.getLogger(__name__)


class ProfileList:
    """"A thin wrapper around a list for sound speed profiles"""

    def __init__(self) -> None:
        self._list: list[Profile] = list()
        self._current_index: int | None = None

        # True only if loaded from a project db
        # The current use of this flag is in the app to change the behavior of the metadata dialog
        self.loaded_from_db: bool = False

    @classmethod
    def constant_gradient(cls, start_depth: float = 0.0,
                          start_temp: float = 12.94,
                          start_sal: float = 35.0,
                          start_speed: float = 1500.0,
                          end_depth: float = 1000.0,
                          end_temp: float = 12.94,
                          end_sal: float = 35.0,
                          end_speed: float = 1516.7,
                          thinned: bool = False
                          ) -> 'ProfileList':
        ssp = ProfileList()
        ssp.append()  # append a new profile
        # initialize probe/sensor type
        ssp.cur.meta.sensor_type = Dicts.sensor_types['Synthetic']
        ssp.cur.meta.probe_type = Dicts.probe_types['Unknown']
        ssp.cur.meta.latitude = 43.13555
        ssp.cur.meta.longitude = -70.9395
        ssp.cur.meta.utc_time = datetime.now(tz=timezone.utc)

        ssp.cur.init_data(2)

        ssp.cur.data.depth[0] = start_depth
        ssp.cur.data.temp[0] = start_temp
        ssp.cur.data.sal[0] = start_sal
        ssp.cur.data.speed[0] = start_speed

        ssp.cur.data.depth[1] = end_depth
        ssp.cur.data.temp[1] = end_temp
        ssp.cur.data.sal[1] = end_sal
        ssp.cur.data.speed[1] = end_speed

        ssp.cur.clone_data_to_proc()
        if thinned:
            ssp.cur.init_sis(2)

            ssp.cur.sis.depth[0] = start_depth
            ssp.cur.sis.temp[0] = start_temp
            ssp.cur.sis.sal[0] = start_sal
            ssp.cur.sis.speed[0] = start_speed
            ssp.cur.sis.flag[0] = Dicts.flags['thin']

            ssp.cur.sis.depth[1] = end_depth
            ssp.cur.sis.temp[1] = end_temp
            ssp.cur.sis.sal[1] = end_sal
            ssp.cur.sis.speed[1] = end_speed
            ssp.cur.sis.flag[1] = Dicts.flags['thin']
        else:
            ssp.cur.init_sis()  # initialize to zero

        return ssp

    @property
    def l(self) -> list[Profile]:
        return self._list

    @property
    def nr_profiles(self) -> int:
        return len(self._list)

    @property
    def cur(self) -> Profile:
        if self._current_index is None:
            raise RuntimeError("current index is None")
        return self.l[self._current_index]

    @property
    def current_index(self) -> int:
        if self._current_index is None:
            raise RuntimeError("current index is None")
        return self._current_index

    @current_index.setter
    def current_index(self, value: int) -> None:
        if (value >= len(self.l)) or (value < 0):
            raise RuntimeError("unable to set the current profile at index: %s (list sz: %s)" % (value, len(self.l)))
        self._current_index = value

    def clear(self) -> None:
        del self._list[:]
        self._list = list()
        self._current_index = None

    def append(self) -> None:
        self._list.append(Profile())
        self.current_index = len(self._list) - 1

    def append_profile(self, profile: Profile) -> None:
        self._list.append(profile)
        self.current_index = len(self._list) - 1

    def debug_plot(self, more: bool = False) -> None:
        """Create a debug plot with the data, optionally with the extra data if available"""
        for s in self.l:
            s.data_debug_plot(more=more)
            s.proc_debug_plot(more=more)
            s.sis_debug_plot(more=more)

    def __repr__(self) -> str:
        msg = "<ProfileList: %s>\n" % len(self.l)
        for i, p in enumerate(self.l):
            msg += "#%02d%s" % (i, p)
        return msg
