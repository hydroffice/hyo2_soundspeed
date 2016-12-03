from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime, timedelta
import os

from PySide import QtGui, QtCore

import logging

from hydroffice.soundspeed.base.callbacks import AbstractCallbacks

logger = logging.getLogger(__name__)


def get_filename(parent=None, saving=True, keyname=None, default_path=".",
                 title="Choose a path/filename", default_file="",
                 ffilter="All Files (*.*)", multifile=False):
    #flt = "Format %s(*.%s);;All files (*.*)" % (desc, " *.".join(ext))
    settings = QtCore.QSettings()
    dlg_options = {'parent': parent, 'caption': title, 'filter': ffilter}
    if keyname:
        dlg_options['dir'] = settings.value(keyname)
    if not multifile:
        if saving:
            selection, _ = QtGui.QFileDialog.getSaveFileName(**dlg_options)
        else:
            selection, _ = QtGui.QFileDialog.getOpenFileName(**dlg_options)
        if selection:
            settings.setValue("import_folder", os.path.dirname(selection))
    else:
        selection, _ = QtGui.QFileDialog.getOpenFileNames(**dlg_options)
        if selection:
            settings.setValue("import_folder", os.path.dirname(selection[0]))

    if selection:
        logger.debug('user selection: %s' % selection)
    return selection


def get_directory(parent=None, keyname=None, default_path=".",
                  title="Select output folder", message=""):
    # ask user for output folder path
    settings = QtCore.QSettings()
    default_dir = settings.value(keyname) if keyname else ""
    output_folder = QtGui.QFileDialog.getExistingDirectory(self, caption=title,
                                                           dir=default_dir)
    if output_folder:
        settings.setValue("export_folder", output_folder)
        logger.debug('user selection: %s' % output_folder)
    return output_folder


class QtCallbacks(AbstractCallbacks):
    """Qt-based callbacks"""

    def __init__(self, parent):
        self.parent = parent

    def ask_number(self, title="", msg="Enter number", default=0,
                   minval=-2147483647, maxval=2147483647, decimals=7):
        val, ok = QtGui.QInputDialog.getDouble(self.parent, title, msg,
                                               default, minval, maxval, decimals)
        if not ok:
            val = None
        return val

    def ask_text(self, title="", msg="Enter text"):
            date, ok = QtGui.QInputDialog.getText(self.parent, title, msg)
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

#     def ask_location(self):
#         """Ask user for location"""
# 
#         # latitude
#         lat = self.ask_number("Location", "Enter latitude as dd.ddd:",
#                                   37.540, -90.0, 90.0, 7)
# 
#         if lat is not None:  # don't check for lon if lat already failed
#             # longitude
#             lon = self.ask_number("Location", "Enter longitude as dd.ddd:",
#                                       -42.910, -180.0, 180.0, 7)
# 
#         if (lat is None) or (lon is None):  # return None if one of the two is invalid
#             return None, None
# 
#         return lat, lon

    def ask_filename(self, saving=True, keyname=None, default_path=".",
                     title="Choose a path/filename", default_file="",
                     ffilter="All Files|*.*", multifile=False): 
        return get_filename(self.parent, saving, keyname, default_path, title, default_file, ffilter, multifile)

    def ask_directory(self, keyname=None, default_path=".",
                       title="Browse for folder", message=""):
        '''Pops up a wx.DirDialog to get a directory from the user.
           Returns a two-item tuple (return code, pathname or None)
        '''
        return get_directory(self.parent, keyname, default_path, title, message)

    def ask_location_from_sis(self):
        """Ask user whether retrieving location from SIS"""
        msg = "Geographic location required for pressure/depth conversion and atlas lookup.\n" \
              "Use geographic position from SIS?\nChoose 'no' to enter position manually."
        ret = QtGui.QMessageBox.information(self.parent, "Location", msg,
                                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.No:
            return False
        return True

    def ask_tss(self):
        """Ask user for transducer sound speed"""
        tss, ok = QtGui.QInputDialog.getDouble(self.parent, "TSS", "Enter transducer sound speed:",
                                               1500.0, 1000.0, 20000.0, 2)
        if not ok:
            tss = None
        return tss

    def ask_draft(self):
        """Ask user for draft"""
        draft, ok = QtGui.QInputDialog.getDouble(self.parent, "Draft", "Enter transducer draft:",
                                                 8.0, -1000.0, 1000.0, 3)
        if not ok:
            draft = None
        return draft

    def msg_tx_no_verification(self, name, protocol):
        """Profile transmitted but not verification available"""
        QtGui.QMessageBox.information(self.parent, "Profile transmitted",
                                      "Profile transmitted to \'%s\'.\n\n"
                                      "The %s protocol does not allow verification." %
                                      (name, protocol))

    def msg_tx_sis_wait(self, name):
        """Profile transmitted, SIS is waiting for confirmation"""
        QtGui.QMessageBox.information(self.parent, "Profile Transmitted",
                                      "Profile transmitted to \'%s\'.\n\n"
                                      "SIS is waiting for operator confirmation." % name)

    def msg_tx_sis_confirmed(self, name):
        """Profile transmitted, SIS confirmed"""
        QtGui.QMessageBox.information(self.parent, "Transmitted",
                                      "Reception confirmed from \'%s\'!" % name)

    def msg_tx_sis_not_confirmed(self, name, ip):
        """Profile transmitted, SIS not confirmed"""
        QtGui.QMessageBox.warning(self.parent, "Transmitted",
                                  "Profile transmitted, but \'%s\' did not confirm the recption\n\n"
                                  "Please do the following checks on SIS:\n"
                                  "1) Check sound speed file name in SIS run-time parameters "
                                  "and match date/time in SIS .asvp filename with cast date/time to ensure receipt\n"
                                  "2) Ensure SVP datagram is being distributed to this IP "
                                  "on port %d to enable future confirmations"
                                  % (name, ip))