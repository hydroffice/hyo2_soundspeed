from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

from PySide import QtGui, QtCore

logger = logging.getLogger(__name__)

from .widget import AbstractWidget
from ..dialogs.import_dialog import ImportDialog
from ..dialogs.spreadsheet_dialog import SpreadSheetDialog
from ..dialogs.metadata_dialog import MetadataDialog
from ..dialogs.export_dialog import ExportDialog
from .dataplots import DataPlots


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

    def on_clear_data(self):
        logger.debug('user wants to clear data')
        self.prj.clear_data()
        self.main_win.data_cleared()

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

    def data_cleared(self):
        # dialogs
        self.spreadsheet_act.setDisabled(True)
        self.metadata_act.setDisabled(True)
        self.clear_act.setDisabled(True)
        self.export_act.setDisabled(True)
        self.transmit_act.setDisabled(True)
        # data plots
        self.dataplots.setHidden(True)

    def data_imported(self):
        # dialogs
        self.spreadsheet_act.setDisabled(False)
        self.metadata_act.setDisabled(False)
        self.clear_act.setDisabled(False)
        self.export_act.setDisabled(False)
        self.transmit_act.setDisabled(False)
        # data plots
        self.dataplots.reset()
        self.dataplots.on_draw()
        self.dataplots.setVisible(True)
