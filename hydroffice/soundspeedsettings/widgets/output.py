from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

from PySide import QtGui, QtCore

logger = logging.getLogger(__name__)

from .widget import AbstractWidget
from hydroffice.soundspeed.profile.dicts import Dicts


class Output(AbstractWidget):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win, db):
        AbstractWidget.__init__(self, main_win=main_win, db=db)

        lbl_width = 100

        # outline ui
        self.main_layout = QtGui.QVBoxLayout()
        self.frame.setLayout(self.main_layout)

        # - list of setups
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Client list:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- list
        self.client_list = QtGui.QTableWidget()
        self.client_list.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.client_list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        hbox.addWidget(self.client_list)
        # -- button box
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        self.btn_box = QtGui.QDialogButtonBox(QtCore.Qt.Vertical)
        vbox.addWidget(self.btn_box)
        vbox.addStretch()
        # --- new setup
        self.btn_new_client = QtGui.QPushButton("New client")
        self.btn_new_client.clicked.connect(self.new_client)
        self.btn_box.addButton(self.btn_new_client, QtGui.QDialogButtonBox.ActionRole)
        # --- delete setup
        self.btn_delete_client = QtGui.QPushButton("Delete client")
        self.btn_delete_client.clicked.connect(self.delete_client)
        self.btn_box.addButton(self.btn_delete_client, QtGui.QDialogButtonBox.ActionRole)
        # --- refresh
        self.btn_refresh_list = QtGui.QPushButton("Refresh")
        self.btn_refresh_list.clicked.connect(self.refresh)
        self.btn_box.addButton(self.btn_refresh_list, QtGui.QDialogButtonBox.ActionRole)

        self.main_layout.addStretch()

        # - other
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        hbox.addStretch()
        self.label = QtGui.QLabel("Other settings:")
        hbox.addWidget(self.label)
        hbox.addStretch()

        # - append_caris_file
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Append Caris file:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.append_caris_file = QtGui.QComboBox()
        self.append_caris_file.addItems(["True", "False"])
        vbox.addWidget(self.append_caris_file)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_append_caris_file)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        # - log_user
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("User logging:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.log_user = QtGui.QComboBox()
        self.log_user.addItems(["True", "False"])
        vbox.addWidget(self.log_user)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_log_user)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        # - log_server
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Server logging:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.log_server = QtGui.QComboBox()
        self.log_server.addItems(["True", "False"])
        vbox.addWidget(self.log_server)
        vbox.addStretch()
        # -- buttons
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        btn_apply = QtGui.QPushButton("Apply")
        btn_apply.setFixedWidth(lbl_width)
        btn_apply.clicked.connect(self.apply_log_server)
        vbox.addWidget(btn_apply)
        vbox.addStretch()

        self.main_layout.addStretch()

    def new_client(self):
        logger.debug("new setup")

        name = None
        ip = None
        port = None
        protocol = None

        # name
        while True:
            name, ok = QtGui.QInputDialog.getText(self, "New client", "Input a name for the new client")
            if not ok:
                return

            if self.db.client_exists(name):
                QtGui.QMessageBox.information(self, "Invalid client name",
                                              "The input client name already exists.\n"
                                              "You entered: %s" % name)
                continue
            break

        # ip
        while True:
            ip, ok = QtGui.QInputDialog.getText(self, "New client", "Input the IP (e.g., 127.0.0.1)")
            if not ok:
                return

            if not self._valid_ip(ip):
                QtGui.QMessageBox.information(self, "Invalid client IP",
                                              "The format input is not valid.\n"
                                              "You entered: %s" % ip)
                continue
            break

        # port
        while True:
            port, ok = QtGui.QInputDialog.getInteger(self, "New client", "Input the port (e.g., 4001)",
                                                     4001, 0, 65535)
            if not ok:
                return

            if (port < 0) or (port > 65535):
                QtGui.QMessageBox.information(self, "Invalid client port",
                                              "The port valus is outside validity range.\n"
                                              "You entered: %s" % port)
                continue
            break

        # protocol
        while True:
            protocol, ok = QtGui.QInputDialog.getText(self, "New client",
                                                      "Input the protocol (SIS, HYPACK, PDS2000, or QINSY)",
                                                      QtGui.QLineEdit.Normal,
                                                      "SIS")
            if not ok:
                return

            if protocol not in Dicts.clients:
                QtGui.QMessageBox.information(self, "Invalid client protocol",
                                              "You entered: %s" % protocol)
                continue
            break

        self.db.add_client(client_name=name, client_ip=ip, client_port=port, client_protocol=protocol)

        self.refresh()

    @staticmethod
    def _valid_ip(ip):
        tokens = ip.split('.')
        if len(tokens) != 4:
            return False
        for token in tokens:
            try:
                int_token = int(token)
                if (int_token < 0) or (int_token > 255):
                    return False
            except ValueError:
                return False
        return True

    def delete_client(self):
        """Delete a setup if selected"""
        logger.debug("delete client")

        # check if any selection
        sel = self.client_list.selectedItems()
        if len(sel) == 0:
            QtGui.QMessageBox.information(self, "Client deletion",
                                          "You need to first select the client to delete!")
            return

        client_name = sel[1].text()
        self.db.delete_client(client_name)
        self.refresh()

    def apply_append_caris_file(self):
        logger.debug("apply append caris file")
        self.db.append_caris_file = self.append_caris_file.currentText()
        self.setup_changed()

    def apply_log_user(self):
        logger.debug("apply log user")
        self.db.log_user = self.log_user.currentText()
        self.main_win.prj.logging()
        self.setup_changed()

    def apply_log_server(self):
        logger.debug("apply log server")
        self.db.log_server = self.log_server.currentText()
        self.main_win.prj.logging()
        self.setup_changed()

    def refresh(self):
        self.main_win.setup_changed()

    def setup_changed(self):
        """Refresh the setup list"""
        # logger.debug("refresh clients")

        # prepare the table
        self.client_list.clear()
        self.client_list.setColumnCount(5)
        self.client_list.setHorizontalHeaderLabels(['id', 'name', 'IP', 'port', 'protocol'])

        # populate the table
        clients = self.db.client_list
        if len(clients) == 0:
            self.client_list.resizeColumnsToContents()
            return
        self.client_list.setRowCount(len(clients))
        for i, client in enumerate(clients):
            for j, field in enumerate(client):
                item = QtGui.QTableWidgetItem("%s" % field)
                item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.client_list.setItem(i, j, item)

        self.client_list.resizeColumnsToContents()

        # append_caris_file
        if self.db.append_caris_file:
            self.append_caris_file.setCurrentIndex(0)  # True
        else:
            self.append_caris_file.setCurrentIndex(1)  # False

        # log_user
        if self.db.log_user:
            self.log_user.setCurrentIndex(0)  # True
        else:
            self.log_user.setCurrentIndex(1)  # False

        # log_server
        if self.db.log_server:
            self.log_server.setCurrentIndex(0)  # True
        else:
            self.log_server.setCurrentIndex(1)  # False
