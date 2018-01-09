from PySide import QtGui
from PySide import QtCore

import logging
logger = logging.getLogger(__name__)

from hyo.soundspeedmanager.dialogs.dialog import AbstractDialog


class AutomateDialog(AbstractDialog):

    def __init__(self, main_win, lib, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        settings = QtCore.QSettings()

        self.setWindowTitle("Automated Processing Setup")
        self.setMinimumWidth(300)

        self.botton_min_width = 80
        lbl_width = 180

        # outline ui
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # input file formats
        self.importLayout = QtGui.QVBoxLayout()
        self.mainLayout.addLayout(self.importLayout)
        # - import
        import_hbox = QtGui.QHBoxLayout()
        self.importLayout.addLayout(import_hbox)
        import_hbox.addStretch()
        import_label = QtGui.QLabel("Input file format:")
        import_hbox.addWidget(import_label)
        import_hbox.addStretch()
        # - fmt layout
        self.fmtLayout = QtGui.QHBoxLayout()
        self.importLayout.addLayout(self.fmtLayout)
        # -- left
        self.leftButtonBox = QtGui.QDialogButtonBox(QtCore.Qt.Vertical)
        self.fmtLayout.addWidget(self.leftButtonBox)
        # -- middle
        self.midButtonBox = QtGui.QDialogButtonBox(QtCore.Qt.Vertical)
        self.fmtLayout.addWidget(self.midButtonBox)
        # -- right
        self.rightButtonBox = QtGui.QDialogButtonBox(QtCore.Qt.Vertical)
        self.fmtLayout.addWidget(self.rightButtonBox)
        # --- add "Ask user"
        ask_label = "Ask user"
        btn = QtGui.QPushButton(ask_label)
        btn.setToolTip("Ask user for input format")
        btn.setMinimumWidth(self.botton_min_width)
        btn.setCheckable(True)
        if settings.value("default_input_format") is None:
            btn.setChecked(True)
        elif settings.value("default_input_format") == ask_label:
            btn.setChecked(True)
        self.leftButtonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
        # --- add buttons
        idx_reminder = 0
        for idx, _ in enumerate(self.lib.name_readers):

            if len(self.lib.ext_readers[idx]) == 0:
                continue

            btn = QtGui.QPushButton("%s" % self.lib.desc_readers[idx])
            btn.setToolTip("Import %s format [*.%s]" % (self.lib.desc_readers[idx],
                                                        ", *.".join(self.lib.ext_readers[idx])))
            btn.setMinimumWidth(self.botton_min_width)
            btn.setCheckable(True)
            if settings.value("default_input_format") == self.lib.desc_readers[idx]:
                btn.setChecked(True)

            idx_reminder = idx % 3
            if idx_reminder == 2:
                self.leftButtonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
            elif idx_reminder == 0:
                self.midButtonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
            else:
                self.rightButtonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
        # --- add Seabird CTD
        seabird_ctd_label = "Seabird CTD"
        btn = QtGui.QPushButton(seabird_ctd_label)
        btn.setToolTip("Retrieve profiles from Seabird CTD")
        btn.setMinimumWidth(self.botton_min_width)
        btn.setCheckable(True)
        if settings.value("default_input_format") == seabird_ctd_label:
            btn.setChecked(True)
        if idx_reminder == 1:
            self.leftButtonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
        elif idx_reminder == 2:
            self.midButtonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
        else:
            self.rightButtonBox.addButton(btn, QtGui.QDialogButtonBox.ActionRole)
        # noinspection PyUnresolvedReferences
        self.leftButtonBox.clicked.connect(self.on_input_format)
        # noinspection PyUnresolvedReferences
        self.midButtonBox.clicked.connect(self.on_input_format)
        # noinspection PyUnresolvedReferences
        self.rightButtonBox.clicked.connect(self.on_input_format)

        self.mainLayout.addSpacing(18)

        # auto apply
        self.applyLayout = QtGui.QVBoxLayout()
        self.mainLayout.addLayout(self.applyLayout)
        apply_hbox = QtGui.QHBoxLayout()
        self.applyLayout.addLayout(apply_hbox)
        apply_hbox.addStretch()
        apply_label = QtGui.QLabel("Auto apply:")
        apply_hbox.addWidget(apply_label)
        apply_hbox.addStretch()

        # - smooth/filter data
        hbox = QtGui.QHBoxLayout()
        self.applyLayout.addLayout(hbox)
        # -- label
        label = QtGui.QLabel("Smooth/filter profile data:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- label
        self.smooth_filter = QtGui.QComboBox()
        self.smooth_filter.addItems(["True", "False"])
        if settings.value("auto_smooth_filter") == "true":
            self.smooth_filter.setCurrentIndex(0)
        else:
            self.smooth_filter.setCurrentIndex(1)
        # noinspection PyUnresolvedReferences
        self.smooth_filter.currentIndexChanged.connect(self.changed_smooth_filter)
        hbox.addWidget(self.smooth_filter)

        # - salinity/temperature
        hbox = QtGui.QHBoxLayout()
        self.applyLayout.addLayout(hbox)
        # -- label
        label = QtGui.QLabel("Retrieve salinity/temperature:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- label
        self.sal_temp = QtGui.QComboBox()
        self.sal_temp.addItems(["True", "False"])
        if settings.value("auto_sal_temp") == "true":
            self.sal_temp.setCurrentIndex(0)
        else:
            self.sal_temp.setCurrentIndex(1)
        # noinspection PyUnresolvedReferences
        self.sal_temp.currentIndexChanged.connect(self.changed_sal_temp)
        hbox.addWidget(self.sal_temp)

        # - TSS
        hbox = QtGui.QHBoxLayout()
        self.applyLayout.addLayout(hbox)
        # -- label
        label = QtGui.QLabel("Retrieve transducer sound speed:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- label
        self.tss = QtGui.QComboBox()
        self.tss.addItems(["True", "False"])
        if settings.value("auto_tss") == "true":
            self.tss.setCurrentIndex(0)
        else:
            self.tss.setCurrentIndex(1)
        # noinspection PyUnresolvedReferences
        self.tss.currentIndexChanged.connect(self.changed_tss)
        hbox.addWidget(self.tss)

        # - extend
        hbox = QtGui.QHBoxLayout()
        self.applyLayout.addLayout(hbox)
        # -- label
        label = QtGui.QLabel("Extend profile data:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        # -- label
        self.extend = QtGui.QComboBox()
        self.extend.addItems(["True", "False"])
        if settings.value("auto_extend") == "true":
            self.extend.setCurrentIndex(0)
        else:
            self.extend.setCurrentIndex(1)
        # noinspection PyUnresolvedReferences
        self.extend.currentIndexChanged.connect(self.changed_extend)
        hbox.addWidget(self.extend)

        self.mainLayout.addStretch()

        # edit/apply
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch()
        self.apply = QtGui.QPushButton("OK")
        self.apply.setFixedWidth(40)
        # noinspection PyUnresolvedReferences
        self.apply.clicked.connect(self.on_apply)
        hbox.addWidget(self.apply)
        hbox.addStretch()
        self.mainLayout.addLayout(hbox)

    def changed_smooth_filter(self):
        changed_text = self.smooth_filter.currentText()
        logger.debug("change smooth filter: %s" % changed_text)
        settings = QtCore.QSettings()
        settings.setValue("auto_smooth_filter", changed_text == "True")

    def changed_sal_temp(self):
        changed_text = self.sal_temp.currentText()
        logger.debug("change sal/temp: %s" % changed_text)
        settings = QtCore.QSettings()
        settings.setValue("auto_sal_temp", changed_text == "True")

    def changed_tss(self):
        changed_text = self.tss.currentText()
        logger.debug("change tss: %s" % changed_text)
        settings = QtCore.QSettings()
        settings.setValue("auto_tss", changed_text == "True")

    def changed_extend(self):
        changed_text = self.extend.currentText()
        logger.debug("change extend: %s" % changed_text)
        settings = QtCore.QSettings()
        settings.setValue("auto_extend", changed_text == "True")

    def on_input_format(self, btn):

        # uncheck all the buttons except the selected one
        for b in self.leftButtonBox.buttons():
            if b != btn:
                b.setChecked(False)
        for b in self.midButtonBox.buttons():
            if b != btn:
                b.setChecked(False)
        for b in self.rightButtonBox.buttons():
            if b != btn:
                b.setChecked(False)

        # store in the registry the newly selected format
        fmt_name = btn.text()
        logger.debug("set default input format: %s" % fmt_name)
        settings = QtCore.QSettings()
        settings.setValue("default_input_format", fmt_name)

        # idx = self.lib.desc_readers.index(btn.text())
        # name = self.lib.name_readers[idx]
        # desc = self.lib.desc_readers[idx]
        # ext = self.lib.ext_readers[idx]

    def on_apply(self):
        self.accept()
