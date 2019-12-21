import numpy as np
import os
import logging

from PySide2 import QtCore, QtGui, QtWidgets

from hyo2.soundspeedmanager.widgets.widget import AbstractWidget
from hyo2.soundspeedmanager.dialogs.automate_dialog import AutomateDialog
from hyo2.soundspeedmanager.dialogs.buttons_dialog import ButtonsDialog
from hyo2.soundspeedmanager.dialogs.import_single_profile_dialog import ImportSingleProfileDialog
from hyo2.soundspeedmanager.dialogs.constant_gradient_profile_dialog import ConstantGradientProfileDialog
from hyo2.soundspeedmanager.dialogs.reference_dialog import ReferenceDialog
from hyo2.soundspeedmanager.dialogs.spreadsheet_dialog import SpreadSheetDialog
from hyo2.soundspeedmanager.dialogs.metadata_dialog import MetadataDialog
from hyo2.soundspeedmanager.dialogs.export_single_profile_dialog import ExportSingleProfileDialog
from hyo2.soundspeedmanager.widgets.dataplots import DataPlots
from hyo2.soundspeedmanager.dialogs.seacat_dialog import SeacatDialog

from hyo2.soundspeed.profile.dicts import Dicts

logger = logging.getLogger(__name__)


class Editor(AbstractWidget):
    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win, lib):
        AbstractWidget.__init__(self, main_win=main_win, lib=lib)

        settings = QtCore.QSettings()
        settings.setValue("input_buttons/seacat_plugin", settings.value("input_buttons/seacat_plugin", 0))
        settings.setValue("editor_buttons/reference", settings.value("editor_buttons/reference", 1))
        settings.setValue("editor_buttons/spreadsheet", settings.value("editor_buttons/spreadsheet", 0))
        settings.setValue("editor_buttons/metadata", settings.value("editor_buttons/metadata", 1))
        settings.setValue("editor_buttons/filter", settings.value("editor_buttons/filter", 1))
        settings.setValue("editor_buttons/thinning", settings.value("editor_buttons/thinning", 0))
        settings.setValue("editor_buttons/restart", settings.value("editor_buttons/restart", 1))
        settings.setValue("editor_buttons/export", settings.value("editor_buttons/export", 1))
        settings.setValue("editor_buttons/transmit", settings.value("editor_buttons/transmit", 1))
        settings.setValue("editor_buttons/database", settings.value("editor_buttons/database", 0))

        self.input_bar = self.addToolBar('Input')
        self.input_bar.setIconSize(QtCore.QSize(40, 40))

        # import
        self.input_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'input.png')),
                                           'Import Input Data', self)
        self.input_act.setShortcut('Alt+I')
        # noinspection PyUnresolvedReferences
        self.input_act.triggered.connect(self.on_input_data)
        self.input_bar.addAction(self.input_act)
        self.main_win.file_menu.addAction(self.input_act)

        # import
        self.create_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'constant_gradient.png')),
                                            'Constant-gradient Profile', self)
        # self.create_act.setShortcut('Alt+G')
        # noinspection PyUnresolvedReferences
        self.create_act.triggered.connect(self.on_create_data)
        # self.input_bar.addAction(self.create_act)
        self.main_win.file_menu.addAction(self.create_act)

        # clear
        self.clear_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'clear.png')),
                                           'Clear Data', self)
        self.clear_act.setShortcut('Alt+C')
        # noinspection PyUnresolvedReferences
        self.clear_act.triggered.connect(self.on_clear_data)
        # set hidden, but the whole action is candidate to deletion
        self.clear_act.setVisible(False)
        self.input_bar.addAction(self.clear_act)

        # set ref
        self.set_ref_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'ref.png')),
                                             'Reference Cast', self)
        self.set_ref_act.setShortcut('Alt+R')
        # noinspection PyUnresolvedReferences
        self.set_ref_act.triggered.connect(self.on_set_ref)
        if settings.value("editor_buttons/reference", 1) == 1:
            self.input_bar.addAction(self.set_ref_act)
        self.main_win.file_menu.addAction(self.set_ref_act)

        # seacat
        self.seacat_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'seacat.png')),
                                            'Seabird CTD Setup', self)
        self.seacat_act.setShortcut('Alt+B')
        # noinspection PyUnresolvedReferences
        self.seacat_act.triggered.connect(self.on_seacat)
        if settings.value("input_buttons/seacat_plugin", 1) == 1:
            self.input_bar.addAction(self.seacat_act)
        self.main_win.file_menu.addAction(self.seacat_act)

        self.process_bar = self.addToolBar('Process')
        self.process_bar.setIconSize(QtCore.QSize(40, 40))

        # spreadsheet
        self.spreadsheet_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'grid.png')),
                                                 'Show/Edit Data Spreadsheet', self)
        self.spreadsheet_act.setShortcut('Alt+S')
        # noinspection PyUnresolvedReferences
        self.spreadsheet_act.triggered.connect(self.on_spreadsheet)
        if settings.value("editor_buttons/spreadsheet", 0) == 1:
            self.process_bar.addAction(self.spreadsheet_act)
        self.main_win.edit_menu.addAction(self.spreadsheet_act)

        # metadata
        self.metadata_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'metadata.png')),
                                              'Show/Edit Cast Metadata', self)
        self.metadata_act.setShortcut('Alt+M')
        # noinspection PyUnresolvedReferences
        self.metadata_act.triggered.connect(self.on_metadata)
        if settings.value("editor_buttons/metadata", 1) == 1:
            self.process_bar.addAction(self.metadata_act)
        self.main_win.edit_menu.addAction(self.metadata_act)

        # - separator
        self.process_bar.addSeparator()
        self.main_win.edit_menu.addSeparator()

        # filter
        self.filter_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'filter.png')),
                                            'Filter/Smooth Data', self)
        self.filter_act.setShortcut('Alt+F')
        # noinspection PyUnresolvedReferences
        self.filter_act.triggered.connect(self.on_data_filter)
        if settings.value("editor_buttons/filter", 1) == 1:
            self.process_bar.addAction(self.filter_act)
        self.main_win.edit_menu.addAction(self.filter_act)

        # retrieve sal
        self.sal_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'sal.png')),
                                         'Retrieve Salinity', self)
        # self.sal_act.setShortcut('Alt+A')
        # noinspection PyUnresolvedReferences
        self.sal_act.triggered.connect(self.on_retrieve_sal)
        self.process_bar.addAction(self.sal_act)

        # retrieve temp/sal
        self.temp_sal_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'temp_sal.png')),
                                              'Retrieve Temperature/Salinity', self)
        # self.temp_sal_act.setShortcut('Alt+T')
        # noinspection PyUnresolvedReferences
        self.temp_sal_act.triggered.connect(self.on_retrieve_temp_sal)
        self.process_bar.addAction(self.temp_sal_act)
        self.main_win.edit_menu.addAction(self.temp_sal_act)

        # retrieve transducer sound speed
        self.tss_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'tss.png')),
                                         'Retrieve Transducer Sound Speed', self)
        # self.tss_act.setShortcut('Alt+W')
        # noinspection PyUnresolvedReferences
        self.tss_act.triggered.connect(self.on_retrieve_tss)
        self.process_bar.addAction(self.tss_act)
        self.main_win.edit_menu.addAction(self.tss_act)

        # extend profile
        self.extend_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'extend.png')),
                                            'Extend Profile', self)
        # self.extend_act.setShortcut('Alt+E')
        # noinspection PyUnresolvedReferences
        self.extend_act.triggered.connect(self.on_extend_profile)
        self.process_bar.addAction(self.extend_act)
        self.main_win.edit_menu.addAction(self.extend_act)

        # preview thinning
        self.thin_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'thinning.png')),
                                          'Preview Thinning', self)
        # self.thin_act.setShortcut('Alt+T')
        # noinspection PyUnresolvedReferences
        self.thin_act.triggered.connect(self.on_preview_thinning)
        # self.thin_act.setVisible(False)
        if settings.value("editor_buttons/thinning", 0) == 1:
            self.process_bar.addAction(self.thin_act)
        self.main_win.edit_menu.addAction(self.thin_act)

        # - separator
        self.process_bar.addSeparator()

        # restart processing
        self.restart_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'restart.png')),
                                             'Restart Processing', self)
        # self.restart_act.setShortcut('Alt+N')
        # noinspection PyUnresolvedReferences
        self.restart_act.triggered.connect(self.on_restart_proc)
        if settings.value("editor_buttons/restart", 1) == 1:
            self.process_bar.addAction(self.restart_act)
        self.main_win.edit_menu.addAction(self.restart_act)

        self.output_bar = self.addToolBar('Output')
        self.output_bar.setIconSize(QtCore.QSize(40, 40))

        self.main_win.edit_menu.addSeparator()

        # export
        self.export_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'export.png')),
                                            'Export Data', self)
        self.export_act.setShortcut('Alt+X')
        # noinspection PyUnresolvedReferences
        self.export_act.triggered.connect(self.on_export_single_profile)
        if settings.value("editor_buttons/export", 1) == 1:
            self.output_bar.addAction(self.export_act)
        self.main_win.edit_menu.addAction(self.export_act)

        # transmit
        self.transmit_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'transmit.png')),
                                              'Transmit Data', self)
        self.transmit_act.setShortcut('Alt+T')
        # noinspection PyUnresolvedReferences
        self.transmit_act.triggered.connect(self.on_transmit_data)
        if settings.value("editor_buttons/transmit", 1) == 1:
            self.output_bar.addAction(self.transmit_act)
        self.main_win.edit_menu.addAction(self.transmit_act)

        # save db
        self.save_db_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'db_save.png')),
                                             'Save to Database', self)
        self.save_db_act.setShortcut('Alt+D')
        # noinspection PyUnresolvedReferences
        self.save_db_act.triggered.connect(self.on_save_db)
        if settings.value("editor_buttons/database", 0) == 1:
            self.output_bar.addAction(self.save_db_act)
        self.main_win.edit_menu.addAction(self.save_db_act)

        self.main_win.edit_menu.addSeparator()

        # automate steps
        self.automate_processing_acts = QtWidgets.QAction("Automate processing", self)
        self.automate_processing_acts.setShortcut("Ctrl+A")
        self.automate_processing_acts.setStatusTip("Automate the processing steps")
        # noinspection PyUnresolvedReferences
        self.automate_processing_acts.triggered.connect(self.on_automate_processing)
        self.main_win.edit_menu.addAction(self.automate_processing_acts)

        # buttons visibility
        self.buttons_visibility_acts = QtWidgets.QAction("Change buttons visibility", self)
        self.buttons_visibility_acts.setStatusTip("Define which buttons are displayed on the toolbar")
        # noinspection PyUnresolvedReferences
        self.buttons_visibility_acts.triggered.connect(self.on_buttons_visibility)
        self.main_win.edit_menu.addAction(self.buttons_visibility_acts)

        # exit action
        exit_action = QtWidgets.QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit application")
        # noinspection PyUnresolvedReferences
        exit_action.triggered.connect(self.main_win.close)
        self.main_win.file_menu.addSeparator()
        self.main_win.file_menu.addAction(exit_action)

        # plots
        self.dataplots = DataPlots(main_win=self.main_win, lib=self.lib)
        self.setCentralWidget(self.dataplots)

    def on_input_data(self):
        """Import a data file"""
        logger.debug('user wants to input data')

        self.main_win.switch_to_editor_tab()
        dlg = ImportSingleProfileDialog(lib=self.lib, main_win=self.main_win, parent=self)
        ret = dlg.exec_()
        if ret != QtWidgets.QDialog.Accepted:
            return

        if not self.lib.has_ssp():
            msg = "Unable to retrieve a profile"
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.warning(self, "Input Data", msg, QtWidgets.QMessageBox.Ok)
            return

        if self.lib.cur.data.num_samples == 0:
            msg = "Unable to retrieve samples from the profile"
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.warning(self, "Input Data", msg, QtWidgets.QMessageBox.Ok)
            return

        self.main_win.data_imported()

        # auto-apply options
        self._auto_apply_to_current_profile()

    def on_create_data(self):
        """Import a data file"""
        logger.debug('user wants to create data')

        self.main_win.switch_to_editor_tab()
        dlg = ConstantGradientProfileDialog(lib=self.lib, main_win=self.main_win, parent=self)
        ret = dlg.exec_()
        if ret != QtWidgets.QDialog.Accepted:
            return

        if not self.lib.has_ssp():
            msg = "Unable to retrieve a profile"
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.warning(self, "Input Data", msg, QtWidgets.QMessageBox.Ok)
            return

        if self.lib.cur.data.num_samples == 0:
            msg = "Unable to retrieve samples from the profile"
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.warning(self, "Input Data", msg, QtWidgets.QMessageBox.Ok)
            return

        self.main_win.data_imported()

        # auto-apply options
        self._auto_apply_to_current_profile()

    def _auto_apply_to_current_profile(self):
        settings = QtCore.QSettings()
        if settings.value("auto_smooth_filter") == "true":
            logger.info("auto apply smooth/filter")
            self.on_data_filter()
        if settings.value("auto_sal_temp") == "true":
            if self.temp_sal_act.isEnabled():
                logger.info("auto retrieve temp/sal")
                self.on_retrieve_temp_sal()
            elif self.sal_act.isEnabled():
                logger.info("auto retrieve sal")
                self.on_retrieve_sal()
        if settings.value("auto_tss") == "true":
            logger.info("auto retrieve TSS")
            self.on_retrieve_tss()
        if settings.value("auto_extend") == "true":
            logger.info("auto extend cast")
            self.on_extend_profile()

    def on_clear_data(self):
        logger.debug('user wants to clear data')
        self.lib.clear_data()
        self.main_win.data_cleared()

    def on_seacat(self):
        logger.debug("Open Seabird CTD dialog")
        dlg = SeacatDialog(lib=self.lib, main_win=self.main_win, parent=self)
        ret = dlg.exec_()
        if ret != QtWidgets.QDialog.Accepted:
            logger.info("Seabird CTD dialog closed without selection")
            return

        self.accept()

    def on_set_ref(self):
        logger.debug('user wants to set as a reference')

        self.main_win.switch_to_editor_tab()
        dlg = ReferenceDialog(lib=self.lib, main_win=self.main_win, parent=self)
        success = dlg.exec_()
        if success:
            self.main_win.data_imported()

    def on_restart_proc(self):
        logger.debug('user wants to restart processing')

        self.main_win.switch_to_editor_tab()
        self.lib.restart_proc()
        self.main_win.data_imported()

    def on_data_filter(self):
        logger.debug('user wants to filter/smooth data')

        self.main_win.switch_to_editor_tab()

        if not self.lib.filter_cur_data():
            msg = "Issue in filtering/smoothing the profile"
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.warning(self, "Filter/Smooth", msg, QtWidgets.QMessageBox.Ok)
            return

        self.dataplots.update_data()
        self.dataplots.update_speed_limits()
        self.dataplots.update_temp_limits()
        self.dataplots.update_sal_limits()

    def on_retrieve_sal(self):
        logger.debug('user wants to retrieve salinity')

        self.main_win.switch_to_editor_tab()

        if self.lib.cur.meta.sensor_type not in [Dicts.sensor_types['XBT'], ]:
            msg = "This is a XBT-specific function!"
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.warning(self, "Salinity", msg, QtWidgets.QMessageBox.Ok)
            return

        if not self.lib.replace_cur_salinity():
            msg = "Issue in replacing the salinity"
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.warning(self, "Salinity", msg, QtWidgets.QMessageBox.Ok)
            return

        self.dataplots.update_data()
        self.dataplots.update_speed_limits()
        self.dataplots.update_sal_limits()

    def on_retrieve_temp_sal(self):
        logger.debug('user wants to retrieve temp/sal')

        self.main_win.switch_to_editor_tab()

        if self.lib.cur.meta.sensor_type not in [Dicts.sensor_types['XSV'],
                                                 Dicts.sensor_types['SVP'],
                                                 Dicts.sensor_types['MVP']]:
            msg = "This is a XSV- and SVP-specific function!"
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.warning(self, "Temperature/Salinity", msg, QtWidgets.QMessageBox.Ok)
            return

        if not self.lib.replace_cur_temp_sal():
            msg = "Issue in replacing temperature and salinity"
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.warning(self, "Temperature/Salinity", msg, QtWidgets.QMessageBox.Ok)
            return

        self.dataplots.update_data()
        self.dataplots.update_speed_limits()
        self.dataplots.update_temp_limits()
        self.dataplots.update_sal_limits()

    def on_retrieve_tss(self):
        logger.debug('user wants to retrieve transducer sound speed')

        self.main_win.switch_to_editor_tab()

        if not self.lib.add_cur_tss():
            msg = "Issue in retrieving transducer sound speed"
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.warning(self, "Sound speed", msg, QtWidgets.QMessageBox.Ok)
            return

        self.dataplots.update_data()

    def on_extend_profile(self):
        logger.debug('user wants to extend the profile')

        self.main_win.switch_to_editor_tab()

        if not self.lib.extend_profile():
            msg = "Issue in extending the profile!\n\n" \
                  "Possible causes:\n" \
                  "- The extension source is not active. Look at Setup/Input!\n" \
                  "- The profile from the extension source is too short. Check it on the plots!\n" \
                  "- The extension source does not have a profile at the geographic location.\n" \
                  "Use another source or manually extend the profile!"
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.warning(self, "Profile extension", msg, QtWidgets.QMessageBox.Ok)
            return

        self.dataplots.update_data()
        self.dataplots.update_depth_limits()
        self.dataplots.update_speed_limits()
        self.dataplots.update_temp_limits()
        self.dataplots.update_sal_limits()

    def on_preview_thinning(self):
        logger.debug('user wants to preview thinning')

        self.main_win.switch_to_editor_tab()

        tolerances = [0.01, 0.1, 0.5]
        for tolerance in tolerances:

            if not self.lib.prepare_sis(thin_tolerance=tolerance):
                msg = "Issue in preview the thinning"
                # noinspection PyCallByClass
                QtWidgets.QMessageBox.warning(self, "Thinning preview", msg, QtWidgets.QMessageBox.Ok)
                return

            # checking for number of samples
            si = self.lib.cur.sis_thinned
            thin_profile_length = self.lib.cur.sis.flag[si].size
            logger.debug("thin profile size: %d (with tolerance: %.3f)" % (thin_profile_length, tolerance))
            if thin_profile_length < 1000:
                break

            logger.info("too many samples, attempting with a lower tolerance")

        self.dataplots.update_data()

    def on_spreadsheet(self):
        logger.debug('user wants to read/edit spreadsheet')

        self.main_win.switch_to_editor_tab()

        if not self.lib.has_ssp():
            msg = "Import data before visualize them in a spreadsheet!"
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.warning(self, "Spreadsheet warning", msg, QtWidgets.QMessageBox.Ok)
            return
        dlg = SpreadSheetDialog(lib=self.lib, main_win=self.main_win, parent=self)
        dlg.exec_()

    def on_metadata(self):
        logger.debug('user wants to read/edit metadata')

        self.main_win.switch_to_editor_tab()

        if not self.lib.has_ssp():
            msg = "Import data before visualize metadata!"
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.warning(self, "Metadata warning", msg, QtWidgets.QMessageBox.Ok)
            return
        dlg = MetadataDialog(lib=self.lib, main_win=self.main_win, parent=self)
        dlg.exec_()

    def _run_safety_checks_on_output(self):
        logger.debug('running safety checks on output')

        if not self.lib.has_ssp():
            msg = "You need to first import data!"
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.warning(self, "Data Warning", msg, QtWidgets.QMessageBox.Ok)
            return False

        min_samples = 5

        if len(self.lib.cur.proc.temp) < min_samples:

            msg = "Suspect short temperature profile detected!\n\n" \
                  "Do you really want to continue?"
            # noinspection PyCallByClass
            ret = QtWidgets.QMessageBox.warning(self, "Data Warning", msg,
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if ret == QtWidgets.QMessageBox.No:
                return False

        elif all(i == 0 for i in self.lib.cur.proc.temp[self.lib.cur.proc_valid][:min_samples]):

            msg = "Suspect zero values in the temperature profile detected!\n" \
                  "Invalid values can heavily affect the quality of sonar data.\n\n" \
                  "Do you really want to continue?"
            # noinspection PyCallByClass
            ret = QtWidgets.QMessageBox.warning(self, "Data Warning", msg,
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if ret == QtWidgets.QMessageBox.No:
                return False

        if len(self.lib.cur.proc.sal) < min_samples:

            msg = "Suspect short salinity profile detected!\n\n" \
                  "Do you really want to continue?"
            # noinspection PyCallByClass
            ret = QtWidgets.QMessageBox.warning(self, "Data Warning", msg,
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if ret == QtWidgets.QMessageBox.No:
                return False

        elif all(i == 0 for i in self.lib.cur.proc.sal[self.lib.cur.proc_valid][:min_samples]):

            msg = "Suspect zero values in the salinity profile detected!\n" \
                  "Invalid values can heavily affect the quality of sonar data.\n\n" \
                  "Do you really want to continue?"
            # noinspection PyCallByClass
            ret = QtWidgets.QMessageBox.warning(self, "Data Warning", msg,
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if ret == QtWidgets.QMessageBox.No:
                return False

        if len(self.lib.cur.proc.speed) < min_samples:

            msg = "Suspect short sound speed profile detected!\n\n" \
                  "Do you really want to continue?"
            # noinspection PyCallByClass
            ret = QtWidgets.QMessageBox.warning(self, "Data Warning", msg,
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if ret == QtWidgets.QMessageBox.No:
                return False

        elif all(i == 0 for i in self.lib.cur.proc.speed[self.lib.cur.proc_valid][:min_samples]):

            msg = "Suspect zero values in the sound speed profile detected!\n" \
                  "Invalid values can heavily affect the quality of sonar data.\n\n" \
                  "Do you really want to continue?"
            # noinspection PyCallByClass
            ret = QtWidgets.QMessageBox.warning(self, "Data Warning", msg,
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if ret == QtWidgets.QMessageBox.No:
                return False

        return True

    def on_export_single_profile(self):
        logger.debug('user wants to export a single profile')

        self.main_win.switch_to_editor_tab()

        valid = self._run_safety_checks_on_output()
        if not valid:
            return

        if self.lib.cur.meta.sensor_type in [Dicts.sensor_types['Synthetic'], ]:

            msg = "Do you really want to export a profile\nbased on synthetic %s data?" \
                  % Dicts.first_match(Dicts.probe_types, self.lib.cur.meta.probe_type)
            # noinspection PyCallByClass
            ret = QtWidgets.QMessageBox.warning(self, "Synthetic source warning", msg,
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if ret == QtWidgets.QMessageBox.No:
                return

        if self.lib.cur.meta.probe_type in [Dicts.probe_types['ASVP'],
                                            Dicts.probe_types['CARIS'],
                                            Dicts.probe_types['ELAC'],
                                            Dicts.probe_types['HYPACK']]:

            msg = "Do you really want to export a profile\nbased on pre-processed %s data?" \
                  % Dicts.first_match(Dicts.probe_types, self.lib.cur.meta.probe_type)
            # noinspection PyCallByClass
            ret = QtWidgets.QMessageBox.warning(self, "Pre-processed source warning", msg,
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if ret == QtWidgets.QMessageBox.No:
                return

        dlg = ExportSingleProfileDialog(lib=self.lib, main_win=self.main_win, parent=self)
        result = dlg.exec_()
        if result == QtWidgets.QDialog.Accepted:
            self.on_save_db(auto_save=True)

        self.dataplots.update_data()

    def on_transmit_data(self):
        logger.debug('user wants to transmit the data')

        self.main_win.switch_to_editor_tab()

        valid = self._run_safety_checks_on_output()
        if not valid:
            return

        if self.lib.cur.meta.sensor_type in [Dicts.sensor_types['Synthetic'], ]:

            msg = "Do you really want to transmit a profile\nbased on synthetic %s data?" \
                  % Dicts.first_match(Dicts.probe_types, self.lib.cur.meta.probe_type)
            # noinspection PyCallByClass
            ret = QtWidgets.QMessageBox.warning(self, "Synthetic source warning", msg,
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if ret == QtWidgets.QMessageBox.No:
                return

        if self.lib.cur.meta.probe_type in [Dicts.probe_types['ASVP'],
                                            Dicts.probe_types['CARIS'],
                                            Dicts.probe_types['ELAC'],
                                            Dicts.probe_types['HYPACK']]:

            msg = "Do you really want to transmit a profile\nbased on pre-processed %s data?" \
                  % Dicts.first_match(Dicts.probe_types, self.lib.cur.meta.probe_type)
            # noinspection PyCallByClass
            ret = QtWidgets.QMessageBox.warning(self, "Pre-processed source warning", msg,
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if ret == QtWidgets.QMessageBox.No:
                return

        if not self.lib.transmit_ssp():
            msg = "Possible issue in profile transmission."
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.warning(self, "Profile transmission", msg, QtWidgets.QMessageBox.Ok)

        self.on_save_db(auto_save=True)
        self.dataplots.update_data()

    def on_save_db(self, auto_save=False):

        if auto_save:
            logger.debug('auto-save data to db')
        else:
            logger.debug('user wants to save data to db')
            self.main_win.switch_to_editor_tab()

            # since auto-save the same checks and questions have been asked!

            valid = self._run_safety_checks_on_output()
            if not valid:
                return

            if self.lib.cur.meta.sensor_type in [Dicts.sensor_types['Synthetic'], ]:

                msg = "Do you really want to store a profile based \non synthetic %s data?\n" \
                      % Dicts.first_match(Dicts.probe_types, self.lib.cur.meta.probe_type)
                # noinspection PyCallByClass
                ret = QtWidgets.QMessageBox.warning(self, "Synthetic source warning", msg,
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if ret == QtWidgets.QMessageBox.No:
                    return

            if self.lib.cur.meta.probe_type in [Dicts.probe_types['ASVP'],
                                                Dicts.probe_types['CARIS'],
                                                Dicts.probe_types['ELAC'],
                                                Dicts.probe_types['HYPACK']]:

                msg = "Do you really want to store a profile based \non pre-processed %s data?\n\n" \
                      "This operation may OVERWRITE existing raw data \nin the database!" \
                      % Dicts.first_match(Dicts.probe_types, self.lib.cur.meta.probe_type)
                # noinspection PyCallByClass
                ret = QtWidgets.QMessageBox.warning(self, "Pre-processed source warning", msg,
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if ret == QtWidgets.QMessageBox.No:
                    return

        if not self.lib.store_data():
            msg = "Unable to save to db!"
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.warning(self, "Database warning", msg, QtWidgets.QMessageBox.Ok)
            return

        self.main_win.data_stored()

    def on_automate_processing(self):

        logger.debug('open automate processing dialog')

        self.main_win.switch_to_editor_tab()

        dlg = AutomateDialog(lib=self.lib, main_win=self.main_win, parent=self)
        dlg.exec_()

    def on_buttons_visibility(self):

        logger.debug('open buttons visibility dialog')

        self.main_win.switch_to_editor_tab()

        dlg = ButtonsDialog(lib=self.lib, main_win=self.main_win, parent=self)
        dlg.exec_()

    def data_cleared(self):
        # bars
        self.process_bar.hide()
        self.output_bar.hide()

        # dialogs
        # self.clear_act.setDisabled(True)
        self.set_ref_act.setVisible(False)
        self.restart_act.setVisible(False)
        self.spreadsheet_act.setVisible(False)
        self.filter_act.setVisible(False)
        self.sal_act.setVisible(False)
        self.temp_sal_act.setVisible(False)
        self.tss_act.setVisible(False)
        self.extend_act.setVisible(False)
        self.thin_act.setVisible(False)
        self.metadata_act.setVisible(False)
        self.export_act.setVisible(False)
        self.transmit_act.setVisible(False)
        self.save_db_act.setVisible(False)
        # data plots
        self.dataplots.setHidden(True)

    def data_imported(self):
        # bars
        self.process_bar.show()
        self.output_bar.show()

        # dialogs
        # self.clear_act.setDisabled(False)
        self.set_ref_act.setVisible(True)
        self.restart_act.setVisible(True)
        self.spreadsheet_act.setVisible(True)
        self.metadata_act.setVisible(True)

        self.filter_act.setVisible(True)
        if self.lib.cur.meta.sensor_type in [Dicts.sensor_types['XBT'], ]:
            self.sal_act.setVisible(True)
        else:
            self.sal_act.setVisible(False)

        if self.lib.cur.meta.sensor_type in [Dicts.sensor_types['XSV'],
                                             Dicts.sensor_types['SVP']]:
            self.temp_sal_act.setVisible(True)

        elif self.lib.cur.meta.sensor_type in [Dicts.sensor_types['MVP'], ]:

            if (np.sum(self.lib.cur.proc.temp) == 0) and (np.sum(self.lib.cur.proc.sal) == 0):
                self.temp_sal_act.setVisible(True)
            else:
                self.temp_sal_act.setVisible(False)

        else:
            self.temp_sal_act.setVisible(False)

        if self.lib.use_sis4():
            self.tss_act.setVisible(True)
        else:
            self.tss_act.setVisible(False)

        self.extend_act.setVisible(True)
        self.thin_act.setVisible(True)
        self.export_act.setVisible(True)
        self.transmit_act.setVisible(True)
        self.save_db_act.setVisible(True)

        # data plots
        self.dataplots.reset()
        self.dataplots.on_first_draw()
        self.dataplots.setVisible(True)

        # call required to set a flag that a profile was viewed (and hopefully QC)
        self.lib.cur_plotted()

    def server_started(self):
        self.setDisabled(True)

    def server_stopped(self):
        self.setEnabled(True)
