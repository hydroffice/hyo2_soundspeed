from __future__ import absolute_import, division, print_function, unicode_literals

from PySide import QtGui
from PySide import QtCore

import os
import logging
logger = logging.getLogger(__name__)

from .dialog import AbstractDialog
from hydroffice.soundspeed.base.helper import explore_folder


class ExportDialog(AbstractDialog):

    def __init__(self, main_win, prj, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, prj=prj, parent=parent)

        self.name_outputs = list()

        self.setWindowTitle("Export data")
        self.setMinimumWidth(160)

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
        # add buttons
        for idx, _ in enumerate(self.prj.name_writers):
            if len(self.prj.ext_writers[idx]) == 0:
                continue
            btn = QtGui.QPushButton("%s" % self.prj.desc_writers[idx])
            btn.setCheckable(True)
            self.buttonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
            btn.setToolTip("Select %s format [*.%s]" % (self.prj.desc_writers[idx],
                                                        ", *.".join(self.prj.ext_writers[idx])))
        self.buttonBox.clicked.connect(self.on_select_btn)

        self.mainLayout.addSpacing(16)

        # export
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        hbox.addStretch()
        btn = QtGui.QPushButton("Export data")
        btn.setMinimumHeight(36)
        hbox.addWidget(btn)
        btn.clicked.connect(self.on_export_btn)
        hbox.addStretch()

    def on_select_btn(self, btn):
        logger.debug("%s -> %s" % (btn.text(), btn.isChecked()))
        idx = self.prj.desc_writers.index(btn.text())
        name = self.prj.name_writers[idx]

        if btn.isChecked():
            self.name_outputs.append(name)
        else:
            if name in self.name_outputs:
                self.name_outputs.remove(name)

    def on_export_btn(self):
        logger.debug("export clicked")
        if len(self.name_outputs) == 0:
            msg = "Select output formats before data export!"
            QtGui.QMessageBox.warning(self, "Export warning", msg, QtGui.QMessageBox.Ok)
            return

        # ask user for output folder path
        settings = QtCore.QSettings()
        output_folder = QtGui.QFileDialog.getExistingDirectory(self, "Select output folder",
                                                               settings.value("export_folder"))
        if not output_folder:
            return
        settings.setValue("export_folder", output_folder)
        logger.debug('user selection: %s' % output_folder)

        # ask user for basename (only for single selection)
        basenames = list()
        if len(self.name_outputs) == 1:
            basename_msg = "Enter output basename (without extension):"
            while True:
                basename, ok = QtGui.QInputDialog.getText(self, "Output basename", basename_msg,
                                                          text=self.prj.cur_basename)
                if not ok:
                    return
                basenames.append(basename)
                break

        # actually do the export
        self.progress.forceShow()
        self.progress.setValue(20)
        try:
            self.prj.export_data(data_path=output_folder, data_files=basenames,
                                 data_formats=self.name_outputs)
        except RuntimeError as e:
            self.progress.setValue(100)
            msg = "Issue in exporting the data.\nReason: %s" % e
            QtGui.QMessageBox.critical(self, "Export error", msg, QtGui.QMessageBox.Ok)
            return

        explore_folder(output_folder)  # open the output folder
        self.progress.setValue(100)
