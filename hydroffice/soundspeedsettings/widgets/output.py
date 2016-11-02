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

        lbl_width = 120

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
        self.btn_box.addButton(self.btn_new_client, QtGui.QDialogButtonBox.ActionRole)
        # --- delete setup
        self.btn_delete_client = QtGui.QPushButton("Delete client")
        self.btn_box.addButton(self.btn_delete_client, QtGui.QDialogButtonBox.ActionRole)
        # --- refresh
        self.btn_refresh_list = QtGui.QPushButton("Refresh")
        self.btn_box.addButton(self.btn_refresh_list, QtGui.QDialogButtonBox.ActionRole)

        # - left and right sub-frames
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- left
        self.left_frame = QtGui.QFrame()
        self.left_layout = QtGui.QVBoxLayout()
        self.left_frame.setLayout(self.left_layout)
        hbox.addWidget(self.left_frame, stretch=1)
        # -- stretch
        hbox.addStretch()
        # -- right
        self.right_frame = QtGui.QFrame()
        self.right_layout = QtGui.QVBoxLayout()
        self.right_frame.setLayout(self.right_layout)
        hbox.addWidget(self.right_frame, stretch=1)

        # LEFT

        # - Editor settings
        hbox = QtGui.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        hbox.addStretch()
        self.label = QtGui.QLabel("Editor settings:")
        hbox.addWidget(self.label)
        hbox.addStretch()

        # - append_caris_file
        hbox = QtGui.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Append Caris file:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.append_caris_file = QtGui.QComboBox()
        self.append_caris_file.addItems(["True", "False"])
        vbox.addWidget(self.append_caris_file)
        vbox.addStretch()

        # - log_user
        hbox = QtGui.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("User logging:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.log_user = QtGui.QComboBox()
        self.log_user.addItems(["True", "False"])
        vbox.addWidget(self.log_user)
        vbox.addStretch()

        self.left_layout.addStretch()

        # RIGHT

        # - server
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        hbox.addStretch()
        self.label = QtGui.QLabel("Server settings:")
        hbox.addWidget(self.label)
        hbox.addStretch()

        # - server_source
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Source:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.server_source = QtGui.QComboBox()
        self.server_source.addItems(Dicts.server_sources.keys())
        vbox.addWidget(self.server_source)
        vbox.addStretch()

        # - server_apply_surface_sound_speed
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Surface sound speed:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.server_apply_surface_sound_speed = QtGui.QComboBox()
        self.server_apply_surface_sound_speed.addItems(["True", "False"])
        vbox.addWidget(self.server_apply_surface_sound_speed)
        vbox.addStretch()

        # - log_server
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Server logging:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.log_server = QtGui.QComboBox()
        self.log_server.addItems(["True", "False"])
        vbox.addWidget(self.log_server)
        vbox.addStretch()

        self.right_layout.addStretch()

        self.main_layout.addStretch()

        self.setup_changed()

        # noinspection PyUnresolvedReferences
        self.btn_new_client.clicked.connect(self.new_client)
        # noinspection PyUnresolvedReferences
        self.btn_delete_client.clicked.connect(self.delete_client)
        # noinspection PyUnresolvedReferences
        self.btn_refresh_list.clicked.connect(self.setup_changed)
        # noinspection PyUnresolvedReferences
        self.append_caris_file.currentIndexChanged.connect(self.apply_append_caris_file)
        # noinspection PyUnresolvedReferences
        self.log_user.currentIndexChanged.connect(self.apply_log_user)
        # noinspection PyUnresolvedReferences
        self.server_source.currentIndexChanged.connect(self.apply_server_source)
        # noinspection PyUnresolvedReferences
        self.server_apply_surface_sound_speed.currentIndexChanged.connect(self.apply_server_apply_surface_sound_speed)
        # noinspection PyUnresolvedReferences
        self.log_server.currentIndexChanged.connect(self.apply_log_server)

    def new_client(self):
        logger.debug("new setup")

        name = None
        ip = None
        port = None
        protocol = None

        # name
        while True:
            # noinspection PyCallByClass
            name, ok = QtGui.QInputDialog.getText(self, "New client", "Input a name for the new client")
            if not ok:
                return

            if self.db.client_exists(name):
                # noinspection PyCallByClass
                QtGui.QMessageBox.information(self, "Invalid client name",
                                              "The input client name already exists.\n"
                                              "You entered: %s" % name)
                continue
            break

        # ip
        while True:
            # noinspection PyCallByClass
            ip, ok = QtGui.QInputDialog.getText(self, "New client", "Input the IP (e.g., 127.0.0.1)")
            if not ok:
                return

            if not self._valid_ip(ip):
                # noinspection PyCallByClass
                QtGui.QMessageBox.information(self, "Invalid client IP",
                                              "The format input is not valid.\n"
                                              "You entered: %s" % ip)
                continue
            break

        # port
        while True:
            # noinspection PyCallByClass
            port, ok = QtGui.QInputDialog.getInteger(self, "New client", "Input the port (e.g., 4001)",
                                                     4001, 0, 65535)
            if not ok:
                return

            if (port < 0) or (port > 65535):
                # noinspection PyCallByClass
                QtGui.QMessageBox.information(self, "Invalid client port",
                                              "The port valus is outside validity range.\n"
                                              "You entered: %s" % port)
                continue
            break

        # protocol
        while True:
            # noinspection PyCallByClass
            protocol, ok = QtGui.QInputDialog.getText(self, "New client",
                                                      "Input the protocol (SIS, HYPACK, PDS2000, or QINSY)",
                                                      QtGui.QLineEdit.Normal,
                                                      "SIS")
            if not ok:
                return

            if protocol not in Dicts.clients:
                # noinspection PyCallByClass
                QtGui.QMessageBox.information(self, "Invalid client protocol",
                                              "You entered: %s" % protocol)
                continue
            break

        self.db.add_client(client_name=name, client_ip=ip, client_port=port, client_protocol=protocol)

        self.setup_changed()
        self.main_win.reload_settings()

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
            # noinspection PyCallByClass
            QtGui.QMessageBox.information(self, "Client deletion",
                                          "You need to first select the client to delete!")
            return

        client_name = sel[1].text()
        self.db.delete_client(client_name)
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_append_caris_file(self):
        # logger.debug("apply append caris file")
        self.db.append_caris_file = self.append_caris_file.currentText() == "True"
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_log_user(self):
        # logger.debug("apply log user")
        self.db.log_user = self.log_user.currentText() == "True"
        self.setup_changed()
        self.main_win.reload_settings()
        self.main_win.lib.logging()

    def apply_server_source(self):
        # logger.debug("apply server source")
        self.db.server_source = self.server_source.currentText()
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_server_apply_surface_sound_speed(self):
        # logger.debug("apply apply surface sound speed")
        self.db.server_apply_surface_sound_speed = self.server_apply_surface_sound_speed.currentText() == "True"
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_log_server(self):
        # logger.debug("apply log server")
        self.db.log_server = self.log_server.currentText() == "True"
        self.setup_changed()
        self.main_win.reload_settings()
        self.main_win.lib.logging()

    def setup_changed(self):
        """Refresh the setup list"""
        # logger.debug("refresh clients")

        # set the top label
        self.active_label.setText("<b>Current setup: %s [#%02d]</b>" % (self.db.setup_name, self.db.active_setup_id))

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

        # extension source
        _str = self.db.server_source
        _idx = Dicts.server_sources[_str]
        self.server_source.setCurrentIndex(_idx)

        # server_apply_surface_sound_speed
        if self.db.server_apply_surface_sound_speed:
            self.server_apply_surface_sound_speed.setCurrentIndex(0)  # True
        else:
            self.server_apply_surface_sound_speed.setCurrentIndex(1)  # False

        # log_server
        if self.db.log_server:
            self.log_server.setCurrentIndex(0)  # True
        else:
            self.log_server.setCurrentIndex(1)  # False

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

