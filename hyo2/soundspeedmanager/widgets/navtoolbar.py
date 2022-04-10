from matplotlib.backends.qt_compat import QtCore, QtGui, QtWidgets

import os
import logging
from collections import namedtuple
from enum import Enum

import numpy as np
import matplotlib
from matplotlib import rc_context, cbook
# noinspection PyProtectedMember
from matplotlib.backend_bases import _Mode, MouseButton
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
# noinspection PyProtectedMember
from matplotlib.backends.qt_compat import _devicePixelRatioF, _setDevicePixelRatio
from matplotlib.backend_bases import cursors

from hyo2.soundspeed.profile.dicts import Dicts

logger = logging.getLogger(__name__)


class Sample:
    def __init__(self):
        self.depth = None
        self.speed = None
        self.temp = None
        self.sal = None


class NavToolbar(NavigationToolbar2QT):
    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded
    media = os.path.abspath(os.path.join(here, os.pardir, 'media'))
    font_size = 6
    rc_context = {
        'font.family': 'sans-serif',
        'font.sans-serif': ['Tahoma', 'Bitstream Vera Sans', 'Lucida Grande', 'Verdana'],
        'font.size': font_size,
        'figure.titlesize': font_size + 1,
        'axes.labelsize': font_size,
        'legend.fontsize': font_size,
        'xtick.labelsize': font_size - 3,
        'ytick.labelsize': font_size - 3,
        'axes.linewidth': 0.5,
        'axes.xmargin': 0.01,
        'axes.ymargin': 0.01,
        'grid.alpha': 0.2,
    }

    def __init__(self, canvas, parent, plot_win, prj, coordinates=True):

        self.plot_win = plot_win
        self.prj = prj

        self._active = None
        self._xypress = None
        self._ids_flag = None
        self._flag_mode = None
        self._flag_start = None
        self._flag_end = None
        self.insert_sample = None

        NavigationToolbar2QT.toolitems = (
            ('Home', 'Reset view', 'home', 'home'),
            ('Back', 'Previous view', 'back', 'back'),
            ('Forward', 'Next view', 'forward', 'forward'),
            (None, None, None, None),
            ('Pan', 'Pan on plot', 'move', 'pan'),
            ('Scale', 'Scale plot', 'scale', 'scale'),
            ('Zoom in', 'Zoom in area', 'zoomin', 'zoom_in'),
            ('Zoom out', 'Zoom out area', 'zoomout', 'zoom_out'),
            ('Flag', 'Flag samples', 'flag', 'flag'),
            ('Unflag', 'Unflag samples', 'unflag', 'unflag'),
            ('Insert', 'Insert samples', 'insert', 'insert'),
            (None, None, None, None),
            ('Flagged', 'Show/hide flagged', 'flagged', 'flagged_plot'),
            ('Grid', 'Toggle grids', 'plot_grid', 'grid_plot'),
            ('Legend', 'Toggle legends', 'plot_legend', 'legend_plot'),
            ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
            ("Customize", "Edit axis, curve and image parameters",
             "qt5_editor_options", "edit_parameters"),
            (None, None, None, None),
            ('Save', 'Save the figure', 'filesave', 'save_figure'),
          )
        super().__init__(canvas=canvas, parent=parent, coordinates=coordinates)
        self.setIconSize(QtCore.QSize(24, 24))

        # set checkable buttons
        self._actions['scale'].setCheckable(True)
        self._actions['zoom_in'].setCheckable(True)
        self._actions['zoom_out'].setCheckable(True)
        self._actions['flag'].setCheckable(True)
        self._actions['unflag'].setCheckable(True)
        self._actions['insert'].setCheckable(True)
        self._actions['flagged_plot'].setCheckable(True)
        self._actions['grid_plot'].setCheckable(True)
        self._actions['legend_plot'].setCheckable(True)
        self._actions['legend_plot'].setChecked(False)

        self.canvas.mpl_connect('button_press_event', self.press)
        self.canvas.mpl_connect('button_release_event', self.release)

        # Add the x,y location widget at the right side of the toolbar
        self.mon_label = None
        if self.coordinates:
            frame = QtWidgets.QFrame()
            # policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Ignored)
            # frame.setSizePolicy(policy)
            self.addWidget(frame)
            hbox = QtWidgets.QHBoxLayout()
            frame.setLayout(hbox)
            hbox.addStretch()
            vbox = QtWidgets.QVBoxLayout()
            hbox.addLayout(vbox)
            # - location label
            self.locLabel = QtWidgets.QLabel("", self)
            self.locLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
            vbox.addWidget(self.locLabel)
            # - insert label
            self.mon_label = QtWidgets.QLabel("", self)
            self.mon_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
            self.mon_label.setStyleSheet("QLabel { color : red; }")
            vbox.addWidget(self.mon_label)
            # vbox.addStretch()

    def reset(self):
        self._active = None
        self._xypress = None
        self._ids_flag = None
        self._flag_mode = None
        self._flag_start = None
        self._flag_end = None
        self.insert_sample = None

    def _icon(self, name):
        # Modified to use local icons
        icon_path = os.path.join(self.media, name)
        if not os.path.exists(icon_path):
            # noinspection PyProtectedMember
            icon_path = str(cbook._get_data_path('images', name))
            logger.warning("using icon at %s" % icon_path)
        pm = QtGui.QPixmap(icon_path)
        _setDevicePixelRatio(pm, _devicePixelRatioF(self))
        if self.palette().color(self.backgroundRole()).value() < 128:
            icon_color = self.palette().color(self.foregroundRole())
            mask = pm.createMaskFromColor(
                QtGui.QColor('black'),
                _enum("QtCore.Qt.MaskMode").MaskOutColor)
            pm.fill(icon_color)
            pm.setMask(mask)
        return QtGui.QIcon(pm)

    def _active_button(self):
        # sync button checkstates to match active mode
        logger.debug("Mode: %s" % self._active)
        self._actions['pan'].setChecked(self._active == 'PAN')
        self._actions['scale'].setChecked(self._active == 'SCALE')
        self._actions['zoom_in'].setChecked(self._active == 'ZOOM_IN')
        self._actions['zoom_out'].setChecked(self._active == 'ZOOM_OUT')
        self._actions['flag'].setChecked(self._active == 'FLAG')
        self._actions['unflag'].setChecked(self._active == 'UNFLAG')
        self._actions['insert'].setChecked(self._active == 'INSERT')

    # ### actions ###

    def press(self, event):
        # print("press", event.button)
        if event.button == 3:
            menu = QtWidgets.QMenu(self)
            menu.addAction(self._actions['home'])
            menu.addSeparator()
            menu.addAction(self._actions['pan'])
            menu.addAction(self._actions['scale'])
            menu.addAction(self._actions['zoom_in'])
            menu.addAction(self._actions['zoom_out'])
            menu.addSeparator()
            menu.addAction(self._actions['flag'])
            menu.addAction(self._actions['unflag'])
            menu.addAction(self._actions['insert'])
            menu.popup(QtGui.QCursor.pos())
            menu.exec_()

    def release(self, event):
        # print("release", event.button)
        pass

    # --- mouse movements ---

    def mouse_move(self, event):
        self._update_cursor(event)

        if event.inaxes and event.inaxes.get_navigate():
            plt_label = event.inaxes.get_label()
            try:
                s = "d:%.2f" % event.ydata
                if plt_label == "speed":
                    s += ", vs:%.2f" % event.xdata
                elif plt_label == "temp":
                    s += ", t:%.2f" % event.xdata
                elif plt_label == "sal":
                    s += ", s:%.2f" % event.xdata
            except (ValueError, OverflowError):
                if self._active:
                    self.set_message('%s' % self._active)
                else:
                    self.set_message('')
                return

            artists = [a for a in event.inaxes.get_children() if a.contains(event)]
            if artists:
                a = max(enumerate(artists), key=lambda x: x[1].zorder)[1]
                if a is not event.inaxes.patch:
                    data = a.get_cursor_data(event)
                    if data is not None:
                        s += '[%s]' % a.format_cursor_data(data)

            if self._active:
                self.set_message('%s | %s' % (s, self._active.lower()))
            else:
                self.set_message(s)

            if self._active == 'INSERT':
                # logger.debug("insert mode")
                msg = str()
                if self.insert_sample:  # we are adding a 2-step sample

                    if plt_label == "speed":
                        msg += "1-step insert [d:%.2f" % event.ydata
                    else:
                        if not self.insert_sample.temp:
                            msg += "now set temp [d:%.2f" % self.insert_sample.depth
                        elif not self.insert_sample.sal:
                            msg += "now set sal [d:%.2f" % self.insert_sample.depth

                    if self.insert_sample.speed:
                        msg += ", vs:%.2f" % self.insert_sample.speed
                    else:
                        if plt_label == "speed":
                            msg += ", vs:%.2f" % event.xdata
                        else:
                            msg += ", vs:*"

                    if self.insert_sample.temp:
                        msg += ", t:%.2f" % self.insert_sample.temp
                    else:
                        if plt_label == "temp":
                            msg += ", t:%.2f" % event.xdata
                        else:
                            msg += ", t:*"

                    if self.insert_sample.sal:
                        msg += ", s:%.2f]" % self.insert_sample.sal
                    else:
                        if plt_label == "sal":
                            msg += ", s:%.2f]" % event.xdata
                        else:
                            msg += ", s:*]"

                else:  # we don't know if the user will select a 2-step insertion or directly a sound speed value

                    if plt_label == "speed":
                        msg += "1-step insert [d:%.2f" % event.ydata
                    else:
                        msg += "2-step insert [d:%.2f" % event.ydata

                    if plt_label == "speed":
                        msg += ", vs:%.2f" % event.xdata
                    else:
                        msg += ", vs:*"

                    if plt_label == "temp":
                        msg += ", t:%.2f" % event.xdata
                    else:
                        msg += ", t:*"

                    if plt_label == "sal":
                        msg += ", s:%.2f]" % event.xdata
                    else:
                        msg += ", s:*]"

                self.mon_label.setText(msg)

            else:
                self.mon_label.setText('')

        else:
            if self.mode:
                self.set_message('%s' % self.mode)

            else:
                self.set_message('')

            self.mon_label.setText('')

    def _update_cursor(self, event):
        """Set cursor by mode"""

        if not event.inaxes or not self._active:
            if self._lastCursor != cursors.POINTER:
                self.set_cursor(cursors.POINTER)
                self._lastCursor = cursors.POINTER
        else:
            if (self._active == 'ZOOM_IN') or (self._active == 'ZOOM_OUT') or (self._active == 'INSERT'):
                if self._lastCursor != cursors.SELECT_REGION:
                    self.set_cursor(cursors.SELECT_REGION)
                    self._lastCursor = cursors.SELECT_REGION

            elif (self._active == 'PAN') and (self._lastCursor != cursors.HAND):
                if self._lastCursor != cursors.HAND:
                    self.set_cursor(cursors.HAND)
                    self._lastCursor = cursors.HAND

            elif (self._active == 'SCALE') and (self._lastCursor != cursors.MOVE):
                self.set_cursor(cursors.MOVE)
                self._lastCursor = cursors.MOVE

    # --- pan ---

    def pan(self, *args):
        if self._active == "SCALE":
            super().pan(*args)
        super().pan(*args)

        if self.mode != _Mode.PAN:
            self._active = None
        else:
            self._active = "PAN"

        self._active_button()

    def scale(self, *args):
        """Activate the scale tool"""
        if self._active == "PAN":
            super().pan(*args)
        super().pan(*args)

        if self.mode != _Mode.PAN:
            self._active = None
        else:
            self._active = "SCALE"

        self._active_button()

    def press_pan(self, event):
        # logger.debug("Press pan")
        if event.button != MouseButton.LEFT:
            return
        if self._active == "PAN":
            super().press_pan(event=event)
        elif self._active == "SCALE":
            self.press_scale(event=event)

    def drag_pan(self, event):
        # logger.debug("Drag pan")
        if self._active == "PAN":
            super().drag_pan(event=event)
        elif self._active == "SCALE":
            self.drag_scale(event=event)

    def release_pan(self, event):
        # logger.debug("Release pan")
        if self._active == "PAN":
            super().release_pan(event=event)
        elif self._active == "SCALE":
            super().release_pan(event=event)

    def press_scale(self, event):
        # logger.debug("Press scale")
        if (event.button not in [MouseButton.LEFT, MouseButton.RIGHT]
                or event.x is None or event.y is None):
            return
        axes = [a for a in self.canvas.figure.get_axes()
                if a.in_axes(event) and a.get_navigate() and a.can_pan()]
        if not axes:
            return
        if self._nav_stack() is None:
            self.push_current()  # set the home button to this view
        for ax in axes:
            # MODIFIED for passing MouseButton.RIGHT
            ax.start_pan(event.x, event.y, MouseButton.RIGHT)
        self.canvas.mpl_disconnect(self._id_drag)
        id_drag = self.canvas.mpl_connect("motion_notify_event", self.drag_pan)
        self._pan_info = self._PanInfo(
            button=event.button, axes=axes, cid=id_drag)

    def drag_scale(self, event):
        # logger.debug("Drag scale")
        for ax in self._pan_info.axes:
            # Using the recorded button at the press is safer than the current
            # button, as multiple buttons can get pressed during motion.
            # MODIFIED for passing MouseButton.RIGHT
            ax.drag_pan(MouseButton.RIGHT, event.key, event.x, event.y)
        self.canvas.draw_idle()

    # --- zoom in/out ---

    def zoom_in(self, *args):
        if self._active == "ZOOM_OUT":
            super().zoom(*args)
        super().zoom(*args)

        if self.mode != _Mode.ZOOM:
            self._active = None
        else:
            self._active = "ZOOM_IN"

        self._active_button()

    def zoom_out(self, *args):
        if self._active == "ZOOM_IN":
            super().zoom(*args)
        super().zoom(*args)

        if self.mode != _Mode.ZOOM:
            self._active = None
        else:
            self._active = "ZOOM_OUT"

        self._active_button()

    def press_zoom(self, event):
        if self._active == "ZOOM_IN":
            super().press_zoom(event=event)
        elif self._active == "ZOOM_OUT":
            super().press_zoom(event=event)
            self._zoom_info = self._ZoomInfo(direction="out", start_xy=self._zoom_info.start_xy,
                                             axes=self._zoom_info.axes, cid=self._zoom_info.cid,
                                             cbar=self._zoom_info.cbar)

    # --- flag ---

    def flag(self):
        self.mode = _Mode.NONE
        if self._active == 'FLAG':
            self._active = None
            if self._id_press:
                self.canvas.mpl_disconnect(self._id_press)
            if self._id_release:
                self.canvas.mpl_disconnect(self._id_release)
            self.canvas.widgetlock.release(self)
        else:
            self._active = 'FLAG'
            if self._id_press:
                self.canvas.mpl_disconnect(self._id_press)
            self._id_press = self.canvas.mpl_connect('button_press_event', self.press_flag)
            if self._id_release:
                self.canvas.mpl_disconnect(self._id_release)
            self._id_release = self.canvas.mpl_connect('button_release_event', self.release_flag)
            self.canvas.widgetlock(self)

        self.set_message(self._active)
        self._update_buttons_checked()
        self._active_button()

    def press_flag(self, event):
        """Mouse press callback for flag"""

        # store the pressed button
        if event.button != MouseButton.LEFT:  # left
            return
        # logger.debug("FLAG > press > button #%s" % event.button)

        x, y = event.x, event.y  # cursor position in pixel
        xd, yd = event.xdata, event.ydata  # cursor position in data coords
        # logger.debug("FLAG > press > loc (%.3f,%.3f)(%.3f,%.3f)" % (x, y, xd, yd))

        self._xypress = []  # clear past press
        self._flag_start = None  # clear past data
        self._flag_end = None  # clear past data
        for i, ax in enumerate(self.canvas.figure.get_axes()):
            if ((x is not None) and (y is not None) and
                    ax.in_axes(event) and  # if the given mouse event (in display coords) in axes
                    ax.get_navigate() and  # whether the axes responds to navigation commands
                    ax.can_zoom()):  # if this axes supports the zoom box button functionality.
                # noinspection PyProtectedMember
                self._xypress.append((x, y, ax, i, ax._get_view()))
                self._flag_start = (xd, yd, ax)
                # logger.debug("FLAG > press > axes %s" % ax.get_label())

        # connect drag/press/release events
        id1 = self.canvas.mpl_connect('motion_notify_event', self._drag_flag)
        id2 = self.canvas.mpl_connect('key_press_event', self._switch_on_flag_mode)
        id3 = self.canvas.mpl_connect('key_release_event', self._switch_off_flag_mode)
        self._ids_flag = id1, id2, id3
        self._flag_mode = event.key
        # logger.debug("FLAG > press > key: %s" % self._flag_mode)

    def release_flag(self, event):
        """release mouse button callback in flagging mode"""
        # disconnect callbacks
        for flag_id in self._ids_flag:
            self.canvas.mpl_disconnect(flag_id)
        self._ids_flag = []
        # remove flagging area
        self.remove_rubberband()

        if not self._xypress:  # invalid first click
            return

        if not event.inaxes:

            # we assume that the axis is the same as the first click
            event.inaxes = self._xypress[0][2]

            # what are the axis bounds in display coords?
            y_down, y_up = self._xypress[0][2].get_ylim()
            x_left, x_right = self._xypress[0][2].get_xlim()
            ax_left, ax_down = self._xypress[0][2].transData.transform((x_left, y_down))
            ax_right, ax_up = self._xypress[0][2].transData.transform((x_right, y_up))
            # logger.debug("bottom-left: %s, %s" % (ax_left, ax_down))
            # logger.debug("top-right: %s, %s" % (ax_right, ax_up))

            # what are the clicked display coords in data coords?
            inv = self._xypress[0][2].transData.inverted()
            click_xdata, click_ydata = inv.transform((event.x, event.y))
            # logger.debug("clicked data: %s, %s" % (click_xdata, click_ydata))

            # in which direction was the click outside the axis?
            # logger.debug("released outside axes: %s, %s" % (event.x, event.y))
            if event.x > ax_right:
                event.xdata = x_right
                # logger.debug("right")
            elif event.x < ax_left:
                event.xdata = x_left
                # logger.debug("left")
            else:
                event.xdata = click_xdata

            if event.y > ax_up:
                event.ydata = y_up
                # logger.debug("up")
            elif event.y < ax_down:
                event.ydata = y_down
                # logger.debug("down")
            else:
                event.ydata = click_ydata

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
        # logger.debug("FLAG > x: %.3f %.3f, y: %.3f %.3f" % (min_xd, max_xd, min_yd, max_yd))
        yd2, yd1 = ax.get_ylim()  # bottom-to-top and the y-axis is reverted !!
        xd1, xd2 = ax.get_xlim()  # left-to-right
        min_xd, max_xd = max(min_xd, xd1), min(max_xd, xd2)
        min_yd, max_yd = max(min_yd, yd1), min(max_yd, yd2)
        # logger.debug("FLAG > x: %.3f %.3f, y: %.3f %.3f" % (min_xd, max_xd, min_yd, max_yd))

        # actually do the flagging
        plt_label = event.inaxes.get_label()
        y_selected = np.logical_and(self.prj.cur.proc.depth > min_yd, self.prj.cur.proc.depth < max_yd)
        if plt_label == 'speed':
            x_selected = np.logical_and(self.prj.cur.proc.speed > min_xd, self.prj.cur.proc.speed < max_xd)
        elif plt_label == 'temp':
            x_selected = np.logical_and(self.prj.cur.proc.temp > min_xd, self.prj.cur.proc.temp < max_xd)
        else:  # sal
            x_selected = np.logical_and(self.prj.cur.proc.sal > min_xd, self.prj.cur.proc.sal < max_xd)
        selected = np.logical_and(y_selected, x_selected)
        self.prj.cur.proc.flag[np.logical_and(self.plot_win.vi, selected)] = Dicts.flags['user']
        self.plot_win.update_data()

        self.canvas.draw_idle()
        self._xypress = None
        self._flag_start = None
        self._flag_end = None
        self._flag_mode = None

    def unflag(self):
        self.mode = _Mode.NONE
        if self._active == 'UNFLAG':
            self._active = None
            if self._id_press:
                self.canvas.mpl_disconnect(self._id_press)
            if self._id_release:
                self.canvas.mpl_disconnect(self._id_release)
            self.canvas.widgetlock.release(self)
        else:
            self._active = 'UNFLAG'
            if self._id_press:
                self.canvas.mpl_disconnect(self._id_press)
            self._id_press = self.canvas.mpl_connect('button_press_event', self.press_unflag)
            if self._id_release:
                self.canvas.mpl_disconnect(self._id_release)
            self._id_release = self.canvas.mpl_connect('button_release_event', self.release_unflag)
            self.canvas.widgetlock(self)

        self.set_message(self._active)
        self._update_buttons_checked()
        self._active_button()

    def press_unflag(self, event):
        """Mouse press callback for flag"""

        # store the pressed button
        if event.button != MouseButton.LEFT:  # left
            return
        # logger.debug("UNFLAG > press > button #%s" % self._button_pressed)

        x, y = event.x, event.y  # cursor position in pixel
        xd, yd = event.xdata, event.ydata  # cursor position in data coords
        # logger.debug("UNFLAG > press > loc (%.3f,%.3f)(%.3f,%.3f)" % (x, y, xd, yd))

        self._xypress = []  # clear past press
        self._flag_start = None  # clear past data
        self._flag_end = None  # clear past data
        for i, ax in enumerate(self.canvas.figure.get_axes()):
            if ((x is not None) and (y is not None) and
                    ax.in_axes(event) and  # if the given mouse event (in display coords) in axes
                    ax.get_navigate() and  # whether the axes responds to navigation commands
                    ax.can_zoom()):  # if this axes supports the zoom box button functionality.
                # noinspection PyProtectedMember
                self._xypress.append((x, y, ax, i, ax._get_view()))
                self._flag_start = (xd, yd, ax)
                # logger.debug("FLAG > press > axes %s" % ax.get_label())

        # connect drag/press/release events
        id1 = self.canvas.mpl_connect('motion_notify_event', self._drag_flag)
        id2 = self.canvas.mpl_connect('key_press_event', self._switch_on_flag_mode)
        id3 = self.canvas.mpl_connect('key_release_event', self._switch_off_flag_mode)
        self._ids_flag = id1, id2, id3
        self._flag_mode = event.key
        # logger.debug("UNFLAG > press > key: %s" % self._flag_mode)

    def release_unflag(self, event):
        """release mouse button callback in flagging mode"""
        # disconnect callbacks
        for flag_id in self._ids_flag:
            self.canvas.mpl_disconnect(flag_id)
        self._ids_flag = []
        # remove flagging area
        self.remove_rubberband()

        if not self._xypress:  # invalid first click
            return

        if not event.inaxes:

            # we assume that the axis is the same as the first click
            event.inaxes = self._xypress[0][2]

            # what are the axis bounds in display coords?
            y_down, y_up = self._xypress[0][2].get_ylim()
            x_left, x_right = self._xypress[0][2].get_xlim()
            ax_left, ax_down = self._xypress[0][2].transData.transform((x_left, y_down))
            ax_right, ax_up = self._xypress[0][2].transData.transform((x_right, y_up))
            # logger.debug("bottom-left: %s, %s" % (ax_left, ax_down))
            # logger.debug("top-right: %s, %s" % (ax_right, ax_up))

            # what are the clicked display coords in data coords?
            inv = self._xypress[0][2].transData.inverted()
            click_xdata, click_ydata = inv.transform((event.x, event.y))
            # logger.debug("clicked data: %s, %s" % (click_xdata, click_ydata))

            # in which direction was the click outside the axis?
            # logger.debug("released outside axes: %s, %s" % (event.x, event.y))
            if event.x > ax_right:
                event.xdata = x_right
                # logger.debug("right")
            elif event.x < ax_left:
                event.xdata = x_left
                # logger.debug("left")
            else:
                event.xdata = click_xdata

            if event.y > ax_up:
                event.ydata = y_up
                # logger.debug("up")
            elif event.y < ax_down:
                event.ydata = y_down
                # logger.debug("down")
            else:
                event.ydata = click_ydata

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
        # logger.debug("UNFLAG > x: %.3f %.3f, y: %.3f %.3f" % (min_xd, max_xd, min_yd, max_yd))
        yd2, yd1 = ax.get_ylim()  # bottom-to-top and the y-axis is reverted !!
        xd1, xd2 = ax.get_xlim()  # left-to-right
        min_xd, max_xd = max(min_xd, xd1), min(max_xd, xd2)
        min_yd, max_yd = max(min_yd, yd1), min(max_yd, yd2)
        # logger.debug("UNFLAG > x: %.3f %.3f, y: %.3f %.3f" % (min_xd, max_xd, min_yd, max_yd))

        plt_label = event.inaxes.get_label()
        y_selected = np.logical_and(self.prj.cur.proc.depth > min_yd, self.prj.cur.proc.depth < max_yd)
        if plt_label == 'speed':
            x_selected = np.logical_and(self.prj.cur.proc.speed > min_xd, self.prj.cur.proc.speed < max_xd)
        elif plt_label == 'temp':
            x_selected = np.logical_and(self.prj.cur.proc.temp > min_xd, self.prj.cur.proc.temp < max_xd)
        else:  # sal
            x_selected = np.logical_and(self.prj.cur.proc.sal > min_xd, self.prj.cur.proc.sal < max_xd)
        selected = np.logical_and(y_selected, x_selected)
        self.prj.cur.proc.flag[np.logical_and(self.plot_win.ii, selected)] = Dicts.flags['valid']
        self.plot_win.update_data()

        self.canvas.draw_idle()
        self._xypress = None
        self._flag_start = None
        self._flag_end = None
        self._flag_mode = None

    # flag/unflag helper methods

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

    def _drag_flag(self, event):
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

    # --- insert ---

    def insert(self):
        self.mode = _Mode.NONE
        if self._active == 'INSERT':
            self._active = None
            if self._id_press:
                self.canvas.mpl_disconnect(self._id_press)
            if self._id_release:
                self.canvas.mpl_disconnect(self._id_release)
            self.canvas.widgetlock.release(self)
        else:
            self._active = 'INSERT'
            if self._id_press:
                self.canvas.mpl_disconnect(self._id_press)
            self._id_press = self.canvas.mpl_connect('button_press_event', self.press_insert)
            if self._id_release:
                self.canvas.mpl_disconnect(self._id_release)
            self._id_release = self.canvas.mpl_connect('button_release_event', self.release_insert)
            self.canvas.widgetlock(self)

        self.set_message(self._active)
        self._update_buttons_checked()
        self._active_button()

    def press_insert(self, event):
        """Mouse press callback for flag"""

        # store the pressed button
        if event.button != MouseButton.LEFT:  # left
            self.insert_sample = None
            return
        # logger.debug("INSERT > press > button #%s" % self._button_pressed)

        # x, y = event.x, event.y  # cursor position in pixel
        xd, yd = event.xdata, event.ydata  # cursor position in data coords
        # using %s since they might be None
        # logger.debug("INSERT > press > loc (%s,%s)(%s,%s)" % (x, y, xd, yd))

        if not self.insert_sample:
            self.insert_sample = Sample()

        # click outside the axes
        if event.inaxes is None:
            return

        plt_label = event.inaxes.get_label()
        if plt_label == "speed":  # we store both y and x
            if self.insert_sample.temp:
                self.insert_sample.temp = None
            if self.insert_sample.sal:
                self.insert_sample.sal = None
            self.insert_sample.depth = yd
            self.insert_sample.speed = xd

        elif plt_label == "temp":  # we don't overwrite y, if present
            if not self.insert_sample.depth:
                self.insert_sample.depth = yd
            self.insert_sample.temp = xd

        elif plt_label == "sal":  # we don't overwrite y, if present
            if not self.insert_sample.depth:
                self.insert_sample.depth = yd
            self.insert_sample.sal = xd

        if self.insert_sample.speed:
            self.prj.cur.insert_proc_speed(depth=self.insert_sample.depth, speed=self.insert_sample.speed)
            self.insert_sample = None
            self.plot_win.update_data()

        elif self.insert_sample.temp and self.insert_sample.sal:
            self.prj.cur.insert_proc_temp_sal(depth=self.insert_sample.depth, temp=self.insert_sample.temp,
                                              sal=self.insert_sample.sal)
            self.insert_sample = None
            self.plot_win.update_data()

    def release_insert(self, event):
        """the release mouse button callback in insert mode"""
        self.canvas.draw_idle()

    # --- plotting ---

    def flagged_plot(self):
        flagged_flag = self._actions['flagged_plot'].isChecked()
        logger.debug("plot flagged: %s" % flagged_flag)
        self.plot_win.set_invalid_visibility(flagged_flag)

        self.canvas.draw_idle()

    def grid_plot(self):
        grid_flag = self._actions['grid_plot'].isChecked()
        logger.debug("plot grid: %s" % grid_flag)

        with rc_context(self.rc_context):
            for a in self.canvas.figure.get_axes():
                a.grid(grid_flag)

        self.canvas.draw_idle()

    def legend_plot(self):
        legend_flag = self._actions['legend_plot'].isChecked()
        logger.debug("plot legend: %s" % legend_flag)

        with rc_context(self.rc_context):
            if legend_flag:
                for a in self.canvas.figure.get_axes():
                    a.legend(loc='lower left')
            else:
                for a in self.canvas.figure.get_axes():
                    try:
                        a.legend_.remove()
                    except AttributeError:
                        logger.info("missing legend to remove")

        self.canvas.draw_idle()
