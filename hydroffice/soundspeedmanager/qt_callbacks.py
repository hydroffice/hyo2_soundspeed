from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime, timedelta
import os

from PySide import QtGui, QtCore

import logging

from hydroffice.soundspeed.base.callbacks.abstract_callbacks import AbstractCallbacks

logger = logging.getLogger(__name__)


class QtCallbacks(AbstractCallbacks):
    """Qt-based callbacks"""

    def __init__(self, parent):
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
                     file_filter="All Files|*.*", multi_file=False):
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
