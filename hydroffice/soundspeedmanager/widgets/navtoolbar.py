from __future__ import absolute_import, division, print_function, unicode_literals

from matplotlib.backends.qt_compat import QtCore, QtGui, QtWidgets, _getSaveFileName, __version__

import os
import logging

from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT
try:
    import matplotlib.backends.qt_editor.figureoptions as figureoptions
except ImportError:
    figureoptions = None

logger = logging.getLogger(__name__)


class NavToolbar(NavigationToolbar2QT):

    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.join(here, os.pardir, 'media')

    def __init__(self, canvas, parent, coordinates=True):
        self.grid_action = None
        self.flag_action = None
        self.unflag_action = None
        self._ids_flag = None
        self._flag_mode = None
        NavigationToolbar2QT.__init__(self, canvas=canvas, parent=parent, coordinates=coordinates)
        self.setIconSize(QtCore.QSize(32, 32))

    def _icon(self, name):
        return QtGui.QIcon(os.path.join(self.media, name))

    def _init_toolbar(self):

        for text, tooltip_text, image_file, callback in self.toolitems:

            if text is None:
                self.addSeparator()

            else:
                a = self.addAction(self._icon(image_file + '.png'), text, getattr(self, callback))
                self._actions[callback] = a
                if callback in ['zoom', 'pan']:
                    a.setCheckable(True)
                if tooltip_text is not None:
                    a.setToolTip(tooltip_text)

                # add edit actions
                if callback == 'zoom':
                    self.flag_action = self.addAction(self._icon("flag.png"), 'Flag', self.flag)
                    self.flag_action.setToolTip('Flag samples')
                    self.flag_action.setCheckable(True)
                    self._actions['flag'] = self.flag_action
                    self.unflag_action = self.addAction(self._icon("unflag.png"), 'Unflag', self.unflag)
                    self.unflag_action.setToolTip('Unflag samples')
                    self.unflag_action.setCheckable(True)
                    self._actions['unflag'] = self.unflag_action

        if figureoptions is not None:
            a = self.addAction(self._icon("qt4_editor_options.png"), 'Customize', self.edit_parameters)
            a.setToolTip('Edit curves line and axes parameters')

        self.addSeparator()
        self.grid_action = self.addAction(self._icon("plot_grid.png"), 'Grid', self.grid_plot)
        self.grid_action.setToolTip('Toggle for grid plot')
        self.grid_action.setCheckable(True)
        self.grid_action.setChecked(True)

        # Add the x,y location widget at the right side of the toolbar
        if self.coordinates:
            self.locLabel = QtWidgets.QLabel("", self)
            self.locLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
            policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Ignored)
            self.locLabel.setSizePolicy(policy)
            labelAction = self.addWidget(self.locLabel)
            labelAction.setVisible(True)

        # reference holder for subplots_adjust window
        self.adj_window = None

    def grid_plot(self):
        grid_flag = self.grid_action.isChecked()
        for a in self.canvas.figure.get_axes():
            a.grid(grid_flag)
        self.dynamic_update()

    def _update_buttons_checked(self):
        # sync button checkstates to match active mode
        self._actions['pan'].setChecked(self._active == 'PAN')
        self._actions['zoom'].setChecked(self._active == 'ZOOM')
        self._actions['flag'].setChecked(self._active == 'FLAG')
        self._actions['unflag'].setChecked(self._active == 'UNFLAG')

    def flag(self):
        if self._active == 'FLAG':
            self._active = None
        else:
            self._active = 'FLAG'

        if self._idPress is not None:
            self._idPress = self.canvas.mpl_disconnect(self._idPress)
            self.mode = ''

        if self._idRelease is not None:
            self._idRelease = self.canvas.mpl_disconnect(self._idRelease)
            self.mode = ''

        if self._active:
            self._idPress = self.canvas.mpl_connect('button_press_event', self.press_flag)
            self._idRelease = self.canvas.mpl_connect('button_release_event', self.release_flag)
            self.mode = "flag"
            self.canvas.widgetlock(self)
        else:
            self.canvas.widgetlock.release(self)

        for a in self.canvas.figure.get_axes():
            a.set_navigate_mode(self._active)

        self.set_message(self.mode)
        self._update_buttons_checked()

    def unflag(self):
        if self._active == 'UNFLAG':
            self._active = None
        else:
            self._active = 'UNFLAG'

        if self._idPress is not None:
            self._idPress = self.canvas.mpl_disconnect(self._idPress)
            self.mode = ''

        if self._idRelease is not None:
            self._idRelease = self.canvas.mpl_disconnect(self._idRelease)
            self.mode = ''

        if self._active:
            self._idPress = self.canvas.mpl_connect('button_press_event', self.press_unflag)
            self._idRelease = self.canvas.mpl_connect('button_release_event', self.release_unflag)
            self.mode = "unflag"
            self.canvas.widgetlock(self)
        else:
            self.canvas.widgetlock.release(self)

        for a in self.canvas.figure.get_axes():
            a.set_navigate_mode(self._active)

        self.set_message(self.mode)
        self._update_buttons_checked()

    def press_flag(self, event):
        if event.button == 1:
            self._button_pressed = 1
        elif event.button == 3:
            self._button_pressed = 3
        else:
            self._button_pressed = None
            return

        x, y = event.x, event.y

        # push the current view to define home if stack is empty
        if self._views.empty():
            self.push_current()

        self._xypress = []
        for i, a in enumerate(self.canvas.figure.get_axes()):
            if (x is not None and y is not None and
                    a.in_axes(event) and  # if the given mouse event (in display coords) in axes
                    a.get_navigate() and  # whether the axes responds to navigation commands
                    a.can_zoom()):  # if this axes supports the zoom box button functionality.
                self._xypress.append((x, y, a, i, a._get_view()))

        id1 = self.canvas.mpl_connect('motion_notify_event', self.drag_flag)
        id2 = self.canvas.mpl_connect('key_press_event', self._switch_on_flag_mode)
        id3 = self.canvas.mpl_connect('key_release_event', self._switch_off_flag_mode)

        self._ids_flag = id1, id2, id3
        self._flag_mode = event.key

        self.press(event)

    def _switch_on_flag_mode(self, event):
        self._flag_mode = event.key
        self.mouse_move(event)

    def _switch_off_flag_mode(self, event):
        self._flag_mode = None
        self.mouse_move(event)

    def drag_flag(self, event):
        """the drag callback in flag mode"""

        if self._xypress:
            x, y = event.x, event.y
            lastx, lasty, a, ind, view = self._xypress[0]

            # adjust x, last, y, last
            x1, y1, x2, y2 = a.bbox.extents
            x, lastx = max(min(x, lastx), x1), min(max(x, lastx), x2)
            y, lasty = max(min(y, lasty), y1), min(max(y, lasty), y2)

            if self._flag_mode == "x":
                x1, y1, x2, y2 = a.bbox.extents
                y, lasty = y1, y2
            elif self._flag_mode == "y":
                x1, y1, x2, y2 = a.bbox.extents
                x, lastx = x1, x2

            self.draw_rubberband(event, x, y, lastx, lasty)

    def release_flag(self, event):
        if self._button_pressed is None:
            return

        for flag_id in self._ids_flag:
            self.canvas.mpl_disconnect(flag_id)
        self._ids_flag = []

        self.remove_rubberband()

        if not self._xypress:
            return

        self.draw()
        self._xypress = None
        self._button_pressed = None
        self._flag_mode = None
        self.release(event)

    def press_unflag(self, event):
        if event.button == 1:
            self._button_pressed = 1
        elif event.button == 3:
            self._button_pressed = 3
        else:
            self._button_pressed = None
            return

        x, y = event.x, event.y

        # push the current view to define home if stack is empty
        if self._views.empty():
            self.push_current()

        print(self._button_pressed, x, y)

        self.press(event)

    def release_unflag(self, event):
        if self._button_pressed is None:
            return
        print("released")
