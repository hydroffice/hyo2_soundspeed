import traceback
import os
import logging

from PySide2 import QtCore, QtWidgets

from hyo2.abc.lib.helper import Helper
from hyo2.soundspeed import lib_info
from hyo2.soundspeedmanager.dialogs.dialog import AbstractDialog
from hyo2.soundspeedmanager.dialogs.seacat_dialog import SeacatDialog

logger = logging.getLogger(__name__)


class ImportSingleProfileDialog(AbstractDialog):

    def __init__(self, main_win, lib, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        self.setWindowTitle("Input data")
        self.botton_min_width = 80

        # outline ui
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.setLayout(self.mainLayout)

        # import data
        self.importLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.addLayout(self.importLayout)
        # - import
        import_hbox = QtWidgets.QHBoxLayout()
        self.importLayout.addLayout(import_hbox)
        import_hbox.addStretch()
        import_label = QtWidgets.QLabel("Import file:")
        import_hbox.addWidget(import_label)
        import_hbox.addStretch()
        # - fmt layout
        self.fmtLayout = QtWidgets.QHBoxLayout()
        self.importLayout.addLayout(self.fmtLayout)
        # -- left
        # noinspection PyUnresolvedReferences
        self.leftButtonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        self.fmtLayout.addWidget(self.leftButtonBox)
        # -- middle
        # noinspection PyUnresolvedReferences
        self.midButtonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        self.fmtLayout.addWidget(self.midButtonBox)
        # -- right
        # noinspection PyUnresolvedReferences
        self.rightButtonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        self.fmtLayout.addWidget(self.rightButtonBox)
        # --- add buttons
        for idx, _ in enumerate(self.lib.name_readers):

            if len(self.lib.ext_readers[idx]) == 0:
                continue

            btn = QtWidgets.QPushButton("%s" % self.lib.desc_readers[idx])
            btn.setToolTip("Import %s format [*.%s]" % (self.lib.desc_readers[idx],
                                                        ", *.".join(self.lib.ext_readers[idx])))
            btn.setMinimumWidth(self.botton_min_width)
            if (idx % 3) == 0:
                self.leftButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
            elif (idx % 3) == 1:
                self.midButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
            else:
                self.rightButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        # noinspection PyUnresolvedReferences
        self.leftButtonBox.clicked.connect(self.on_click_import)
        # noinspection PyUnresolvedReferences
        self.midButtonBox.clicked.connect(self.on_click_import)
        # noinspection PyUnresolvedReferences
        self.rightButtonBox.clicked.connect(self.on_click_import)

        self.mainLayout.addSpacing(36)

        # retrieve data
        self.retrieveLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.addLayout(self.retrieveLayout)
        # - retrieve Label
        retrieve_hbox = QtWidgets.QHBoxLayout()
        self.retrieveLayout.addLayout(retrieve_hbox)
        retrieve_hbox.addStretch()
        retrieve_label = QtWidgets.QLabel("Retrieve from:")
        retrieve_hbox.addWidget(retrieve_label)
        retrieve_hbox.addStretch()
        # - retrieve Sources
        self.retrieveSources = QtWidgets.QHBoxLayout()
        self.retrieveLayout.addLayout(self.retrieveSources)

        # -- left button box
        # noinspection PyUnresolvedReferences
        self.leftRetrieveButtonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        self.leftRetrieveButtonBox.setMinimumWidth(self.botton_min_width)
        self.retrieveSources.addWidget(self.leftRetrieveButtonBox)

        # --- add buttons
        # ---- current project
        btn = QtWidgets.QPushButton("Project DB")
        self.leftRetrieveButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve profile from current project DB")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_load_db)
        # ---- SIS4
        btn = QtWidgets.QPushButton("SIS")
        self.leftRetrieveButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve current profile from SIS")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_click_sis)
        # ---- Seabird CTD
        btn = QtWidgets.QPushButton("Seabird CTD")
        self.leftRetrieveButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve profiles from Seabird CTD")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_click_seabird_ctd)
        # --- WOA09
        btn = QtWidgets.QPushButton("WOA09 DB")
        self.leftRetrieveButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve synthetic data from WOA09 Atlas")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_click_woa09)
        # --- WOA13
        btn = QtWidgets.QPushButton("WOA13 DB")
        self.leftRetrieveButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve synthetic data from WOA13 Atlas")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_click_woa13)
        # -- Offline OFS
        btn = QtWidgets.QPushButton("OFS .nc")
        self.leftRetrieveButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve synthetic data from RegOFS .nc files")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_click_offofs)
        # ---- RTOFS
        btn = QtWidgets.QPushButton("RTOFS")
        self.leftRetrieveButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve synthetic data from RTOFS Atlas")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_click_rtofs)

        # -- mid button box
        # noinspection PyUnresolvedReferences
        self.midRetrieveButtonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        self.midRetrieveButtonBox.setMinimumWidth(self.botton_min_width)
        self.retrieveSources.addWidget(self.midRetrieveButtonBox)

        # --- add buttons
        # ---- CBOFS
        btn = QtWidgets.QPushButton("CBOFS")
        self.midRetrieveButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve synthetic data from CBOFS Atlas")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_click_cbofs)
        # ---- CREOFS
        btn = QtWidgets.QPushButton("CREOFS")
        self.midRetrieveButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve synthetic data from CREOFS Atlas")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_click_creofs)
        # ---- DBOFS
        btn = QtWidgets.QPushButton("DBOFS")
        self.midRetrieveButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve synthetic data from DBOFS Atlas")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_click_dbofs)
        # ---- GoMOFS
        btn = QtWidgets.QPushButton("GoMOFS")
        self.midRetrieveButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve synthetic data from GoMOFS Atlas")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_click_gomofs)
        # ---- LEOFS
        btn = QtWidgets.QPushButton("LEOFS")
        self.midRetrieveButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve synthetic data from LEOFS Atlas")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_click_leofs)
        # ---- LHOFS
        btn = QtWidgets.QPushButton("LHOFS")
        self.midRetrieveButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve synthetic data from LHOFS Atlas")
        # TODO: Add support for Regional OFS without regular grids
        btn.setDisabled(True)
        # -- LMOFS
        btn = QtWidgets.QPushButton("LMOFS")
        self.midRetrieveButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve synthetic data from LMOFS Atlas")
        # TODO: Add support for Regional OFS without regular grids
        btn.setDisabled(True)

        # --- right button box
        # noinspection PyUnresolvedReferences
        self.rightRetrieveButtonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        self.rightRetrieveButtonBox.setMinimumWidth(self.botton_min_width)
        self.retrieveSources.addWidget(self.rightRetrieveButtonBox)
        # ---- LOOFS
        btn = QtWidgets.QPushButton("LOOFS")
        self.rightRetrieveButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve synthetic data from LOOFS Atlas")
        # TODO: Add support for Regional OFS without regular grids
        btn.setDisabled(True)
        # -- LSOFS
        btn = QtWidgets.QPushButton("LSOFS")
        self.rightRetrieveButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve synthetic data from LSOFS Atlas")
        # TODO: Add support for Regional OFS without regular grids
        btn.setDisabled(True)
        # -- NGOFS
        btn = QtWidgets.QPushButton("NGOFS")
        self.rightRetrieveButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve synthetic data from NGOFS Atlas")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_click_ngofs)
        # -- NYOFS
        btn = QtWidgets.QPushButton("NYOFS")
        self.rightRetrieveButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve synthetic data from NYOFS Atlas")
        # TODO: Add support for Regional OFS without regular grids
        btn.setDisabled(True)
        # -- SFBOFS
        btn = QtWidgets.QPushButton("SFBOFS")
        self.rightRetrieveButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve synthetic data from SFBOFS Atlas")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_click_sfbofs)
        # -- SJROFS
        btn = QtWidgets.QPushButton("SJROFS")
        self.rightRetrieveButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve synthetic data from SJROFS Atlas")
        # TODO: Add support for Regional OFS without regular grids
        btn.setDisabled(True)
        # -- TBOFS
        btn = QtWidgets.QPushButton("TBOFS")
        self.rightRetrieveButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ActionRole)
        btn.setToolTip("Retrieve synthetic data from TBOFS Atlas")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_click_tbofs)

        self.retrieveLayout.addStretch()

    def _auto_apply(self):
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

    def showEvent(self, event):
        super().showEvent(event)
        # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
        QtCore.QTimer.singleShot(100, self._auto_apply)

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
        start_dir = settings.value("import_folders_%s" % name, settings.value("import_folder"))
        # noinspection PyCallByClass
        selection, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Load %s data file" % desc,
                                                             start_dir, flt)
        if not selection:
            return
        settings.setValue("import_folder", os.path.dirname(selection))
        settings.setValue("import_folders_%s" % name, os.path.dirname(selection))
        logger.debug('user selection: %s' % selection)

        self.main_win.change_info_url(Helper(lib_info=lib_info).web_url(suffix="%s" % name))

        self.progress.start()
        try:
            self.lib.import_data(data_path=selection, data_format=name)

        except RuntimeError as e:
            self.progress.end()
            traceback.print_exc()
            msg = "Issue in importing the data:\n\n> %s" % e
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Import error", msg, QtWidgets.QMessageBox.Ok)
            return

        if self.lib.ssp_list.nr_profiles > 1:
            ssp_list = list()
            for i, ssp in enumerate(self.lib.ssp_list.l):
                ssp_list.append(
                    "#%03d: %s (%.6f, %.6f)" % (i, ssp.meta.utc_time, ssp.meta.latitude, ssp.meta.longitude))

            # noinspection PyCallByClass
            sel, ok = QtWidgets.QInputDialog.getItem(self, 'Multiple profiles',
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
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.warning(self, "Database", msg, QtWidgets.QMessageBox.Ok)
            return

        # noinspection PyCallByClass
        sel, ok = QtWidgets.QInputDialog.getItem(self, 'Database', 'Select profile to load:', lst, 0, False)
        if not ok:
            return

        success = self.lib.load_profile(profiles[lst.index(sel)][0])
        if not success:
            msg = "Unable to load profile!"
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.warning(self, "Database", msg, QtWidgets.QMessageBox.Ok)
            return

        self.accept()

    def on_click_sis(self) -> None:
        """Retrieve SIS data"""
        logger.debug("user wants to retrieve SIS profile")
        if not self.lib.use_sis():
            msg = "The SIS listening is not activated!\n\nGo to Settings/Input/Listen SIS"
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Receive error", msg, QtWidgets.QMessageBox.Ok)
            return

        try:
            self.lib.retrieve_sis()

        except RuntimeError as e:
            msg = "Issue in retrieving data from SIS:\n\n%s" % e
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Receive error", msg, QtWidgets.QMessageBox.Ok)
            return

        self.accept()

    def on_click_seabird_ctd(self):
        logger.debug("Open Seabird CTD dialog")
        dlg = SeacatDialog(lib=self.lib, main_win=self.main_win, parent=self)
        ret = dlg.exec_()
        if ret != QtWidgets.QDialog.Accepted:
            logger.info("Seabird CTD dialog closed without selection")
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
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Receive error", msg, QtWidgets.QMessageBox.Ok)
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
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Receive error", msg, QtWidgets.QMessageBox.Ok)
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
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Receive error", msg, QtWidgets.QMessageBox.Ok)
            self.progress.end()
            return

        self.accept()
        self.progress.end()

    def on_click_cbofs(self):
        """Retrieve CBOFS"""

        self.progress.start(text='Retrieve CBOFS')
        self.progress.update(value=30)

        try:
            self.lib.retrieve_cbofs()

        except RuntimeError as e:
            msg = 'Issue in importing the CBOFS data:\n\n> %s' % e
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Receive error", msg, QtWidgets.QMessageBox.Ok)
            self.progress.end()
            return

        self.accept()
        self.progress.end()

    def on_click_creofs(self):
        """Retrieve CREOFS"""

        self.progress.start(text='Retrieve CREOFS')
        self.progress.update(value=30)

        try:
            self.lib.retrieve_creofs()

        except RuntimeError as e:
            msg = 'Issue in importing the CREOFS data:\n\n> %s' % e
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Receive error", msg, QtWidgets.QMessageBox.Ok)
            self.progress.end()
            return

        self.accept()
        self.progress.end()

    def on_click_dbofs(self):
        """Retrieve DBOFS"""

        self.progress.start(text='Retrieve DBOFS')
        self.progress.update(value=30)

        try:
            self.lib.retrieve_dbofs()

        except RuntimeError as e:
            msg = 'Issue in importing the DBOFS data:\n\n> %s' % e
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Receive error", msg, QtWidgets.QMessageBox.Ok)
            self.progress.end()
            return

        self.accept()
        self.progress.end()

    def on_click_gomofs(self):
        """Retrieve RTOFS data"""

        self.progress.start(text="Retrieve GoMOFS")
        self.progress.update(value=30)

        try:
            self.lib.retrieve_gomofs()

        except RuntimeError as e:
            msg = "Issue in importing the GoMOFS data:\n\n> %s" % e
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Receive error", msg, QtWidgets.QMessageBox.Ok)
            self.progress.end()
            return

        self.accept()
        self.progress.end()

    def on_click_leofs(self):
        """Retrieve LEOFS data"""

        self.progress.start(text="Retrieve LEOFS")
        self.progress.update(value=30)

        try:
            self.lib.retrieve_leofs()

        except RuntimeError as e:
            msg = "Issue in importing the LEOFS data:\n\n> %s" % e
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Receive error", msg, QtWidgets.QMessageBox.Ok)
            self.progress.end()
            return

        self.accept()
        self.progress.end()

    def on_click_lhofs(self):
        """Retrieve LHOFS"""

        self.progress.start(text='Retrieve LEOFS')
        self.progress.update(value=30)

        try:
            self.lib.retrieve_lhofs()

        except RuntimeError as e:
            msg = 'Issue in importing the LHOFS data:\n\n> %s' % e
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Receive error", msg, QtWidgets.QMessageBox.Ok)
            self.progress.end()
            return

        self.accept()
        self.progress.end()

    def on_click_lmofs(self):
        """Retrieve LMOFS"""

        self.progress.start(text='Retrieve LMOFS')
        self.progress.update(value=30)

        try:
            self.lib.retrieve_lmofs()

        except RuntimeError as e:
            msg = 'Issue in importing the LMOFS data:\n\n> %s' % e
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Receive error", msg, QtWidgets.QMessageBox.Ok)
            self.progress.end()
            return

        self.accept()
        self.progress.end()

    def on_click_loofs(self):
        """Retrieve LOOFS"""

        self.progress.start(text='Retrieve LOOFS')
        self.progress.update(value=30)

        try:
            self.lib.retrieve_loofs()

        except RuntimeError as e:
            msg = 'Issue in importing the LOOFS data:\n\n> %s' % e
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Receive error", msg, QtWidgets.QMessageBox.Ok)
            self.progress.end()
            return

        self.accept()
        self.progress.end()

    def on_click_lsofs(self):
        """Retrieve LSOFS"""

        self.progress.start(text='Retrieve LSOFS')
        self.progress.update(value=30)

        try:
            self.lib.retrieve_lsofs()

        except RuntimeError as e:
            msg = 'Issue in importing the LSOFS data:\n\n> %s' % e
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Receive error", msg, QtWidgets.QMessageBox.Ok)
            self.progress.end()
            return

        self.accept()
        self.progress.end()

    def on_click_ngofs(self):
        """Retrieve NGOFS"""

        self.progress.start(text='Retrieve NGOFS')
        self.progress.update(value=30)

        try:
            self.lib.retrieve_ngofs()

        except RuntimeError as e:
            msg = 'Issue in importing the NGOFS data:\n\n> %s' % e
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Receive error", msg, QtWidgets.QMessageBox.Ok)
            self.progress.end()
            return

        self.accept()
        self.progress.end()

    def on_click_nyofs(self):
        """Retrieve NYOFS"""

        self.progress.start(text='Retrieve NYOFS')
        self.progress.update(value=30)

        try:
            self.lib.retrieve_nyofs()

        except RuntimeError as e:
            msg = 'Issue in importing the NYOFS data:\n\n> %s' % e
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Receive error", msg, QtWidgets.QMessageBox.Ok)
            self.progress.end()
            return

        self.accept()
        self.progress.end()

    def on_click_sfbofs(self):
        """Retrieve SFBOFS"""

        self.progress.start(text='Retrieve SFBOFS')
        self.progress.update(value=30)

        try:
            self.lib.retrieve_sfbofs()

        except RuntimeError as e:
            msg = 'Issue in importing the SFBOFS data:\n\n> %s' % e
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Receive error", msg, QtWidgets.QMessageBox.Ok)
            self.progress.end()
            return

        self.accept()
        self.progress.end()

    def on_click_sjrofs(self):
        """Retrieve SJROFS"""

        self.progress.start(text='Retrieve SJROFS')
        self.progress.update(value=30)

        try:
            self.lib.retrieve_sjrofs()

        except RuntimeError as e:
            msg = 'Issue in importing the SJROFS data:\n\n> %s' % e
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Receive error", msg, QtWidgets.QMessageBox.Ok)
            self.progress.end()
            return

        self.accept()
        self.progress.end()

    def on_click_tbofs(self):
        """Retrieve TBOFS"""

        self.progress.start(text='Retrieve TBOFS')
        self.progress.update(value=30)

        try:
            self.lib.retrieve_tbofs()

        except RuntimeError as e:
            msg = 'Issue in importing the TBOFS data:\n\n> %s' % e
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Receive error", msg, QtWidgets.QMessageBox.Ok)
            self.progress.end()
            return

        self.accept()
        self.progress.end()

    def on_click_offofs(self):
        """Retrieve Regional OFS"""

        self.progress.start(text='Retrieve from .nc OFS')
        self.progress.update(value=30)

        try:
            self.lib.retrieve_offofs()

        except RuntimeError as e:
            msg = 'Issue in retrieving the regional OFS data:\n\n> %s' % e
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Retrieve error", msg, QtWidgets.QMessageBox.Ok)
            self.progress.end()
            return

        self.accept()
        self.progress.end()
