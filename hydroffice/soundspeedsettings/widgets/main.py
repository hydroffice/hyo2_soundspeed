from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

from PySide import QtGui, QtCore

logger = logging.getLogger(__name__)

from .widget import AbstractWidget
from hydroffice.soundspeed.base.setup import Setup


class Main(AbstractWidget):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win, db):
        AbstractWidget.__init__(self, main_win=main_win, db=db)

        lbl_width = 60

        # outline ui
        self.main_layout = QtGui.QVBoxLayout()
        self.frame.setLayout(self.main_layout)

        # - active setup
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        hbox.addStretch()
        self.active_label = QtGui.QLabel()
        hbox.addWidget(self.active_label)
        hbox.addStretch()

        # - list of setups
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)

        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Setups:")
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
        self.btn_new_setup = QtGui.QPushButton("New")
        # noinspection PyUnresolvedReferences
        self.btn_new_setup.clicked.connect(self.new_setup)
        self.btn_box.addButton(self.btn_new_setup, QtGui.QDialogButtonBox.ActionRole)
        # --- import setup
        self.btn_import_setup = QtGui.QPushButton("Import")
        # noinspection PyUnresolvedReferences
        self.btn_import_setup.clicked.connect(self.import_setup)
        self.btn_box.addButton(self.btn_import_setup, QtGui.QDialogButtonBox.ActionRole)
        # --- clone setup
        self.btn_clone_setup = QtGui.QPushButton("Clone")
        # noinspection PyUnresolvedReferences
        self.btn_clone_setup.clicked.connect(self.clone_setup)
        self.btn_box.addButton(self.btn_clone_setup, QtGui.QDialogButtonBox.ActionRole)
        # --- rename setup
        self.btn_rename_setup = QtGui.QPushButton("Rename")
        # noinspection PyUnresolvedReferences
        self.btn_rename_setup.clicked.connect(self.rename_setup)
        self.btn_box.addButton(self.btn_rename_setup, QtGui.QDialogButtonBox.ActionRole)
        # --- delete setup
        self.btn_delete_setup = QtGui.QPushButton("Delete")
        # noinspection PyUnresolvedReferences
        self.btn_delete_setup.clicked.connect(self.delete_setup)
        self.btn_box.addButton(self.btn_delete_setup, QtGui.QDialogButtonBox.ActionRole)
        # --- activate setup
        self.btn_activate_setup = QtGui.QPushButton("Activate")
        # noinspection PyUnresolvedReferences
        self.btn_activate_setup.clicked.connect(self.activate_setup)
        self.btn_box.addButton(self.btn_activate_setup, QtGui.QDialogButtonBox.ActionRole)
        # --- refresh
        self.btn_refresh_list = QtGui.QPushButton("Refresh")
        # noinspection PyUnresolvedReferences
        self.btn_refresh_list.clicked.connect(self.on_setup_changed)
        self.btn_box.addButton(self.btn_refresh_list, QtGui.QDialogButtonBox.ActionRole)

        self.main_layout.addSpacing(18)

    def new_setup(self):
        logger.debug("new setup")
        while True:
            # noinspection PyCallByClass
            name, ok = QtGui.QInputDialog.getText(self, "New setup", "Input a name for the new setup")
            if not ok:
                return

            if self.db.setup_exists(name):
                # noinspection PyCallByClass
                QtGui.QMessageBox.information(self, "Invalid setup name",
                                              "The input setup name already exists.\n"
                                              "You entered: %s" % name)
                continue

            self.db.add_setup(name)
            self.setup_changed()
            break

    def import_setup(self):
        logger.debug("import setup")

        # ask the file path to the user
        flt = "Setup DB (setup.db)"
        settings = QtCore.QSettings()
        selection, _ = QtGui.QFileDialog.getOpenFileName(self, "Select input setup DB",
                                                         settings.value("export_folder"),
                                                         flt)
        if not selection:
            return

        try:
            # look inside the user selected setup db
            input_db = Setup(release_folder=os.path.dirname(selection))
            input_setups = input_db.db.setup_list
        except Exception as e:
            QtGui.QMessageBox.information(self, "Importable setup",
                                          "Unable to load the selected setup.\n"
                                          "Reason: %s" % e)
            return

        # be sure that there is not naming crash
        importable_setups = list()
        stopped_setups = list()
        for input_setup in input_setups:
            if self.db.setup_exists(input_setup[1]):
                stopped_setups.append(input_setup[1])
            else:
                importable_setups.append(input_setup[1])

        # in case of not importable setup, notify users
        if len(importable_setups) == 0:
            msg = str()
            for stopped_setup in stopped_setups:
                msg += "- %s\n" % stopped_setup

            QtGui.QMessageBox.information(self, "Importable setup",
                                          "No importable setups! Naming crash?\n\n"
                                          "List of troublesome setups:\n%s" % msg)
            return

        # ask the user which setup to import
        sel, ok = QtGui.QInputDialog.getItem(self, 'Do you want to import an existing setup?',
                                             'Select one (or click on Cancel to create a new one):',
                                             importable_setups, 0, False)
        if ok:
            # add the new setup name
            self.db.add_setup(sel)
            input_db.use_setup_name = sel
            input_db.load_from_db()
            input_db.release_folder = self.db.data_folder
            input_db.save_to_db()

            self.setup_changed()

    def clone_setup(self):
        logger.debug("clone setup")

        # check if any selection
        sel = self.setup_list.selectedItems()
        if len(sel) == 0:
            # noinspection PyCallByClass
            QtGui.QMessageBox.information(self, "Setup cloning",
                                          "You need to first select the setup to clone!")
            return

        original_setup_name = sel[0].text()

        while True:
            # noinspection PyCallByClass
            cloned_setup_name, ok = QtGui.QInputDialog.getText(self, "New setup", "Input a name for the cloned setup")
            if not ok:
                return

            if self.db.setup_exists(cloned_setup_name):
                # noinspection PyCallByClass
                QtGui.QMessageBox.information(self, "Invalid setup name",
                                              "The name for the cloned setup already exists.\n"
                                              "You entered: %s" % cloned_setup_name)
                continue

            self.main_win.lib.clone_setup(original_setup_name, cloned_setup_name)
            self.setup_changed()
            break

    def rename_setup(self):
        """Delete a setup if selected"""
        logger.debug("rename setup")

        # check if any selection
        sel = self.setup_list.selectedItems()
        if len(sel) == 0:
            # noinspection PyCallByClass
            QtGui.QMessageBox.information(self, "Setup renaming",
                                          "You need to first select the setup to rename!")
            return

        # check if the selected setup is active
        original_setup_name = sel[0].text()
        original_setup_id = self.db.setup_id_from_setup_name(original_setup_name)
        if original_setup_id == self.db.active_setup_id:
            # noinspection PyCallByClass
            QtGui.QMessageBox.information(self, "Setup renaming",
                                          "The setup \'%s\' is active!\n"
                                          "You need to first activate another setup." % original_setup_name)
            return

        while True:
            # noinspection PyCallByClass
            cloned_setup_name, ok = QtGui.QInputDialog.getText(self, "New setup", "Input a name for the cloned setup")
            if not ok:
                return

            if self.db.setup_exists(cloned_setup_name):
                # noinspection PyCallByClass
                QtGui.QMessageBox.information(self, "Invalid setup name",
                                              "The name for the cloned setup already exists.\n"
                                              "You entered: %s" % cloned_setup_name)
                continue

            self.main_win.lib.rename_setup(original_setup_name, cloned_setup_name)
            self.setup_changed()
            break

    def delete_setup(self):
        """Delete a setup if selected"""
        logger.debug("delete setup")

        # check if any selection
        sel = self.setup_list.selectedItems()
        if len(sel) == 0:
            # noinspection PyCallByClass
            QtGui.QMessageBox.information(self, "Setup deletion",
                                          "You need to first select the setup to delete!")
            return

        # check if the selected setup is active
        setup_name = sel[0].text()
        setup_id = self.db.setup_id_from_setup_name(setup_name)
        if setup_id == self.db.active_setup_id:
            # noinspection PyCallByClass
            QtGui.QMessageBox.information(self, "Setup deletion",
                                          "The setup \'%s\' is active!\n"
                                          "You need to first activate another setup." % setup_name)
            return

        self.db.delete_setup(setup_name)
        self.setup_changed()

    def activate_setup(self):
        logger.debug("activate setup")

        # check if any selection
        sel = self.setup_list.selectedItems()
        if len(sel) == 0:
            # noinspection PyCallByClass
            QtGui.QMessageBox.information(self, "Setup activation",
                                          "You need to first select the setup to activate!")
            return

        # check if the selected setup is active
        setup_name = sel[0].text()
        setup_id = self.db.setup_id_from_setup_name(setup_name)
        if setup_id == self.db.active_setup_id:
            # noinspection PyCallByClass
            QtGui.QMessageBox.information(self, "Setup activation",
                                          "The setup \'%s\' is already active!" % setup_name)
            return

        self.db.activate_setup(setup_name)
        self.main_win.setup_changed()

    def on_setup_changed(self):
        self.main_win.setup_changed()

    def setup_changed(self):
        """Refresh the setup list"""
        # logger.debug("refresh main")

        # set the top label
        self.active_label.setText("<b>Current setup: %s [#%02d]</b>" % (self.db.setup_name, self.db.active_setup_id))

        # prepare the table
        self.setup_list.clear()
        self.setup_list.setColumnCount(3)
        self.setup_list.setHorizontalHeaderLabels(['name', 'status', 'setup version'])

        # populate the table
        setups = self.db.setup_list
        if len(setups) == 0:
            self.setup_list.resizeColumnsToContents()
            return

        bold_font = QtGui.QFont()
        bold_font.setBold(True)

        self.setup_list.setRowCount(len(setups))
        for i, setup in enumerate(setups):

            # print(setup)
            is_active = False

            for j, field in enumerate(setup):

                if j == 0:
                    continue

                item = QtGui.QTableWidgetItem("%s" % field)
                item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

                # make bold the active
                if j == 2:
                    if field == 'active':
                        item.setFont(bold_font)

                self.setup_list.setItem(i, j - 1, item)

        self.setup_list.resizeColumnsToContents()
