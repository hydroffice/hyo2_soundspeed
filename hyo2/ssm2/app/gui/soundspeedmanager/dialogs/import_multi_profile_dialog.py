import os
import logging

from PySide6 import QtCore, QtWidgets

from hyo2.abc2.lib.package.pkg_helper import PkgHelper
from hyo2.ssm2 import pkg_info
from hyo2.ssm2.app.gui.soundspeedmanager.dialogs.dialog import AbstractDialog

logger = logging.getLogger(__name__)


class ImportMultiProfileDialog(AbstractDialog):

    def __init__(self, main_win, lib, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        self.setWindowTitle("Import multiple profiles")
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
        import_label = QtWidgets.QLabel("Cast formats:")
        import_hbox.addWidget(import_label)
        import_hbox.addStretch()
        # - fmt layout
        self.fmtLayout = QtWidgets.QHBoxLayout()
        self.importLayout.addLayout(self.fmtLayout)
        # -- left
        self.leftButtonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        self.fmtLayout.addWidget(self.leftButtonBox)
        # -- middle
        self.midButtonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        self.fmtLayout.addWidget(self.midButtonBox)
        # -- right
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

    def on_click_import(self, btn):
        # print("clicked %s" % btn.text())
        idx = self.lib.desc_readers.index(btn.text())
        name = self.lib.name_readers[idx]
        desc = self.lib.desc_readers[idx]
        ext = self.lib.ext_readers[idx]

        if desc in ["CARIS", "ELAC", "Kongsberg", "Hypack"]:
            msg = "Do you really want to store profiles based \non pre-processed %s data?\n\n" \
                  "This operation may OVERWRITE existing raw data \nin the database!" \
                  % desc
            # noinspection PyCallByClass,PyArgumentList
            ret = QtWidgets.QMessageBox.warning(self, "Pre-processed source warning", msg,
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if ret == QtWidgets.QMessageBox.No:
                return

        # ask the file path to the user
        flt = "Format %s(*.%s);;All files (*.*)" % (desc, " *.".join(ext))
        settings = QtCore.QSettings()
        # noinspection PyCallByClass
        selections, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Load data files",
                                                               settings.value("import_folder"),
                                                               flt)
        if len(selections) == 0:
            return
        settings.setValue("import_folder", os.path.dirname(selections[0]))

        nr_profiles = len(selections)
        logger.debug('user selections: %s' % nr_profiles)
        quantum = 100 / (nr_profiles * 2 + 1)
        self.progress.start()

        self.main_win.change_info_url(PkgHelper(pkg_info=pkg_info).web_url(suffix="%s" % name))

        for i, selection in enumerate(selections):

            try:
                self.progress.add(quantum=quantum, text="profile %s/%s" % (i, nr_profiles))
                self.lib.import_data(data_path=selection, data_format=name, skip_atlas=True)

                self.progress.add(quantum=quantum)
                self.lib.store_data()

            except RuntimeError as e:
                self.progress.end()
                msg = "Issue in importing the file #%s: %s\n\n> %s" % (i, selection, e)
                # noinspection PyCallByClass,PyArgumentList
                QtWidgets.QMessageBox.critical(self, "Import error", msg, QtWidgets.QMessageBox.Ok)
                return

        self.progress.end()
        self.accept()
