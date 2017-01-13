from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
import sys

import time
from PySide import QtGui
from hydroffice.soundspeedmanager.qt_progress import QtProgress


class TestSoundSpeedManagerQtProgress(unittest.TestCase):

    # app = QtGui.QApplication([])

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # @unittest.expectedFailure
    # def test_start_minimal(self):
    #
    #     widget = QtGui.QWidget()
    #     widget.show()
    #     progress = QtProgress(parent=widget)
    #
    #     try:
    #         progress.start()
    #
    #     except Exception as e:
    #         self.fail(e)
    #
    # @unittest.expectedFailure
    # def test_end_minimal(self):
    #
    #     widget = QtGui.QWidget()
    #     widget.show()
    #     progress = QtProgress(parent=widget)
    #
    #     try:
    #         progress.start()
    #         progress.end()
    #
    #     except Exception as e:
    #         self.fail(e)
    #
    # @unittest.expectedFailure
    # def test_start_custom_title_text(self):
    #
    #     widget = QtGui.QWidget()
    #     widget.show()
    #     progress = QtProgress(parent=widget)
    #
    #     try:
    #         progress.start(title='Test Bar', text='Doing stuff')
    #
    #     except Exception as e:
    #         self.fail(e)
    #
    # @unittest.expectedFailure
    # def test_start_minimal_update(self):
    #
    #     widget = QtGui.QWidget()
    #     widget.show()
    #     progress = QtProgress(parent=widget)
    #
    #     try:
    #         progress.start()
    #         progress.update(50)
    #     except Exception as e:
    #         self.fail(e)
    #
    # @unittest.expectedFailure
    # def test_start_minimal_update_raising(self):
    #
    #     widget = QtGui.QWidget()
    #     widget.show()
    #     progress = QtProgress(parent=widget)
    #
    #     with self.assertRaises(Exception) as context:
    #         progress.start()
    #         progress.update(1000)
    #
    # @unittest.expectedFailure
    # def test_start_minimal_add(self):
    #
    #     widget = QtGui.QWidget()
    #     widget.show()
    #     progress = QtProgress(parent=widget)
    #
    #     try:
    #         progress.start()
    #         progress.add(50)
    #     except Exception as e:
    #         self.fail(e)
    #
    # @unittest.expectedFailure
    # def test_start_minimal_add_raising(self):
    #
    #     widget = QtGui.QWidget()
    #     widget.show()
    #     progress = QtProgress(parent=widget)
    #
    #     with self.assertRaises(Exception) as context:
    #         progress.start()
    #         progress.add(1000)
    #
    # @unittest.expectedFailure
    # def test_start_custom_min_max(self):
    #
    #     widget = QtGui.QWidget()
    #     widget.show()
    #     progress = QtProgress(parent=widget)
    #
    #     try:
    #         progress.start(min_value=100, max_value=300)
    #     except Exception as e:
    #         self.fail(e)
    #
    # @unittest.expectedFailure
    # def test_start_custom_minimal_update(self):
    #
    #     widget = QtGui.QWidget()
    #     widget.show()
    #     progress = QtProgress(parent=widget)
    #
    #     try:
    #         progress.start(min_value=100, max_value=300)
    #         progress.update(200)
    #     except Exception as e:
    #         self.fail(e)
    #
    # @unittest.expectedFailure
    # def test_start_custom_minimal_update_raising(self):
    #
    #     widget = QtGui.QWidget()
    #     widget.show()
    #     progress = QtProgress(parent=widget)
    #
    #     with self.assertRaises(Exception) as context:
    #         progress.start(min_value=100, max_value=300)
    #         progress.update(1000)
    #
    # @unittest.expectedFailure
    # def test_start_custom_minimal_add(self):
    #
    #     widget = QtGui.QWidget()
    #     widget.show()
    #     progress = QtProgress(parent=widget)
    #
    #     try:
    #         progress.start(min_value=100, max_value=300)
    #         progress.add(150)
    #     except Exception as e:
    #         self.fail(e)
    #
    # @unittest.expectedFailure
    # def test_start_custom_minimal_add_twice(self):
    #
    #     widget = QtGui.QWidget()
    #     widget.show()
    #     progress = QtProgress(parent=widget)
    #
    #     try:
    #         progress.start(min_value=100, max_value=300)
    #         progress.add(100)
    #         progress.add(100)
    #     except Exception as e:
    #         self.fail(e)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedManagerQtProgress))
    return s
