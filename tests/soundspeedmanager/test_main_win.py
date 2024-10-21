import unittest

from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

from hyo2.ssm2.app.gui.soundspeedmanager.mainwin import MainWin


class TestSoundSpeedManagerMainWin(unittest.TestCase):

    def setUp(self):
        self.app = QApplication.instance() or QApplication([])
        self.window = MainWin()
        self.window.skip_do_you_really_quit = True
        self.window.show()

    def test_menu_file(self):

        # Simulate clicking the "File" menu
        QTest.mouseClick(self.window.menu, Qt.LeftButton,
                         pos=self.window.menu.actionGeometry(self.window.menu.actions()[0]).center())

        # Simulate clicking the "Import Input Data" menu
        QTest.mouseClick(self.window.menu, Qt.LeftButton,
                         pos=self.window.file_menu.actionGeometry(self.window.file_menu.actions()[0]).center())

    def tearDown(self):
        self.window.close()
        self.app.quit()


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedManagerMainWin))
    return s
