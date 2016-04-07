from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

from PySide import QtGui

logger = logging.getLogger(__name__)

from .widget import AbstractWidget


class Basic(AbstractWidget):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, main_win, db):
        AbstractWidget.__init__(self, main_win=main_win, db=db)

        lbl_width = 60

        # outline ui
        self.mainLayout = QtGui.QVBoxLayout()
        self.frame.setLayout(self.mainLayout)

        # types
        hbox = QtGui.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtGui.QLabel("Data type:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.sensor_type = QtGui.QLineEdit()
        # self.sensor_type.setDisabled(True)
        # self.sensor_type.setText(self.prj.cur.meta.sensor)
        hbox.addWidget(self.sensor_type)
        self.probe_type = QtGui.QLineEdit()
        # self.probe_type.setDisabled(True)
        # self.probe_type.setText(self.prj.cur.meta.probe)
        hbox.addWidget(self.probe_type)