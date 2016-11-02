from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

from PySide import QtGui
from hydroffice.soundspeed.profile.dicts import Dicts

logger = logging.getLogger(__name__)

from .widget import AbstractWidget


class Input(AbstractWidget):

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

        # - atlases
        hbox = QtGui.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        hbox.addStretch()
        self.label = QtGui.QLabel("Atlases")
        hbox.addWidget(self.label)
        hbox.addStretch()

        # - use woa09
        hbox = QtGui.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Use WOA09:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.use_woa09 = QtGui.QComboBox()
        self.use_woa09.addItems(["True", "False"])
        vbox.addWidget(self.use_woa09)
        vbox.addStretch()

        # - use woa13
        hbox = QtGui.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Use WOA13:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.use_woa13 = QtGui.QComboBox()
        self.use_woa13.addItems(["True", "False"])
        vbox.addWidget(self.use_woa13)
        vbox.addStretch()

        # - use rtofs
        hbox = QtGui.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Use RTOFS:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.use_rtofs = QtGui.QComboBox()
        self.use_rtofs.addItems(["True", "False"])
        vbox.addWidget(self.use_rtofs)
        vbox.addStretch()

        # - ssp_extension_source
        hbox = QtGui.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Extend with:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.extension_source = QtGui.QComboBox()
        self.extension_source.addItems(Dicts.atlases.keys())
        vbox.addWidget(self.extension_source)
        vbox.addStretch()

        # - ssp_salinity_source
        hbox = QtGui.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Salinity from:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.salinity_source = QtGui.QComboBox()
        self.salinity_source.addItems(Dicts.atlases.keys())
        vbox.addWidget(self.salinity_source)
        vbox.addStretch()

        # - ssp_temp_sal_source
        hbox = QtGui.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Temp/sal from:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.temp_sal_source = QtGui.QComboBox()
        self.temp_sal_source.addItems(Dicts.atlases.keys())
        vbox.addWidget(self.temp_sal_source)
        vbox.addStretch()

        self.left_layout.addStretch()

        # RIGHT FRAME

        # - listeners
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        hbox.addStretch()
        self.label = QtGui.QLabel("Listeners")
        hbox.addWidget(self.label)
        hbox.addStretch()

        # - use sis
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Listen SIS:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.use_sis = QtGui.QComboBox()
        self.use_sis.addItems(["True", "False"])
        vbox.addWidget(self.use_sis)
        vbox.addStretch()

        # - use sippican
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Listen Sippican:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.use_sippican = QtGui.QComboBox()
        self.use_sippican.addItems(["True", "False"])
        vbox.addWidget(self.use_sippican)
        vbox.addStretch()

        # - use mvp
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Listen MVP:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.use_mvp = QtGui.QComboBox()
        self.use_mvp.addItems(["True", "False"])
        vbox.addWidget(self.use_mvp)
        vbox.addStretch()

        # - rx max waiting time
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("RX timeout:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.rx_max_wait_time = QtGui.QLineEdit()
        validator = QtGui.QIntValidator(0, 99999)
        self.rx_max_wait_time.setValidator(validator)
        vbox.addWidget(self.rx_max_wait_time)
        vbox.addStretch()

        self.right_layout.addSpacing(12)

        # - processing
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        hbox.addStretch()
        label = QtGui.QLabel("Other settings")
        hbox.addWidget(label)
        hbox.addStretch()

        # - profile direction
        hbox = QtGui.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtGui.QLabel("Profile direction:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtGui.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.profile_direction = QtGui.QComboBox()
        self.profile_direction.addItems(Dicts.ssp_directions.keys())
        vbox.addWidget(self.profile_direction)
        vbox.addStretch()

        self.right_layout.addStretch()

        self.main_layout.addStretch()

        self.setup_changed()  # to trigger the first data population

        # -- connect functions:
        # noinspection PyUnresolvedReferences
        self.use_woa09.currentIndexChanged.connect(self.apply_use_woa09)
        # noinspection PyUnresolvedReferences
        self.use_woa13.currentIndexChanged.connect(self.apply_use_woa13)
        # noinspection PyUnresolvedReferences
        self.use_rtofs.currentIndexChanged.connect(self.apply_use_rtofs)
        # noinspection PyUnresolvedReferences
        self.extension_source.currentIndexChanged.connect(self.apply_extension_source)
        # noinspection PyUnresolvedReferences
        self.salinity_source.currentIndexChanged.connect(self.apply_salinity_source)
        # noinspection PyUnresolvedReferences
        self.temp_sal_source.currentIndexChanged.connect(self.apply_temp_sal_source)
        # noinspection PyUnresolvedReferences
        self.use_sis.currentIndexChanged.connect(self.apply_use_sis)
        # noinspection PyUnresolvedReferences
        self.use_sippican.currentIndexChanged.connect(self.apply_use_sippican)
        # noinspection PyUnresolvedReferences
        self.use_mvp.currentIndexChanged.connect(self.apply_use_mvp)
        # noinspection PyUnresolvedReferences
        self.rx_max_wait_time.textChanged.connect(self.apply_rx_max_wait_time)
        # noinspection PyUnresolvedReferences
        self.profile_direction.currentIndexChanged.connect(self.apply_profile_direction)

    def apply_profile_direction(self):
        logger.debug("apply profile direction")
        self.db.ssp_up_or_down = self.profile_direction.currentText()
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_use_woa09(self):
        # logger.debug("apply use woa09: %s" % self.use_woa09.currentText())
        self.db.use_woa09 = self.use_woa09.currentText() == "True"
        self.setup_changed()
        self.main_win.reload_settings()

        if self.main_win.main_win:
            self.main_win.main_win.check_woa09()

    def apply_use_woa13(self):
        # logger.debug("apply use woa13: %s" % self.use_woa13.currentText())
        self.db.use_woa13 = self.use_woa13.currentText() == "True"
        self.setup_changed()
        self.main_win.reload_settings()

        if self.main_win.main_win:
            self.main_win.main_win.check_woa13()

    def apply_use_rtofs(self):
        # logger.debug("apply use rtofs: %s" % self.use_rtofs.currentText())
        self.db.use_rtofs = self.use_rtofs.currentText() == "True"
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_extension_source(self):
        # logger.debug("apply extension source")
        self.db.ssp_extension_source = self.extension_source.currentText()
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_salinity_source(self):
        # logger.debug("apply salinity source")
        self.db.ssp_salinity_source = self.salinity_source.currentText()
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_temp_sal_source(self):
        # logger.debug("apply temp/sal source")
        self.db.ssp_temp_sal_source = self.temp_sal_source.currentText()
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_use_sis(self):
        # logger.debug("apply use SIS")
        self.db.use_sis = self.use_sis.currentText() == "True"
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_use_sippican(self):
        # logger.debug("apply use Sippican")
        self.db.use_sippican = self.use_sippican.currentText() == "True"
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_use_mvp(self):
        # logger.debug("apply use MVP")
        self.db.use_mvp = self.use_mvp.currentText() == "True"
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_rx_max_wait_time(self):
        # logger.debug("apply rx timeout")
        self.db.rx_max_wait_time = int(self.rx_max_wait_time.text())
        self.setup_changed()
        self.main_win.reload_settings()

    def setup_changed(self):
        """Refresh items"""
        # logger.debug("refresh input settings")

        # set the top label
        self.active_label.setText("<b>Current setup: %s [#%02d]</b>" % (self.db.setup_name, self.db.active_setup_id))

        # use woa09
        if self.db.use_woa09:
            self.use_woa09.setCurrentIndex(0)  # True
        else:
            self.use_woa09.setCurrentIndex(1)  # False

        # use woa13
        if self.db.use_woa13:
            self.use_woa13.setCurrentIndex(0)  # True
        else:
            self.use_woa13.setCurrentIndex(1)  # False

        # use rtofs
        if self.db.use_rtofs:
            self.use_rtofs.setCurrentIndex(0)  # True
        else:
            self.use_rtofs.setCurrentIndex(1)  # False

        # extension source
        _str = self.db.ssp_extension_source
        _idx = Dicts.atlases[_str]
        self.extension_source.setCurrentIndex(_idx)

        # salinity source
        _str = self.db.ssp_salinity_source
        _idx = Dicts.atlases[_str]
        self.salinity_source.setCurrentIndex(_idx)

        # temperature/salinity source
        _str = self.db.ssp_temp_sal_source
        _idx = Dicts.atlases[_str]
        self.temp_sal_source.setCurrentIndex(_idx)

        # use sis
        if self.db.use_sis:
            self.use_sis.setCurrentIndex(0)  # True
        else:
            self.use_sis.setCurrentIndex(1)  # False

        # use sippican
        if self.db.use_sippican:
            self.use_sippican.setCurrentIndex(0)  # True
        else:
            self.use_sippican.setCurrentIndex(1)  # False

        # use mvp
        if self.db.use_mvp:
            self.use_mvp.setCurrentIndex(0)  # True
        else:
            self.use_mvp.setCurrentIndex(1)  # False

        # rx_max_wait_time
        self.rx_max_wait_time.setText("%d" % self.db.rx_max_wait_time)

        # profile direction
        _str = self.db.ssp_up_or_down
        _idx = Dicts.ssp_directions[_str]
        self.profile_direction.setCurrentIndex(_idx)
