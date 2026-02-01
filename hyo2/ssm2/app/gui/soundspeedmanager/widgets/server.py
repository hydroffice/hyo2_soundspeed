import os
import logging
import time
from typing import TYPE_CHECKING

from PySide6 import QtCore, QtGui, QtWidgets

from hyo2.abc2.app.freeze_debugger import FreezeDebugger
from hyo2.ssm2.app.gui.soundspeedmanager.widgets.widget import AbstractWidget
from hyo2.ssm2.app.gui.soundspeedmanager.widgets.dataplots import DataPlots

if TYPE_CHECKING:
    from hyo2.ssm2.app.gui.soundspeedmanager.mainwin import MainWin
    from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary

logger = logging.getLogger(__name__)


class Server(AbstractWidget):
    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win: 'MainWin', lib: 'SoundSpeedLibrary') -> None:
        AbstractWidget.__init__(self, main_win=main_win, lib=lib)

        # create the overall layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.frame.setLayout(self.main_layout)

        # info box
        hbox = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        hbox.addStretch()
        self.group_box = QtWidgets.QGroupBox("Synthetic Profile Server")
        self.group_box.setMaximumHeight(150)
        self.group_box.setFixedWidth(580)
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
        img_label.setPixmap(QtGui.QPixmap.fromImage(img))
        group_layout.addWidget(img_label)
        # - text
        info_label = QtWidgets.QLabel(
            "This tool delivers WOA/model-derived synthetic profiles to one or more network\n"
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
        self.start_btn = QtWidgets.QPushButton("Start server")
        self.start_btn.clicked.connect(self.on_start_server)
        self.start_btn.setToolTip("Start server mode")
        hbox.addWidget(self.start_btn)
        self.start_server_act = QtGui.QAction('Start Server', self)
        self.start_server_act.triggered.connect(self.on_start_server)
        self.main_win.server_menu.addAction(self.start_server_act)

        # -- force
        self.force_btn = QtWidgets.QPushButton("Send SSP now")
        self.force_btn.clicked.connect(self.on_force_server)
        self.force_btn.setToolTip("Force the transmission of a synthethic profile")
        hbox.addWidget(self.force_btn)
        self.force_server_act = QtGui.QAction('Force Transmission', self)
        self.force_server_act.triggered.connect(self.on_force_server)
        self.main_win.server_menu.addAction(self.force_server_act)

        # -- stop
        self.stop_btn = QtWidgets.QPushButton("Stop server")
        self.stop_btn.clicked.connect(self.on_stop_server)
        self.stop_btn.setToolTip("Stop server mode")
        hbox.addWidget(self.stop_btn)
        self.stop_server_act = QtGui.QAction('Stop Server', self)
        self.stop_server_act.triggered.connect(self.on_stop_server)
        self.main_win.server_menu.addAction(self.stop_server_act)

        hbox.addStretch()

        # - plots
        self.dataplots = DataPlots(main_win=self.main_win, lib=self.lib, server_mode=True)
        self.main_layout.addWidget(self.dataplots)
        self.hidden = QtWidgets.QFrame()
        self.main_layout.addWidget(self.hidden)

        self._deactivate_gui(also_main_win=False)

        self.freeze_dbg: FreezeDebugger | None = None
        self.activated_server = False
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_gui)
        timer.start(2000)

    def start_debugger(self) -> None:
        log_basename = os.path.join(self.lib.logs_folder, "synthetic_profile_server")
        self.freeze_dbg = FreezeDebugger(parent=self, log_basename=log_basename)

    def stop_debugger(self) -> None:
        if self.freeze_dbg:
            self.freeze_dbg.stop()

    def on_start_server(self):
        logger.debug('start server')

        self.progress.start(text="Checking server status... Please wait!")

        counter = 0
        while self.lib.server_is_alive():
            time.sleep(2)
            counter += 1
            self.progress.add(20)
            if counter == 4:
                break

        if self.lib.server_is_alive():
            msg = "The server mode is still stopping. Please try again in a few seconds!"
            QtWidgets.QMessageBox.warning(self, "Server mode", msg, QtWidgets.QMessageBox.StandardButton.Ok)
            self.progress.end()
            return

        self.progress.end()

        self.main_win.switch_to_server_tab()

        msg = "Do you really want to start the Server Mode?\n\n" \
              "The Server Mode creates sound speed profiles based on oceanographic models.\n" \
              "Thus, it is meant for use in transit, NOT for systematic seabed mapping.\n" \
              "This Mode will OVERWRITE the current SIS SSP.\n"
        ret = QtWidgets.QMessageBox.warning(
            self, "Server mode", msg,
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        if ret == QtWidgets.QMessageBox.StandardButton.No:
            return

        uni_clients = self.lib.server.list_uni_clients()
        use_uni_clients = False
        if len(uni_clients) > 0:
            msg = "The following clients do NOT provide acknowledgment of the received profiles:\n"
            for uni_client in uni_clients:
                msg += "- %s\n" % uni_client
            msg += "\nDo you still want to transmit the profiles to them?\n"
            ret = QtWidgets.QMessageBox.warning(
                self, "Server mode", msg,
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            if ret == QtWidgets.QMessageBox.StandardButton.Yes:
                use_uni_clients = True
            elif ret == QtWidgets.QMessageBox.StandardButton.No:
                use_uni_clients = False
            else:
                logger.debug("Cancelled by user.")
                return

        if not self.lib.server.check_settings(use_uni_clients=use_uni_clients):
            msg = "Unable to start the server mode!\n"
            for err in self.lib.server.settings_errors:
                msg += "Reason: %s\n" % err
            msg += "\nDouble-check the server settings and be sure that SIS is properly configured."
            QtWidgets.QMessageBox.critical(self, "Server mode", msg, QtWidgets.QMessageBox.StandardButton.Ok)
            return

        self.progress.start(text="Starting server... Please wait!")

        self.start_debugger()

        self.progress.add(quantum=20)

        self.lib.start_server()

        self.progress.add(quantum=40)

        self.activated_server = True
        self._activate_gui()

        self.progress.end()

    def on_force_server(self):
        logger.debug('force server')

        self.main_win.switch_to_server_tab()

        if not self.lib.server_is_alive():
            msg = "First start the server mode!"
            QtWidgets.QMessageBox.warning(self, "Server mode", msg, QtWidgets.QMessageBox.StandardButton.Ok)
            return

        self.progress.start(text="Sending profile... Please wait!", init_value=20)

        self.lib.force_server()

        self.progress.add(quantum=40)

        self.main_win.data_stored()

        self.progress.end()

    def on_stop_server(self):
        logger.debug('stop server')

        self.main_win.switch_to_server_tab()

        if not self.lib.server_is_alive():
            msg = "First start the server mode!"
            QtWidgets.QMessageBox.warning(self, "Server mode", msg, QtWidgets.QMessageBox.StandardButton.Ok)
            return

        self.progress.start(text="Stopping server... Please wait!")

        self.stop_debugger()

        self.progress.add(quantum=10)

        self.lib.stop_server()

        self.progress.add(quantum=20)

        wait_secs = 100
        quantum = 60 / wait_secs
        for i in range(wait_secs):
            if not self.lib.server_is_alive():
                break
            time.sleep(1)
            self.progress.add(quantum=quantum)

        self.activated_server = False
        self._deactivate_gui()

        self.progress.end()

    def update_gui(self):
        if self.activated_server and not self.lib.server_is_alive():
            self._deactivate_gui()
            self.activated_server = False
            msg = "Server Mode automatically stopped!\n"
            for err in self.lib.server.runtime_errors:
                msg += "Reason: %s\n" % err
            QtWidgets.QMessageBox.warning(self, "Server mode", msg, QtWidgets.QMessageBox.StandardButton.Ok)
            return

    def _activate_gui(self):
        self.dataplots.setVisible(True)
        self.hidden.setHidden(True)
        self.group_box.setHidden(True)

        self.start_btn.setDisabled(True)
        self.force_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)

        self.main_win.server_started()

    def _deactivate_gui(self, also_main_win=True):
        self.dataplots.setHidden(True)
        self.hidden.setVisible(True)
        self.group_box.setVisible(True)

        self.start_btn.setEnabled(True)
        self.force_btn.setDisabled(True)
        self.stop_btn.setDisabled(True)

        if also_main_win:
            self.main_win.data_stored()
            self.main_win.server_stopped()
