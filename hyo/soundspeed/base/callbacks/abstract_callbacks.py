from abc import ABCMeta, abstractmethod
import logging

logger = logging.getLogger(__name__)


class GeneralAbstractCallbacks(metaclass=ABCMeta):
    """Abstract class with several callbacks that has to be implemented for a new backend"""

    def __init__(self, sis_listener=None):
        self.sis_listener = sis_listener

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

    @abstractmethod
    def ask_location(self, default_lat=None, default_lon=None):
        """Ask user for location (it is not an abstract method because it is based on ask_number)"""
        pass

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


class AbstractCallbacks(GeneralAbstractCallbacks, metaclass=ABCMeta):
    """Abstract class with several callbacks that has to be implemented for a new backend
    Specifies that the general callback exist as well as sound speed specific ones."""

    def __init__(self, sis_listener=None):
        super(AbstractCallbacks, self).__init__(sis_listener=sis_listener)

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
