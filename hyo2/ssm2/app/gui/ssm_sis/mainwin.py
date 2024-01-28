import logging

from PySide6 import QtCore, QtGui, QtWidgets
from urllib.request import urlopen

from hyo2.abc2.lib.package.pkg_helper import PkgHelper
from hyo2.abc2.app.web_renderer import WebRenderer
from hyo2.ssm2.app.gui.ssm_sis import app_info
from hyo2.ssm2.app.gui.ssm_sis.controlpanel import ControlPanel


logger = logging.getLogger(__name__)


class MainWin(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self._web = WebRenderer()
        self._check_web_page()
        self._check_latest_release()

        # set the application name and the version
        self.name = app_info.app_name
        self.version = app_info.app_version
        self.setWindowTitle('%s v.%s' % (self.name, self.version))
        # noinspection PyArgumentList
        _app = QtCore.QCoreApplication.instance()
        _app.setApplicationName('%s' % self.name)
        _app.setOrganizationName("HydrOffice")
        _app.setOrganizationDomain("hydroffice.org")

        # set the minimum and the initial size
        # noinspection PyArgumentList
        self.setMinimumSize(240, 320)
        # noinspection PyArgumentList
        self.resize(320, 460)

        # set icons
        self.setWindowIcon(QtGui.QIcon(app_info.app_icon_path))

        self.panel = ControlPanel()
        self.setCentralWidget(self.panel)

    def _check_web_page(self, token: str = ""):
        try:
            if len(token) > 0:
                url = "%s_%s" % (PkgHelper(lib_info=app_info).web_url(), token)
            else:
                url = "%s" % PkgHelper(lib_info=app_info).web_url()
            self._web.open(url=url)
            # logger.debug('check %s' % url)

        except Exception as e:
            logger.warning(e, exc_info=True)

    @classmethod
    def _check_latest_release(cls):
        try:
            response = urlopen(app_info.lib_latest_url, timeout=1)
            latest_version = response.read().split()[0].decode()
            cur_maj, cur_min, cur_fix = app_info.app_version.split('.')
            lat_maj, lat_min, lat_fix = latest_version.split('.')

            if int(lat_maj) > int(cur_maj):
                logger.info("new release available: %s" % latest_version)

            elif (int(lat_maj) == int(cur_maj)) and (int(lat_min) > int(cur_min)):
                logger.info("new release available: %s" % latest_version)

            elif (int(lat_maj) == int(cur_maj)) and (int(lat_min) == int(cur_min)) and (int(lat_fix) > int(cur_fix)):
                logger.info("new bugfix available: %s" % latest_version)

        except Exception as e:
            logger.warning(e)

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
            self.panel.stop_listening()
            super().closeEvent(event)

        else:
            event.ignore()
