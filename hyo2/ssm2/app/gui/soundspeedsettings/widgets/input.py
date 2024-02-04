import logging

from PySide6 import QtGui, QtWidgets

from hyo2.ssm2.lib.profile.dicts import Dicts
from hyo2.ssm2.app.gui.soundspeedsettings.widgets.widget import AbstractWidget

logger = logging.getLogger(__name__)


class Input(AbstractWidget):

    def __init__(self, main_win, db):
        AbstractWidget.__init__(self, main_win=main_win, db=db)

        lbl_width = 120

        # outline ui
        self.main_layout = QtWidgets.QVBoxLayout()
        self.frame.setLayout(self.main_layout)

        # - active setup
        hbox = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        hbox.addStretch()
        self.active_label = QtWidgets.QLabel()
        hbox.addWidget(self.active_label)
        hbox.addStretch()

        # - left and right sub-frames
        hbox = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        # -- left
        self.left_frame = QtWidgets.QFrame()
        self.left_layout = QtWidgets.QVBoxLayout()
        self.left_frame.setLayout(self.left_layout)
        hbox.addWidget(self.left_frame, stretch=1)
        # -- stretch
        hbox.addStretch()
        # -- right
        self.right_frame = QtWidgets.QFrame()
        self.right_layout = QtWidgets.QVBoxLayout()
        self.right_frame.setLayout(self.right_layout)
        hbox.addWidget(self.right_frame, stretch=1)

        # LEFT

        # - atlases
        hbox = QtWidgets.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        hbox.addStretch()
        self.label = QtWidgets.QLabel("Atlases")
        hbox.addWidget(self.label)
        hbox.addStretch()

        # - use woa09
        hbox = QtWidgets.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtWidgets.QLabel("Use WOA09:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.use_woa09 = QtWidgets.QComboBox()
        self.use_woa09.addItems(["True", "False"])
        vbox.addWidget(self.use_woa09)
        vbox.addStretch()

        # - use woa13
        hbox = QtWidgets.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtWidgets.QLabel("Use WOA13:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.use_woa13 = QtWidgets.QComboBox()
        self.use_woa13.addItems(["True", "False"])
        vbox.addWidget(self.use_woa13)
        vbox.addStretch()

        # - use woa18
        hbox = QtWidgets.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtWidgets.QLabel("Use WOA18:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.use_woa18 = QtWidgets.QComboBox()
        self.use_woa18.addItems(["True", "False"])
        vbox.addWidget(self.use_woa18)
        vbox.addStretch()

        # - use rtofs
        hbox = QtWidgets.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtWidgets.QLabel("Use RTOFS:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.use_rtofs = QtWidgets.QComboBox()
        self.use_rtofs.addItems(["True", "False"])
        vbox.addWidget(self.use_rtofs)
        vbox.addStretch()

        # - use gomofs
        hbox = QtWidgets.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtWidgets.QLabel("Use GoMOFS:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.use_gomofs = QtWidgets.QComboBox()
        self.use_gomofs.addItems(["True", "False"])
        vbox.addWidget(self.use_gomofs)
        vbox.addStretch()

        # - ssp_extension_source
        hbox = QtWidgets.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtWidgets.QLabel("Extend with:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.extension_source = QtWidgets.QComboBox()
        self.extension_source.addItems([k for k in Dicts.atlases.keys()])
        vbox.addWidget(self.extension_source)
        vbox.addStretch()

        # - ssp_salinity_source
        hbox = QtWidgets.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtWidgets.QLabel("Salinity from:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.salinity_source = QtWidgets.QComboBox()
        self.salinity_source.addItems([k for k in Dicts.atlases.keys()])
        vbox.addWidget(self.salinity_source)
        vbox.addStretch()

        # - ssp_temp_sal_source
        hbox = QtWidgets.QHBoxLayout()
        self.left_layout.addLayout(hbox)
        # -- label
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtWidgets.QLabel("Temp/sal from:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.temp_sal_source = QtWidgets.QComboBox()
        self.temp_sal_source.addItems([k for k in Dicts.atlases.keys()])
        vbox.addWidget(self.temp_sal_source)
        vbox.addStretch()

        self.left_layout.addStretch()

        # RIGHT FRAME

        # - listeners
        hbox = QtWidgets.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        hbox.addStretch()
        self.label = QtWidgets.QLabel("Listeners(*)")
        hbox.addWidget(self.label)
        hbox.addStretch()

        # - use sis4
        hbox = QtWidgets.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtWidgets.QLabel("Listen SIS4:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.use_sis4 = QtWidgets.QComboBox()
        self.use_sis4.addItems(["True", "False"])
        vbox.addWidget(self.use_sis4)
        vbox.addStretch()

        # - use sis5
        hbox = QtWidgets.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtWidgets.QLabel("Listen SIS5:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.use_sis5 = QtWidgets.QComboBox()
        self.use_sis5.addItems(["True", "False"])
        vbox.addWidget(self.use_sis5)
        vbox.addStretch()

        # - use nmea
        hbox = QtWidgets.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtWidgets.QLabel("Listen NMEA 0183:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.use_nmea_0183 = QtWidgets.QComboBox()
        self.use_nmea_0183.addItems(["True", "False"])
        vbox.addWidget(self.use_nmea_0183)
        vbox.addStretch()

        # - use sippican
        hbox = QtWidgets.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtWidgets.QLabel("Listen Sippican:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.use_sippican = QtWidgets.QComboBox()
        self.use_sippican.addItems(["True", "False"])
        vbox.addWidget(self.use_sippican)
        vbox.addStretch()

        # - use mvp
        hbox = QtWidgets.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtWidgets.QLabel("Listen MVP:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.use_mvp = QtWidgets.QComboBox()
        self.use_mvp.addItems(["True", "False"])
        vbox.addWidget(self.use_mvp)
        vbox.addStretch()

        # - rx max waiting time
        hbox = QtWidgets.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtWidgets.QLabel("RX timeout:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- value
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.rx_max_wait_time = QtWidgets.QLineEdit()
        validator = QtGui.QIntValidator(0, 99999)
        self.rx_max_wait_time.setValidator(validator)
        vbox.addWidget(self.rx_max_wait_time)
        vbox.addStretch()

        self.right_layout.addSpacing(12)

        # - processing
        hbox = QtWidgets.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        hbox.addStretch()
        label = QtWidgets.QLabel("Other settings")
        hbox.addWidget(label)
        hbox.addStretch()

        # - profile direction
        hbox = QtWidgets.QHBoxLayout()
        self.right_layout.addLayout(hbox)
        # -- label
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        label = QtWidgets.QLabel("Profile direction:")
        label.setFixedWidth(lbl_width)
        vbox.addWidget(label)
        vbox.addStretch()
        # -- label
        vbox = QtWidgets.QVBoxLayout()
        hbox.addLayout(vbox)
        vbox.addStretch()
        self.profile_direction = QtWidgets.QComboBox()
        self.profile_direction.addItems([k for k in Dicts.ssp_directions.keys()])
        vbox.addWidget(self.profile_direction)
        vbox.addStretch()

        self.right_layout.addStretch()

        # - active setup
        hbox = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(hbox)
        hbox.addStretch()
        label = QtWidgets.QLabel("<i>* Restart the application to apply any change to the listeners.</i>")
        label.setFixedHeight(22)
        label.setStyleSheet("QLabel { color : #FF6347; }")
        hbox.addWidget(label)
        hbox.addStretch()

        self.main_layout.addStretch()

        self.setup_changed()  # to trigger the first data population

        # -- connect functions:
        # noinspection PyUnresolvedReferences
        self.use_woa09.currentIndexChanged.connect(self.apply_use_woa09)
        # noinspection PyUnresolvedReferences
        self.use_woa13.currentIndexChanged.connect(self.apply_use_woa13)
        # noinspection PyUnresolvedReferences
        self.use_woa18.currentIndexChanged.connect(self.apply_use_woa18)
        # noinspection PyUnresolvedReferences
        self.use_rtofs.currentIndexChanged.connect(self.apply_use_rtofs)
        # noinspection PyUnresolvedReferences
        self.use_gomofs.currentIndexChanged.connect(self.apply_use_gomofs)
        # noinspection PyUnresolvedReferences
        self.extension_source.currentIndexChanged.connect(self.apply_extension_source)
        # noinspection PyUnresolvedReferences
        self.salinity_source.currentIndexChanged.connect(self.apply_salinity_source)
        # noinspection PyUnresolvedReferences
        self.temp_sal_source.currentIndexChanged.connect(self.apply_temp_sal_source)
        # noinspection PyUnresolvedReferences
        self.use_sis4.currentIndexChanged.connect(self.apply_use_sis)
        # noinspection PyUnresolvedReferences
        self.use_sis5.currentIndexChanged.connect(self.apply_use_sis)
        # noinspection PyUnresolvedReferences
        self.use_nmea_0183.currentIndexChanged.connect(self.apply_use_sis)
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

    def apply_use_woa18(self):
        # logger.debug("apply use woa18: %s" % self.use_woa18.currentText())
        self.db.use_woa18 = self.use_woa18.currentText() == "True"
        self.setup_changed()
        self.main_win.reload_settings()

        if self.main_win.main_win:
            self.main_win.main_win.check_woa18()

    def apply_use_rtofs(self):
        # logger.debug("apply use rtofs: %s" % self.use_rtofs.currentText())
        self.db.use_rtofs = self.use_rtofs.currentText() == "True"
        self.setup_changed()
        self.main_win.reload_settings()

    def apply_use_gomofs(self):
        # logger.debug("apply use gomofs: %s" % self.use_gomofs.currentText())
        self.db.use_gomofs = self.use_gomofs.currentText() == "True"
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
        # logger.debug("apply use SIS: %s" % self.sender())

        if self.sender() is self.use_sis4:
            use_value = self.use_sis4.currentText() == "True"
            self.db.use_sis4 = use_value
            if use_value:
                self.use_sis5.setCurrentText("False")
                self.use_nmea_0183.setCurrentText("False")
        elif self.sender() is self.use_sis5:
            use_value = self.use_sis5.currentText() == "True"
            self.db.use_sis5 = use_value
            if use_value:
                self.use_sis4.setCurrentText("False")
                self.use_nmea_0183.setCurrentText("False")
        elif self.sender() is self.use_nmea_0183:
            use_value = self.use_nmea_0183.currentText() == "True"
            self.db.use_nmea_0183 = use_value
            if use_value:
                self.use_sis4.setCurrentText("False")
                self.use_sis5.setCurrentText("False")

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

        # use woa18
        if self.db.use_woa18:
            self.use_woa18.setCurrentIndex(0)  # True
        else:
            self.use_woa18.setCurrentIndex(1)  # False

        # use rtofs
        if self.db.use_rtofs:
            self.use_rtofs.setCurrentIndex(0)  # True
        else:
            self.use_rtofs.setCurrentIndex(1)  # False

        # use gomofs
        if self.db.use_gomofs:
            self.use_gomofs.setCurrentIndex(0)  # True
        else:
            self.use_gomofs.setCurrentIndex(1)  # False

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

        # use sis4
        if self.db.use_sis4:
            self.use_sis4.setCurrentIndex(0)  # True
        else:
            self.use_sis4.setCurrentIndex(1)  # False

        # use sis5
        if self.db.use_sis5:
            self.use_sis5.setCurrentIndex(0)  # True
        else:
            self.use_sis5.setCurrentIndex(1)  # False

        # use sippican
        if self.db.use_sippican:
            self.use_sippican.setCurrentIndex(0)  # True
        else:
            self.use_sippican.setCurrentIndex(1)  # False

        # use nmea
        if self.db.use_nmea_0183:
            self.use_nmea_0183.setCurrentIndex(0)  # True
        else:
            self.use_nmea_0183.setCurrentIndex(1)  # False

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
