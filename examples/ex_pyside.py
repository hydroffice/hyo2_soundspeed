import sys
from PySide import QtGui
import matplotlib
matplotlib.rcParams['backend.qt4'] = 'PySide'
matplotlib.use('Qt4Agg')
import matplotlib.figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar


class PrettyWidget(QtGui.QWidget):
    def __init__(self):
        super(PrettyWidget, self).__init__()
        self.setGeometry(100, 100, 800, 600)
        self.center()
        self.setWindowTitle('PySide')

        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        self.figure = matplotlib.figure.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.mpl_connect('pick_event', self.on_pick)
        self.toolbar = NavigationToolbar(self.canvas, self)
        vbox.addWidget(self.toolbar)
        vbox.addWidget(self.canvas)

        # buttons
        hbox = QtGui.QHBoxLayout()
        vbox.addLayout(hbox)
        btn1 = QtGui.QPushButton('Plot 1 ')
        btn1.resize(btn1.sizeHint())
        btn1.clicked.connect(self.plot1)
        hbox.addWidget(btn1)
        btn2 = QtGui.QPushButton('Plot 2 ')
        btn2.resize(btn2.sizeHint())
        btn2.clicked.connect(self.plot2)
        hbox.addWidget(btn2)

        self.show()

    def plot1(self):
        self.figure.clf()
        ax1 = self.figure.add_subplot(211)
        x1 = [i for i in range(100)]
        y1 = [i**0.5 for i in x1]
        ax1.plot(x1, y1, 'b.-')

        ax2 = self.figure.add_subplot(212)
        x2 = [i for i in range(100)]
        y2 = [i for i in x2]
        ax2.plot(x2, y2, 'b.-')
        self.canvas.draw_idle()

    def plot2(self):
        self.figure.clf()
        ax3 = self.figure.add_subplot(111)
        x = [i for i in range(100)]
        y = [i**0.5 for i in x]
        ax3.plot(x, y, 'r.-')
        ax3.set_title('Square Root Plot')
        self.canvas.draw_idle()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def on_pick(self, event):
        box_points = event.artist.get_bbox().get_points()
        msg = "You've clicked on a bar with coords:\n %s" % box_points
        QtGui.QMessageBox.information(self, "Click!", msg)

app = QtGui.QApplication(sys.argv)
app.aboutToQuit.connect(app.deleteLater)
GUI = PrettyWidget()
sys.exit(app.exec_())