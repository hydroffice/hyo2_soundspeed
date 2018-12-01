import unittest

from hyo2.soundspeedmanager import AppInfo
from PySide2 import QtWidgets
from hyo2.abc.app.qt_progress import QtProgress


class TestSoundSpeedManagerQtProgress(unittest.TestCase):

    # app = QtWidgets.QApplication([])

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_start_minimal(self):

        if not QtWidgets.qApp:
            QtWidgets.QApplication([])

        widget = QtWidgets.QWidget()
        widget.show()
        progress = QtProgress(parent=widget)

        try:
            progress.start()

        except Exception as e:
            self.fail(e)

    def test_end_minimal(self):

        if not QtWidgets.qApp:
            QtWidgets.QApplication([])

        widget = QtWidgets.QWidget()
        widget.show()
        progress = QtProgress(parent=widget)

        try:
            progress.start()
            progress.end()

        except Exception as e:
            self.fail(e)

    def test_start_custom_title_text(self):

        if not QtWidgets.qApp:
            QtWidgets.QApplication([])

        widget = QtWidgets.QWidget()
        widget.show()
        progress = QtProgress(parent=widget)

        try:
            progress.start(title='Test Bar', text='Doing stuff')

        except Exception as e:
            self.fail(e)

    def test_start_minimal_update(self):

        if not QtWidgets.qApp:
            QtWidgets.QApplication([])

        widget = QtWidgets.QWidget()
        widget.show()
        progress = QtProgress(parent=widget)

        try:
            progress.start()
            progress.update(50)
        except Exception as e:
            self.fail(e)

    def test_start_minimal_update_raising(self):

        widget = QtWidgets.QWidget()
        widget.show()
        progress = QtProgress(parent=widget)

        with self.assertRaises(Exception) as context:
            progress.start()
            progress.update(1000)

    def test_start_minimal_add(self):

        if not QtWidgets.qApp:
            QtWidgets.QApplication([])

        widget = QtWidgets.QWidget()
        widget.show()
        progress = QtProgress(parent=widget)

        try:
            progress.start()
            progress.add(50)
        except Exception as e:
            self.fail(e)

    def test_start_minimal_add_raising(self):

        if not QtWidgets.qApp:
            QtWidgets.QApplication([])

        widget = QtWidgets.QWidget()
        widget.show()
        progress = QtProgress(parent=widget)

        with self.assertRaises(Exception) as context:
            progress.start()
            progress.add(1000)

    def test_start_custom_min_max(self):

        if not QtWidgets.qApp:
            QtWidgets.QApplication([])

        widget = QtWidgets.QWidget()
        widget.show()
        progress = QtProgress(parent=widget)

        try:
            progress.start(min_value=100, max_value=300, init_value=100)
        except Exception as e:
            self.fail(e)

    def test_start_custom_minimal_update(self):

        if not QtWidgets.qApp:
            QtWidgets.QApplication([])

        widget = QtWidgets.QWidget()
        widget.show()
        progress = QtProgress(parent=widget)

        try:
            progress.start(min_value=100, max_value=300, init_value=100)
            progress.update(200)
        except Exception as e:
            self.fail(e)

    def test_start_custom_minimal_update_raising(self):

        if not QtWidgets.qApp:
            QtWidgets.QApplication([])

        widget = QtWidgets.QWidget()
        widget.show()
        progress = QtProgress(parent=widget)

        with self.assertRaises(Exception) as context:
            progress.start(min_value=100, max_value=300)
            progress.update(1000)

    def test_start_custom_minimal_add(self):

        if not QtWidgets.qApp:
            QtWidgets.QApplication([])

        widget = QtWidgets.QWidget()
        widget.show()
        progress = QtProgress(parent=widget)

        try:
            progress.start(min_value=100, max_value=300, init_value=100)
            progress.add(150)
        except Exception as e:
            self.fail(e)

    def test_start_custom_minimal_add_twice(self):

        if not QtWidgets.qApp:
            QtWidgets.QApplication([])

        widget = QtWidgets.QWidget()
        widget.show()
        progress = QtProgress(parent=widget)

        try:
            progress.start(min_value=100, max_value=300, init_value=100)
            progress.add(100)
            progress.add(100)
        except Exception as e:
            self.fail(e)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedManagerQtProgress))
    return s
