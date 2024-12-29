import logging
import os
from typing import TYPE_CHECKING

import numpy as np
from matplotlib import cbook, rc_context
# noinspection PyProtectedMember,PyUnresolvedReferences
from matplotlib.backend_bases import _Mode, MouseButton, cursors, MouseEvent
from matplotlib.backend_tools import Cursors
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
# noinspection PyUnresolvedReferences
from matplotlib.backends.qt_compat import QtCore, QtGui, QtWidgets

from hyo2.ssm2.lib.profile.dicts import Dicts

if TYPE_CHECKING:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from hyo2.ssm2.lib.soundspeed import SoundSpeedLibrary
    from hyo2.ssm2.app.gui.soundspeedmanager.widgets.dataplots import DataPlots

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

    def __init__(self, canvas: 'FigureCanvas', parent: QtWidgets.QWidget, plot_win: 'DataPlots',
                 prj: 'SoundSpeedLibrary', coordinates: bool = True):

        self.plot_win = plot_win
        self.prj = prj

        self._lastCursor: None | Cursors = None
        self._active: None | str = None
        self._id_press: None | int = None
        self._id_release: None | int = None
        self._xypress: None | list = None
        self._ids_flag: None | tuple = None
        self._flag_mode: None | str = None
        self._flag_start: None | tuple = None
        self._flag_end: None | tuple = None
        self.insert_sample = None

        self.toolitems = [
            ('Home', 'Reset original view', 'home', 'home'),
            ('Back', 'Back to previous view', 'back', 'back'),
            ('Forward', 'Forward to next view', 'forward', 'forward'),
            (None, None, None, None),
            ('Pan', 'Pan on plot', 'move', 'pan'),  # MOD
            ('Scale', 'Scale plot', 'scale', 'scale'),  # MOD
            ('Zoom in', 'Zoom in area', 'zoomin', 'zoom_in'),  # MOD
            ('Zoom out', 'Zoom out area', 'zoomout', 'zoom_out'),  # MOD
            ('Flag', 'Flag samples', 'flag', 'flag'),  # NEW
            ('Unflag', 'Unflag samples', 'unflag', 'unflag'),  # NEW
            ('Insert', 'Insert samples', 'insert', 'insert'),  # NEW
            (None, None, None, None),  # NEW
            ('Flagged', 'Show/hide flagged', 'flagged', 'flagged_plot'),  # NEW
            ('Grid', 'Toggle grids', 'plot_grid', 'grid_plot'),  # NEW
            ('Legend', 'Toggle legends', 'plot_legend', 'legend_plot'),  # NEW
            ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
            ('Customize', 'Edit axis, curve and image parameters', 'qt5_editor_options', 'edit_parameters'),
            (None, None, None, None),
            ('Save', 'Save the figure', 'filesave', 'save_figure')
        ]

        super().__init__(canvas=canvas, parent=parent, coordinates=coordinates)
        # noinspection PyProtectedMember
        self._pan_info: None | super()._PanInfo = None
        # noinspection PyProtectedMember
        self._zoom_info: None | super()._ZoomInfo = None
        self.setIconSize(QtCore.QSize(24, 24))

        # set checkable buttons
        self._actions['scale'].setCheckable(True)
        self._actions['zoom_in'].setCheckable(True)
        self._actions['zoom_out'].setCheckable(True)
        self._actions['flag'].setCheckable(True)
        self._actions['unflag'].setCheckable(True)
        self._actions['insert'].setCheckable(True)
        self._actions['flagged_plot'].setCheckable(True)
        self._actions['flagged_plot'].setChecked(True)
        self._actions['grid_plot'].setCheckable(True)
        self._actions['grid_plot'].setChecked(True)
        self._actions['legend_plot'].setCheckable(True)
        self._actions['legend_plot'].setChecked(False)

        # noinspection PyTypeChecker
        self.canvas.mpl_connect('button_press_event', self.press)
        # noinspection PyTypeChecker
        self.canvas.mpl_connect('button_release_event', self.release)

        # Add the x,y location widget on the right side of the toolbar
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

    # ################### Helper functions ###################

    def _icon(self, name: str) -> QtGui.QIcon:
        # Modified to use local icons

        filename = os.path.join(self.media, name)
        if not os.path.exists(filename):

            # use a high-resolution icon with suffix '_large' if available
            # note: user-provided icons may not have '_large' versions
            # noinspection PyUnresolvedReferences,PyProtectedMember
            path_regular = cbook._get_data_path('images', name)
            path_large = path_regular.with_name(
                path_regular.name.replace('.png', '_large.png'))
            filename = str(path_large if path_large.exists() else path_regular)

        pm = QtGui.QPixmap(filename)
        pm.setDevicePixelRatio(
            self.devicePixelRatioF() or 1)  # rarely, devicePixelRatioF=0
        if self.palette().color(self.backgroundRole()).value() < 128:
            icon_color = self.palette().color(self.foregroundRole())
            mask = pm.createMaskFromColor(
                QtGui.QColor('black'),
                QtCore.Qt.MaskMode.MaskOutColor)
            pm.fill(icon_color)
            pm.setMask(mask)
        return QtGui.QIcon(pm)

    def _update_buttons_checked(self) -> None:
        # sync button check states to match active mode
        logger.debug("Mode: %s" % self._active)
        self._actions['pan'].setChecked(self._active == 'PAN')
        self._actions['scale'].setChecked(self._active == 'SCALE')
        self._actions['zoom_in'].setChecked(self._active == 'ZOOM_IN')
        self._actions['zoom_out'].setChecked(self._active == 'ZOOM_OUT')
        self._actions['flag'].setChecked(self._active == 'FLAG')
        self._actions['unflag'].setChecked(self._active == 'UNFLAG')
        self._actions['insert'].setChecked(self._active == 'INSERT')

    def mouse_move(self, event):
        self._update_cursor(event)

        if event.inaxes and event.inaxes.get_navigate():
            plt_label = event.inaxes.get_label()
            try:
                s = "d:%.2f" % event.ydata
                if plt_label == "speed":
                    s += ", ss:%.2f" % event.xdata
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
                            msg += ", ss:%.2f" % event.xdata
                        else:
                            msg += ", ss:*"

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
            if self._active:
                self.set_message('%s' % self._active.lower())

            else:
                self.set_message('')

            self.mon_label.setText('')

    def _update_cursor(self, event):
        """Set cursor by mode"""

        if not event.inaxes or not self._active:
            if self._lastCursor != cursors.POINTER:
                self.canvas.set_cursor(cursors.POINTER)
                self._lastCursor = cursors.POINTER
        else:
            if (self._active == 'ZOOM_IN') or (self._active == 'ZOOM_OUT') or (self._active == 'INSERT')\
                    or (self._active == 'FLAG') or (self._active == 'UNFLAG'):
                if self._lastCursor != cursors.SELECT_REGION:
                    self.canvas.set_cursor(cursors.SELECT_REGION)
                    self._lastCursor = cursors.SELECT_REGION

            elif (self._active == 'PAN') or (self._active == 'SCALE'):
                if self._lastCursor != cursors.MOVE:
                    self.canvas.set_cursor(cursors.MOVE)
                    self._lastCursor = cursors.MOVE

            else:
                raise RuntimeError("Unsupported cursor mode: %s" % self._active)

    def reset(self) -> None:
        logger.debug("reset")
        self._lastCursor = None
        self._active = None
        self._id_press = None
        self._id_release = None
        self._xypress = None
        self._ids_flag = None
        self._flag_mode = None
        self._flag_start = None
        self._flag_end = None
        self.insert_sample = None

        self._pan_info = None
        self._zoom_info = None

    def press(self, event: MouseEvent) -> None:
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
            menu.exec()

    def release(self, event: MouseEvent) -> None:
        # print("release", event.button)
        pass

    # ################### ACTIONS ###################

    # ------------------- pan / scale  -------------------

    def pan(self) -> None:
        self.mode = _Mode.NONE
        if self._active == 'PAN':
            self._active = None
            if self._id_press:
                self.canvas.mpl_disconnect(self._id_press)
            if self._id_release:
                self.canvas.mpl_disconnect(self._id_release)
            self.canvas.widgetlock.release(self)
        else:
            self._active = 'PAN'
            if self._id_press:
                self.canvas.mpl_disconnect(self._id_press)
            # noinspection PyTypeChecker
            self._id_press = self.canvas.mpl_connect('button_press_event', self.press_pan)
            if self._id_release:
                self.canvas.mpl_disconnect(self._id_release)
            self._id_release = self.canvas.mpl_connect('button_release_event', self.release_pan)
            self.canvas.widgetlock(self)

        # logger.debug("active: %s" % self._active)
        self.set_message(self._active)
        self._update_buttons_checked()

    def scale(self) -> None:
        self.mode = _Mode.NONE
        if self._active == 'SCALE':
            self._active = None
            if self._id_press:
                self.canvas.mpl_disconnect(self._id_press)
            if self._id_release:
                self.canvas.mpl_disconnect(self._id_release)
            self.canvas.widgetlock.release(self)
        else:
            self._active = 'SCALE'
            if self._id_press:
                self.canvas.mpl_disconnect(self._id_press)
            # noinspection PyTypeChecker
            self._id_press = self.canvas.mpl_connect('button_press_event', self.press_pan)
            if self._id_release:
                self.canvas.mpl_disconnect(self._id_release)
            self._id_release = self.canvas.mpl_connect('button_release_event', self.release_pan)
            self.canvas.widgetlock(self)

        # logger.debug("active: %s" % self._active)
        self.set_message(self._active)
        self._update_buttons_checked()

    def press_pan(self, event: MouseEvent) -> None:
        """Callback for mouse button press in pan/zoom mode."""
        logger.debug("mode: %s" % self._active)

        if (event.button not in [MouseButton.LEFT]
                or event.x is None or event.y is None):
            return
        axes = [a for a in self.canvas.figure.get_axes()
                if a.in_axes(event) and a.get_navigate() and a.can_pan()]
        if not axes:
            return
        if self._nav_stack() is None:
            self.push_current()  # set the home button to this view
        for ax in axes:
            # MOD
            if self._active == 'SCALE':
                ax.start_pan(event.x, event.y, MouseButton.RIGHT)
            else:
                ax.start_pan(event.x, event.y, event.button)
        self.canvas.mpl_disconnect(self._id_drag)
        # noinspection PyTypeChecker
        id_drag = self.canvas.mpl_connect("motion_notify_event", self.drag_pan)
        # MOD
        if self._active == 'SCALE':
            self._pan_info = self._PanInfo(button=MouseButton.RIGHT, axes=axes, cid=id_drag)
        else:
            self._pan_info = self._PanInfo(button=MouseButton.LEFT, axes=axes, cid=id_drag)

    def drag_pan(self, event: MouseEvent) -> None:
        logger.debug("mode: %s" % self._active)

        """Callback for dragging in pan/zoom mode."""
        for ax in self._pan_info.axes:
            # Using the recorded button at the press is safer than the current
            # button, as multiple buttons can get pressed during motion.
            # MOD
            if self._active == 'SCALE':
                ax.drag_pan(MouseButton.RIGHT, event.key, event.x, event.y)
            else:
                ax.drag_pan(self._pan_info.button, event.key, event.x, event.y)
        self.canvas.draw_idle()

    #  ------------------- zoom in / out  -------------------

    def zoom_in(self) -> None:
        self.mode = _Mode.NONE
        if self._active == 'ZOOM_IN':
            self._active = None
            if self._id_press:
                self.canvas.mpl_disconnect(self._id_press)
            if self._id_release:
                self.canvas.mpl_disconnect(self._id_release)
            self.canvas.widgetlock.release(self)
        else:
            self._active = 'ZOOM_IN'
            if self._id_press:
                self.canvas.mpl_disconnect(self._id_press)
            # noinspection PyTypeChecker
            self._id_press = self.canvas.mpl_connect('button_press_event', self.press_zoom)
            if self._id_release:
                self.canvas.mpl_disconnect(self._id_release)
            self._id_release = self.canvas.mpl_connect('button_release_event', self.release_zoom)
            self.canvas.widgetlock(self)

        # logger.debug("active: %s" % self._active)
        self.set_message(self._active)
        self._update_buttons_checked()

    def zoom_out(self) -> None:
        self.mode = _Mode.NONE
        if self._active == 'ZOOM_OUT':
            self._active = None
            if self._id_press:
                self.canvas.mpl_disconnect(self._id_press)
            if self._id_release:
                self.canvas.mpl_disconnect(self._id_release)
            self.canvas.widgetlock.release(self)
        else:
            self._active = 'ZOOM_OUT'
            if self._id_press:
                self.canvas.mpl_disconnect(self._id_press)
            # noinspection PyTypeChecker
            self._id_press = self.canvas.mpl_connect('button_press_event', self.press_zoom)
            if self._id_release:
                self.canvas.mpl_disconnect(self._id_release)
            self._id_release = self.canvas.mpl_connect('button_release_event', self.release_zoom)
            self.canvas.widgetlock(self)

        # logger.debug("active: %s" % self._active)
        self.set_message(self._active)
        self._update_buttons_checked()

    def press_zoom(self, event: MouseEvent) -> None:
        """Callback for mouse button press in zoom to rect mode."""
        if (event.button not in [MouseButton.LEFT, MouseButton.RIGHT]
                or event.x is None or event.y is None):
            return
        axes = [a for a in self.canvas.figure.get_axes()
                if a.in_axes(event) and a.get_navigate() and a.can_zoom()]
        if not axes:
            return
        if self._nav_stack() is None:
            self.push_current()  # set the home button to this view
        id_zoom = self.canvas.mpl_connect(
            "motion_notify_event", self.drag_zoom)
        # A colorbar is one-dimensional, so we extend the zoom rectangle out
        # to the edge of the Axes bbox in the other dimension. To do that we
        # store the orientation of the colorbar for later.
        if hasattr(axes[0], "_colorbar"):
            # noinspection PyProtectedMember
            cbar = axes[0]._colorbar.orientation
        else:
            cbar = None
        # MOD
        self._zoom_info = self._ZoomInfo(
            direction="in" if self._active == "ZOOM_IN" else "out",
            start_xy=(event.x, event.y), axes=axes, cid=id_zoom, cbar=cbar)

    #  ------------------- flag / unflag -------------------

    def flag(self) -> None:
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
            # noinspection PyTypeChecker
            self._id_press = self.canvas.mpl_connect('button_press_event', self.press_flag)
            if self._id_release:
                self.canvas.mpl_disconnect(self._id_release)
            # noinspection PyTypeChecker
            self._id_release = self.canvas.mpl_connect('button_release_event', self.release_flag)
            self.canvas.widgetlock(self)

        # logger.debug("active: %s" % self._active)
        self.set_message(self._active)
        self._update_buttons_checked()

    def press_flag(self, event: MouseEvent) -> None:
        # logger.debug("Press flag")

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
        # noinspection PyTypeChecker
        id1 = self.canvas.mpl_connect('motion_notify_event', self._drag_flag)
        # noinspection PyTypeChecker
        id2 = self.canvas.mpl_connect('key_press_event', self._switch_on_flag_mode)
        # noinspection PyTypeChecker
        id3 = self.canvas.mpl_connect('key_release_event', self._switch_off_flag_mode)
        self._ids_flag = id1, id2, id3
        self._flag_mode = event.key
        # logger.debug("FLAG > press > key: %s" % self._flag_mode)

    def release_flag(self, event: MouseEvent) -> None:
        # logger.debug("Release flag")
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

    def unflag(self) -> None:
        # logger.debug("Unflag")
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
            # noinspection PyTypeChecker
            self._id_press = self.canvas.mpl_connect('button_press_event', self.press_unflag)
            if self._id_release:
                self.canvas.mpl_disconnect(self._id_release)
            # noinspection PyTypeChecker
            self._id_release = self.canvas.mpl_connect('button_release_event', self.release_unflag)
            self.canvas.widgetlock(self)

        self.set_message(self._active)
        self._update_buttons_checked()

    def press_unflag(self, event: MouseEvent) -> None:
        # logger.debug("Press unflag")

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
        # noinspection PyTypeChecker
        id1 = self.canvas.mpl_connect('motion_notify_event', self._drag_flag)
        # noinspection PyTypeChecker
        id2 = self.canvas.mpl_connect('key_press_event', self._switch_on_flag_mode)
        # noinspection PyTypeChecker
        id3 = self.canvas.mpl_connect('key_release_event', self._switch_off_flag_mode)
        self._ids_flag = id1, id2, id3
        self._flag_mode = event.key
        # logger.debug("UNFLAG > press > key: %s" % self._flag_mode)

    def release_unflag(self, event: MouseEvent) -> None:
        # logger.debug("Release unflag")
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

    def _switch_on_flag_mode(self, event: MouseEvent) -> None:
        """optional key-press switch in flagging mode (used for x- and y- selections)"""

        self._flag_mode = event.key
        if self._flag_mode == "x":
            logger.debug("FLAG > switch > x-selection: ON")
        elif self._flag_mode == "y":
            logger.debug("FLAG > switch > y-selection: ON")

        self.mouse_move(event)

    def _switch_off_flag_mode(self, event: MouseEvent) -> None:
        """optional key-press switch in flagging mode (used for x- and y- selections)"""

        self._flag_mode = None
        if event.key == "x":
            logger.debug("FLAG > switch > x-selection: OFF")
        elif event.key == "y":
            logger.debug("FLAG > switch > y-selection: OFF")

        self.mouse_move(event)

    def _drag_flag(self, event: MouseEvent) -> None:
        """the mouse-motion dragging callback in flagging mode"""

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

    #  ------------------- insert  -------------------

    def insert(self) -> None:
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
            # noinspection PyTypeChecker
            self._id_press = self.canvas.mpl_connect('button_press_event', self.press_insert)
            if self._id_release:
                self.canvas.mpl_disconnect(self._id_release)
            # noinspection PyTypeChecker
            self._id_release = self.canvas.mpl_connect('button_release_event', self.release_insert)
            self.canvas.widgetlock(self)

        # logger.debug("active: %s" % self._active)
        self.set_message(self._active)
        self._update_buttons_checked()

    def press_insert(self, event: MouseEvent) -> None:
        """Mouse press callback for insert"""

        # store the pressed button
        if event.button != MouseButton.LEFT:  # left
            self.insert_sample = None
            return
        # logger.debug("INSERT > press > button #%s" % event.button)

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

    def release_insert(self, _: MouseEvent) -> None:
        """the release mouse button callback in insert mode"""
        self.canvas.draw_idle()

    # ------------------ plotting ---------------------

    def flagged_plot(self):
        flagged_flag = self._actions['flagged_plot'].isChecked()
        # logger.debug("plot flagged: %s" % flagged_flag)
        self.plot_win.set_invalid_visibility(flagged_flag)

        self.canvas.draw_idle()

    def grid_plot(self):
        grid_flag = self._actions['grid_plot'].isChecked()
        # logger.debug("plot grid: %s" % grid_flag)

        with rc_context(self.rc_context):
            for a in self.canvas.figure.get_axes():
                a.grid(grid_flag)

        self.canvas.draw_idle()

    def legend_plot(self):
        legend_flag = self._actions['legend_plot'].isChecked()
        # logger.debug("plot legend: %s" % legend_flag)

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
