from PySide import QtGui
from PySide import QtCore

import traceback
import os
import logging
logger = logging.getLogger(__name__)

from hyo.soundspeedmanager.dialogs.dialog import AbstractDialog
from hyo.soundspeedmanager.dialogs.seacat_dialog import SeacatDialog


class ImportSingleProfileDialog(AbstractDialog):

    def __init__(self, main_win, lib, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        self.setWindowTitle("Input data")
        self.botton_min_width = 80

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
        # -- middle
        self.midButtonBox = QtGui.QDialogButtonBox(QtCore.Qt.Vertical)
        self.fmtLayout.addWidget(self.midButtonBox)
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
            btn.setMinimumWidth(self.botton_min_width)
            if (idx % 3) == 0:
                self.leftButtonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
            elif (idx % 3) == 1:
                self.midButtonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
            else:
                self.rightButtonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
        # noinspection PyUnresolvedReferences
        self.leftButtonBox.clicked.connect(self.on_click_import)
        # noinspection PyUnresolvedReferences
        self.midButtonBox.clicked.connect(self.on_click_import)
        # noinspection PyUnresolvedReferences
        self.rightButtonBox.clicked.connect(self.on_click_import)

        self.mainLayout.addSpacing(18)

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
        self.retrieveButtonBox.setMinimumWidth(self.botton_min_width)
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
        # -- Seabird CTD
        btn = QtGui.QPushButton("Seabird CTD")
        self.retrieveButtonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve profiles from Seabird CTD")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_click_seabird_ctd)

        self.retrieveLayout.addStretch()

    def showEvent(self, event):
        self.show()

        # manage case of default format
        settings = QtCore.QSettings()
        fmt_desc = settings.value("default_input_format")
        if (fmt_desc is None) or ("Ask" in fmt_desc):
            return
        if fmt_desc == "Seabird CTD":
            self.on_click_seabird_ctd()
            return
        try:
            idx = self.lib.desc_readers.index(fmt_desc)
        except Exception as e:
            logger.debug("while retrieving default format, %s (%s)" % (e, fmt_desc))
            return
        self.do_import(idx)

    def on_click_import(self, btn):
        # print("clicked %s" % btn.text())
        idx = self.lib.desc_readers.index(btn.text())
        self.do_import(idx)

    def do_import(self, idx):
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
            traceback.print_exc()
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

        if settings.value("show_metadata_at_import") == 'true':
            if self.parent() is not None:
                self.parent().on_metadata()

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

        self.progress.start(text="Retrieve WOA09")
        self.progress.update(value=30)

        try:
            self.lib.retrieve_woa09()

        except RuntimeError as e:
            msg = "Issue in importing the WOA09 data:\n\n> %s" % e
            # noinspection PyCallByClass
            QtGui.QMessageBox.critical(self, "Receive error", msg, QtGui.QMessageBox.Ok)
            self.progress.end()
            return

        self.accept()
        self.progress.end()

    def on_click_woa13(self):
        """Retrieve WOA13 data"""

        self.progress.start(text="Retrieve WOA13")
        self.progress.update(value=30)

        try:
            self.lib.retrieve_woa13()

        except RuntimeError as e:
            msg = "Issue in importing the WOA13 data:\n\n> %s" % e
            # noinspection PyCallByClass
            QtGui.QMessageBox.critical(self, "Receive error", msg, QtGui.QMessageBox.Ok)
            self.progress.end()
            return

        self.accept()
        self.progress.end()

    def on_click_rtofs(self):
        """Retrieve RTOFS data"""

        self.progress.start(text="Retrieve RTOFS")
        self.progress.update(value=30)

        try:
            self.lib.retrieve_rtofs()

        except RuntimeError as e:
            msg = "Issue in importing the RTOFS data:\n\n> %s" % e
            # noinspection PyCallByClass
            QtGui.QMessageBox.critical(self, "Receive error", msg, QtGui.QMessageBox.Ok)
            self.progress.end()
            return

        self.accept()
        self.progress.end()

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

    def on_click_seabird_ctd(self):
        logger.debug("Open Seabird CTD dialog")
        dlg = SeacatDialog(lib=self.lib, main_win=self.main_win, parent=self)
        ret = dlg.exec_()
        if ret != QtGui.QDialog.Accepted:
            logger.info("Seabird CTD dialog closed without selection")
            return

        self.accept()
