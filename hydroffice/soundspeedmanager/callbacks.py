from __future__ import absolute_import, division, print_function, unicode_literals

from PySide import QtGui
from datetime import datetime, timedelta

import logging

logger = logging.getLogger(__name__)

from hydroffice.soundspeed.base.callbacks import AbstractCallbacks


class Callbacks(AbstractCallbacks):

    def __init__(self, parent):
        self.parent = parent

    def ask_location(self):
        lat = None
        lon = None

        # latitude
        lat, ok = QtGui.QInputDialog.getDouble(self.parent, "Location", "Enter latitude as dd.ddd:",
                                               37.540, -90.0, 90.0, 7)
        if not ok:
            lat = None
        # longitude
        lon, ok = QtGui.QInputDialog.getDouble(self.parent, "Location", "Enter longitude as dd.ddd:",
                                               -42.910, -180.0, 180.0, 7)
        if not ok:
            lon = None

        if (lat is None) or (lon is None):  # return None if one of the two is invalid
            return None, None

        return lat, lon

    def ask_date(self):
        """Ask user for date"""
        now = datetime.utcnow()
        date_msg = "Enter date as DD/MM/YYYY [default: %s]:" % now.strftime("%d/%m/%Y")
        time_msg = "Enter time as HH:MM:SS [default: %s]:" % now.strftime("%H:%M:%S")
        dt = None

        # date
        while True:
            date, ok = QtGui.QInputDialog.getText(self.parent, "Date", date_msg)
            if not ok:
                return None

            if date == "":
                dt = datetime(year=now.year, month=now.month, day=now.day)
                break

            try:
                dt = datetime.strptime(date, "%d/%m/%Y")
                break

            except ValueError:
                QtGui.QMessageBox.information(self.parent, "Invalid input",
                                              "The input date format is DD/MM/YYYY (e.g., 08/08/1980).\n"
                                              "You entered: %s" % date)
                continue

        # time
        while True:
            time, ok = QtGui.QInputDialog.getText(self.parent, "Time", time_msg)
            if not ok:
                return None

            if time == "":
                dt += timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
                break

            try:
                in_time = datetime.strptime(time, "%H:%M:%S")
                dt += timedelta(hours=in_time.hour, minutes=in_time.minute,
                                seconds=in_time.second)
                break

            except ValueError:
                QtGui.QMessageBox.information(self.parent, "Invalid input",
                                              "The input time format is HH:MM:SS (e.g., 10:30:00).\n"
                                              "You entered: %s" % time)
                continue

        return dt
