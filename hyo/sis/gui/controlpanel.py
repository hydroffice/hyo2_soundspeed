import logging
import os
from multiprocessing import Pipe
from threading import Timer

from PySide import QtCore
from PySide import QtGui

logger = logging.getLogger(__name__)

from hyo.sis.lib.process import SisProcess
from hyo.sis.gui.infoviewer import InfoViewerDialog
from hyo.soundspeedmanager.qt_progress import QtProgress


class ControlPanel(QtGui.QWidget):

    here = os.path.abspath(os.path.dirname(__file__)).replace("\\", "/")

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

        self.vbox.addSpacing(12)
        credits = QtGui.QLabel("<i>Comments and suggestions:</i> "
                               "<a href='mailto:gmasetti@ccom.unh.edu'>gmasetti@ccom.unh.edu</a>")
        credits.setOpenExternalLinks(True)
        self.vbox.addWidget(credits)

        # info viewer
        self.info_viewer = InfoViewerDialog(self)

        # processing pipe

        self.conn = None
        self.child_conn = None
        self._active = False
        self._replay_timing = 1.0

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

        vbox.addSpacing(12)

        # replay timing
        hbox = QtGui.QHBoxLayout()
        vbox.addLayout(hbox)
        text_timing = QtGui.QLabel("Timing:")
        hbox.addWidget(text_timing)
        text_timing.setMinimumWidth(80)
        self.set_timing = QtGui.QSlider()
        self.set_timing.setOrientation(QtCore.Qt.Horizontal)
        self.set_timing.setMinimum(1)
        self.set_timing.setMaximum(5)
        self.set_timing.setTickInterval(1)
        self.set_timing.setValue(1)
        self.set_timing.setTickPosition(QtGui.QSlider.TicksBelow)
        # noinspection PyUnresolvedReferences
        self.set_timing.valueChanged.connect(self.on_replay_timing)
        hbox.addWidget(self.set_timing)

        # verbose
        hbox = QtGui.QHBoxLayout()
        vbox.addLayout(hbox)
        text_verbose = QtGui.QLabel("Verbose:")
        hbox.addWidget(text_verbose)
        text_verbose.setMinimumWidth(80)
        self.set_verbose = QtGui.QCheckBox()
        self.set_verbose.setChecked(True)
        hbox.addWidget(self.set_verbose)
        hbox.addStretch()

    def _make_sis_inputs(self):

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
        # noinspection PyUnresolvedReferences
        button_add_files.clicked.connect(self._add_source_files)

        button_clear_files = QtGui.QPushButton()
        hbox.addWidget(button_clear_files)
        button_clear_files.setText("Clear files")
        button_clear_files.setToolTip('Clear the file list')
        # noinspection PyUnresolvedReferences
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
        # noinspection PyUnresolvedReferences
        button_start_sis.clicked.connect(self.start_emulation)

        button_stop_sis = QtGui.QPushButton()
        hbox.addWidget(button_stop_sis)
        button_stop_sis.setText("Stop SIS")
        button_stop_sis.setToolTip('Stop emulation')
        # noinspection PyUnresolvedReferences
        button_stop_sis.clicked.connect(self.stop_emulation)

        hbox.addStretch()

    # #################################################################################
    # ################################ action slots ###################################

    def _add_source_files(self):
        logger.debug('adding files')

        settings = QtCore.QSettings()
        source_folder = settings.value("source_folder", self.here)

        # ask the file path to the user
        # noinspection PyCallByClass
        selections, _ = QtGui.QFileDialog.getOpenFileNames(self, "Add Kongsberg data files", source_folder,
                                                           "Kongsberg file (*.all);;All files (*.*)", None,
                                                           QtGui.QFileDialog.ExistingFiles)
        if not selections:
            logger.debug('no selection')
            return

        selected_folder = os.path.dirname(selections[0])
        logger.debug("selected folder: %s" % selected_folder)
        settings.setValue("source_folder", selected_folder)

        for f in selections:
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

    def monitoring(self):

        if self.conn is None:
            return

        if self.conn.poll():

            data = self.conn.recv()

            if isinstance(data, str):

                self.info_viewer.append(data)
                # logger.debug("%s" % data)

        if not self._active:
            return

        Timer(1.0, self.monitoring).start()

    def start_emulation(self):
        if self.sis:
            if self.sis.is_alive():
                # noinspection PyCallByClass
                QtGui.QMessageBox.warning(self, "Emulator running ...", "The emulator is running! Stop it",
                                          QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                return

        self.info_viewer.viewer.verticalScrollBar().setValue(self.info_viewer.viewer.verticalScrollBar().maximum())
        self.info_viewer.show()

        # create a new thread
        input_port = int(self.set_input_port.text())
        output_ip = self.set_output_ip.text()
        output_port = int(self.set_output_port.text())
        self.conn, self.child_conn = Pipe()
        self.sis = SisProcess(conn=self.child_conn, port_in=input_port, port_out=output_port, ip_out=output_ip,
                              replay_timing=self._replay_timing,
                              verbose=self.set_verbose.isChecked())
        logger.debug('created new simulator')

        file_list = list()
        for i in range(self.list_files.count()):

            logger.debug("passing file: %s" % self.list_files.item(i).text())
            file_path = self.list_files.item(i).text()
            if os.path.exists(file_path):
                file_list.append(file_path)

        if len(file_list) > 0:
            logger.debug('added source files: %s' % len(file_list))

            self.sis.set_files(file_list)

        self.sis.start()

        self._active = True
        self.monitoring()

    def stop_emulation(self):
        logger.debug("stop SIS")
        if self.sis:

            progress = QtProgress(self)
            progress.start(title="Halting", text="Wait while threads stop")
            progress.update(value=20)
            self.sis.stop()

            progress.update(value=30)
            self.sis.join()
            self.sis = None

            progress.end()

        self._active = False
        self.info_viewer.hide()

    def on_replay_timing(self):
        value = self.set_timing.value()

        if value == 1:
            self._replay_timing = 1.0

        elif value == 2:
            self._replay_timing = 0.5

        elif value == 3:
            self._replay_timing = 0.1

        elif value == 4:
            self._replay_timing = 0.01

        else:
            self._replay_timing = 0.0001

        if self.sis is not None:
            self.conn.send(self._replay_timing)

        logger.debug("changed timing: %.4f" % self._replay_timing)
