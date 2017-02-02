from __future__ import absolute_import, division, print_function, unicode_literals

from PySide import QtGui
from PySide import QtCore

import os
import logging
logger = logging.getLogger(__name__)

from hydroffice.soundspeedmanager.dialogs.dialog import AbstractDialog


class ImportSingleProfileDialog(AbstractDialog):

    def __init__(self, main_win, lib, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        self.setWindowTitle("Input data")

        # outline ui
        self.mainLayout = QtGui.QHBoxLayout()
        self.setLayout(self.mainLayout)

        # import data
        self.importLayout = QtGui.QVBoxLayout()
        self.mainLayout.addLayout(self.importLayout)
        # - import
        import_hbox = QtGui.QHBoxLayout()
        self.importLayout.addLayout(import_hbox)
        import_hbox.addStretch()
        import_label = QtGui.QLabel("Import file:")
        import_hbox.addWidget(import_label)
        import_hbox.addStretch()
        # - fmt layout
        self.fmtLayout = QtGui.QHBoxLayout()
        self.importLayout.addLayout(self.fmtLayout)
        # -- left
        self.leftButtonBox = QtGui.QDialogButtonBox(QtCore.Qt.Vertical)
        self.fmtLayout.addWidget(self.leftButtonBox)
        # -- right
        self.rightButtonBox = QtGui.QDialogButtonBox(QtCore.Qt.Vertical)
        self.fmtLayout.addWidget(self.rightButtonBox)
        # --- add buttons
        for idx, _ in enumerate(self.lib.name_readers):

            if len(self.lib.ext_readers[idx]) == 0:
                continue

            btn = QtGui.QPushButton("%s" % self.lib.desc_readers[idx])
            btn.setToolTip("Import %s format [*.%s]" % (self.lib.desc_readers[idx],
                                                        ", *.".join(self.lib.ext_readers[idx])))
            if (idx % 2) == 0:
                self.leftButtonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
            else:
                self.rightButtonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
        # noinspection PyUnresolvedReferences
        self.leftButtonBox.clicked.connect(self.on_click_import)
        # noinspection PyUnresolvedReferences
        self.rightButtonBox.clicked.connect(self.on_click_import)

        self.mainLayout.addSpacing(12)

        # retrieve data
        self.retrieveLayout = QtGui.QVBoxLayout()
        self.mainLayout.addLayout(self.retrieveLayout)
        # - retrieve
        retrieve_hbox = QtGui.QHBoxLayout()
        self.retrieveLayout.addLayout(retrieve_hbox)
        retrieve_hbox.addStretch()
        retrieve_label = QtGui.QLabel("Retrieve from:")
        retrieve_hbox.addWidget(retrieve_label)
        retrieve_hbox.addStretch()
        # - button box
        self.retrieveButtonBox = QtGui.QDialogButtonBox(QtCore.Qt.Vertical)
        self.retrieveLayout.addWidget(self.retrieveButtonBox)
        # add buttons
        # -- current project
        btn = QtGui.QPushButton("Project DB")
        self.retrieveButtonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve profile from current project DB")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_load_db)
        # -- WOA09
        btn = QtGui.QPushButton("WOA09 DB")
        self.retrieveButtonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve synthetic data from WOA09 Atlas")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_click_woa09)
        # -- WOA13
        btn = QtGui.QPushButton("WOA13 DB")
        self.retrieveButtonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve synthetic data from WOA13 Atlas")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_click_woa13)
        # -- RTOFS
        btn = QtGui.QPushButton("RTOFS")
        self.retrieveButtonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve synthetic data from RTOFS Atlas")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_click_rtofs)
        # -- SIS
        btn = QtGui.QPushButton("SIS")
        self.retrieveButtonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve current profile from SIS")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_click_sis)

        self.retrieveLayout.addStretch()

    def on_click_import(self, btn):
        # print("clicked %s" % btn.text())
        idx = self.lib.desc_readers.index(btn.text())
        name = self.lib.name_readers[idx]
        desc = self.lib.desc_readers[idx]
        ext = self.lib.ext_readers[idx]

        # ask the file path to the user
        flt = "Format %s(*.%s);;All files (*.*)" % (desc, " *.".join(ext))
        settings = QtCore.QSettings()
        # noinspection PyCallByClass
        selection, _ = QtGui.QFileDialog.getOpenFileName(self, "Load data file",
                                                         settings.value("import_folder"),
                                                         flt)
        if not selection:
            return
        settings.setValue("import_folder", os.path.dirname(selection))
        logger.debug('user selection: %s' % selection)

        self.progress.start()
        try:
            self.lib.import_data(data_path=selection, data_format=name)

        except RuntimeError as e:
            self.progress.end()
            msg = "Issue in importing the data:\n\n> %s" % e
            # noinspection PyCallByClass
            QtGui.QMessageBox.critical(self, "Import error", msg, QtGui.QMessageBox.Ok)
            return

        if self.lib.ssp_list.nr_profiles > 1:
            ssp_list = list()
            for i, ssp in enumerate(self.lib.ssp_list.l):
                ssp_list.append("#%03d: %s (%.6f, %.6f)" % (i, ssp.meta.utc_time, ssp.meta.latitude, ssp.meta.longitude))

            sel, ok = QtGui.QInputDialog.getItem(self, 'Multiple profiles',
                                                 'Select a profile (if you want to import all of them,\n'
                                                 'use the multi-import dialog in Database tab):',
                                                 ssp_list, 0, False)

            if sel and ok:
                self.lib.ssp_list.current_index = ssp_list.index(sel)

            else:
                self.lib.clear_data()
                self.progress.end()
                self.accept()
                return

        self.progress.end()
        self.accept()

    def on_load_db(self):
        """Load data from database"""
        logger.debug('user wants to load data from db')

        profiles = self.lib.db_list_profiles()
        lst = ["#%03d: %s" % (p[0], p[1]) for p in profiles]
        if len(lst) == 0:
            msg = "Store data before import!"
            # noinspection PyCallByClass
            QtGui.QMessageBox.warning(self, "Database", msg, QtGui.QMessageBox.Ok)
            return

        # noinspection PyCallByClass
        sel, ok = QtGui.QInputDialog.getItem(self, 'Database', 'Select profile to load:', lst, 0, False)
        if not ok:
            return

        success = self.lib.load_profile(profiles[lst.index(sel)][0])
        if not success:
            msg = "Unable to load profile!"
            # noinspection PyCallByClass
            QtGui.QMessageBox.warning(self, "Database", msg, QtGui.QMessageBox.Ok)
            return

        self.accept()

    def on_click_woa09(self):
        """Retrieve WOA09 data"""
        try:
            self.lib.retrieve_woa09()

        except RuntimeError as e:
            msg = "Issue in importing the data:\n\n> %s" % e
            # noinspection PyCallByClass
            QtGui.QMessageBox.critical(self, "Receive error", msg, QtGui.QMessageBox.Ok)
            return

        self.accept()

    def on_click_woa13(self):
        """Retrieve WOA13 data"""
        try:
            self.lib.retrieve_woa13()

        except RuntimeError as e:
            msg = "Issue in importing the data:\n\n> %s" % e
            # noinspection PyCallByClass
            QtGui.QMessageBox.critical(self, "Receive error", msg, QtGui.QMessageBox.Ok)
            return

        self.accept()

    def on_click_rtofs(self):
        """Retrieve RTOFS data"""
        try:
            self.lib.retrieve_rtofs()

        except RuntimeError as e:
            msg = "Issue in importing the data:\n\n> %s" % e
            # noinspection PyCallByClass
            QtGui.QMessageBox.critical(self, "Receive error", msg, QtGui.QMessageBox.Ok)
            return

        self.accept()

    def on_click_sis(self):
        """Retrieve SIS data"""
        if not self.lib.use_sis():
            msg = "The SIS listening is not activated!\n\nGo to Settings/Input/Listen SIS"
            # noinspection PyCallByClass
            QtGui.QMessageBox.critical(self, "Receive error", msg, QtGui.QMessageBox.Ok)
            return

        try:
            self.lib.retrieve_sis()

        except RuntimeError as e:
            msg = "Issue in retrieving data from SIS:\n\n%s" % e
            # noinspection PyCallByClass
            QtGui.QMessageBox.critical(self, "Receive error", msg, QtGui.QMessageBox.Ok)
            return

        self.accept()
