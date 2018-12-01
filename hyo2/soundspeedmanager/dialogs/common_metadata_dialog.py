import logging

from PySide2 import QtWidgets

from hyo2.soundspeedmanager.dialogs.dialog import AbstractDialog
from hyo2.soundspeed.base.setup_sql import vessel_list, institution_list

logger = logging.getLogger(__name__)


class CommonMetadataDialog(AbstractDialog):

    def __init__(self, main_win, lib, pks, parent=None):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        self.pks = pks

        self.setWindowTitle("Edit common metadata fields")
        self.setMinimumWidth(400)

        lbl_width = 90

        # outline ui
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # institution
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtWidgets.QLabel("Institution:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.institution = QtWidgets.QComboBox()
        if not lib.setup.noaa_tools:
            self.institution.setEditable(True)
        self.institution.addItems(institution_list)
        self.institution.insertItem(0, "")
        self.institution.setCurrentIndex(self.institution.findText(""))
        hbox.addWidget(self.institution)
        self.institution.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.institution.editTextChanged.connect(self.changed_institution)
        # noinspection PyUnresolvedReferences
        self.institution.currentIndexChanged.connect(self.changed_institution)

        # survey
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtWidgets.QLabel("Survey:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.survey = QtWidgets.QLineEdit()
        hbox.addWidget(self.survey)
        self.survey.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.survey.textChanged.connect(self.changed_survey)

        # vessel
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtWidgets.QLabel("Vessel:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.vessel = QtWidgets.QComboBox()
        if not lib.setup.noaa_tools:
            self.vessel.setEditable(True)
        self.vessel.addItems(vessel_list)
        self.vessel.insertItem(0, "")
        self.vessel.setCurrentIndex(self.vessel.findText(""))
        hbox.addWidget(self.vessel)
        self.vessel.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.vessel.editTextChanged.connect(self.changed_vessel)
        # noinspection PyUnresolvedReferences
        self.vessel.currentIndexChanged.connect(self.changed_vessel)

        # serial number
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtWidgets.QLabel("S/N:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.sn = QtWidgets.QLineEdit()
        hbox.addWidget(self.sn)
        self.sn.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.sn.textChanged.connect(self.changed_sn)

        # comments
        hbox = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(hbox)
        label = QtWidgets.QLabel("Comments:")
        label.setFixedWidth(lbl_width)
        hbox.addWidget(label)
        self.comments = QtWidgets.QTextEdit()
        self.comments.setMinimumHeight(24)
        self.comments.setMaximumHeight(60)
        hbox.addWidget(self.comments)
        self.comments.setAutoFillBackground(True)
        # noinspection PyUnresolvedReferences
        self.comments.textChanged.connect(self.changed_comments)

        self.mainLayout.addStretch()
        self.mainLayout.addSpacing(8)

        # edit/apply
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch()
        # --
        self.load_default = QtWidgets.QPushButton("Load default")
        self.load_default.setFixedHeight(30)
        self.load_default.setFixedWidth(90)
        # noinspection PyUnresolvedReferences
        self.load_default.clicked.connect(self.on_load_default)
        self.load_default.setToolTip("Load default metadata (if any)")
        hbox.addWidget(self.load_default)
        # --
        self.apply = QtWidgets.QPushButton("Apply")
        self.apply.setFixedHeight(self.load_default.height())
        self.apply.setFixedWidth(self.load_default.width())
        # noinspection PyUnresolvedReferences
        self.apply.clicked.connect(self.on_apply)
        self.apply.setToolTip("Apply changes (if any)")
        hbox.addWidget(self.apply)
        # --
        self.cancel = QtWidgets.QPushButton("Cancel")
        self.cancel.setFixedHeight(self.load_default.height())
        self.cancel.setFixedWidth(self.load_default.width())
        # noinspection PyUnresolvedReferences
        self.cancel.clicked.connect(self.reject)
        self.cancel.setToolTip("Not apply changes")
        hbox.addWidget(self.cancel)
        hbox.addStretch()
        self.mainLayout.addLayout(hbox)

    def changed_institution(self):
        self.institution.setStyleSheet("background-color: rgba(255,255,153, 255);")

    def changed_survey(self):
        self.survey.setStyleSheet("background-color: rgba(255,255,153, 255);")

    def changed_vessel(self):
        self.vessel.setStyleSheet("background-color: rgba(255,255,153, 255);")

    def changed_sn(self):
        self.sn.setStyleSheet("background-color: rgba(255,255,153, 255);")

    def changed_comments(self):
        self.comments.setStyleSheet("background-color: rgba(255,255,153, 255);")

    def on_load_default(self):
        logger.debug("load default")

        if self.lib.setup.default_institution and self.institution.findText(self.lib.setup.default_institution) < 0:
            self.institution.insertItem(0, self.lib.setup.default_institution)
        self.institution.setCurrentIndex(self.institution.findText(self.lib.setup.default_institution))
        self.survey.setText(self.lib.setup.default_survey)
        if self.lib.setup.default_vessel and self.vessel.findText(self.lib.setup.default_vessel) < 0:
            self.vessel.insertItem(0, self.lib.setup.default_vessel)
        self.vessel.setCurrentIndex(self.vessel.findText(self.lib.setup.default_vessel))

    def on_apply(self):
        logger.debug("apply")

        for pk in self.pks:

            success = self.lib.load_profile(pk, skip_atlas=True)
            if not success:
                # noinspection PyCallByClass
                QtWidgets.QMessageBox.warning(self, "Database", "Unable to load profile #%s!" % pk,
                                              QtWidgets.QMessageBox.Ok)
                continue

            # apply changes
            try:
                if len(self.institution.currentText()) != 0:
                    self.lib.cur.meta.institution = self.institution.currentText()
                if len(self.survey.text()) != 0:
                    self.lib.cur.meta.survey = self.survey.text()
                if len(self.vessel.currentText()) != 0:
                    self.lib.cur.meta.vessel = self.vessel.currentText()
                if len(self.sn.text()) != 0:
                    self.lib.cur.meta.sn = self.sn.text()
                if len(self.comments.toPlainText()) != 0:
                    self.lib.cur.meta.comments = self.comments.toPlainText()

            except RuntimeError as e:
                msg = "Issue in apply changes\n%s" % e
                # noinspection PyCallByClass
                QtWidgets.QMessageBox.critical(self, "Metadata error", msg, QtWidgets.QMessageBox.Ok)
                continue

            # we store the metadata to the db
            if not self.lib.store_data():
                msg = "Unable to save to db!"
                # noinspection PyCallByClass
                QtWidgets.QMessageBox.warning(self, "Database warning for profile #%s" % pk, msg,
                                              QtWidgets.QMessageBox.Ok)
                continue

        self.main_win.data_stored()

        # reset to transparent
        self.institution.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.survey.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.vessel.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.sn.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
        self.comments.setStyleSheet("background-color: rgba(255, 255, 255, 255);")
