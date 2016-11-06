from __future__ import absolute_import, division, print_function, unicode_literals

import os
import copy
import logging

from PySide import QtGui, QtCore

logger = logging.getLogger(__name__)

from .widget import AbstractWidget
from ..dialogs.input_dialog import InputDialog
from ..dialogs.spreadsheet_dialog import SpreadSheetDialog
from ..dialogs.metadata_dialog import MetadataDialog
from ..dialogs.export_dialog import ExportDialog
from .dataplots import DataPlots

from hydroffice.soundspeed.profile.dicts import Dicts


class Editor(AbstractWidget):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win, lib):
        AbstractWidget.__init__(self, main_win=main_win, lib=lib)

        self.input_bar = self.addToolBar('Input')
        self.input_bar.setIconSize(QtCore.QSize(42, 42))
        # import
        self.input_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'input.png')),
                                        'Input data', self)
        self.input_act.setShortcut('Alt+I')
        # noinspection PyUnresolvedReferences
        self.input_act.triggered.connect(self.on_input_data)
        self.input_bar.addAction(self.input_act)
        # clear
        self.clear_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'clear.png')), 'Clear data', self)
        self.clear_act.setShortcut('Alt+C')
        # noinspection PyUnresolvedReferences
        self.clear_act.triggered.connect(self.on_clear_data)
        self.input_bar.addAction(self.clear_act)

        self.process_bar = self.addToolBar('Process')
        self.process_bar.setIconSize(QtCore.QSize(42, 42))
        # spreadsheet
        self.spreadsheet_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'grid.png')), 'Spreadsheet', self)
        self.spreadsheet_act.setShortcut('Alt+S')
        # noinspection PyUnresolvedReferences
        self.spreadsheet_act.triggered.connect(self.on_spreadsheet)
        self.process_bar.addAction(self.spreadsheet_act)
        # metadata
        self.metadata_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'metadata.png')), 'Metadata', self)
        self.metadata_act.setShortcut('Alt+M')
        # noinspection PyUnresolvedReferences
        self.metadata_act.triggered.connect(self.on_metadata)
        self.process_bar.addAction(self.metadata_act)
        # - separator
        self.process_bar.addSeparator()
        # retrieve sal
        self.sal_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'sal.png')), 'Retrieve salinity', self)
        self.sal_act.setShortcut('Alt+A')
        # noinspection PyUnresolvedReferences
        self.sal_act.triggered.connect(self.on_retrieve_sal)
        self.process_bar.addAction(self.sal_act)
        # retrieve temp/sal
        self.temp_sal_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'temp_sal.png')),
                                          'Retrieve temperature/salinity', self)
        self.temp_sal_act.setShortcut('Alt+T')
        # noinspection PyUnresolvedReferences
        self.temp_sal_act.triggered.connect(self.on_retrieve_temp_sal)
        self.process_bar.addAction(self.temp_sal_act)
        # retrieve transducer sound speed
        self.tss_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'tss.png')),
                                     'Retrieve transducer sound speed', self)
        self.tss_act.setShortcut('Alt+W')
        # noinspection PyUnresolvedReferences
        self.tss_act.triggered.connect(self.on_retrieve_tss)
        self.process_bar.addAction(self.tss_act)
        # extend profile
        self.extend_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'extend.png')), 'Extend profile', self)
        self.extend_act.setShortcut('Alt+E')
        # noinspection PyUnresolvedReferences
        self.extend_act.triggered.connect(self.on_extend_profile)
        self.process_bar.addAction(self.extend_act)
        # preview thinning
        self.thin_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'thinning.png')), 'Preview thinning', self)
        self.thin_act.setShortcut('Alt+H')
        # noinspection PyUnresolvedReferences
        self.thin_act.triggered.connect(self.on_preview_thinning)
        self.process_bar.addAction(self.thin_act)
        # - separator
        self.process_bar.addSeparator()
        # restart processing
        self.restart_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'restart.png')),
                                         'Restart processing', self)
        self.restart_act.setShortcut('Alt+N')
        # noinspection PyUnresolvedReferences
        self.restart_act.triggered.connect(self.on_restart_proc)
        self.process_bar.addAction(self.restart_act)

        self.output_bar = self.addToolBar('Output')
        self.output_bar.setIconSize(QtCore.QSize(42, 42))
        # export
        self.export_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'export.png')), 'Export data', self)
        self.export_act.setShortcut('Alt+E')
        # noinspection PyUnresolvedReferences
        self.export_act.triggered.connect(self.on_export_data)
        self.output_bar.addAction(self.export_act)
        # transmit
        self.transmit_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'transmit.png')), 'Transmit data', self)
        self.transmit_act.setShortcut('Alt+E')
        # noinspection PyUnresolvedReferences
        self.transmit_act.triggered.connect(self.on_transmit_data)
        self.output_bar.addAction(self.transmit_act)
        # save db
        self.save_db_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'db_save.png')), 'Save to database', self)
        self.save_db_act.setShortcut('Alt+D')
        # noinspection PyUnresolvedReferences
        self.save_db_act.triggered.connect(self.on_save_db)
        self.output_bar.addAction(self.save_db_act)
        # set ref
        self.set_ref_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'ref.png')), 'Reference cast', self)
        self.set_ref_act.setShortcut('Alt+R')
        # noinspection PyUnresolvedReferences
        self.set_ref_act.triggered.connect(self.on_set_ref)
        self.output_bar.addAction(self.set_ref_act)

        # plots
        self.dataplots = DataPlots(main_win=self.main_win, lib=self.lib)
        self.setCentralWidget(self.dataplots)

    def on_input_data(self):
        """Import a data file"""
        logger.debug('user wants to input data')
        dlg = InputDialog(lib=self.lib, main_win=self.main_win, parent=self)
        dlg.exec_()
        if self.lib.has_ssp():
            self.main_win.data_imported()

    def on_clear_data(self):
        logger.debug('user wants to clear data')
        self.lib.clear_data()
        self.main_win.data_cleared()

    def on_restart_proc(self):
        logger.debug('user wants to restart processing')
        self.lib.restart_proc()
        self.main_win.data_imported()

    def on_retrieve_sal(self):
        logger.debug('user wants to retrieve salinity')

        if self.lib.cur.meta.sensor_type != Dicts.sensor_types['XBT']:
            msg = "This is a XBT-specific function!"
            QtGui.QMessageBox.warning(self, "Salinity", msg, QtGui.QMessageBox.Ok)
            return

        if not self.lib.replace_cur_salinity():
            msg = "Issue in replacing the salinity"
            QtGui.QMessageBox.warning(self, "Salinity", msg, QtGui.QMessageBox.Ok)
            return

        self.dataplots.update_data()

    def on_retrieve_temp_sal(self):
        logger.debug('user wants to retrieve temp/sal')

        if (self.lib.cur.meta.sensor_type != Dicts.sensor_types['XSV']) \
                and (self.lib.cur.meta.sensor_type != Dicts.sensor_types['SVP']):
            msg = "This is a XSV- and SVP-specific function!"
            QtGui.QMessageBox.warning(self, "Temperature/Salinity", msg, QtGui.QMessageBox.Ok)
            return

        if not self.lib.replace_cur_temp_sal():
            msg = "Issue in replacing temperature and salinity"
            QtGui.QMessageBox.warning(self, "Temperature/Salinity", msg, QtGui.QMessageBox.Ok)
            return

        self.dataplots.update_data()

    def on_retrieve_tss(self):
        logger.debug('user wants to retrieve transducer sound speed')

        if not self.lib.add_cur_tss():
            msg = "Issue in retrieving transducer sound speed"
            QtGui.QMessageBox.warning(self, "Sound speed", msg, QtGui.QMessageBox.Ok)
            return

        self.dataplots.update_data()

    def on_extend_profile(self):
        logger.debug('user wants to extend the profile')

        if not self.lib.extend_profile():
            msg = "Issue in extending the profile"
            QtGui.QMessageBox.warning(self, "Profile extension", msg, QtGui.QMessageBox.Ok)
            return

        self.dataplots.update_data()

    def on_preview_thinning(self):
        logger.debug('user wants to preview thinning')

        if not self.lib.prepare_sis():
            msg = "Issue in preview the thinning"
            QtGui.QMessageBox.warning(self, "Thinning preview", msg, QtGui.QMessageBox.Ok)
            return

        self.dataplots.update_data()

    def on_spreadsheet(self):
        logger.debug('user wants to read/edit spreadsheet')
        if not self.lib.has_ssp():
            msg = "Import data before visualize them in a spreadsheet!"
            QtGui.QMessageBox.warning(self, "Spreadsheet warning", msg, QtGui.QMessageBox.Ok)
            return
        dlg = SpreadSheetDialog(lib=self.lib, main_win=self.main_win, parent=self)
        dlg.exec_()

    def on_metadata(self):
        logger.debug('user wants to read/edit metadata')
        if not self.lib.has_ssp():
            msg = "Import data before visualize metadata!"
            QtGui.QMessageBox.warning(self, "Metadata warning", msg, QtGui.QMessageBox.Ok)
            return
        dlg = MetadataDialog(lib=self.lib, main_win=self.main_win, parent=self)
        dlg.exec_()

    def on_export_data(self):
        logger.debug('user wants to export the data')
        if not self.lib.has_ssp():
            msg = "Import data before export!"
            QtGui.QMessageBox.warning(self, "Export warning", msg, QtGui.QMessageBox.Ok)
            return
        dlg = ExportDialog(lib=self.lib, main_win=self.main_win, parent=self)
        dlg.exec_()

    def on_transmit_data(self):
        logger.debug('user wants to transmit the data')
        if not self.lib.has_ssp():
            msg = "Import data before transmit!"
            QtGui.QMessageBox.warning(self, "Transmit warning", msg, QtGui.QMessageBox.Ok)
            return

        if not self.lib.transmit_ssp():
            msg = "Issue in profile transmission"
            QtGui.QMessageBox.warning(self, "Profile transmission", msg, QtGui.QMessageBox.Ok)
            return

        self.dataplots.update_data()

    def on_save_db(self):
        logger.debug('user wants to save data to db')
        if not self.lib.has_ssp():
            msg = "Import data before save to db!"
            QtGui.QMessageBox.warning(self, "Database warning", msg, QtGui.QMessageBox.Ok)
            return

        if not self.lib.store_data():
            msg = "Unable to save to db!"
            QtGui.QMessageBox.warning(self, "Database warning", msg, QtGui.QMessageBox.Ok)
            return
        else:
            self.main_win.data_stored()

    def on_set_ref(self):
        logger.debug('user wants to set as a reference')
        if not self.lib.has_ssp():
            logger.debug('cleaning reference')
            self.lib.ref = None
        else:
            logger.debug('cloning current profile')
            self.lib.ref = copy.deepcopy(self.lib.ssp)

    def data_cleared(self):
        # bars
        self.process_bar.hide()
        self.output_bar.hide()
        # dialogs
        self.restart_act.setDisabled(True)
        self.clear_act.setDisabled(True)
        self.spreadsheet_act.setDisabled(True)
        self.sal_act.setDisabled(True)
        self.temp_sal_act.setDisabled(True)
        self.tss_act.setDisabled(True)
        self.extend_act.setDisabled(True)
        self.thin_act.setDisabled(True)
        self.metadata_act.setDisabled(True)
        self.export_act.setDisabled(True)
        self.transmit_act.setDisabled(True)
        self.save_db_act.setDisabled(True)
        # data plots
        self.dataplots.setHidden(True)

    def data_imported(self):
        # bars
        self.process_bar.show()
        self.output_bar.show()
        # dialogs
        self.restart_act.setDisabled(False)
        self.clear_act.setDisabled(False)
        self.spreadsheet_act.setDisabled(False)
        self.metadata_act.setDisabled(False)
        if self.lib.cur.meta.sensor_type == Dicts.sensor_types['XBT']:
            self.sal_act.setDisabled(False)
        else:
            self.sal_act.setDisabled(True)
        if (self.lib.cur.meta.sensor_type == Dicts.sensor_types['XSV']) or \
            (self.lib.cur.meta.sensor_type == Dicts.sensor_types['SVP']):
            self.temp_sal_act.setDisabled(False)
        else:
            self.temp_sal_act.setDisabled(True)
        if self.lib.use_sis():
            self.tss_act.setDisabled(False)
        else:
            self.tss_act.setDisabled(True)
        self.extend_act.setDisabled(False)
        self.thin_act.setDisabled(False)
        self.export_act.setDisabled(False)
        self.transmit_act.setDisabled(False)
        self.save_db_act.setDisabled(False)

        # data plots
        self.dataplots.reset()
        self.dataplots.on_draw()
        self.dataplots.setVisible(True)

    def server_started(self):
        self.setDisabled(True)

    def server_stopped(self):
        self.setEnabled(True)
