from __future__ import absolute_import, division, print_function, unicode_literals

from abc import ABCMeta, abstractmethod, abstractproperty
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)


class AbstractCallbacks(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def ask_date(self):
        """Ask user for date"""
        pass

    @abstractmethod
    def ask_location(self):
        """Ask user for location"""
        pass

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


class TestCallbacks(AbstractCallbacks):
    """Used only for testing since the methods do not require user interaction"""
    def ask_date(self):
        return datetime.utcnow()

    def ask_location(self):
        return 43.13555 + random.random(), -70.9395 + random.random()

    def ask_location_from_sis(self):
        return True

    def ask_tss(self):
        return 1500.0

    @abstractmethod
    def ask_draft(self):
        return 8.0


class Callbacks(AbstractCallbacks):
    """CLI-based callbacks"""

    def ask_date(self):
        """Ask user for date"""
        now = datetime.utcnow()
        date_msg = "Enter date as DD/MM/YYYY [default: %s]:" % now.strftime("%d/%m/%Y")
        time_msg = "Enter time as HH:MM:SS [default: %s]:" % now.strftime("%H:%M:%S")
        dt = None

        # date
        while True:
            raw = raw_input(date_msg)
            # print(raw)
            if raw == "":
                dt = datetime(year=now.year, month=now.month, day=now.day)
                break

            try:
                dt = datetime.strptime(raw, "%d/%m/%Y")
                break

            except ValueError as e:
                logger.info("invalid input: %s\n" % e)
                continue

        # time
        while True:
            raw = raw_input(time_msg)
            # print(raw)
            if raw == "":
                dt += timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
                break

            try:
                in_time = datetime.strptime(raw, "%H:%M:%S")
                dt += timedelta(hours=in_time.hour, minutes=in_time.minute,
                                seconds=in_time.second)
                break

            except ValueError as e:
                logger.info("invalid input: %s\n" % e)
                continue

        return dt

    def ask_location(self):
        """Ask user for location"""
        lat = 43.13555
        lat_msg = "Enter latitude as DD.DDD [default: %s]:" % lat
        lon = -70.9395
        lon_msg = "Enter longitude as DD.DDD [default: %s]:" % lon

        # lat
        while True:
            raw = raw_input(lat_msg)
            # print(raw)
            if raw == "":
                break
            try:
                lat = float(raw)
                if (lat > 90) or (lat < -90):
                    logger.info("invalid latitude range [90/-90]: %s" % lat)
                    continue
                break
            except ValueError as e:
                logger.info("invalid input: %s\n" % e)
                continue

        # lon
        while True:
            raw = raw_input(lon_msg)
            # print(raw)
            if raw == "":
                break
            try:
                lon = float(raw)
                if (lon > 180) or (lon < -180):
                    logger.info("invalid longitude range [180/-180]: %s" % lon)
                    continue
                break
            except ValueError as e:
                logger.info("invalid input: %s\n" % e)
                continue

        return lat, lon

    def ask_location_from_sis(self):
        """Ask user whether retrieving location from SIS"""
        bool_msg = "Geographic location required for pressure/depth conversion and atlas lookup.\n" \
                   "Use geographic position from SIS?\'y' for yes, other inputs to enter position manually."

        raw = raw_input(bool_msg)
        # print(raw)
        if (raw == "Y") or (raw == "y"):
            return True
        return False

    def ask_tss(self):
        """Ask user for transducer sound speed"""
        tss = 1500.0
        tss_msg = "Enter transducer sound speed in m/sec [default: %s]:" % tss

        # lat
        while True:
            raw = raw_input(tss_msg)
            # print(raw)
            if raw == "":
                break
            try:
                tss = float(raw)
                if (tss > 2000) or (tss < 1000):
                    logger.info("invalid sound speed value: %s" % tss)
                    continue
                break
            except ValueError as e:
                logger.info("invalid input: %s\n" % e)
                continue

        return tss

    def ask_draft(self):
        """Ask user for draft"""
        draft = 8.0
        draft_msg = "Enter transducer draft in m [default: %s]:" % draft

        # lat
        while True:
            raw = raw_input(draft_msg)
            # print(raw)
            if raw == "":
                break
            try:
                draft = float(raw)
                if (draft > 1000) or (draft < -1000):
                    logger.info("invalid draft value: %s" % draft)
                    continue
                break
            except ValueError as e:
                logger.info("invalid input: %s\n" % e)
                continue

        return draft