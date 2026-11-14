import logging
import os
from typing import TYPE_CHECKING

import numpy as np
from PySide6 import QtCore, QtGui, QtWidgets

# noinspection PyUnresolvedReferences
from hyo2.abc2.lib.package.pkg_helper import PkgHelper
# noinspection PyUnresolvedReferences
from hyo2.ssm2 import pkg_info
# noinspection PyUnresolvedReferences
from hyo2.ssm2.app.gui.soundspeedmanager import app_info
# noinspection PyUnresolvedReferences
from hyo2.ssm2.app.gui.soundspeedmanager.dialogs.dialog import AbstractDialog
# noinspection PyUnresolvedReferences
from hyo2.ssm2.app.gui.soundspeedmanager.dialogs.automate_dialog import AutomateDialog
from hyo2.ssm2.lib.profile.dicts import Dicts

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from hyo2.ssm2.app.gui.soundspeedmanager.mainwin import MainWin
    # noinspection PyUnresolvedReferences
    from hyo2.ssm2.app.gui.soundspeedmanager.widgets.database import Database
    # noinspection PyUnresolvedReferences
    from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary

logger = logging.getLogger(__name__)


class ImportMultiProfileDialog(AbstractDialog):

    def __init__(self, main_win: 'MainWin', lib: 'SoundSpeedLibrary', parent: 'Database' = None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        self.setWindowTitle("Input profiles")
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
        import_label = QtWidgets.QLabel("Import from file:")
        import_hbox.addWidget(import_label)
        import_hbox.addStretch()
        # - fmt layout
        self.fmtLayout = QtWidgets.QHBoxLayout()
        self.importLayout.addLayout(self.fmtLayout)
        # -- left
        self.leftButtonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Orientation.Vertical)
        self.fmtLayout.addWidget(self.leftButtonBox)
        # -- middle
        self.midButtonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Orientation.Vertical)
        self.fmtLayout.addWidget(self.midButtonBox)
        # -- right
        self.rightButtonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Orientation.Vertical)
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
                self.leftButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
            elif (idx % 3) == 1:
                self.midButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
            else:
                self.rightButtonBox.addButton(btn, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
        # noinspection PyUnresolvedReferences
        self.leftButtonBox.clicked.connect(self.on_click_import)
        # noinspection PyUnresolvedReferences
        self.midButtonBox.clicked.connect(self.on_click_import)
        # noinspection PyUnresolvedReferences
        self.rightButtonBox.clicked.connect(self.on_click_import)

        # flag to apply automatic processing
        self.importLayout.addSpacing(9)
        automation_hbox = QtWidgets.QHBoxLayout()
        self.importLayout.addLayout(automation_hbox)
        self._apply_auto_chk = QtWidgets.QCheckBox("Apply Automated Processing")
        automation_hbox.addWidget(self._apply_auto_chk)
        setup_icon = QtGui.QIcon(os.path.join(app_info.app_media_path, 'settings.png'))
        open_auto_setup_btn = QtWidgets.QPushButton(icon=setup_icon)
        open_auto_setup_btn.setIconSize(QtCore.QSize(16, 16))
        open_auto_setup_btn.setToolTip("Open Automate Processing setup")
        open_auto_setup_btn.clicked.connect(self.on_setup_automated_processing)
        automation_hbox.addWidget(open_auto_setup_btn)
        automation_hbox.addStretch()

    def on_setup_automated_processing(self, _):
        dlg = AutomateDialog(lib=self.lib, main_win=self.main_win, parent=self,
                             multi_profiles=True)
        dlg.exec()

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
            ret = QtWidgets.QMessageBox.warning(
                self, "Pre-processed source warning", msg,
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            if ret == QtWidgets.QMessageBox.StandardButton.No:
                return

        # ask the file path to the user
        flt = "Format %s(*.%s);;All files (*.*)" % (desc, " *.".join(ext))
        settings = QtCore.QSettings()
        # noinspection PyCallByClass
        selections, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Load data files",
                                                               str(settings.value("import_folder", "")),
                                                               flt)
        if len(selections) == 0:
            return
        settings.setValue("import_folder", os.path.dirname(selections[0]))

        if not self._apply_auto_chk.isChecked():
            multi_smooth_filter = False
            multi_sal_temp = False
            multi_tss = False
            multi_extend = False
        else:
            multi_smooth_filter = settings.value("multi_smooth_filter") == "true"
            multi_sal_temp = settings.value("multi_sal_temp") == "true"
            multi_tss = settings.value("multi_tss") == "true"
            multi_extend = settings.value("multi_extend") == "true"

        skip_atlas = True
        if multi_sal_temp or multi_extend:
            skip_atlas = False

        logger.debug(f"{skip_atlas=}: {multi_smooth_filter=}, {multi_sal_temp=}, {multi_tss=}, {multi_extend=}")

        nr_profiles = len(selections)
        logger.debug('user selections: %s' % nr_profiles)
        quantum = 100 / (nr_profiles * 3 + 1)
        self.progress.start()

        self.main_win.change_info_url(PkgHelper(pkg_info=pkg_info).web_url(suffix="%s" % name))

        for i, selection in enumerate(selections):

            try:
                self.progress.add(quantum=quantum, text="profile %s/%s" % (i, nr_profiles))

                self.lib.import_data(data_path=selection, data_format=name, skip_atlas=skip_atlas)

                self.progress.add(quantum=quantum)

                if multi_smooth_filter and not self.lib.filter_cur_data():
                    msg = "Issue in filtering/smoothing the profile"
                    QtWidgets.QMessageBox.warning(self, "Filter/Smooth", msg,
                                                  QtWidgets.QMessageBox.StandardButton.Ok)
                    continue

                if multi_sal_temp:
                    if self.lib.cur.meta.sensor_type in [Dicts.sensor_types['XBT'], ]:
                        if not self.lib.replace_cur_salinity():
                            msg = "Issue in replacing the salinity"
                            QtWidgets.QMessageBox.warning(self, "Salinity", msg,
                                                          QtWidgets.QMessageBox.StandardButton.Ok)
                            continue

                    if self.lib.cur.meta.sensor_type in [Dicts.sensor_types['XSV'],
                                                         Dicts.sensor_types['SVP']]:
                        if not self.lib.replace_cur_temp_sal():
                            msg = "Issue in replacing temperature and salinity"
                            QtWidgets.QMessageBox.warning(self, "Temperature/Salinity", msg,
                                                          QtWidgets.QMessageBox.StandardButton.Ok)
                            continue
                    elif self.lib.cur.meta.sensor_type in [Dicts.sensor_types['MVP'], ]:

                        if (np.sum(self.lib.cur.proc.temp) == 0) and (np.sum(self.lib.cur.proc.sal) == 0):
                            if not self.lib.replace_cur_temp_sal():
                                msg = "Issue in replacing temperature and salinity"
                                QtWidgets.QMessageBox.warning(self, "Temperature/Salinity", msg,
                                                              QtWidgets.QMessageBox.StandardButton.Ok)
                                continue

                if multi_tss and not self.lib.add_cur_tss():
                    msg = "Issue in retrieving transducer sound speed"
                    QtWidgets.QMessageBox.warning(self, "Sound speed", msg, QtWidgets.QMessageBox.StandardButton.Ok)
                    continue

                if multi_extend and not self.lib.extend_profile():
                    msg = "Issue in extending the profile!\n\n" \
                          "Possible causes:\n" \
                          "- The extension source is not active. Look at Setup/Input!\n" \
                          "- The profile from the extension source is too short. Check it on the plots!\n" \
                          "- The extension source does not have a profile at the geographic location.\n" \
                          "Use another source or manually extend the profile!"
                    QtWidgets.QMessageBox.warning(self, "Profile extension", msg,
                                                  QtWidgets.QMessageBox.StandardButton.Ok)
                    continue

                self.progress.add(quantum=quantum)

                self.lib.store_data()

            except RuntimeError as e:
                self.progress.end()
                msg = "Issue in importing the file #%s: %s\n\n> %s" % (i, selection, e)
                # noinspection PyCallByClass,PyArgumentList
                QtWidgets.QMessageBox.critical(self, "Import error", msg, QtWidgets.QMessageBox.StandardButton.Ok)
                return

        self.progress.end()
        self.accept()
