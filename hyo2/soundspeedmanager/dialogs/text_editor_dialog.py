import os
import logging

from PySide2 import QtCore, QtGui, QtWidgets

from hyo2.soundspeedmanager import app_info
from hyo2.soundspeedmanager.dialogs.dialog import AbstractDialog
from hyo2.soundspeedmanager.dialogs.text_editor import TextEditor

logger = logging.getLogger(__name__)


class TextEditorDialog(AbstractDialog):

    def __init__(self, title, basename, body, main_win, lib, parent=None, init_size=QtCore.QSize(600, 400)):
        AbstractDialog.__init__(self, main_win=main_win, lib=lib, parent=parent)

        self._title = title
        self.setWindowTitle(self._title)
        self.setMinimumSize(200, 200)
        self.resize(init_size)

        self._basename = basename
        self._body = body

        self._original = str()

        # outline ui
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainWidget = QtWidgets.QMainWindow()
        self.mainLayout.addWidget(self.mainWidget)

        self._editor = TextEditor()
        self.mainWidget.setCentralWidget(self._editor)
        self._editor.set_html_text(body)

        # tool bar
        self._tools_bar = self.mainWidget.addToolBar('Tools')
        self._tools_bar.setIconSize(QtCore.QSize(32, 32))
        self._tools_bar.setAllowedAreas(QtCore.Qt.TopToolBarArea | QtCore.Qt.BottomToolBarArea)

        # lock
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(self.media, 'lock.png'), QtCore.QSize(), QtGui.QIcon.Selected, QtGui.QIcon.Off)
        icon.addFile(os.path.join(self.media, 'unlock.png'), QtCore.QSize(), QtGui.QIcon.Selected, QtGui.QIcon.On)
        self._lock_act = QtWidgets.QAction(icon, 'Lock/unlock editing', self)
        self._lock_act.setCheckable(True)
        self._lock_act.setShortcut('Ctrl+L')
        # noinspection PyUnresolvedReferences
        self._lock_act.triggered.connect(self.on_lock_editing)
        self._tools_bar.addAction(self._lock_act)

        # view
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(self.media, 'html.png'), QtCore.QSize(), QtGui.QIcon.Selected, QtGui.QIcon.Off)
        icon.addFile(os.path.join(self.media, 'text.png'), QtCore.QSize(), QtGui.QIcon.Selected, QtGui.QIcon.On)
        self._view_act = QtWidgets.QAction(icon, 'View as html or raw text', self)
        self._view_act.setCheckable(True)
        self._view_act.setShortcut('Ctrl+T')
        # noinspection PyUnresolvedReferences
        self._view_act.triggered.connect(self.on_view_file)
        self._tools_bar.addAction(self._view_act)

        self._tools_bar.addSeparator()

        # save
        self._save_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'save.png')), 'Save file', self)
        self._save_act.setShortcut('Ctrl+S')
        # noinspection PyUnresolvedReferences
        self._save_act.triggered.connect(self.on_save_file)
        self._tools_bar.addAction(self._save_act)

        self.mainWidget.statusBar().setStyleSheet("QStatusBar{color:rgba(0,0,0,128);font-size: 8pt;}")
        self.status_bar_normal_style = self.mainWidget.statusBar().styleSheet()
        timer = QtCore.QTimer(self)
        # noinspection PyUnresolvedReferences
        timer.timeout.connect(self._update_gui)
        timer.start(400)

    def _update_gui(self):

        win_title = self._title
        if self._editor.dirty:
            self.mainWidget.statusBar().setStyleSheet("QStatusBar{color:rgba(0,0,0,128);"
                                                      "font-size: 8pt; background-color:rgba(255, 255, 200, 255);}")
            win_title += " [unsaved]"
        else:
            self.mainWidget.statusBar().setStyleSheet(self.status_bar_normal_style)

        self.setWindowTitle(win_title)
        self.mainWidget.statusBar().showMessage("%s - row: %s, col: %s"
                                                % (self._basename, self._editor.current_row, self._editor.current_col),
                                                500)

    def on_lock_editing(self):

        if self._lock_act.isChecked():
            logger.debug("unlocking")
            self._editor.set_read_only(False)

        else:
            logger.debug("locking")
            self._editor.set_read_only(True)

    def on_view_file(self):

        if self._view_act.isChecked():
            logger.debug("view raw text")
            self._editor.view_raw_text()
            self._save_act.setDisabled(True)

        else:
            logger.debug("view html text")
            self._editor.view_html_text()
            self._save_act.setEnabled(True)

    def on_save_file(self):
        logger.debug("save file")

        output_folder = QtCore.QSettings().value("%s_export_folder" % self._title.lower())
        if output_folder is None:
            output_folder = self.lib.outputs_folder

        output_path = os.path.join(output_folder, self._basename)
        # noinspection PyCallByClass
        selection, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save file", output_path,
                                                             "Output file (*.txt);;All files (*.*)", "",
                                                             QtWidgets.QFileDialog.DontConfirmOverwrite)
        if selection == "":
            logger.debug('save file: aborted')
            return

        output_folder = os.path.dirname(selection)
        if os.path.exists(output_folder):
            QtCore.QSettings().setValue("%s_export_folder" % self._title.lower(), output_folder)

        append = False
        if os.path.exists(selection):

            msg = "Do you want to append to the existing file?"
            # noinspection PyCallByClass
            ret = QtWidgets.QMessageBox.warning(self, "File exists", msg,
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
            if ret == QtWidgets.QMessageBox.Cancel:
                return
            elif ret == QtWidgets.QMessageBox.Yes:
                append = True

        self._editor.save_txt(selection, append=append)

    # Quitting #

    def do_you_really_want(self, title="Quit", text="quit"):
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setIconPixmap(QtGui.QPixmap(app_info.app_icon_path).scaled(QtCore.QSize(36, 36)))
        msg_box.setText('There are unsaved changes!\nDo you really want to %s?' % text)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msg_box.setDefaultButton(QtWidgets.QMessageBox.No)
        return msg_box.exec_()

    def closeEvent(self, event):
        """ actions to be done before close the app """
        if not self._editor.dirty:
            super(TextEditorDialog, self).closeEvent(event)
            return

        reply = self.do_you_really_want("Close", "close the editor")

        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
            super(TextEditorDialog, self).closeEvent(event)
            return

        else:
            event.ignore()
            return
