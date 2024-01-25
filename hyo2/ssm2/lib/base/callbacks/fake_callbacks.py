from datetime import datetime
import os
import random
import logging
from typing import Optional

from hyo2.ssm2.lib.base.callbacks.abstract_callbacks import AbstractCallbacks

logger = logging.getLogger(__name__)


class FakeCallbacks(AbstractCallbacks):
    """Used only for testing since the methods do not require user interaction"""

    def __init__(self) -> None:
        super(FakeCallbacks, self).__init__()

    def ask_number(self, title: Optional[str] = "", msg: Optional[str] = "Enter number", default: Optional[float] = 0.0,
                   min_value: Optional[float] = -2147483647.0, max_value: Optional[float] = 2147483647.0,
                   decimals: Optional[int] = 7) -> Optional[float]:
        return random.random() * 100.0

    def ask_text(self, title: Optional[str] = "", msg: Optional[str] = "Enter text") -> Optional[str]:
        return "Hello world"

    def ask_text_with_flag(self, title: Optional[str] = "", msg: Optional[str] = "Enter text",
                           flag_label: Optional[str] = "") -> tuple:
        return "Hello world", True

    def ask_date(self) -> Optional[datetime]:
        return datetime.utcnow()

    def ask_location(self, default_lat: Optional[float] = 43.13555, default_lon: Optional[float] = -70.9395) -> tuple:
        # noinspection PyBroadException
        try:
            _ = float(default_lat)
            _ = float(default_lon)

        except Exception:
            default_lat = 43.13555
            default_lon = -70.9395

        return default_lat + random.random(), default_lon + random.random()

    def ask_filename(self, saving: Optional[bool] = True, key_name: Optional[str] = None,
                     default_path: Optional[str] = ".",
                     title: Optional[str] = "Choose a path/filename", default_file: Optional[str] = "",
                     file_filter: Optional[str] = "All Files (*.*)", multi_file: Optional[bool] = False) -> str:
        return os.path.normpath(__file__)

    def ask_directory(self, key_name: Optional[str] = None, default_path: Optional[str] = ".",
                      title: Optional[str] = "Browse for folder", message: Optional[str] = "") -> str:
        return os.path.normpath(os.path.dirname(__file__))

    def ask_location_from_sis(self) -> bool:
        return True

    def ask_location_from_nmea(self) -> bool:
        return True    

    def ask_tss(self) -> Optional[float]:
        return 1500.0

    def ask_draft(self) -> Optional[float]:
        return 8.0

    def msg_tx_no_verification(self, name: str, protocol: str) -> None:
        """Profile transmitted but not verification available"""
        pass

    def msg_tx_sis_wait(self, name: str) -> None:
        """Profile transmitted, SIS is waiting for confirmation"""
        pass

    def msg_tx_sis_confirmed(self, name: str) -> None:
        """Profile transmitted, SIS confirmed"""
        pass

    def msg_tx_sis_not_confirmed(self, name: str, port: int) -> None:
        """Profile transmitted, SIS not confirmed"""
        pass
