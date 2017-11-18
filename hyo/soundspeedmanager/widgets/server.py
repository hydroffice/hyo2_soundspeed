import os
import logging

from PySide import QtGui

logger = logging.getLogger(__name__)

from hyo.soundspeedmanager.widgets.widget import AbstractWidget
from hyo.soundspeedmanager.widgets.dataplots import DataPlots


class Server(AbstractWidget):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win, lib):
        AbstractWidget.__init__(self, main_win=main_win, lib=lib)

        # create the overall layout
        self.main_layout = QtGui.QVBoxLayout()
        self.frame.setLayout(self.main_layout)

        # info box
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        hbox.addStretch()
        self.group_box = QtGui.QGroupBox("Synthetic Profile Server")
        self.group_box.setMaximumHeight(120)
        self.group_box.setFixedWidth(500)
        hbox.addWidget(self.group_box)
        hbox.addStretch()

        # image and text
        group_layout = QtGui.QHBoxLayout()
        self.group_box.setLayout(group_layout)
        group_layout.addStretch()
        # - image
        img_label = QtGui.QLabel()
        img = QtGui.QImage(os.path.join(self.media, 'server.png'))
        if img.isNull():
            raise RuntimeError("unable to open refraction image")
        img_label.setPixmap(QtGui.QPixmap.fromImage(img))
        group_layout.addWidget(img_label)
        # - text
        info_label = QtGui.QLabel(
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
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        hbox.addStretch()
        # -- start
        btn = QtGui.QPushButton("Start server")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_start_server)
        btn.setToolTip("Start server mode")
        hbox.addWidget(btn)
        self.start_server_act = QtGui.QAction('Start Server', self)
        self.start_server_act.setShortcut('Ctrl+Alt+S')
        # noinspection PyUnresolvedReferences
        self.start_server_act.triggered.connect(self.on_start_server)
        self.main_win.server_menu.addAction(self.start_server_act)

        # -- force
        btn = QtGui.QPushButton("Send now")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_force_server)
        btn.setToolTip("Force the transmission of a synthethic profile")
        hbox.addWidget(btn)
        self.force_server_act = QtGui.QAction('Force Transmission', self)
        self.force_server_act.setShortcut('Ctrl+Alt+T')
        # noinspection PyUnresolvedReferences
        self.force_server_act.triggered.connect(self.on_force_server)
        self.main_win.server_menu.addAction(self.force_server_act)

        # -- stop
        btn = QtGui.QPushButton("Stop server")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_stop_server)
        btn.setToolTip("Stop server mode")
        hbox.addWidget(btn)
        self.stop_server_act = QtGui.QAction('Stop Server', self)
        self.stop_server_act.setShortcut('Ctrl+Alt+E')
        # noinspection PyUnresolvedReferences
        self.stop_server_act.triggered.connect(self.on_stop_server)
        self.main_win.server_menu.addAction(self.stop_server_act)

        hbox.addStretch()

        # - plots
        self.dataplots = DataPlots(main_win=self.main_win, lib=self.lib, server_mode=True)
        self.main_layout.addWidget(self.dataplots)
        self.dataplots.setHidden(True)
        self.hidden = QtGui.QFrame()
        self.main_layout.addWidget(self.hidden)
        self.hidden.setVisible(True)

    def on_start_server(self):
        logger.debug('start server')

        self.main_win.switch_to_server_tab()

        msg = "Do you really want to start the Server Mode?\n\n" \
              "The Server Mode creates sound speed profiles based on oceanographic models.\n" \
              "Thus, it is meant for use in transit, NOT for systematic seabed mapping.\n" \
              "This Mode will OVERWRITE the current SIS SSP.\n"
        ret = QtGui.QMessageBox.warning(self, "Server mode", msg, QtGui.QMessageBox.Ok|QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.No:
            return

        if not self.lib.server.check_settings():
            msg = "Unable to start the server mode.\n\n" \
                  "Double-check the server settings and be sure that SIS is properly configured."
            QtGui.QMessageBox.critical(self, "Server mode", msg, QtGui.QMessageBox.Ok)
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
            QtGui.QMessageBox.warning(self, "Server mode", msg, QtGui.QMessageBox.Ok)
            return

        self.lib.force_server()

    def on_stop_server(self):
        logger.debug('stop server')

        self.main_win.switch_to_server_tab()

        self.lib.stop_server()

        self.dataplots.setHidden(True)
        self.hidden.setVisible(True)
        self.group_box.setVisible(True)
        self.main_win.server_stopped()
