from datetime import datetime, timedelta
import os
import re

from PySide import QtGui, QtCore

import logging

from hyo.soundspeed.base.callbacks.abstract_callbacks import AbstractCallbacks

logger = logging.getLogger(__name__)


class QtCallbacks(AbstractCallbacks):
    """Qt-based callbacks"""

    def __init__(self, parent, sis_listener=None):
        super(QtCallbacks, self).__init__(sis_listener=sis_listener)
        self._parent = parent
        self._settings = QtCore.QSettings()

    def ask_number(self, title="", msg="Enter number", default=0.0,
                   min_value=-2147483647.0, max_value=2147483647.0, decimals=7):
        val, ok = QtGui.QInputDialog.getDouble(self._parent, title, msg,
                                               default, min_value, max_value, decimals)
        if not ok:
            val = None
        return val

    def ask_text(self, title="", msg="Enter text"):
        date, ok = QtGui.QInputDialog.getText(self._parent, title, msg)
        if not ok:
            date = None
        return date

    @classmethod
    def dms2dd(cls, degrees, minutes, seconds, direction=''):

        dd_deg = float(degrees)
        min_float = float(minutes)
        if (min_float > 60.0) or (min_float < 0.0):
            return None
        dd_min = min_float / 60
        sec_float = float(seconds)
        if (sec_float > 60.0) or (sec_float < 0.0):
            return None
        dd_sec = sec_float / (60 * 60)

        neg_deg = dd_deg < 0
        dd = abs(dd_deg) + dd_min + dd_sec

        if neg_deg and (direction in ['W', 'S']):
            return None

        if neg_deg:
            dd *= -1

        if direction in ['W', 'S']:
            dd *= -1

        return dd

    @classmethod
    def dm2dd(cls, degrees, minutes, direction=''):

        dd_deg = float(degrees)
        min_float = float(minutes)
        if (min_float > 60.0) or (min_float < 0.0):
            return None
        dd_min = min_float / 60

        neg_deg = dd_deg < 0
        dd = abs(dd_deg) + dd_min

        if neg_deg and (direction in ['W', 'S']):
            return None

        if neg_deg:
            dd *= -1

        if direction in ['W', 'S']:
            dd *= -1

        return dd

    @classmethod
    def interpret_latitude(cls, str_value):

        try:

            lat_tokens = re.split('[^\d\w.-]+', str_value)
            logger.debug("lat tokens: %s" % (lat_tokens,))
            nr_lat_tokens = len(lat_tokens)
            if nr_lat_tokens == 0:

                lat = None

            elif nr_lat_tokens == 1:

                logger.debug("DD")
                lat = float(lat_tokens[0])

            elif nr_lat_tokens == 2:

                if lat_tokens[1].strip() in ["N", "S"]:

                    logger.debug("DD E")
                    lat = float(lat_tokens[0])
                    if lat_tokens[1].strip() == "S":
                        lat *= -1

                else:
                    logger.debug("DM")
                    lat = cls.dm2dd(lat_tokens[0], lat_tokens[1])

            elif nr_lat_tokens == 3:

                if lat_tokens[2].strip() in ["N", "S"]:

                    logger.debug("DM E")
                    lat = cls.dm2dd(lat_tokens[0], lat_tokens[1], lat_tokens[2])

                else:

                    logger.debug("DMS")
                    lat = cls.dms2dd(lat_tokens[0], lat_tokens[1], lat_tokens[2])

            elif nr_lat_tokens == 4:

                if lat_tokens[3].strip() in ["N", "S"]:

                    logger.debug("DMS E")
                    lat = cls.dms2dd(lat_tokens[0], lat_tokens[1], lat_tokens[2], lat_tokens[3])

                else:

                    lat = None

            else:

                lat = None

        except:

            lat = None

        if lat is not None:

            if (lat < -90.0) or (lat > 90.0):
                logger.warning("out of bounds: %s" % lat)
                lat = None

        logger.debug("latitude: %s" % lat)
        return lat

    @classmethod
    def interpret_longitude(cls, str_value):

        try:

            lon_tokens = re.split('[^\d\w.-]+', str_value)
            logger.debug("lon tokens: %s" % (lon_tokens,))
            nr_lon_tokens = len(lon_tokens)
            if nr_lon_tokens == 0:

                lon = None

            elif nr_lon_tokens == 1:

                logger.debug("DD")
                lon = float(lon_tokens[0])

            elif nr_lon_tokens == 2:

                if lon_tokens[1].strip() in ["N", "S"]:

                    logger.debug("DD E")
                    lon = float(lon_tokens[0])
                    if lon_tokens[1].strip() == "S":
                        lon *= -1

                else:
                    logger.debug("DM")
                    lon = cls.dm2dd(lon_tokens[0], lon_tokens[1])

            elif nr_lon_tokens == 3:

                if lon_tokens[2].strip() in ["N", "S"]:

                    logger.debug("DM E")
                    lon = cls.dm2dd(lon_tokens[0], lon_tokens[1], lon_tokens[2])

                else:

                    logger.debug("DMS")
                    lon = cls.dms2dd(lon_tokens[0], lon_tokens[1], lon_tokens[2])

            elif nr_lon_tokens == 4:

                if lon_tokens[3].strip() in ["N", "S"]:

                    logger.debug("DMS E")
                    lon = cls.dms2dd(lon_tokens[0], lon_tokens[1], lon_tokens[2], lon_tokens[3])

                else:

                    lon = None

            else:

                lon = None

        except:

            lon = None

        if lon is not None:

            if (lon < -180.0) or (lon > 180.0):
                logger.warning("out of bounds: %s" % lon)
                lon = None

        logger.debug("longitude: %s" % lon)
        return lon

    def ask_location(self, default_lat=None, default_lon=None):
        """Ask user for location (it is not an abstract method because it is based on ask_number)"""

        # try to convert the passed default values
        if (default_lat is not None) and (default_lon is not None):

            try:
                _ = float(default_lat)
                _ = float(default_lon)

            except Exception:
                default_lat = 43.13555
                default_lon = -70.9395

        # if both default lat and lon are None, check if sis has position
        else:

            if self.sis_listener is not None:
                if self.sis_listener.nav is not None:
                    if (self.sis_listener.nav.latitude is not None) and (self.sis_listener.nav.longitude is not None):
                        default_lat = self.sis_listener.nav.latitude
                        default_lon = self.sis_listener.nav.longitude

            if (default_lat is None) or (default_lon is None):
                default_lat = 43.13555
                default_lon = -70.9395

        # ask user for both lat and long
        lat = None
        lon = None

        # first latitude
        while True:

            lat, ok = QtGui.QInputDialog.getText(self._parent, "Location",
                                                 "Enter latitude as DD, DM, or DMS:",
                                                 text="%s" % default_lat)
            if not ok:
                lat = None
                break

            lat = self.interpret_latitude(lat)
            if lat is not None:
                break

        # then longitude
        if lat is not None:  # don't check for lon if lat already failed

            while True:

                lon, ok = QtGui.QInputDialog.getText(self._parent, "Location",
                                                     "Enter longitude as DD, DM, or DMS:",
                                                     text="%s" % default_lon)
                if not ok:
                    lat = None
                    break

                lon = self.interpret_longitude(lon)
                if lon is not None:
                    break

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
            date, ok = QtGui.QInputDialog.getText(self._parent, "Date", date_msg)
            if not ok:
                return None

            if date == "":
                dt = datetime(year=now.year, month=now.month, day=now.day)
                break

            try:
                dt = datetime.strptime(date, "%d/%m/%Y")
                break

            except ValueError:
                QtGui.QMessageBox.information(self._parent, "Invalid input",
                                              "The input date format is DD/MM/YYYY (e.g., 08/08/1980).\n"
                                              "You entered: %s" % date)
                continue

        # time
        while True:
            time, ok = QtGui.QInputDialog.getText(self._parent, "Time", time_msg)
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
                QtGui.QMessageBox.information(self._parent, "Invalid input",
                                              "The input time format is HH:MM:SS (e.g., 10:30:00).\n"
                                              "You entered: %s" % time)
                continue

        return dt

    def ask_filename(self, saving=True, key_name=None, default_path=".",
                     title="Choose a path/filename", default_file="",
                     file_filter="All Files (*.*)", multi_file=False):
        '''key_name is used to save/restore the last directory a file was selected in'''

        # flt = "Format %s(*.%s);;All files (*.*)" % (desc, " *.".join(ext))
        dlg_options = {'parent': self._parent, 'caption': title, 'filter': file_filter}
        if key_name:
            dlg_options['dir'] = self._settings.value(key_name)

        if not multi_file:
            if saving:
                selection, _ = QtGui.QFileDialog.getSaveFileName(**dlg_options)
            else:
                selection, _ = QtGui.QFileDialog.getOpenFileName(**dlg_options)
            if selection and key_name:
                self._settings.setValue(key_name, os.path.dirname(selection))
        else:
            selection, _ = QtGui.QFileDialog.getOpenFileNames(**dlg_options)
            if selection and key_name:
                self._settings.setValue(key_name, os.path.dirname(selection[0]))

        if selection:
            logger.debug('user selection: %s' % selection)

        return selection

    def ask_directory(self, key_name=None, default_path=".",
                      title="Browse for folder", message=""):
        """Ask a directory to the user.
        key_name is used to save/restore the last directory selected
        """

        default_dir = self._settings.value(key_name) if key_name else ""

        output_folder = QtGui.QFileDialog.getExistingDirectory(self._parent, caption=title,
                                                               dir=default_dir)
        if output_folder and key_name:
            self._settings.setValue(key_name, output_folder)
            logger.debug('user selection: %s' % output_folder)

        return output_folder

    def ask_location_from_sis(self):
        """Ask user whether retrieving location from SIS"""
        msg = "Geographic location required for pressure/depth conversion and atlas lookup.\n" \
              "Use geographic position from SIS?\nChoose 'no' to enter position manually."
        ret = QtGui.QMessageBox.information(self._parent, "Location", msg,
                                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.No:
            return False
        return True

    def ask_tss(self):
        """Ask user for transducer sound speed"""
        tss, ok = QtGui.QInputDialog.getDouble(self._parent, "TSS", "Enter transducer sound speed:",
                                               1500.0, 1000.0, 20000.0, 2)
        if not ok:
            tss = None
        return tss

    def ask_draft(self):
        """Ask user for draft"""
        draft, ok = QtGui.QInputDialog.getDouble(self._parent, "Draft", "Enter transducer draft:",
                                                 8.0, -1000.0, 1000.0, 3)
        if not ok:
            draft = None
        return draft

    def msg_tx_no_verification(self, name, protocol):
        """Profile transmitted but not verification available"""
        QtGui.QMessageBox.information(self._parent, "Profile transmitted",
                                      "Profile transmitted to \'%s\'.\n\n"
                                      "The %s protocol does not allow verification." %
                                      (name, protocol))

    def msg_tx_sis_wait(self, name):
        """Profile transmitted, SIS is waiting for confirmation"""
        QtGui.QMessageBox.information(self._parent, "Profile Transmitted",
                                      "Profile transmitted to \'%s\'.\n\n"
                                      "SIS is waiting for operator confirmation." % name)

    def msg_tx_sis_confirmed(self, name):
        """Profile transmitted, SIS confirmed"""
        QtGui.QMessageBox.information(self._parent, "Transmitted",
                                      "Reception confirmed from \'%s\'!" % name)

    def msg_tx_sis_not_confirmed(self, name, ip):
        """Profile transmitted, SIS not confirmed"""
        QtGui.QMessageBox.warning(self._parent, "Transmitted",
                                  "Profile transmitted, but \'%s\' did not confirm the reception\n\n"
                                  "Please do the following checks on SIS:\n"
                                  "1) Check sound speed file name in SIS run-time parameters "
                                  "and match date/time in SIS .asvp filename with cast date/time to ensure receipt\n"
                                  "2) Ensure SVP datagram is being distributed to this IP "
                                  "on port %d to enable future confirmations"
                                  % (name, ip))
