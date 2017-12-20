import numpy as np
import os
import logging

from PySide import QtGui, QtCore

logger = logging.getLogger(__name__)

from hyo.soundspeedmanager.widgets.widget import AbstractWidget
from hyo.soundspeedmanager.dialogs.import_single_profile_dialog import ImportSingleProfileDialog
from hyo.soundspeedmanager.dialogs.reference_dialog import ReferenceDialog
from hyo.soundspeedmanager.dialogs.spreadsheet_dialog import SpreadSheetDialog
from hyo.soundspeedmanager.dialogs.metadata_dialog import MetadataDialog
from hyo.soundspeedmanager.dialogs.export_single_profile_dialog import ExportSingleProfileDialog
from hyo.soundspeedmanager.widgets.dataplots import DataPlots

from hyo.soundspeed.profile.dicts import Dicts


class Editor(AbstractWidget):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win, lib):
        AbstractWidget.__init__(self, main_win=main_win, lib=lib)

        self.input_bar = self.addToolBar('Input')
        self.input_bar.setIconSize(QtCore.QSize(40, 40))

        # import
        self.input_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'input.png')),
                                       'Input Data', self)
        self.input_act.setShortcut('Alt+I')
        # noinspection PyUnresolvedReferences
        self.input_act.triggered.connect(self.on_input_data)
        self.input_bar.addAction(self.input_act)
        self.main_win.file_menu.addAction(self.input_act)

        # clear
        self.clear_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'clear.png')),
                                       'Clear Data', self)
        self.clear_act.setShortcut('Alt+C')
        # noinspection PyUnresolvedReferences
        self.clear_act.triggered.connect(self.on_clear_data)
        # set hidden, but the whole action is candidate to deletion
        self.clear_act.setVisible(False)
        self.input_bar.addAction(self.clear_act)

        # set ref
        self.set_ref_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'ref.png')),
                                         'Reference Cast', self)
        self.set_ref_act.setShortcut('Alt+R')
        # noinspection PyUnresolvedReferences
        self.set_ref_act.triggered.connect(self.on_set_ref)
        self.input_bar.addAction(self.set_ref_act)
        self.main_win.file_menu.addAction(self.set_ref_act)

        self.process_bar = self.addToolBar('Process')
        self.process_bar.setIconSize(QtCore.QSize(40, 40))

        # spreadsheet
        self.spreadsheet_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'grid.png')),
                                             'Show/Edit Data Spreadsheet', self)
        self.spreadsheet_act.setShortcut('Alt+S')
        # noinspection PyUnresolvedReferences
        self.spreadsheet_act.triggered.connect(self.on_spreadsheet)
        # self.process_bar.addAction(self.spreadsheet_act)
        self.main_win.edit_menu.addAction(self.spreadsheet_act)

        # metadata
        self.metadata_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'metadata.png')),
                                          'Show/Edit Cast Metadata', self)
        self.metadata_act.setShortcut('Alt+M')
        # noinspection PyUnresolvedReferences
        self.metadata_act.triggered.connect(self.on_metadata)
        self.process_bar.addAction(self.metadata_act)
        self.main_win.edit_menu.addAction(self.metadata_act)

        # - separator
        self.process_bar.addSeparator()

        # filter
        self.filter_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'filter.png')),
                                        'Apply Data Filter', self)
        self.filter_act.setShortcut('Alt+F')
        # noinspection PyUnresolvedReferences
        self.filter_act.triggered.connect(self.on_data_filter)
        self.process_bar.addAction(self.filter_act)
        self.main_win.edit_menu.addSeparator()
        self.main_win.edit_menu.addAction(self.filter_act)

        # retrieve sal
        self.sal_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'sal.png')),
                                     'Retrieve Salinity', self)
        self.sal_act.setShortcut('Alt+A')
        # noinspection PyUnresolvedReferences
        self.sal_act.triggered.connect(self.on_retrieve_sal)
        self.process_bar.addAction(self.sal_act)

        # retrieve temp/sal
        self.temp_sal_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'temp_sal.png')),
                                          'Retrieve Temperature/Salinity', self)
        self.temp_sal_act.setShortcut('Alt+T')
        # noinspection PyUnresolvedReferences
        self.temp_sal_act.triggered.connect(self.on_retrieve_temp_sal)
        self.process_bar.addAction(self.temp_sal_act)
        self.main_win.edit_menu.addAction(self.temp_sal_act)

        # retrieve transducer sound speed
        self.tss_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'tss.png')),
                                     'Retrieve Transducer Sound Speed', self)
        self.tss_act.setShortcut('Alt+W')
        # noinspection PyUnresolvedReferences
        self.tss_act.triggered.connect(self.on_retrieve_tss)
        self.process_bar.addAction(self.tss_act)
        self.main_win.edit_menu.addAction(self.tss_act)

        # extend profile
        self.extend_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'extend.png')),
                                        'Extend Profile', self)
        self.extend_act.setShortcut('Alt+E')
        # noinspection PyUnresolvedReferences
        self.extend_act.triggered.connect(self.on_extend_profile)
        self.process_bar.addAction(self.extend_act)
        self.main_win.edit_menu.addAction(self.extend_act)

        # preview thinning
        self.thin_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'thinning.png')),
                                      'Preview Thinning', self)
        self.thin_act.setShortcut('Alt+H')
        # noinspection PyUnresolvedReferences
        self.thin_act.triggered.connect(self.on_preview_thinning)
        # self.thin_act.setVisible(False)
        # self.process_bar.addAction(self.thin_act)
        self.main_win.edit_menu.addAction(self.thin_act)

        # - separator
        self.process_bar.addSeparator()

        # restart processing
        self.restart_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'restart.png')),
                                         'Restart Processing', self)
        self.restart_act.setShortcut('Alt+N')
        # noinspection PyUnresolvedReferences
        self.restart_act.triggered.connect(self.on_restart_proc)
        self.process_bar.addAction(self.restart_act)
        self.main_win.edit_menu.addAction(self.restart_act)

        self.output_bar = self.addToolBar('Output')
        self.output_bar.setIconSize(QtCore.QSize(40, 40))

        # export
        self.export_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'export.png')),
                                        'Export Data', self)
        self.export_act.setShortcut('Alt+X')
        # noinspection PyUnresolvedReferences
        self.export_act.triggered.connect(self.on_export_single_profile)
        self.output_bar.addAction(self.export_act)
        self.main_win.edit_menu.addSeparator()
        self.main_win.edit_menu.addAction(self.export_act)

        # transmit
        self.transmit_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'transmit.png')),
                                          'Transmit Data', self)
        self.transmit_act.setShortcut('Alt+T')
        # noinspection PyUnresolvedReferences
        self.transmit_act.triggered.connect(self.on_transmit_data)
        self.output_bar.addAction(self.transmit_act)
        self.main_win.edit_menu.addAction(self.transmit_act)

        # save db
        self.save_db_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'db_save.png')),
                                         'Save to Database', self)
        self.save_db_act.setShortcut('Alt+D')
        # noinspection PyUnresolvedReferences
        self.save_db_act.triggered.connect(self.on_save_db)
        # self.output_bar.addAction(self.save_db_act)
        self.main_win.edit_menu.addAction(self.save_db_act)

        # exit action
        exit_action = QtGui.QAction("Exit", self)
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
        dlg.exec_()
        if self.lib.has_ssp():
            self.main_win.data_imported()

    def on_clear_data(self):
        logger.debug('user wants to clear data')
        self.lib.clear_data()
        self.main_win.data_cleared()

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
        logger.debug('user wants to filter data')
        self.lib.cur.remove_pre_water_entry()
        self.lib.cur.statistical_filter()
        self.lib.cur.cosine_smooth()

        self.main_win.switch_to_editor_tab()

    def on_retrieve_sal(self):
        logger.debug('user wants to retrieve salinity')

        self.main_win.switch_to_editor_tab()

        if self.lib.cur.meta.sensor_type not in [Dicts.sensor_types['XBT'], ]:
            msg = "This is a XBT-specific function!"
            # noinspection PyCallByClass
            QtGui.QMessageBox.warning(self, "Salinity", msg, QtGui.QMessageBox.Ok)
            return

        if not self.lib.replace_cur_salinity():

            msg = "Issue in replacing the salinity"
            # noinspection PyCallByClass
            QtGui.QMessageBox.warning(self, "Salinity", msg, QtGui.QMessageBox.Ok)
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
            QtGui.QMessageBox.warning(self, "Temperature/Salinity", msg, QtGui.QMessageBox.Ok)
            return

        if not self.lib.replace_cur_temp_sal():
            msg = "Issue in replacing temperature and salinity"
            # noinspection PyCallByClass
            QtGui.QMessageBox.warning(self, "Temperature/Salinity", msg, QtGui.QMessageBox.Ok)
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
            QtGui.QMessageBox.warning(self, "Sound speed", msg, QtGui.QMessageBox.Ok)
            return

        self.dataplots.update_data()

    def on_extend_profile(self):
        logger.debug('user wants to extend the profile')

        self.main_win.switch_to_editor_tab()

        if not self.lib.extend_profile():
            msg = "Issue in extending the profile.\n\nCheck in the settings if the selected atlas source is active!"
            # noinspection PyCallByClass
            QtGui.QMessageBox.warning(self, "Profile extension", msg, QtGui.QMessageBox.Ok)
            return

        self.dataplots.update_data()
        self.dataplots.update_depth_limits()
        self.dataplots.update_speed_limits()
        self.dataplots.update_temp_limits()
        self.dataplots.update_sal_limits()

    def on_preview_thinning(self):
        logger.debug('user wants to preview thinning')

        self.main_win.switch_to_editor_tab()

        if not self.lib.prepare_sis():
            msg = "Issue in preview the thinning"
            # noinspection PyCallByClass
            QtGui.QMessageBox.warning(self, "Thinning preview", msg, QtGui.QMessageBox.Ok)
            return

        self.dataplots.update_data()

    def on_spreadsheet(self):
        logger.debug('user wants to read/edit spreadsheet')

        self.main_win.switch_to_editor_tab()

        if not self.lib.has_ssp():
            msg = "Import data before visualize them in a spreadsheet!"
            # noinspection PyCallByClass
            QtGui.QMessageBox.warning(self, "Spreadsheet warning", msg, QtGui.QMessageBox.Ok)
            return
        dlg = SpreadSheetDialog(lib=self.lib, main_win=self.main_win, parent=self)
        dlg.exec_()

    def on_metadata(self):
        logger.debug('user wants to read/edit metadata')

        self.main_win.switch_to_editor_tab()

        if not self.lib.has_ssp():
            msg = "Import data before visualize metadata!"
            # noinspection PyCallByClass
            QtGui.QMessageBox.warning(self, "Metadata warning", msg, QtGui.QMessageBox.Ok)
            return
        dlg = MetadataDialog(lib=self.lib, main_win=self.main_win, parent=self)
        dlg.exec_()

    def _run_safety_checks_on_output(self):
        logger.debug('running safety checks on output')

        if not self.lib.has_ssp():

            msg = "You need to first import data!"
            # noinspection PyCallByClass
            QtGui.QMessageBox.warning(self, "Data Warning", msg, QtGui.QMessageBox.Ok)
            return False

        min_samples = 5

        if len(self.lib.cur.proc.temp) < min_samples:

            msg = "Suspect short temperature profile detected!\n\n" \
                  "Do you really want to continue?"
            # noinspection PyCallByClass
            ret = QtGui.QMessageBox.warning(self, "Data Warning", msg, QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return False

        elif all(i == 0 for i in self.lib.cur.proc.temp[self.lib.cur.proc_valid][:min_samples]):

            msg = "Suspect zero values in the temperature profile detected!\n" \
                  "Invalid values can heavily affect the quality of sonar data.\n\n" \
                  "Do you really want to continue?"
            # noinspection PyCallByClass
            ret = QtGui.QMessageBox.warning(self, "Data Warning", msg, QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return False

        if len(self.lib.cur.proc.sal) < min_samples:

            msg = "Suspect short salinity profile detected!\n\n" \
                  "Do you really want to continue?"
            # noinspection PyCallByClass
            ret = QtGui.QMessageBox.warning(self, "Data Warning", msg, QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return False

        elif all(i == 0 for i in self.lib.cur.proc.sal[self.lib.cur.proc_valid][:min_samples]):

            msg = "Suspect zero values in the salinity profile detected!\n" \
                  "Invalid values can heavily affect the quality of sonar data.\n\n" \
                  "Do you really want to continue?"
            # noinspection PyCallByClass
            ret = QtGui.QMessageBox.warning(self, "Data Warning", msg, QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return False

        if len(self.lib.cur.proc.speed) < min_samples:

            msg = "Suspect short sound speed profile detected!\n\n" \
                  "Do you really want to continue?"
            # noinspection PyCallByClass
            ret = QtGui.QMessageBox.warning(self, "Data Warning", msg, QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return False

        elif all(i == 0 for i in self.lib.cur.proc.speed[self.lib.cur.proc_valid][:min_samples]):

            msg = "Suspect zero values in the sound speed profile detected!\n" \
                  "Invalid values can heavily affect the quality of sonar data.\n\n" \
                  "Do you really want to continue?"
            # noinspection PyCallByClass
            ret = QtGui.QMessageBox.warning(self, "Data Warning", msg, QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
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
            ret = QtGui.QMessageBox.warning(self, "Synthetic source warning", msg,
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return

        if self.lib.cur.meta.probe_type in [Dicts.probe_types['ASVP'],
                                            Dicts.probe_types['CARIS'],
                                            Dicts.probe_types['ELAC']]:

            msg = "Do you really want to export a profile\nbased on pre-processed %s data?" \
                  % Dicts.first_match(Dicts.probe_types, self.lib.cur.meta.probe_type)
            # noinspection PyCallByClass
            ret = QtGui.QMessageBox.warning(self, "Pre-processed source warning", msg,
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return

        dlg = ExportSingleProfileDialog(lib=self.lib, main_win=self.main_win, parent=self)
        result = dlg.exec_()
        if result == QtGui.QDialog.Accepted:
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
            ret = QtGui.QMessageBox.warning(self, "Synthetic source warning", msg,
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return

        if self.lib.cur.meta.probe_type in [Dicts.probe_types['ASVP'],
                                            Dicts.probe_types['CARIS'],
                                            Dicts.probe_types['ELAC']]:

            msg = "Do you really want to transmit a profile\nbased on pre-processed %s data?" \
                  % Dicts.first_match(Dicts.probe_types, self.lib.cur.meta.probe_type)
            # noinspection PyCallByClass
            ret = QtGui.QMessageBox.warning(self, "Pre-processed source warning", msg,
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return

        if not self.lib.transmit_ssp():
            msg = "Possible issue in profile transmission."
            # noinspection PyCallByClass
            QtGui.QMessageBox.warning(self, "Profile transmission", msg, QtGui.QMessageBox.Ok)

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
                ret = QtGui.QMessageBox.warning(self, "Synthetic source warning", msg,
                                                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                if ret == QtGui.QMessageBox.No:
                    return

            if self.lib.cur.meta.probe_type in [Dicts.probe_types['ASVP'],
                                                Dicts.probe_types['CARIS'],
                                                Dicts.probe_types['ELAC']]:

                msg = "Do you really want to store a profile based \non pre-processed %s data?\n\n" \
                      "This operation may OVERWRITE existing raw data \nin the database!" \
                      % Dicts.first_match(Dicts.probe_types, self.lib.cur.meta.probe_type)
                # noinspection PyCallByClass
                ret = QtGui.QMessageBox.warning(self, "Pre-processed source warning", msg,
                                                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                if ret == QtGui.QMessageBox.No:
                    return

        if not self.lib.store_data():
            msg = "Unable to save to db!"
            # noinspection PyCallByClass
            QtGui.QMessageBox.warning(self, "Database warning", msg, QtGui.QMessageBox.Ok)
            return

        self.main_win.data_stored()

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

        if self.lib.use_sis():
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
