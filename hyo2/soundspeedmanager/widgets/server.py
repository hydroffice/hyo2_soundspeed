import os
import logging

from PySide2 import QtGui, QtWidgets

from hyo2.soundspeedmanager.widgets.widget import AbstractWidget
from hyo2.soundspeedmanager.widgets.dataplots import DataPlots

logger = logging.getLogger(__name__)


class Server(AbstractWidget):
    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win, lib):
        AbstractWidget.__init__(self, main_win=main_win, lib=lib)

        # create the overall layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.frame.setLayout(self.main_layout)

        # info box
        hbox = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        hbox.addStretch()
        self.group_box = QtWidgets.QGroupBox("Synthetic Profile Server")
        self.group_box.setMaximumHeight(120)
        self.group_box.setFixedWidth(500)
        hbox.addWidget(self.group_box)
        hbox.addStretch()

        # image and text
        group_layout = QtWidgets.QHBoxLayout()
        self.group_box.setLayout(group_layout)
        group_layout.addStretch()
        # - image
        img_label = QtWidgets.QLabel()
        img = QtGui.QImage(os.path.join(self.media, 'server.png'))
        if img.isNull():
            raise RuntimeError("unable to open server image")
        # noinspection PyCallByClass
        img_label.setPixmap(QtGui.QPixmap.fromImage(img))
        group_layout.addWidget(img_label)
        # - text
        info_label = QtWidgets.QLabel(
            "This tool delivers WOA/RTOFS-derived synthetic profiles to one or more network\n"
            "clients in a continuous manner, enabling opportunistic mapping while underway.\n\n"
            "Given the uncertainty of such an approach, this mode is expected to ONLY be used\n"
            "in transit, capturing the position from SIS to lookup into the oceanographic atlas."
        )
        info_label.setStyleSheet("color: #96A8A8;")
        info_label.setWordWrap(True)
        group_layout.addWidget(info_label)
        group_layout.addStretch()

        # - buttons
        hbox = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        hbox.addStretch()
        # -- start
        btn = QtWidgets.QPushButton("Start server")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_start_server)
        btn.setToolTip("Start server mode")
        hbox.addWidget(btn)
        self.start_server_act = QtWidgets.QAction('Start Server', self)
        # self.start_server_act.setShortcut('Ctrl+Alt+S')
        # noinspection PyUnresolvedReferences
        self.start_server_act.triggered.connect(self.on_start_server)
        self.main_win.server_menu.addAction(self.start_server_act)

        # -- force
        btn = QtWidgets.QPushButton("Send now")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_force_server)
        btn.setToolTip("Force the transmission of a synthethic profile")
        hbox.addWidget(btn)
        self.force_server_act = QtWidgets.QAction('Force Transmission', self)
        # self.force_server_act.setShortcut('Ctrl+Alt+T')
        # noinspection PyUnresolvedReferences
        self.force_server_act.triggered.connect(self.on_force_server)
        self.main_win.server_menu.addAction(self.force_server_act)

        # -- refresh
        btn = QtWidgets.QPushButton("Refresh DB")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_refresh_db)
        btn.setToolTip("Refresh the database tab")
        hbox.addWidget(btn)
        self.refresh_db_act = QtWidgets.QAction('Refresh Database', self)
        # noinspection PyUnresolvedReferences
        self.refresh_db_act.triggered.connect(self.on_refresh_db)
        self.main_win.server_menu.addAction(self.refresh_db_act)

        # -- stop
        btn = QtWidgets.QPushButton("Stop server")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_stop_server)
        btn.setToolTip("Stop server mode")
        hbox.addWidget(btn)
        self.stop_server_act = QtWidgets.QAction('Stop Server', self)
        # self.stop_server_act.setShortcut('Ctrl+Alt+E')
        # noinspection PyUnresolvedReferences
        self.stop_server_act.triggered.connect(self.on_stop_server)
        self.main_win.server_menu.addAction(self.stop_server_act)

        hbox.addStretch()

        # - plots
        self.dataplots = DataPlots(main_win=self.main_win, lib=self.lib, server_mode=True)
        self.main_layout.addWidget(self.dataplots)
        self.dataplots.setHidden(True)
        self.hidden = QtWidgets.QFrame()
        self.main_layout.addWidget(self.hidden)
        self.hidden.setVisible(True)

    def on_start_server(self):
        logger.debug('start server')

        self.main_win.switch_to_server_tab()

        msg = "Do you really want to start the Server Mode?\n\n" \
              "The Server Mode creates sound speed profiles based on oceanographic models.\n" \
              "Thus, it is meant for use in transit, NOT for systematic seabed mapping.\n" \
              "This Mode will OVERWRITE the current SIS SSP.\n"
        # noinspection PyCallByClass
        ret = QtWidgets.QMessageBox.warning(self, "Server mode", msg,
                                            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.No)
        if ret == QtWidgets.QMessageBox.No:
            return

        if not self.lib.server.check_settings():
            msg = "Unable to start the server mode.\n\n" \
                  "Double-check the server settings and be sure that SIS is properly configured."
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.critical(self, "Server mode", msg, QtWidgets.QMessageBox.Ok)
            return

        self.lib.start_server()

        self.dataplots.setVisible(True)
        self.hidden.setHidden(True)
        self.group_box.setHidden(True)
        self.main_win.server_started()

    def on_force_server(self):
        logger.debug('force server')

        self.main_win.switch_to_server_tab()

        if not self.lib.server_is_alive():
            msg = "First start the server mode!"
            # noinspection PyCallByClass
            QtWidgets.QMessageBox.warning(self, "Server mode", msg, QtWidgets.QMessageBox.Ok)
            return

        self.lib.force_server()
        self.main_win.data_stored()

    def on_refresh_db(self):
        logger.debug('refresh db')
        self.main_win.data_stored()
        self.main_win.switch_to_database_tab()

    def on_stop_server(self):
        logger.debug('stop server')

        self.main_win.switch_to_server_tab()

        self.lib.stop_server()

        self.dataplots.setHidden(True)
        self.hidden.setVisible(True)
        self.group_box.setVisible(True)
        self.main_win.server_stopped()
        self.main_win.data_stored()
