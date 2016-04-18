from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

from PySide import QtGui

logger = logging.getLogger(__name__)

from .widget import AbstractWidget
from .dataplots import DataPlots


class Server(AbstractWidget):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win, prj):
        AbstractWidget.__init__(self, main_win=main_win, prj=prj)

        self.is_drawn = False

        # create the overall layout
        self.main_layout = QtGui.QVBoxLayout()
        self.frame.setLayout(self.main_layout)

        # - buttons
        hbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        hbox.addStretch()
        # -- start
        btn = QtGui.QPushButton("Start server")
        btn.clicked.connect(self.on_start_server)
        btn.setToolTip("Start server mode")
        hbox.addWidget(btn)
        # -- stop
        btn = QtGui.QPushButton("Stop server")
        btn.clicked.connect(self.on_stop_server)
        btn.setToolTip("Stop server mode")
        hbox.addWidget(btn)
        hbox.addStretch()

        # - plots
        self.dataplots = DataPlots(main_win=self.main_win, prj=self.prj, server_mode=True)
        self.main_layout.addWidget(self.dataplots)
        self.dataplots.setHidden(True)
        self.hidden = QtGui.QFrame()
        self.main_layout.addWidget(self.hidden)
        self.hidden.setVisible(True)

    def on_start_server(self):
        logger.debug('start server')
        msg = "Do you really want to start the Server Mode?\n\n" \
              "The Server Mode creates sound speed profiles based on oceanographic models.\n" \
              "Thus, it is meant for use in transit, NOT for systematic seabed mapping.\n" \
              "This Mode will OVERWRITE the current SIS SSP.\n"
        ret = QtGui.QMessageBox.warning(self, "Server mode", msg, QtGui.QMessageBox.Ok|QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.No:
            return

        if not self.prj.server.check_settings():
            msg = "Unable to start the server mode.\n\n" \
                  "Double-check the server settings and be sure that SIS is properly configured."
            QtGui.QMessageBox.critical(self, "Server mode", msg, QtGui.QMessageBox.Ok)
            return

        self.prj.start_server()

        self.dataplots.setVisible(True)
        self.hidden.setHidden(True)
        self.main_win.server_started()

    def on_stop_server(self):
        logger.debug('stop server')

        self.prj.stop_server()

        self.dataplots.setHidden(True)
        self.hidden.setVisible(True)
        self.main_win.server_stopped()
