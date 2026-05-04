import logging
from datetime import timedelta, datetime, timezone
from enum import IntEnum
from collections.abc import Callable
from typing import TYPE_CHECKING

# noinspection PyUnresolvedReferences
from hyo2.abc2.lib.package.pkg_helper import PkgHelper
# noinspection PyUnresolvedReferences
from hyo2.ssm2.lib.atlas.regofs_thredd_service import RegOfsThreddsService
if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary
    # noinspection PyUnresolvedReferences
    from hyo2.ssm2.lib.profile.profilelist import ProfileList

logger = logging.getLogger(__name__)


class RegOfsModel(IntEnum):
    # East Coast
    CBOFS = 10  # RG = True     # Format is GoMOFS
    DBOFS = 11  # RG = True     # Format is GoMOFS
    GoMOFS = 12  # RG = True     # Format is GoMOFS
    NYOFS = 13  # RG = False
    SJROFS = 14  # RG = False

    # Gulf of Mexico
    NGOFS2 = 20  # RG = True     # Format is GoMOFS
    TBOFS = 21  # RG = True     # Format is GoMOFS

    # Great Lakes
    LEOFS = 30  # RG = True     # Format is GoMOFS
    LMHOFS = 31  # RG = True    # Format is GoMOFS
    LOOFS = 33  # RG = True     # Format is GoMOFS
    LSOFS = 34  # RG = True     # Format is GoMOFS

    # Pacific Coast
    SSCOFS = 40  # RG = True     # Format is GoMOFS
    SFBOFS = 41  # RG = True     # Format is GoMOFS
    WCOFS = 42  # RG = True     # Format is GoMOFS

    @property
    def description(self) -> str:
        return {
            RegOfsModel.CBOFS: "Chesapeake Bay Operational Forecast System",
            RegOfsModel.DBOFS: "Delaware Bay Operational Forecast System",
            RegOfsModel.GoMOFS: "Gulf of Maine Operational Forecast System",
            RegOfsModel.NYOFS: "Port of New York and New Jersey Operational Forecast System",
            RegOfsModel.SJROFS: "St. John's River Operational Forecast System",
            RegOfsModel.NGOFS2: "Northern Gulf of Mexico Operational Forecast System",
            RegOfsModel.TBOFS: "Tampa Bay Operational Forecast System",
            RegOfsModel.LEOFS: "Lake Erie Operational Forecast System",
            RegOfsModel.LMHOFS: "Lake Michigan and Huron Operational Forecast System",
            RegOfsModel.LOOFS: "Lake Ontario Operational Forecast System",
            RegOfsModel.LSOFS: "Lake Superior Operational Forecast System",
            RegOfsModel.SSCOFS: "Salish Sea and Columbia River Operational Forecast System",
            RegOfsModel.SFBOFS: "San Francisco Bay Operational Forecast System",
            RegOfsModel.WCOFS: "West Coast Operational Forecast System",
        }[self]

    @property
    def slug(self) -> str:
        return self.name.lower()

    @property
    def cycle_hour(self) -> str:
        return (
            "03"
            if self in {
                RegOfsModel.NGOFS2,
                RegOfsModel.SSCOFS,
                RegOfsModel.SFBOFS,
                RegOfsModel.WCOFS,
            }
            else "00"
        )

    @property
    def test(self) -> tuple[float, float, datetime]:
        return {
            RegOfsModel.CBOFS: (37.985427, -76.311156, datetime.now(tz=timezone.utc)),
            RegOfsModel.DBOFS: (39.162802, -75.278057, datetime.now(tz=timezone.utc)),
            RegOfsModel.GoMOFS: (43.026480, -70.318824, datetime.now(tz=timezone.utc)),
            RegOfsModel.NYOFS: (40.662218, -74.049306, datetime.now(tz=timezone.utc)),
            RegOfsModel.SJROFS: (30.382518, -81.573615, datetime.now(tz=timezone.utc)),
            RegOfsModel.NGOFS2: (28.976225, -92.078882, datetime.now(tz=timezone.utc)),
            RegOfsModel.TBOFS: (27.762904, -82.557280, datetime.now(tz=timezone.utc)),
            RegOfsModel.LEOFS: (41.806023, -82.393283, datetime.now(tz=timezone.utc)),
            RegOfsModel.LMHOFS: (43.138573, -86.832183, datetime.now(tz=timezone.utc)),
            RegOfsModel.LOOFS: (43.753190, -76.826818, datetime.now(tz=timezone.utc)),
            RegOfsModel.LSOFS: (47.457546, -89.347715, datetime.now(tz=timezone.utc)),
            RegOfsModel.SSCOFS: (46.161403, -124.107396, datetime.now(tz=timezone.utc)),
            RegOfsModel.SFBOFS: (37.689510, -122.298514, datetime.now(tz=timezone.utc)),
            RegOfsModel.WCOFS: (37.779088, -124.209048, datetime.now(tz=timezone.utc)),
        }[self]

    def _thredds_url(self, input_date: datetime, service: RegOfsThreddsService) -> str:
        """Build a THREDDS URL for salinity and temperature data."""
        return (
            f"https://opendap.co-ops.nos.noaa.gov/thredds/{service}/NOAA/"
            f"{self.name.upper()}/MODELS/{input_date:%Y}/{input_date:%m}/{input_date:%d}/"
            f"{self.slug}.t{self.cycle_hour}z.{input_date:%Y%m%d}.regulargrid.n003.nc"
        )

    def download_url(self, input_date: datetime) -> str:
        """Build the download URL for salinity and temperature."""
        return self._thredds_url(
            input_date=input_date,
            service=RegOfsThreddsService.FILE_SERVER,
        )

    def valid_download_url(self, input_date: datetime | None = None) -> str | None:
        if input_date is None:
            input_date: datetime = datetime.now(tz=timezone.utc)

        url = self.download_url(input_date)
        if not PkgHelper.check_url(url=url):
            logger.debug("today's file not available, falling back to yesterday")
            input_date: datetime = input_date - timedelta(days=1)
            url = self.download_url(input_date)

        if not PkgHelper.check_url(url=url):
            logger.info("no valid file found for today or yesterday")
            return None

        return url

    def opendap_url(self, input_date: datetime) -> str:
        """Build the OPeNDAP URL for salinity and temperature."""
        return self._thredds_url(
            input_date=input_date,
            service=RegOfsThreddsService.DODS_C,
        )

    def valid_opendap_url(self, input_date: datetime | None = None) -> str | None:
        if input_date is None:
            input_date: datetime = datetime.now(tz=timezone.utc)

        url = self.opendap_url(input_date)
        if not PkgHelper.check_opendap_url(base_url=url):
            logger.debug("today's file not available, falling back to yesterday")
            input_date: datetime = input_date - timedelta(days=1)
            url = self.opendap_url(input_date)

        if not PkgHelper.check_opendap_url(base_url=url):
            logger.info("no valid file found for today or yesterday")
            return None

        return url

    def lib_func_has_model(self, lib: 'SoundSpeedLibrary') -> Callable[[], bool]:
        return getattr(lib, f"has_{self.slug}")

    def lib_func_download_model(self, lib: 'SoundSpeedLibrary') -> Callable[[], bool]:
        return getattr(lib, f"download_{self.slug}")

    def lib_func_query(self, lib: 'SoundSpeedLibrary') -> Callable[[], 'ProfileList']:
        atlas = getattr(lib.atlases, self.slug)
        return getattr(atlas, "query")
