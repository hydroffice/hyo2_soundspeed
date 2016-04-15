from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

from PySide import QtGui, QtCore

logger = logging.getLogger(__name__)

from .widget import AbstractWidget


class Main(AbstractWidget):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win, db):
        AbstractWidget.__init__(self, main_win=main_win, db=db)

        lbl_width = 100

        # outline ui
        self.main_layout = QtGui.QVBoxLayout()
        self.frame.setLayout(self.main_layout)

        # - active setup
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        hbox.addStretch()
        self.label = QtGui.QLabel()
        hbox.addWidget(self.label)
        hbox.addStretch()

        # - list of setups
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Available settings:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- list
        self.setup_list = QtGui.QTableWidget()
        self.setup_list.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setup_list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        hbox.addWidget(self.setup_list)
        # -- button box
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        self.btn_box = QtGui.QDialogButtonBox(QtCore.Qt.Vertical)
        vbox.addWidget(self.btn_box)
        vbox.addStretch()
        # --- new setup
        self.btn_new_setup = QtGui.QPushButton("New setup")
        self.btn_new_setup.clicked.connect(self.new_setup)
        self.btn_box.addButton(self.btn_new_setup, QtGui.QDialogButtonBox.ActionRole)
        # --- delete setup
        self.btn_delete_setup = QtGui.QPushButton("Delete setup")
        self.btn_delete_setup.clicked.connect(self.delete_setup)
        self.btn_box.addButton(self.btn_delete_setup, QtGui.QDialogButtonBox.ActionRole)
        # --- activate setup
        self.btn_activate_setup = QtGui.QPushButton("Activate setup")
        self.btn_activate_setup.clicked.connect(self.activate_setup)
        self.btn_box.addButton(self.btn_activate_setup, QtGui.QDialogButtonBox.ActionRole)
        # --- refresh
        self.btn_refresh_list = QtGui.QPushButton("Refresh")
        self.btn_refresh_list.clicked.connect(self.refresh)
        self.btn_box.addButton(self.btn_refresh_list, QtGui.QDialogButtonBox.ActionRole)

        self.main_layout.addStretch()

    def new_setup(self):
        logger.debug("new setup")
        while True:
            name, ok = QtGui.QInputDialog.getText(self, "New setup", "Input a name for the new setup")
            if not ok:
                return

            if self.db.setup_exists(name):
                QtGui.QMessageBox.information(self, "Invalid setup name",
                                              "The input setup name already exists.\n"
                                              "You entered: %s" % name)
                continue

            self.db.add_setup(name)
            self.refresh()
            break

    def delete_setup(self):
        """Delete a setup if selected"""
        logger.debug("delete setup")

        # check if any selection
        sel = self.setup_list.selectedItems()
        if len(sel) == 0:
            QtGui.QMessageBox.information(self, "Setup deletion",
                                          "You need to first select the setup to delete!")
            return

        # check if the selected setup is active
        setup_id = int(sel[0].text())
        setup_name = sel[1].text()
        if setup_id == self.db.active_setup_id:
            QtGui.QMessageBox.information(self, "Setup deletion",
                                          "The setup \'%s\' is active!\n"
                                          "You need to first activate another setup." % setup_name)
            return

        self.db.delete_setup(setup_name)
        self.refresh()

    def activate_setup(self):
        logger.debug("activate setup")

        # check if any selection
        sel = self.setup_list.selectedItems()
        if len(sel) == 0:
            QtGui.QMessageBox.information(self, "Setup activation",
                                          "You need to first select the setup to activate!")
            return

        # check if the selected setup is active
        setup_id = int(sel[0].text())
        setup_name = sel[1].text()
        if setup_id == self.db.active_setup_id:
            QtGui.QMessageBox.information(self, "Setup activation",
                                          "The setup \'%s\' is already active!" % setup_name)
            return

        self.db.activate_setup(setup_name)

        self.main_win.setup_changed()

    def refresh(self):
        self.main_win.setup_changed()

    def setup_changed(self):
        """Refresh the setup list"""
        logger.debug("refresh main")

        # set the top label
        self.label.setText("<b>Current setup: %s [#%02d]</b>" % (self.db.setup_name, self.db.active_setup_id))

        # prepare the table
        self.setup_list.clear()
        self.setup_list.setColumnCount(4)
        self.setup_list.setHorizontalHeaderLabels(['id', 'setup name', 'current status', 'version'])

        # populate the table
        setups = self.db.setup_list
        if len(setups) == 0:
            self.setup_list.resizeColumnsToContents()
            return
        self.setup_list.setRowCount(len(setups))
        for i, setup in enumerate(setups):
            for j, field in enumerate(setup):
                item = QtGui.QTableWidgetItem("%s" % field)
                item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.setup_list.setItem(i, j, item)

        self.setup_list.resizeColumnsToContents()
