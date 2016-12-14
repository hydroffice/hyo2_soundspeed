from __future__ import absolute_import, division, print_function, unicode_literals

from PySide import QtGui
from PySide import QtCore

import logging
logger = logging.getLogger(__name__)

from hydroffice.soundspeedmanager.dialogs.dialog import AbstractDialog
from hydroffice.soundspeed.base.helper import explore_folder
from hydroffice.soundspeed.profile.dicts import Dicts


class ExportSingleProfileDialog(AbstractDialog):

    def __init__(self, main_win, lib, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        # the list of selected writers passed to the library
        self.selected_writers = list()

        self.setWindowTitle("Export single profile")
        self.setMinimumWidth(160)

        settings = QtCore.QSettings()

        # outline ui
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # label
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        label = QtGui.QLabel("Select output formats:")
        hbox.addWidget(label)
        hbox.addStretch()
        # buttons
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        self.buttonBox = QtGui.QDialogButtonBox(QtCore.Qt.Vertical)
        hbox.addWidget(self.buttonBox)
        hbox.addStretch()
        # add buttons (retrieving name, description and extension from the library)
        for idx, name in enumerate(self.lib.name_writers):

            if len(self.lib.ext_writers[idx]) == 0:
                continue

            btn = QtGui.QPushButton("%s" % self.lib.desc_writers[idx])
            btn.setCheckable(True)
            btn.setToolTip("Select %s format [*.%s]" % (self.lib.desc_writers[idx],
                                                        ", *.".join(self.lib.ext_writers[idx])))

            btn_settings = settings.value("export_single_%s" % name)
            if btn_settings is None:
                settings.setValue("export_single_%s" % name, False)
            if settings.value("export_single_%s" % name) == 'true':
                btn.setChecked(True)
                self.selected_writers.append(name)

            self.buttonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)

        # noinspection PyUnresolvedReferences
        self.buttonBox.clicked.connect(self.on_select_writer_btn)

        self.mainLayout.addSpacing(16)

        # option for selecting the output folder
        select_output_folder = settings.value("select_output_folder")
        if select_output_folder is None:
            settings.setValue("select_output_folder", False)
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        self.selectFolder = QtGui.QCheckBox('Select output folder', self)
        self.selectFolder.setChecked(settings.value("select_output_folder") == 'true')
        hbox.addWidget(self.selectFolder)
        hbox.addStretch()

        # option for opening the output folder
        export_open_folder = settings.value("export_open_folder")
        if export_open_folder is None:
            settings.setValue("export_open_folder", True)
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        self.openFolder = QtGui.QCheckBox('Open output folder', self)
        self.openFolder.setChecked(settings.value("export_open_folder") == 'true')
        hbox.addWidget(self.openFolder)
        hbox.addStretch()

        # export
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        btn = QtGui.QPushButton("Export profile")
        btn.setMinimumHeight(32)
        hbox.addWidget(btn)
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_export_profile_btn)
        hbox.addStretch()

    def on_select_writer_btn(self, btn):
        """Update the list of writers to pass to the library"""
        logger.debug("%s -> %s" % (btn.text(), btn.isChecked()))
        idx = self.lib.desc_writers.index(btn.text())
        name = self.lib.name_writers[idx]

        settings = QtCore.QSettings()

        if btn.isChecked():
            self.selected_writers.append(name)
            settings.setValue("export_single_%s" % name, True)

        else:
            settings.setValue("export_single_%s" % name, False)
            if name in self.selected_writers:
                self.selected_writers.remove(name)

    def on_export_profile_btn(self):
        logger.debug("export profile clicked")

        if len(self.selected_writers) == 0:
            msg = "Select output formats before data export!"
            QtGui.QMessageBox.warning(self, "Export warning", msg, QtGui.QMessageBox.Ok)
            return

        # special case: synthetic profile and NCEI
        for writer in self.selected_writers:
            if writer != 'ncei':
                continue

            if self.lib.ssp.l[0].meta.sensor_type == Dicts.sensor_types['Synthetic']:
                msg = "Attempt to export a synthetic profile in NCEI format!"
                QtGui.QMessageBox.warning(self, "Export warning", msg, QtGui.QMessageBox.Ok)
                return

            if self.lib.current_project == 'default':
                msg = "The 'default' project cannot be used for NCEI export.\n\n" \
                      "Rename the project in the Database tab!"
                QtGui.QMessageBox.warning(self, "Export warning", msg, QtGui.QMessageBox.Ok)
                return

            if not self.lib.ssp.cur.meta.survey or \
                    not self.lib.ssp.cur.meta.vessel or \
                    not self.lib.ssp.cur.meta.institution:
                msg = "Survey, vessel, and institution metadata are mandatory for NCEI export.\n\n" \
                      "To fix the issue:\n" \
                      "- Load the profile (if not already loaded)\n" \
                      "- Set th missing values using the Metadata button on the Editor tool bar\n"
                QtGui.QMessageBox.warning(self, "Export warning", msg, QtGui.QMessageBox.Ok)
                return

        settings = QtCore.QSettings()

        select_output_folder = self.selectFolder.isChecked()
        settings.setValue("select_output_folder", select_output_folder)
        if select_output_folder:

            # ask user for output folder path
            # noinspection PyCallByClass
            output_folder = QtGui.QFileDialog.getExistingDirectory(self, "Select output folder",
                                                                   settings.value("export_folder"))
            if not output_folder:
                return
        else:
            output_folder = self.lib.outputs_folder
        settings.setValue("export_folder", output_folder)
        logger.debug('output folder: %s' % output_folder)

        # ask user for basename
        basenames = list()
        # NCEI has special filename convention
        if (len(self.selected_writers) == 1) and (self.selected_writers[0] == 'ncei'):

            pass

        else:

            basename_msg = "Enter output basename (without extension):"
            while True:
                # noinspection PyCallByClass
                basename, ok = QtGui.QInputDialog.getText(self, "Output basename", basename_msg,
                                                          text=self.lib.cur_basename)
                if not ok:
                    return
                for _ in self.selected_writers:
                    basenames.append(basename)
                break

        # actually do the export
        self.progress.start()
        try:
            self.lib.export_data(data_path=output_folder, data_files=basenames,
                                 data_formats=self.selected_writers)
        except RuntimeError as e:
            self.progress.end()
            msg = "Issue in exporting the data.\nReason: %s" % e
            # noinspection PyCallByClass
            QtGui.QMessageBox.critical(self, "Export error", msg, QtGui.QMessageBox.Ok)
            return

        # opening the output folder
        export_open_folder = self.openFolder.isChecked()
        settings.setValue("export_open_folder", export_open_folder)
        if export_open_folder:
            explore_folder(output_folder)  # open the output folder
            self.progress.end()

        else:
            self.progress.end()
            msg = "Profile successfully exported!"
            # noinspection PyCallByClass
            QtGui.QMessageBox.information(self, "Export profile", msg, QtGui.QMessageBox.Ok)

        self.accept()
