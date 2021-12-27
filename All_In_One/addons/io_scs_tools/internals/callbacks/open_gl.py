# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Copyright (C) 2013-2014: SCS Software

import bpy
import console_python
from io_scs_tools.internals.open_gl import core as _gl_core
from io_scs_tools.utils import view3d as _view3d_utils

_callback_handle = []  # storing callback handles in the list for being able to properly remove them


def enable(mode="Normal"):
    """Append OpenGL callbacks.

    :rtype: None
    """
    if _callback_handle:
        disable()

    if mode == "Normal":

        handle_pixel = bpy.types.SpaceView3D.draw_handler_add(_gl_core.draw_custom_2d_elements, (), 'WINDOW', 'POST_PIXEL')
        handle_pre_view = bpy.types.SpaceView3D.draw_handler_add(_gl_core.draw_custom_3d_elements, (mode,), 'WINDOW', 'PRE_VIEW')
        handle_post_view = bpy.types.SpaceView3D.draw_handler_add(_gl_core.disable_depth_test, (), 'WINDOW', 'POST_VIEW')

    else:  # X-ray mode

        handle_pixel = bpy.types.SpaceView3D.draw_handler_add(_gl_core.draw_custom_2d_elements, (), 'WINDOW', 'POST_PIXEL')
        handle_pre_view = None
        handle_post_view = bpy.types.SpaceView3D.draw_handler_add(_gl_core.draw_custom_3d_elements, (mode,), 'WINDOW', 'POST_VIEW')

    _callback_handle[:] = handle_pixel, handle_pre_view, handle_post_view

    console_python.execute.hooks.append((_view3d_utils.tag_redraw_all_view3d, ()))


def disable():
    """Remove OpenGL callbacks.

    :rtype: None
    """
    if not _callback_handle:
        return

    console_python.execute.hooks.remove((_view3d_utils.tag_redraw_all_view3d, ()))

    handle_pixel, handle_pre_view, handle_post_view = _callback_handle

    bpy.types.SpaceView3D.draw_handler_remove(handle_pixel, 'WINDOW')
    if handle_pre_view:
        bpy.types.SpaceView3D.draw_handler_remove(handle_pre_view, 'WINDOW')
    bpy.types.SpaceView3D.draw_handler_remove(handle_post_view, 'WINDOW')

    _callback_handle[:] = []