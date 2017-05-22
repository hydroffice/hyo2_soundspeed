from abc import ABCMeta, abstractmethod
import logging

logger = logging.getLogger(__name__)


class GeneralAbstractCallbacks(object):
    """Abstract class with several callbacks that has to be implemented for a new backend"""

    __metaclass__ = ABCMeta

    @abstractmethod
    def ask_number(self, title="", msg="Enter number", default=0.0,
                   min_value=-2147483647.0, max_value=2147483647.0, decimals=7):
        """Ask user for number"""
        pass

    @abstractmethod
    def ask_text(self, title="", msg="Enter text"):
        """Ask user for text"""
        pass

    @abstractmethod
    def ask_date(self):
        """Ask user for date"""
        pass

    def ask_location(self, default_lat=43.13555, default_lon=-70.9395):
        """Ask user for location (it is not an abstract method because it is based on ask_number)"""

        try:
            _ = float(default_lat)
            _ = float(default_lon)

        except Exception:
            default_lat = 43.13555
            default_lon = -70.9395

        # latitude
        lat = self.ask_number(title="Location", msg="Enter latitude as dd.ddd:", default=default_lat,
                              min_value=-90.0, max_value=90.0, decimals=7)

        if lat is not None:  # don't check for lon if lat already failed
            # longitude
            lon = self.ask_number(title="Location", msg="Enter longitude as dd.ddd:", default=default_lon,
                                  min_value=-180.0, max_value=180.0, decimals=7)
        else:
            lon = None

        if (lat is None) or (lon is None):  # return None if one of the two is invalid
            return None, None

        return lat, lon

    @abstractmethod
    def ask_filename(self, saving=True, key_name=None, default_path=".",
                     title="Choose a path/filename", default_file="",
                     file_filter="All Files|*.*", multi_file=False):
        """Ask user for filename(s) and remembers last location used if applicable.
        To store last location keyname must be a string and be a gui callback (not command line)."""
        pass

    @abstractmethod
    def ask_directory(self, key_name=None, default_path=".",
                      title="Browse for folder", message=""):
        """Ask user for a directory path and remembers last location used if applicable
        To store last location key name must be a string and be a gui callback (not command line)."""
        pass


class AbstractCallbacks(GeneralAbstractCallbacks):
    """Abstract class with several callbacks that has to be implemented for a new backend
    Specifies that the general callback exist as well as sound speed specific ones."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def ask_location_from_sis(self):
        """Ask user for location"""
        pass

    @abstractmethod
    def ask_tss(self):
        """Ask user for transducer sound speed"""
        pass

    @abstractmethod
    def ask_draft(self):
        """Ask user for draft"""
        pass

    @abstractmethod
    def msg_tx_no_verification(self, name, protocol):
        """Profile transmitted but not verification available"""
        pass

    @abstractmethod
    def msg_tx_sis_wait(self, name):
        """Profile transmitted, SIS is waiting for confirmation"""
        pass

    @abstractmethod
    def msg_tx_sis_confirmed(self, name):
        """Profile transmitted, SIS confirmed"""
        pass

    @abstractmethod
    def msg_tx_sis_not_confirmed(self, name, ip):
        """Profile transmitted, SIS not confirmed"""
        pass
