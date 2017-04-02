import os

from PySide import QtGui
from PySide import QtCore

# logging settings
import logging
logger = logging.getLogger(__name__)

from .process import SisProcess


class ControlPanel(QtGui.QWidget):

    here = os.path.abspath(os.path.dirname(__file__))

    def __init__(self):
        super(ControlPanel, self).__init__()
        self.sis = None

        self.vbox = QtGui.QVBoxLayout()
        self.setLayout(self.vbox)

        self.sis_settings = QtGui.QGroupBox("settings")
        self.sis_settings.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.vbox.addWidget(self.sis_settings)
        self.set_input_port = None
        self.set_output_ip = None
        self.set_output_port = None
        self._make_sis_settings()

        self.sis_inputs = QtGui.QGroupBox("inputs")
        self.sis_inputs.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.vbox.addWidget(self.sis_inputs)
        self.list_files = None
        self._make_sis_inputs()

        self.sis_commands = QtGui.QGroupBox("commands")
        self.sis_commands.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.vbox.addWidget(self.sis_commands)
        self.start_sis = None
        self.stop_sis = None
        self._make_sis_commands()

    def _make_sis_settings(self):
        """build "settings" groupbox"""

        vbox = QtGui.QVBoxLayout()
        self.sis_settings.setLayout(vbox)

        # input port
        hbox = QtGui.QHBoxLayout()
        vbox.addLayout(hbox)
        text_input_port = QtGui.QLabel("Input port:")
        hbox.addWidget(text_input_port)
        text_input_port.setMinimumWidth(80)
        self.set_input_port = QtGui.QLineEdit("")
        hbox.addWidget(self.set_input_port)
        validator = QtGui.QIntValidator(0, 65535)
        self.set_input_port.setValidator(validator)
        self.set_input_port.setText("4001")

        # output ip
        hbox = QtGui.QHBoxLayout()
        vbox.addLayout(hbox)
        text_output_ip = QtGui.QLabel("Output IP:")
        hbox.addWidget(text_output_ip)
        text_output_ip.setMinimumWidth(80)
        self.set_output_ip = QtGui.QLineEdit("")
        hbox.addWidget(self.set_output_ip)
        octet = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        reg_ex = QtCore.QRegExp("^%s\.%s\.%s\.%s$" % (octet, octet, octet, octet))
        validator = QtGui.QRegExpValidator(reg_ex)
        self.set_output_ip.setValidator(validator)
        self.set_output_ip.setText("127.0.0.1")

        # output port
        hbox = QtGui.QHBoxLayout()
        vbox.addLayout(hbox)
        text_output_port = QtGui.QLabel("Output port:")
        hbox.addWidget(text_output_port)
        text_output_port.setMinimumWidth(80)
        self.set_output_port = QtGui.QLineEdit("")
        hbox.addWidget(self.set_output_port)
        validator = QtGui.QIntValidator(0, 65535)
        self.set_output_port.setValidator(validator)
        self.set_output_port.setText("16103")

    def _make_sis_inputs(self):
        """build "inputs" groupbox"""

        vbox = QtGui.QVBoxLayout()
        self.sis_inputs.setLayout(vbox)

        self.list_files = QtGui.QListWidget()
        vbox.addWidget(self.list_files)

        hbox = QtGui.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()

        button_add_files = QtGui.QPushButton()
        hbox.addWidget(button_add_files)
        button_add_files.setText("Add files")
        button_add_files.setToolTip('Add files as data source for emulation')
        button_add_files.clicked.connect(self._add_source_files)

        button_clear_files = QtGui.QPushButton()
        hbox.addWidget(button_clear_files)
        button_clear_files.setText("Clear files")
        button_clear_files.setToolTip('Clear the file list')
        button_clear_files.clicked.connect(self._clear_source_files)

        hbox.addStretch()

    def _make_sis_commands(self):
        """build "commands" groupbox"""

        vbox = QtGui.QVBoxLayout()
        self.sis_commands.setLayout(vbox)

        hbox = QtGui.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()

        button_start_sis = QtGui.QPushButton()
        hbox.addWidget(button_start_sis)
        button_start_sis.setText("Start SIS")
        button_start_sis.setToolTip('Start emulation using defined settings')
        button_start_sis.clicked.connect(self.sis_start)

        button_stop_sis = QtGui.QPushButton()
        hbox.addWidget(button_stop_sis)
        button_stop_sis.setText("Stop SIS")
        button_stop_sis.setToolTip('Stop emulation')
        button_stop_sis.clicked.connect(self.sis_stop)

        hbox.addStretch()

    # #################################################################################
    # ################################ action slots ###################################

    def _add_source_files(self):
        logger.debug('adding files')

        # ask the file path to the user
        selection, _ = QtGui.QFileDialog.getOpenFileNames(self, "Add Kongsberg data files", "",
                                                          "Kongbserg file (*.all);;All files (*.*)", None,
                                                          QtGui.QFileDialog.ExistingFiles)
        if not selection:
            logger.debug('no selection')
            return

        for f in selection:
            ret = self.list_files.findItems(f, QtCore.Qt.MatchExactly)
            if len(ret) > 0:
                logger.debug('duplicated %s' % os.path.basename(f))
                continue
            item = QtGui.QListWidgetItem(f)
            self.list_files.addItem(item)
            logger.debug('added %s' % os.path.basename(f))

    def _clear_source_files(self):
        logger.debug('clear source files')
        self.list_files.clear()

    def sis_start(self):
        if self.sis:
            if self.sis.is_alive():
                QtGui.QMessageBox.warning(self, "Emulator running ...", "The emulator is running! Stop it",
                                          QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                return

        # create a new thread
        input_port = int(self.set_input_port.text())
        output_ip = self.set_output_ip.text()
        output_port = int(self.set_output_port.text())
        self.sis = SisProcess(port_in=input_port, port_out=output_port, ip_out=output_ip)
        logger.debug('created new simulator')

        file_list = list()
        for i in range(self.list_files.count()):
            print(self.list_files.item(i).text())
            file_path = self.list_files.item(i).text()
            if os.path.exists(file_path):
                file_list.append(file_path)

        if len(file_list) > 0:
            logger.debug('added source files: %s' % len(file_list))

            self.sis.set_files(file_list)

        self.sis.start()

    def sis_stop(self):
        logger.debug("stop SIS")
        if self.sis:
            self.sis.stop()
            self.sis.join()
            self.sis = None
