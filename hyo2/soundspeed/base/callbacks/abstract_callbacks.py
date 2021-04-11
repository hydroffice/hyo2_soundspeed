from abc import ABCMeta, abstractmethod
import logging
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from hyo2.soundspeed.listener.sis.sis import Sis


logger = logging.getLogger(__name__)


class GeneralAbstractCallbacks(metaclass=ABCMeta):
    """Abstract class with several callbacks that has to be implemented for a new backend"""

    def __init__(self) -> None:
        self.sis_listener = None  # type: Optional[Sis]

    @abstractmethod
    def ask_number(self, title: Optional[str] = "", msg: Optional[str] = "Enter number", default: Optional[float] = 0.0,
                   min_value: Optional[float] = -2147483647.0, max_value: Optional[float] = 2147483647.0,
                   decimals: Optional[int] = 7) -> Optional[float]:
        """Ask user for number"""
        pass

    @abstractmethod
    def ask_text(self, title: Optional[str] = "", msg: Optional[str] = "Enter text") -> Optional[str]:
        """Ask user for text"""
        pass

    @abstractmethod
    def ask_text_with_flag(self, title: Optional[str] = "", msg: Optional[str] = "Enter text",
                           flag_label: Optional[str] = "") -> tuple:
        """Ask user for text with a flag optional"""
        pass

    @abstractmethod
    def ask_date(self) -> Optional[datetime]:
        """Ask user for date"""
        pass

    @abstractmethod
    def ask_location(self, default_lat: Optional[float] = None, default_lon: Optional[float] = None) -> tuple:
        """Ask user for location (it is not an abstract method because it is based on ask_number)"""
        pass

    @abstractmethod
    def ask_filename(self, saving: Optional[bool] = True, key_name: Optional[str] = None,
                     default_path: Optional[str] = ".",
                     title: Optional[str] = "Choose a path/filename", default_file: Optional[str] = "",
                     file_filter: Optional[str] = "All Files (*.*)", multi_file: Optional[bool] = False) -> str:
        """Ask user for filename(s) and remembers last location used if applicable.
        To store last location keyname must be a string and be a gui callback (not command line)."""
        pass

    @abstractmethod
    def ask_directory(self, key_name: Optional[str] = None, default_path: Optional[str] = ".",
                      title: Optional[str] = "Browse for folder", message: Optional[str] = "") -> str:
        """Ask user for a directory path and remembers last location used if applicable
        To store last location key name must be a string and be a gui callback (not command line)."""
        pass


class AbstractCallbacks(GeneralAbstractCallbacks, metaclass=ABCMeta):
    """Abstract class with several callbacks that has to be implemented for a new backend
    Specifies that the general callback exist as well as sound speed specific ones."""

    def __init__(self) -> None:
        super(AbstractCallbacks, self).__init__()

    @abstractmethod
    def ask_location_from_sis(self) -> bool:
        """Ask user for location"""
        pass

    @abstractmethod
    def ask_tss(self) -> Optional[float]:
        """Ask user for transducer sound speed"""
        pass

    @abstractmethod
    def ask_draft(self) -> Optional[float]:
        """Ask user for draft"""
        pass

    @abstractmethod
    def msg_tx_no_verification(self, name: str, protocol: str) -> None:
        """Profile transmitted but not verification available"""
        pass

    @abstractmethod
    def msg_tx_sis_wait(self, name: str) -> None:
        """Profile transmitted, SIS is waiting for confirmation"""
        pass

    @abstractmethod
    def msg_tx_sis_confirmed(self, name: str) -> None:
        """Profile transmitted, SIS confirmed"""
        pass

    @abstractmethod
    def msg_tx_sis_not_confirmed(self, name: str, port: int) -> None:
        """Profile transmitted, SIS not confirmed"""
        pass
