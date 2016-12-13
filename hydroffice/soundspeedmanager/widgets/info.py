from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

from PySide import QtCore
from PySide import QtGui
from PySide import QtWebKit

logger = logging.getLogger(__name__)

from hydroffice.soundspeed.base.helper import explore_folder


class Info(QtGui.QMainWindow):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')
    pdf = os.path.join(here, os.pardir, 'pdf')

    def __init__(self, default_url="http://www.hydroffice.org"):
        QtGui.QMainWindow.__init__(self)
        self.default_url = default_url

        self.toolbar = self.addToolBar('Shortcuts')
        self.toolbar.setIconSize(QtCore.QSize(42, 42))
        # default
        home_action = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'home.png')), 'Home page', self)
        home_action.setShortcut('Alt+H')
        # noinspection PyUnresolvedReferences
        home_action.triggered.connect(self.load_default)
        self.toolbar.addAction(home_action)
        # docs
        online_docs_action = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'online_docs.png')),
                                           'Online Documentation', self)
        online_docs_action.setShortcut('Alt+D')
        # noinspection PyUnresolvedReferences
        online_docs_action.triggered.connect(self.load_online_docs)
        self.toolbar.addAction(online_docs_action)
        offline_docs_action = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'offline_docs.png')),
                                            'Offline Documentation', self)
        offline_docs_action.setShortcut('Alt+O')
        # noinspection PyUnresolvedReferences
        offline_docs_action.triggered.connect(self.load_offline_docs)
        self.toolbar.addAction(offline_docs_action)
        # license
        license_action = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'license.png')), 'License', self)
        license_action.setShortcut('Alt+L')
        # noinspection PyUnresolvedReferences
        license_action.triggered.connect(self.load_license)
        self.toolbar.addAction(license_action)
        # authors
        authors_action = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'authors.png')), 'Authors', self)
        authors_action.setShortcut('Alt+A')
        # noinspection PyUnresolvedReferences
        authors_action.triggered.connect(self.show_authors)
        self.toolbar.addAction(authors_action)

        # separator
        self.toolbar.addSeparator()
        # HydrOffice.org
        hyo_action = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'hyo.png')), 'HydrOffice.org', self)
        hyo_action.setShortcut('Ctrl+H')
        # noinspection PyUnresolvedReferences
        hyo_action.triggered.connect(self.load_hydroffice_org)
        self.toolbar.addAction(hyo_action)
        # noaa
        noaa_action = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'noaa.png')), 'nauticalcharts.noaa.gov', self)
        noaa_action.setShortcut('Alt+N')
        # noinspection PyUnresolvedReferences
        noaa_action.triggered.connect(self.load_noaa_ocs_gov)
        self.toolbar.addAction(noaa_action)
        # ccom.unh.edu
        ccom_action = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'ccom.png')), 'ccom.unh.edu', self)
        ccom_action.setShortcut('Alt+C')
        # noinspection PyUnresolvedReferences
        ccom_action.triggered.connect(self.load_ccom_unh_edu)
        self.toolbar.addAction(ccom_action)
        # unh.edu
        unh_action = QtGui.QAction(QtGui.QIcon(os.path.join(self.media, 'unh.png')), 'unh.edu', self)
        unh_action.setShortcut('Alt+U')
        # noinspection PyUnresolvedReferences
        unh_action.triggered.connect(self.load_unh_edu)
        self.toolbar.addAction(unh_action)

        # create the layout
        frame = QtGui.QFrame()
        self.setCentralWidget(frame)
        grid = QtGui.QGridLayout()

        # Create the web widget and the url field
        self.web = QtWebKit.QWebView(self)
        hbox = QtGui.QHBoxLayout()
        go_to_label = QtGui.QLabel('Go to:')
        hbox.addWidget(go_to_label)
        self.url_input = UrlInput(self.web, default_url)
        hbox.addWidget(self.url_input)
        grid.addLayout(hbox, 1, 0)
        grid.addWidget(self.web, 2, 0)
        frame.setLayout(grid)

        # create an author dialog
        self.authors_dialog = QtGui.QDialog(self)
        self.authors_dialog.setWindowTitle("Write to the authors")
        self.authors_dialog.setMaximumSize(QtCore.QSize(150, 120))
        self.authors_dialog.setMaximumSize(QtCore.QSize(300, 240))
        vbox = QtGui.QVBoxLayout()
        self.authors_dialog.setLayout(vbox)

        hbox = QtGui.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        logo = QtGui.QLabel()
        logo.setPixmap(QtGui.QPixmap(os.path.join(self.media, 'favicon.png')))
        hbox.addWidget(logo)
        hbox.addStretch()

        vbox.addSpacing(10)

        text0 = QtGui.QLabel(self.authors_dialog)
        text0.setOpenExternalLinks(True)
        vbox.addWidget(text0)
        text0.setText("""
        <b>Comments and feature requests:</b><br>
        Giuseppe Masetti  <a href=\"mailto:gmasetti@ccom.unh.edu?Subject=Hydroffice%20SoundSpeed\">gmasetti@ccom.unh.edu</a><br>
        Barry Gallagher  <a href=\"mailto:barry.gallagher@noaa.gov?Subject=Hydroffice%20SoundSpeed\">barry.gallagher@noaa.gov</a><br>
        Brian Calder  <a href=\"mailto:brc@ccom.unh.edu?Subject=Hydroffice%20SoundSpeed\">brc@ccom.unh.edu</a><br>
        Chen Zhang  <a href=\"mailto:chen.zhang@noaa.gov?Subject=Hydroffice%20SoundSpeed\">chen.zhang@noaa.gov</a><br>
        Matt Wilson  <a href=\"mailto:matthew.wilson@noaa.gov?Subject=Hydroffice%20SoundSpeed\">matthew.wilson@noaa.gov</a><br>
        Jack Riley  <a href=\"mailto:jack.riley@noaa.gov?Subject=Hydroffice%20SoundSpeed\">jack.riley@noaa.gov</a><br>
        <br>
        <b>Bugs and support:</b><br>
        <a href=\"mailto:hydroffice.soundspeed@ccom.unh.edu?Subject=Hydroffice%20SoundSpeed\">hydroffice.soundspeed@ccom.unh.edu</a>
        """)

        # load default
        self.load_default()

    def load_default(self):
        self.url_input.setText(self.default_url)
        self.web.load(QtCore.QUrl(self.default_url))

    def load_online_docs(self):
        url = 'https://www.hydroffice.org/manuals/soundspeed/index.html'
        self.url_input.setText(url)
        self.web.load(QtCore.QUrl(url))

    def load_offline_docs(self):
        pdf_path = os.path.join(self.pdf, "SoundSpeedManager.pdf")
        if not os.path.exists(pdf_path):
            logger.warning("unable to find offline manual at %s" % pdf_path)
            return
        
        explore_folder(pdf_path)

    def load_license(self):
        url = 'https://www.hydroffice.org/license_lgpl21/'
        self.url_input.setText(url)
        self.web.load(QtCore.QUrl(url))

    def load_hydroffice_org(self):
        url = 'https://www.hydroffice.org'
        self.url_input.setText(url)
        self.web.load(QtCore.QUrl(url))

    def load_noaa_ocs_gov(self):
        url = 'http://www.nauticalcharts.noaa.gov/'
        self.url_input.setText(url)
        self.web.load(QtCore.QUrl(url))

    def load_ccom_unh_edu(self):
        url = 'http://ccom.unh.edu'
        self.url_input.setText(url)
        self.web.load(QtCore.QUrl(url))

    def load_unh_edu(self):
        url = 'http://www.unh.edu'
        self.url_input.setText(url)
        self.web.load(QtCore.QUrl(url))

    def show_authors(self):
        self.authors_dialog.show()


class UrlInput(QtGui.QLineEdit):
    def __init__(self, browser, default_url):
        super(UrlInput, self).__init__()
        self.browser = browser
        self.setText(default_url)
        self.returnPressed.connect(self.return_pressed)

    def return_pressed(self):
        url = QtCore.QUrl(self.text())
        # load url into browser frame
        self.browser.load(url)