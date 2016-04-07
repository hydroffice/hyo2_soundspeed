from __future__ import absolute_import, division, print_function, unicode_literals

from matplotlib.backends.qt_compat import QtCore, QtGui, QtWidgets, _getSaveFileName, __version__

import numpy as np
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

    def __init__(self, canvas, parent, plot_win, prj, coordinates=True):
        self.plot_win = plot_win
        self.prj = prj
        self.grid_action = None
        self.flag_action = None
        self.unflag_action = None
        self._ids_flag = None
        self._flag_mode = None
        self._flag_start = None
        self._flag_end = None
        NavigationToolbar2QT.__init__(self, canvas=canvas, parent=parent, coordinates=coordinates)
        self.setIconSize(QtCore.QSize(32, 32))

    def _icon(self, name):
        return QtGui.QIcon(os.path.join(self.media, name))

    def _init_toolbar(self):

        for text, tooltip_text, image_file, callback in self.toolitems:
            if text == 'Home':
                home_action = self.addAction(self._icon('home.png'), 'Home', self.home)
                home_action.setToolTip('Reset view')
                self._actions['home'] = home_action
            elif text == 'Back':
                back_action = self.addAction(self._icon('back.png'), 'Back', self.back)
                back_action.setToolTip('Previous view')
                self._actions['back'] = back_action
            elif text == 'Forward':
                forward_action = self.addAction(self._icon('forward.png'), 'Forward', self.forward)
                forward_action.setToolTip('Next view')
                self._actions['forward'] = forward_action
            elif text == 'Pan':
                move_action = self.addAction(self._icon('move.png'), 'Move', self.pan)
                move_action.setToolTip('Pan/scale (left/right button)')
                move_action.setCheckable(True)
                self._actions['pan'] = move_action
            elif text == 'Zoom':
                zoom_action = self.addAction(self._icon('zoom_to_rect.png'), 'Zoom', self.zoom)
                zoom_action.setToolTip('Zoom in/out (left/right button)')
                zoom_action.setCheckable(True)
                self._actions['zoom'] = zoom_action
                self.flag_action = self.addAction(self._icon("flag.png"), 'Flag', self.flag)
                self.flag_action.setToolTip('Flag samples')
                self.flag_action.setCheckable(True)
                self._actions['flag'] = self.flag_action
                self.unflag_action = self.addAction(self._icon("unflag.png"), 'Unflag', self.unflag)
                self.unflag_action.setToolTip('Unflag samples')
                self.unflag_action.setCheckable(True)
                self._actions['unflag'] = self.unflag_action
            elif text == 'Subplots':
                self.grid_action = self.addAction(self._icon("plot_grid.png"), 'Grid', self.grid_plot)
                self.grid_action.setToolTip('Toggle grids')
                self.grid_action.setCheckable(True)
                self.grid_action.setChecked(True)
                self._actions['grid'] = self.grid_action
                subplots_action = self.addAction(self._icon('subplots.png'), 'Subplots', self.configure_subplots)
                subplots_action.setToolTip('Configure subplots')
                self._actions['subplots'] = subplots_action
                if figureoptions is not None:
                    a = self.addAction(self._icon("qt4_editor_options.png"), 'Customize', self.edit_parameters)
                    a.setToolTip('Edit curves line and axes parameters')
            elif text == 'Save':
                self.addSeparator()
                save_action = self.addAction(self._icon('filesave.png'), 'Save', self.save_figure)
                save_action.setToolTip('Save the figure')
                self._actions['save'] = save_action
            elif text is None:
                self.addSeparator()
            else:
                a = self.addAction(self._icon(image_file + '.png'), text, getattr(self, callback))
                self._actions[callback] = a
                if tooltip_text is not None:
                    a.setToolTip(tooltip_text)

        # Add the x,y location widget at the right side of the toolbar
        if self.coordinates:
            self.locLabel = QtWidgets.QLabel("", self)
            self.locLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
            policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Ignored)
            self.locLabel.setSizePolicy(policy)
            label_action = self.addWidget(self.locLabel)
            label_action.setVisible(True)

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
        """Mouse press callback for flag"""

        # store the pressed button
        if event.button == 1:  # left
            self._button_pressed = 1
        elif event.button == 3:  # right
            self._button_pressed = 3
        else:  # nothing and return for middle
            self._button_pressed = None
            return
        logger.debug("FLAG > press > button #%s" % self._button_pressed)

        x, y = event.x, event.y  # cursor position in pixel
        xd, yd = event.xdata, event.ydata  # cursor position in data coords
        logger.debug("FLAG > press > loc (%.3f,%.3f)(%.3f,%.3f)" % (x, y, xd, yd))

        self._xypress = []  # clear past press
        self._flag_start = None  # clear past data
        self._flag_end = None  # clear past data
        for i, ax in enumerate(self.canvas.figure.get_axes()):
            if ((x is not None) and (y is not None) and
                    ax.in_axes(event) and  # if the given mouse event (in display coords) in axes
                    ax.get_navigate() and  # whether the axes responds to navigation commands
                    ax.can_zoom()):  # if this axes supports the zoom box button functionality.
                self._xypress.append((x, y, ax, i, ax._get_view()))
                self._flag_start = (xd, yd, ax)
                logger.debug("FLAG > press > axes %s" % ax.get_label())

        # connect drag/press/release events
        id1 = self.canvas.mpl_connect('motion_notify_event', self.drag_flag)
        id2 = self.canvas.mpl_connect('key_press_event', self._switch_on_flag_mode)
        id3 = self.canvas.mpl_connect('key_release_event', self._switch_off_flag_mode)
        self._ids_flag = id1, id2, id3
        self._flag_mode = event.key
        logger.debug("FLAG > press > key: %s" % self._flag_mode)

        # pass the event
        self.press(event)

    def _switch_on_flag_mode(self, event):
        """optional key-press switch in flagging mode (used for x- and y- selections)"""

        self._flag_mode = event.key
        if self._flag_mode == "x":
            logger.debug("FLAG > switch > x-selection: ON")
        elif self._flag_mode == "y":
            logger.debug("FLAG > switch > y-selection: ON")

        self.mouse_move(event)

    def _switch_off_flag_mode(self, event):
        """optional key-press switch in flagging mode (used for x- and y- selections)"""

        self._flag_mode = None
        if event.key == "x":
            logger.debug("FLAG > switch > x-selection: OFF")
        elif event.key == "y":
            logger.debug("FLAG > switch > y-selection: OFF")

        self.mouse_move(event)

    def drag_flag(self, event):
        """the mouse-motion dragging callback in flaggin mode"""

        if not self._xypress:  # return if missing valid initial click
            return

        xd, yd = event.xdata, event.ydata
        if (xd is not None) and (yd is not None):
            self._flag_end = (xd, yd)

        x, y = event.x, event.y
        last_x, last_y, ax, _, _ = self._xypress[0]

        # adjust x, last, y, last
        x1, y1, x2, y2 = ax.bbox.extents
        x, last_x = max(min(x, last_x), x1), min(max(x, last_x), x2)
        y, last_y = max(min(y, last_y), y1), min(max(y, last_y), y2)
        # key-specific mode
        if self._flag_mode == "x":  # x-selection
            x1, y1, x2, y2 = ax.bbox.extents
            y, last_y = y1, y2
        elif self._flag_mode == "y":  # y-selection
            x1, y1, x2, y2 = ax.bbox.extents
            x, last_x = x1, x2

        # logger.debug("FLAG > drag > (%.3f, %.3f)(%.3f, %.3f)" % (x, y, last_x, last_y))
        self.draw_rubberband(event, x, y, last_x, last_y)

    def release_flag(self, event):
        """release mouse button callback in flagging mode"""
        # disconnect callbacks
        for flag_id in self._ids_flag:
            self.canvas.mpl_disconnect(flag_id)
        self._ids_flag = []
        # remove flagging area
        self.remove_rubberband()

        if not self._xypress:
            return

        # retrieve valid initial and ending points
        xd_start, yd_start, ax = self._flag_start
        xd_end, yd_end = event.xdata, event.ydata
        if (xd_end is None) or (yd_end is None):
            if self._flag_end is None:  # nothing to do.. the drag was to small/invalid
                return
            xd_end, yd_end = self._flag_end
        # calculate min/max
        min_xd, max_xd = min(xd_start, xd_end), max(xd_start, xd_end)
        min_yd, max_yd = min(yd_start, yd_end), max(yd_start, yd_end)
        logger.debug("FLAG > x: %.3f %.3f, y: %.3f %.3f" % (min_xd, max_xd, min_yd, max_yd))
        yd2, yd1 = ax.get_ylim()  # bottom-to-top and the y-axis is reverted !!
        xd1, xd2 = ax.get_xlim()  # left-to-right
        min_xd, max_xd = max(min_xd, xd1), min(max_xd, xd2)
        min_yd, max_yd = max(min_yd, yd1), min(max_yd, yd2)
        logger.debug("FLAG > x: %.3f %.3f, y: %.3f %.3f" % (min_xd, max_xd, min_yd, max_yd))

        selected = np.where(np.logical_and(self.prj.cur.proc.depth > min_yd,
                                           self.prj.cur.proc.depth < max_yd))
        print(selected)
        logger.debug(ax.get_label())
        self.plot_win.speed_valid.set_xdata(self.prj.cur.proc.speed[selected])
        self.plot_win.speed_valid.set_ydata(self.prj.cur.proc.depth[selected])

        self.draw()
        self._xypress = None
        self._flag_start = None
        self._flag_end = None
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
