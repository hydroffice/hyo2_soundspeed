from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import os
import numpy as np
from PySide import QtGui
from PySide import QtCore
import matplotlib
matplotlib.rcParams['backend.qt4'] = 'PySide'
matplotlib.use('Qt4Agg')

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class MatplotlibExample(QtGui.QMainWindow):
    """HOW TO EMBED MATPLOTLIB WITH PYSIDE"""

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.abspath(os.path.join(here, "media"))

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        self.x = None
        self.y = None
        self.last_idx = None

        # matplotlib stuff
        self.dpi = 200
        self.figure = None
        self.canvas = None
        self.axes = None
        self.mpl_toolbar = None

        # PySide stuff
        self.main_frame = None
        self.file_menu = None
        self.help_menu = None
        self.textbox = None
        self.draw_button = None
        self.grid_ck = None
        self.slider = None

        # create ui
        self.setWindowTitle('PySide with matplotlib')
        self.center()
        self.create_menu()
        self.create_main_frame()
        self.on_draw()

    def create_menu(self):
        """Menu creation"""
        # file menu
        self.file_menu = self.menuBar().addMenu("&File")
        load_file_action = self.create_action("&Save plot", shortcut="Ctrl+S", slot=self.save_plot, tip="Save the plot")
        self.file_menu.addAction(load_file_action)
        quit_action = self.create_action("&Quit", slot=self.close, shortcut="Ctrl+Q", tip="Close the app")
        self.file_menu.addAction(quit_action)
        # help menu
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", shortcut='F1', slot=self.on_about, tip='About this app')
        self.help_menu.addAction(about_action)

    def create_action(self, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal="triggered()"):
        """Helper function to create an action"""
        action = QtGui.QAction(text, self)
        if icon is not None:
            action.setIcon(QtGui.QIcon(os.path.join(self.media, "%s.png" % icon)))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
        if slot is not None:
            action.triggered.connect(slot)
        if checkable:
            action.setCheckable(True)
        return action

    def create_main_frame(self):
        self.main_frame = QtGui.QWidget()

        # Create Matplotlib figure and canvas
        self.figure = Figure((6.0, 4.0), dpi=self.dpi)  # inches, dots-per-inch
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self.main_frame)
        self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)  # key for press events!!!
        self.canvas.setFocus()
        # we use add_subplot (so that the subplot configuration tool in the navigation toolbar works)
        self.axes = self.figure.add_subplot(111)
        # Bind events
        self.canvas.mpl_connect('pick_event', self.on_pick)
        self.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.canvas.mpl_connect('key_press_event', self.on_key_press)
        # Create the navigation toolbar, tied to the canvas
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        # other GUI controls
        self.textbox = QtGui.QLineEdit()
        self.textbox.setMinimumWidth(200)
        self.textbox.editingFinished.connect(self.on_draw)
        self.textbox.setText('1 3 2 6 3 2 4')
        self.draw_button = QtGui.QPushButton("&Draw")
        self.draw_button.clicked.connect(self.on_draw)
        # grid
        self.grid_ck = QtGui.QCheckBox("Show &Grid")
        self.grid_ck.setChecked(False)
        self.grid_ck.stateChanged.connect(self.on_draw)
        # slider
        slider_label = QtGui.QLabel('Plot width (%):')
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(1, 100)
        self.slider.setValue(20)
        self.slider.setTracking(True)
        self.slider.setTickPosition(QtGui.QSlider.TicksBothSides)
        self.slider.valueChanged.connect(self.on_draw)

        # layouts
        hbox = QtGui.QHBoxLayout()
        for w in [self.textbox, self.draw_button, self.grid_ck, slider_label, self.slider]:
            hbox.addWidget(w)
            hbox.setAlignment(w, QtCore.Qt.AlignVCenter)
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def save_plot(self):
        flt = "PNG (*.png)|*.png"
        path = QtGui.QFileDialog.getSaveFileName(self, 'Save file', '', flt)
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)

    def on_about(self):
        msg = """PySide with matplotlib:
- navigation bar
- grid toggle
- interactivity ('Draw' button, slider, click on bar)
- plot saving
"""
        QtGui.QMessageBox.about(self, "About the demo", msg.strip())

    def on_pick(self, event):
        """Manage pick event"""
        if event.ind is None:
            return

        m_x = event.mouseevent.xdata
        m_y = event.mouseevent.ydata

        msg = "Click event:\n"
        msg += "ind: %s\n" % event.ind
        msg += "mouse.xdata/ydata: %s, %s\n" % (m_x, m_y)  # click location
        msg += "xydata:%s\n" % event.artist.get_xydata()

        print(msg)

        # in case of multiple selection
        distances = np.hypot(m_x - self.x[event.ind], m_y - self.y[event.ind])
        idx_min = distances.argmin()
        self.last_idx = event.ind[idx_min]

        self.update_plot()

    def on_key_press(self, event):
        """Manage press event"""
        print("pressed key: %s" % event.key)

    def on_mouse_press(self, event):
        """Manage press event"""
        print("pressed mouse: %s" % event.key)

    def on_draw(self):
        """Redraws the figure"""
        self.y = [int(d) for d in self.textbox.text().split()]
        self.x = range(len(self.y))

        # clear the axes and redraw
        self.axes.clear()
        self.axes.grid(self.grid_ck.isChecked())
        self.axes.plot(self.x, self.y, linewidth=self.slider.value() / 100.0, alpha=0.5, picker=3)
        self.canvas.draw()

    def update_plot(self):
        if self.last_idx is None:
            return
        print("update")

        self.on_draw()
        self.axes.text(self.x[self.last_idx], self.y[self.last_idx],
                       'x=%1.3f\ny=%1.3f' % (self.x[self.last_idx], self.y[self.last_idx]), va='top')
        self.canvas.draw()


def main():
    app = QtGui.QApplication(sys.argv)
    form = MatplotlibExample()
    form.show()
    app.exec_()


if __name__ == "__main__":
    main()
