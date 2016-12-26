from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

from PySide import QtGui

logger = logging.getLogger(__name__)

from hydroffice.soundspeedmanager.widgets.widget import AbstractWidget
from hydroffice.soundspeedmanager.widgets.dataplots import DataPlots


class Refraction(AbstractWidget):

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
        self.group_box = QtGui.QGroupBox("Refraction Monitor")
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
        img = QtGui.QImage(os.path.join(self.media, 'refraction.png'))
        if img.isNull():
            raise RuntimeError("unable to open server image")
        img_label.setPixmap(QtGui.QPixmap.fromImage(img))
        group_layout.addWidget(img_label)
        # - text
        info_label = QtGui.QLabel(
            "This experimental tool allows to evaluate the impact of applying a sound speed delta.\n\n"
            "The tools calculates the refraction corrections and plots the swath data based on\n"
            "the derived sound speed profile, then the user can decide to use the resulting profile."
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
        btn = QtGui.QPushButton("Enable monitor")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_enable_monitor)
        btn.setToolTip("Enable refraction monitor")
        hbox.addWidget(btn)
        # -- stop
        btn = QtGui.QPushButton("Disable monitor")
        # noinspection PyUnresolvedReferences
        btn.clicked.connect(self.on_disable_monitor)
        btn.setToolTip("Disable refraction monitor")
        hbox.addWidget(btn)
        hbox.addStretch()

        self.hidden = QtGui.QFrame()
        self.main_layout.addWidget(self.hidden)
        self.hidden.setVisible(True)

        self.setDisabled(True)

    def on_enable_monitor(self):
        logger.debug('enable monitor')
        msg = "Do you really want to enable the Refraction Monitor?\n\n"
        ret = QtGui.QMessageBox.warning(self, "Refraction Monitor", msg, QtGui.QMessageBox.Ok|QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.No:
            return

    def on_disable_monitor(self):
        logger.debug('disable monitor')
