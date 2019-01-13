import logging

from PySide2 import QtCore, QtGui, QtWidgets

from hyo2.sis.app import app_info, controlpanel

logger = logging.getLogger(__name__)


class MainWin(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.name = app_info.app_name
        self.version = app_info.app_version

        self.setWindowTitle('%s v.%s' % (self.name, self.version))
        # noinspection PyArgumentList
        _app = QtCore.QCoreApplication.instance()
        _app.setApplicationName('%s' % self.name)
        _app.setOrganizationName("HydrOffice")
        _app.setOrganizationDomain("hydroffice.org")

        # set icons
        self.setWindowIcon(QtGui.QIcon(app_info.app_icon_path))

        self.panel = controlpanel.ControlPanel()
        self.setCentralWidget(self.panel)

    def _do_you_really_want(self, title="Quit", text="quit"):
        """helper function that show to the user a message windows asking to confirm an action"""
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setIconPixmap(QtGui.QPixmap(app_info.app_icon_path).scaled(QtCore.QSize(36, 36)))
        msg_box.setText('Do you really want to %s?' % text)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msg_box.setDefaultButton(QtWidgets.QMessageBox.No)
        return msg_box.exec_()

    def closeEvent(self, event):
        """ actions to be done before close the app """
        reply = self._do_you_really_want("Quit", "quit %s" % self.name)

        if reply == QtWidgets.QMessageBox.Yes:

            event.accept()
            self.panel.stop_emulation()
            super().closeEvent(event)

        else:
            event.ignore()
