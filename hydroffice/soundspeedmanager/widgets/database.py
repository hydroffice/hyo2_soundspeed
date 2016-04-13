from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

from PySide import QtGui, QtCore

logger = logging.getLogger(__name__)

from .widget import AbstractWidget


class Database(AbstractWidget):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win, prj):
        AbstractWidget.__init__(self, main_win=main_win, prj=prj)

        # create the overall layout
        self.main_layout = QtGui.QVBoxLayout()
        self.frame.setLayout(self.main_layout)

        # - label
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        hbox.addStretch()
        self.label = QtGui.QLabel("Database content")
        hbox.addWidget(self.label)
        hbox.addStretch()

        # - list of setups
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- list
        self.ssp_list = QtGui.QTableWidget()
        # self.ssp_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # quit_action = QtGui.QAction("Quit", None)
        # quit_action.triggered.connect(QtGui.qApp.quit)
        # self.ssp_list.addAction(quit_action)

        self.ssp_list.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.ssp_list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        hbox.addWidget(self.ssp_list)

        self.main_layout.addStretch()

        self.update_table()

    def update_table(self):
        lst = self.prj.db_profiles()

        # prepare the table
        self.ssp_list.clear()
        self.ssp_list.setColumnCount(12)
        self.ssp_list.setHorizontalHeaderLabels(['id', 'time', 'location', 'project',
                                                 'sensor', 'probe', 'path',
                                                 'survey', 'vessel', 'sn',
                                                 'proc.time', 'info'])

        # populate the table
        if len(lst) == 0:
            self.setup_list.resizeColumnsToContents()
            return
        self.ssp_list.setRowCount(len(lst))
        for i, ssp in enumerate(lst):
            for j, field in enumerate(ssp):
                item = QtGui.QTableWidgetItem("%s" % field)
                item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.ssp_list.setItem(i, j, item)

        self.ssp_list.resizeColumnsToContents()

    def data_stored(self):
        self.update_table()

    def data_removed(self):
        self.update_table()
