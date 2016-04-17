from __future__ import absolute_import, division, print_function, unicode_literals

import os
import copy
import logging

from PySide import QtGui, QtCore

logger = logging.getLogger(__name__)

from .widget import AbstractWidget
from ..dialogs.import_dialog import ImportDialog
from ..dialogs.receive_dialog import ReceiveDialog
from ..dialogs.spreadsheet_dialog import SpreadSheetDialog
from ..dialogs.metadata_dialog import MetadataDialog
from ..dialogs.export_dialog import ExportDialog
from .dataplots import DataPlots

from hydroffice.soundspeed.profile.dicts import Dicts


class Editor(AbstractWidget):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win, prj):
        AbstractWidget.__init__(self, main_win=main_win, prj=prj)

        self.file_bar = self.addToolBar('File')
        self.file_bar.setIconSize(QtCore.QSize(45, 45))
        # import
        self.import_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'import.png')), 'Import data', self)
        self.import_act.setShortcut('Alt+I')
        self.import_act.triggered.connect(self.on_import_data)
        self.file_bar.addAction(self.import_act)
        # receive
        self.receive_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'receive.png')), 'Receive data', self)
        self.receive_act.setShortcut('Alt+R')
        self.receive_act.triggered.connect(self.on_receive_data)
        self.file_bar.addAction(self.receive_act)
        # load db
        self.load_db_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'db_load.png')), 'Load from database', self)
        self.load_db_act.setShortcut('Alt+L')
        self.load_db_act.triggered.connect(self.on_load_db)
        self.file_bar.addAction(self.load_db_act)
        # clear
        self.clear_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'clear.png')), 'Clear data', self)
        self.clear_act.setShortcut('Alt+C')
        self.clear_act.triggered.connect(self.on_clear_data)
        self.file_bar.addAction(self.clear_act)
        # separator
        self.file_bar.addSeparator()
        # spreadsheet
        self.spreadsheet_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'grid.png')), 'Spreadsheet', self)
        self.spreadsheet_act.setShortcut('Alt+S')
        self.spreadsheet_act.triggered.connect(self.on_spreadsheet)
        self.file_bar.addAction(self.spreadsheet_act)
        # metadata
        self.metadata_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'metadata.png')), 'Metadata', self)
        self.metadata_act.setShortcut('Alt+M')
        self.metadata_act.triggered.connect(self.on_metadata)
        self.file_bar.addAction(self.metadata_act)
        # retrieve sal
        self.sal_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'sal.png')), 'Retrieve salinity', self)
        self.sal_act.setShortcut('Alt+A')
        self.sal_act.triggered.connect(self.on_retrieve_sal)
        self.file_bar.addAction(self.sal_act)
        # retrieve temp/sal
        self.temp_sal_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'temp_sal.png')),
                                          'Retrieve temperature/salinity', self)
        self.temp_sal_act.setShortcut('Alt+T')
        self.temp_sal_act.triggered.connect(self.on_retrieve_temp_sal)
        self.file_bar.addAction(self.temp_sal_act)
        # retrieve transducer sound speed
        self.tss_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'tss.png')),
                                     'Retrieve transducer sound speed', self)
        self.tss_act.setShortcut('Alt+W')
        self.tss_act.triggered.connect(self.on_retrieve_tss)
        self.file_bar.addAction(self.tss_act)
        # extend profile
        self.extend_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'extend.png')), 'Extend profile', self)
        self.extend_act.setShortcut('Alt+E')
        self.extend_act.triggered.connect(self.on_extend_profile)
        self.file_bar.addAction(self.extend_act)
        # preview thinning
        self.thin_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'thinning.png')), 'Preview thinning', self)
        self.thin_act.setShortcut('Alt+H')
        self.thin_act.triggered.connect(self.on_preview_thinning)
        self.file_bar.addAction(self.thin_act)
        # separator
        self.file_bar.addSeparator()
        # export
        self.export_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'export.png')), 'Export data', self)
        self.export_act.setShortcut('Alt+E')
        self.export_act.triggered.connect(self.on_export_data)
        self.file_bar.addAction(self.export_act)
        # transmit
        self.transmit_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'transmit.png')), 'Transmit data', self)
        self.transmit_act.setShortcut('Alt+E')
        self.transmit_act.triggered.connect(self.on_transmit_data)
        self.file_bar.addAction(self.transmit_act)
        # save db
        self.save_db_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'db_save.png')), 'Save to database', self)
        self.save_db_act.setShortcut('Alt+D')
        self.save_db_act.triggered.connect(self.on_save_db)
        self.file_bar.addAction(self.save_db_act)
        # set ref
        self.set_ref_act = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'ref.png')), 'Set as reference', self)
        self.set_ref_act.setShortcut('Alt+R')
        self.set_ref_act.triggered.connect(self.on_set_ref)
        self.file_bar.addAction(self.set_ref_act)

        # plots
        self.dataplots = DataPlots(main_win=self.main_win, prj=self.prj)
        self.setCentralWidget(self.dataplots)

    def on_import_data(self):
        """Import a data file"""
        logger.debug('user wants to import a data file')
        dlg = ImportDialog(prj=self.prj, main_win=self.main_win, parent=self)
        dlg.exec_()
        if self.prj.has_ssp():
            self.main_win.data_imported()

    def on_receive_data(self):
        """Receive data"""
        logger.debug('user wants to receive data')
        dlg = ReceiveDialog(prj=self.prj, main_win=self.main_win, parent=self)
        dlg.exec_()
        if self.prj.has_ssp():
            self.main_win.data_imported()

    def on_load_db(self):
        """Load data from database"""
        logger.debug('user wants to load data from db')

        profiles = self.prj.db_profiles()
        lst = ["#%03d: %s" % (p[0], p[1]) for p in profiles]
        if len(lst) == 0:
            msg = "Store data before import!"
            QtGui.QMessageBox.warning(self, "Database", msg, QtGui.QMessageBox.Ok)
            return

        sel, ok = QtGui.QInputDialog.getItem(self, 'Database', 'Select profile to load:', lst, 0, False)
        if not ok:
            return

        success = self.prj.load_profile(profiles[lst.index(sel)][0])
        if not success:
            msg = "Unable to load profile!"
            QtGui.QMessageBox.warning(self, "Database", msg, QtGui.QMessageBox.Ok)
            return

        if self.prj.has_ssp():
            self.main_win.data_imported()

    def on_clear_data(self):
        logger.debug('user wants to clear data')
        self.prj.clear_data()
        self.main_win.data_cleared()

    def on_retrieve_sal(self):
        logger.debug('user wants to retrieve salinity')

        if self.prj.cur.meta.sensor_type != Dicts.sensor_types['XBT']:
            msg = "This is a XBT-specific function!"
            QtGui.QMessageBox.warning(self, "Salinity", msg, QtGui.QMessageBox.Ok)
            return

        if not self.prj.replace_cur_salinity():
            msg = "Issue in replacing the salinity"
            QtGui.QMessageBox.warning(self, "Salinity", msg, QtGui.QMessageBox.Ok)
            return

        self.dataplots.update_data()

    def on_retrieve_temp_sal(self):
        logger.debug('user wants to retrieve temp/sal')

        if (self.prj.cur.meta.sensor_type != Dicts.sensor_types['XSV']) \
                and (self.prj.cur.meta.sensor_type != Dicts.sensor_types['SVP']):
            msg = "This is a XSV- and SVP-specific function!"
            QtGui.QMessageBox.warning(self, "Temperature/Salinity", msg, QtGui.QMessageBox.Ok)
            return

        if not self.prj.replace_cur_temp_sal():
            msg = "Issue in replacing temperature and salinity"
            QtGui.QMessageBox.warning(self, "Temperature/Salinity", msg, QtGui.QMessageBox.Ok)
            return

        self.dataplots.update_data()

    def on_retrieve_tss(self):
        logger.debug('user wants to retrieve transducer sound speed')

        if not self.prj.add_cur_tss():
            msg = "Issue in retrieving transducer sound speed"
            QtGui.QMessageBox.warning(self, "Sound speed", msg, QtGui.QMessageBox.Ok)
            return

        self.dataplots.update_data()

    def on_extend_profile(self):
        logger.debug('user wants to extend the profile')

        if not self.prj.extend_profile():
            msg = "Issue in extending the profile"
            QtGui.QMessageBox.warning(self, "Profile extension", msg, QtGui.QMessageBox.Ok)
            return

        self.dataplots.update_data()

    def on_preview_thinning(self):
        logger.debug('user wants to preview thinning')

        if not self.prj.prepare_sis():
            msg = "Issue in preview the thinning"
            QtGui.QMessageBox.warning(self, "Thinning preview", msg, QtGui.QMessageBox.Ok)
            return

        self.dataplots.update_data()

    def on_spreadsheet(self):
        logger.debug('user wants to read/edit spreadsheet')
        if not self.prj.has_ssp():
            msg = "Import data before visualize them in a spreadsheet!"
            QtGui.QMessageBox.warning(self, "Spreadsheet warning", msg, QtGui.QMessageBox.Ok)
            return
        dlg = SpreadSheetDialog(prj=self.prj, main_win=self.main_win, parent=self)
        dlg.exec_()

    def on_metadata(self):
        logger.debug('user wants to read/edit metadata')
        if not self.prj.has_ssp():
            msg = "Import data before visualize metadata!"
            QtGui.QMessageBox.warning(self, "Metadata warning", msg, QtGui.QMessageBox.Ok)
            return
        dlg = MetadataDialog(prj=self.prj, main_win=self.main_win, parent=self)
        dlg.exec_()

    def on_export_data(self):
        logger.debug('user wants to export the data')
        if not self.prj.has_ssp():
            msg = "Import data before export!"
            QtGui.QMessageBox.warning(self, "Export warning", msg, QtGui.QMessageBox.Ok)
            return
        dlg = ExportDialog(prj=self.prj, main_win=self.main_win, parent=self)
        dlg.exec_()

    def on_transmit_data(self):
        logger.debug('user wants to transmit the data')
        if not self.prj.has_ssp():
            msg = "Import data before transmit!"
            QtGui.QMessageBox.warning(self, "Transmit warning", msg, QtGui.QMessageBox.Ok)
            return

        if not self.prj.transmit_ssp():
            msg = "Issue in profile transmission"
            QtGui.QMessageBox.warning(self, "Profile transmission", msg, QtGui.QMessageBox.Ok)
            return

        self.dataplots.update_data()

    def on_save_db(self):
        logger.debug('user wants to save data to db')
        if not self.prj.has_ssp():
            msg = "Import data before save to db!"
            QtGui.QMessageBox.warning(self, "Database warning", msg, QtGui.QMessageBox.Ok)
            return

        if not self.prj.store_data():
            msg = "Unable to save to db!"
            QtGui.QMessageBox.warning(self, "Database warning", msg, QtGui.QMessageBox.Ok)
            return
        else:
            self.main_win.data_stored()

    def on_set_ref(self):
        logger.debug('user wants to set as a reference')
        if not self.prj.has_ssp():
            logger.debug('cleaning reference')
            self.prj.ref = None
        else:
            logger.debug('cloning current profile')
            self.prj.ref = copy.deepcopy(self.prj.ssp)

    def data_cleared(self):
        # dialogs
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
        # dialogs
        self.clear_act.setDisabled(False)
        self.spreadsheet_act.setDisabled(False)
        self.metadata_act.setDisabled(False)
        if self.prj.cur.meta.sensor_type == Dicts.sensor_types['XBT']:
            self.sal_act.setDisabled(False)
        else:
            self.sal_act.setDisabled(True)
        if (self.prj.cur.meta.sensor_type == Dicts.sensor_types['XSV']) or \
            (self.prj.cur.meta.sensor_type == Dicts.sensor_types['SVP']):
            self.temp_sal_act.setDisabled(False)
        else:
            self.temp_sal_act.setDisabled(True)
        if self.prj.use_sis():
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
