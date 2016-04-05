from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

from PySide import QtGui, QtCore

logger = logging.getLogger(__name__)

from .widget import AbstractWidget
from ..dialogs.import_dialog import ImportDialog


class Editor(AbstractWidget):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win, prj):
        AbstractWidget.__init__(self, main_win=main_win, prj=prj)

        self.file_bar = self.addToolBar('File')
        self.file_bar.setIconSize(QtCore.QSize(50, 50))
        # import
        import_action = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'import.png')), 'Import data', self)
        import_action.setShortcut('Alt+I')
        import_action.triggered.connect(self.on_import_data)
        self.file_bar.addAction(import_action)
        # export
        export_action = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'export.png')), 'Export data', self)
        export_action.setShortcut('Alt+E')
        export_action.triggered.connect(self.on_export_data)
        self.file_bar.addAction(export_action)
        # transmit
        transmit_action = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'transmit.png')), 'Transmit data', self)
        transmit_action.setShortcut('Alt+E')
        transmit_action.triggered.connect(self.on_transmit_data)
        self.file_bar.addAction(transmit_action)

    def on_import_data(self):
        """Import a data file"""
        logger.debug('user wants to import a data file')
        dlg = ImportDialog(prj=self.prj, main_win=self.main_win, parent=self)
        dlg.exec_()

    def on_export_data(self):
        print("export")

    def on_transmit_data(self):
        print("transmit")

