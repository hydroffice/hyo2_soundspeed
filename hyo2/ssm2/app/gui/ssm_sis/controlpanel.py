import logging
import os

from PySide6 import QtCore, QtGui, QtWidgets

from hyo2.abc2.lib.helper import Helper
from hyo2.ssm2.app.gui.ssm_sis import app_info
from hyo2.ssm2.lib.listener.sis.sis import Sis
from hyo2.ssm2.lib.profile.profilelist import ProfileList


logger = logging.getLogger(__name__)


class ControlPanel(QtWidgets.QWidget):
    here = os.path.abspath(os.path.dirname(__file__)).replace("\\", "/")

    def __init__(self):
        super(ControlPanel, self).__init__()
        self.sis = None  # Type: Optional[Sis]

        self.vbox = QtWidgets.QVBoxLayout()
        self.setLayout(self.vbox)

        self.sis_settings = QtWidgets.QGroupBox("settings")
        self.sis_settings.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.vbox.addWidget(self.sis_settings)
        self.sis_4 = None
        self.sis_5 = None
        self.set_input_port = None
        self.set_output_ip = None
        self.set_output_port = None
        self._make_sis_settings()

        self.vbox.addStretch()

        self.sis_commands = QtWidgets.QGroupBox("commands")
        self.sis_commands.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.vbox.addWidget(self.sis_commands)
        self.button_start = None
        self.button_stop = None
        self._make_sis_commands()

        # info viewer
        self.viewer = QtWidgets.QTextBrowser()
        self.viewer.resize(QtCore.QSize(280, 40))
        self.viewer.setTextColor(QtGui.QColor("#4682b4"))
        self.viewer.ensureCursorVisible()
        # create a monospace font
        font = QtGui.QFont("Courier New")
        font.setStyleHint(QtGui.QFont.TypeWriter)
        font.setFixedPitch(True)
        font.setPointSize(9)
        self.viewer.document().setDefaultFont(font)
        # set the tab size
        metrics = QtGui.QFontMetrics(font)
        # noinspection PyArgumentList
        self.viewer.setTabStopDistance(3 * metrics.horizontalAdvance(' '))
        self.viewer.setReadOnly(True)
        self.vbox.addWidget(self.viewer)

        self.vbox.addSpacing(12)
        hbox = QtWidgets.QHBoxLayout()
        self.vbox.addLayout(hbox)
        hbox.addStretch()

        button = QtWidgets.QPushButton()
        hbox.addWidget(button)
        button.setFixedHeight(28)
        button.setFixedWidth(28)
        icon_info = QtCore.QFileInfo(os.path.join(app_info.app_media_path, 'small_info.png'))
        button.setIcon(QtGui.QIcon(icon_info.absoluteFilePath()))
        button.setToolTip('Open the manual page')
        button.setStyleSheet("QPushButton { background-color: rgba(255, 255, 255, 0); }\n"
                             "QPushButton:hover { background-color: rgba(230, 230, 230, 100); }\n")
        # noinspection PyUnresolvedReferences
        button.clicked.connect(self.click_open_manual)

        comments = QtWidgets.QLabel("<i>Comments and suggestions:</i> "
                                    "<a href='mailto:gmasetti@ccom.unh.edu'>gmasetti@ccom.unh.edu</a>")
        comments.setOpenExternalLinks(True)
        hbox.addWidget(comments)

        hbox.addStretch()

        self.set_sis_4()
        self.enable_commands(True)

        timer = QtCore.QTimer(self)
        # noinspection PyUnresolvedReferences
        timer.timeout.connect(self.update_gui)
        # noinspection PyArgumentList
        timer.start(1500)

    def _make_sis_settings(self):
        """build "settings" groupbox"""

        # default SIS values
        self.default_sis_input_port = "16103"
        self.default_sis_output_ip = "127.0.0.1"
        self.default_sis4_output_port = "4001"
        self.default_sis5_output_port = "14002"

        vbox = QtWidgets.QVBoxLayout()
        self.sis_settings.setLayout(vbox)

        # default values
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        text_input_port = QtWidgets.QLabel("SIS Version:")
        hbox.addWidget(text_input_port)
        text_input_port.setMinimumWidth(80)
        self.sis_4 = QtWidgets.QRadioButton()
        hbox.addWidget(self.sis_4)
        self.sis_4.setText("SIS4")
        self.sis_4.setToolTip('Settings for SIS 4')
        self.sis_4.setChecked(True)
        # noinspection PyUnresolvedReferences
        self.sis_4.clicked.connect(self.set_sis_4)
        self.sis_5 = QtWidgets.QRadioButton()
        hbox.addWidget(self.sis_5)
        self.sis_5.setText("SIS5")
        self.sis_5.setToolTip('Settings for SIS 5')
        # noinspection PyUnresolvedReferences
        self.sis_5.clicked.connect(self.set_sis_5)
        hbox.addStretch()

        # input port
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        text_input_port = QtWidgets.QLabel("Input port:")
        hbox.addWidget(text_input_port)
        text_input_port.setMinimumWidth(80)
        self.set_input_port = QtWidgets.QLineEdit("")
        hbox.addWidget(self.set_input_port)
        validator = QtGui.QIntValidator(0, 65535)
        self.set_input_port.setValidator(validator)

        # output ip
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        text_output_ip = QtWidgets.QLabel("Output IP:")
        hbox.addWidget(text_output_ip)
        text_output_ip.setMinimumWidth(80)
        self.set_output_ip = QtWidgets.QLineEdit("")
        hbox.addWidget(self.set_output_ip)
        octet = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        rex = QtCore.QRegularExpression(r"^%s\.%s\.%s\.%s$" % (octet, octet, octet, octet))
        if not rex.isValid():
            logger.warning(rex.errorString())
        validator = QtGui.QRegularExpressionValidator(rex)
        self.set_output_ip.setValidator(validator)

        # output port
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        text_output_port = QtWidgets.QLabel("Output port:")
        hbox.addWidget(text_output_port)
        text_output_port.setMinimumWidth(80)
        self.set_output_port = QtWidgets.QLineEdit("")
        hbox.addWidget(self.set_output_port)
        validator = QtGui.QIntValidator(0, 65535)
        self.set_output_port.setValidator(validator)

        # verbose
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        text_verbose = QtWidgets.QLabel("Verbose:")
        hbox.addWidget(text_verbose)
        text_verbose.setMinimumWidth(80)
        self.set_verbose = QtWidgets.QCheckBox()
        self.set_verbose.setChecked(True)
        hbox.addWidget(self.set_verbose)
        hbox.addStretch()

    def set_sis_4(self):
        self.set_input_port.setText(self.default_sis_input_port)
        self.set_output_ip.setText(self.default_sis_output_ip)
        self.set_output_port.setText(self.default_sis4_output_port)

    def set_sis_5(self):
        self.set_input_port.setText(self.default_sis_input_port)
        self.set_output_ip.setText(self.default_sis_output_ip)
        self.set_output_port.setText(self.default_sis5_output_port)

    def enable_commands(self, enable: bool):
        self.sis_4.setEnabled(enable)
        self.sis_5.setEnabled(enable)
        self.set_input_port.setEnabled(enable)
        self.set_output_ip.setEnabled(enable)
        self.set_output_port.setEnabled(enable)
        self.set_verbose.setEnabled(enable)
        self.button_start.setEnabled(enable)
        self.button_request.setDisabled(enable)
        self.button_send.setDisabled(enable)
        self.button_stop.setDisabled(enable)

    def _make_sis_commands(self):
        """build "commands" groupbox"""

        vbox = QtWidgets.QVBoxLayout()
        self.sis_commands.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()

        self.button_start = QtWidgets.QPushButton()
        hbox.addWidget(self.button_start)
        self.button_start.setText("Start")
        self.button_start.setToolTip('Start listening using defined settings')
        # noinspection PyUnresolvedReferences
        self.button_start.clicked.connect(self.start_listening)

        self.button_request = QtWidgets.QPushButton()
        hbox.addWidget(self.button_request)
        self.button_request.setText("Require SSP")
        self.button_request.setToolTip('Require the current SSP')
        # noinspection PyUnresolvedReferences
        self.button_request.clicked.connect(self.request_svp)

        self.button_send = QtWidgets.QPushButton()
        hbox.addWidget(self.button_send)
        self.button_send.setText("Send SSP")
        self.button_send.setToolTip('Send a simple SSP')
        # noinspection PyUnresolvedReferences
        self.button_send.clicked.connect(self.send_svp)

        self.button_stop = QtWidgets.QPushButton()
        hbox.addWidget(self.button_stop)
        self.button_stop.setText("Stop")
        self.button_stop.setToolTip('Stop listening')
        # noinspection PyUnresolvedReferences
        self.button_stop.clicked.connect(self.stop_listening)

        hbox.addStretch()

    def start_listening(self):
        logger.info("Start listening ...")
        self.enable_commands(False)
        self.sis = Sis(port=int(self.set_input_port.text()), timeout=10,
                       use_sis5=self.sis_5.isChecked(), debug=self.set_verbose.isChecked())
        self.sis.start()
        logger.info("Start listening ... DONE!")

    def stop_listening(self):
        if self.sis is None:
            return
        logger.info("Stop listening ...")
        self.sis.stop()
        self.sis.join()
        self.sis = None
        self.enable_commands(True)
        logger.info("Stop listening ... DONE!")

    def request_svp(self):
        if self.sis is None:
            return
        logger.info("Requiring SVP ...")
        self.button_request.setEnabled(False)
        self.sis.request_cur_profile(ip=self.set_output_ip.text(),
                                     port=int(self.set_output_port.text()))
        self.button_request.setEnabled(True)
        logger.info("Requiring SVP ... DONE")

    def send_svp(self):
        if self.sis is None:
            return
        logger.info("Sending SVP ...")
        self.button_send.setEnabled(False)
        self.sis.send_profile(
            ssp=ProfileList.constant_gradient(thinned=True),
            ip=self.set_output_ip.text(),
            port=int(self.set_output_port.text()))
        self.button_send.setEnabled(True)
        logger.info("Sending SVP ... DONE")

    @classmethod
    def click_open_manual(cls):
        logger.debug("open manual")
        Helper.explore_folder("https://www.hydroffice.org/manuals/soundspeed/ssm_sis.html")

    def update_gui(self):
        if self.sis is None:
            self.viewer.clear()
            return
        self.viewer.setText(self.sis.info())
