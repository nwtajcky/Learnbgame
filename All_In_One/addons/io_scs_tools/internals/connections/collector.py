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
from mathutils import Vector
from io_scs_tools.consts import PrefabLocators as _PL_consts
from io_scs_tools.utils import curve as _curve_utils
from io_scs_tools.utils import math as _math_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals


def collect_nav_curve_data(loc0_obj, loc1_obj):
    """Recomputes curve data, colors and returns it in final format prepared for drawing

    :param loc0_obj: out locator object
    :type loc0_obj: bpy.types.Object
    :param loc1_obj: in locator object
    :type loc1_obj: bpy.types.Object
    :return: curve data prepared for drawing
    :rtype: {"curve_points": list of Vector,
             "curve_steps": int,
             "curve_color0": tuple,
             "curve_color1": tuple,
             "locrot_0": tuple,
             "locrot_1": tuple}
    """

    curve_steps = _get_scs_globals().curve_segments

    nav_point_0_loc = loc0_obj.matrix_world.translation
    nav_point_0_rot = loc0_obj.matrix_world.to_euler('XYZ')
    nav_point_0_dir = loc0_obj.matrix_world.to_quaternion() * Vector((0, 1, 0))
    nav_point_1_loc = loc1_obj.matrix_world.translation
    nav_point_1_rot = loc1_obj.matrix_world.to_euler('XYZ')
    nav_point_1_dir = loc1_obj.matrix_world.to_quaternion() * Vector((0, 1, 0))

    curve_data = _curve_utils.compute_curve(nav_point_0_loc, nav_point_0_dir,
                                            nav_point_1_loc, nav_point_1_dir, curve_steps)

    curve_data['curve_steps'] = curve_steps

    loc0_scs_props = loc0_obj.scs_props
    """:type: io_scs_tools.properties.object.ObjectSCSTools"""
    loc1_scs_props = loc1_obj.scs_props
    """:type: io_scs_tools.properties.object.ObjectSCSTools"""

    # blinker
    blinker = int(loc0_scs_props.locator_prefab_np_blinker)
    if blinker == _PL_consts.PNCF.LEFT_BLINKER:
        curve_data['curve_color1'] = (1, 0.2, 0.698)
    elif blinker == _PL_consts.PNCF.RIGHT_BLINKER:
        curve_data['curve_color1'] = (0.2, 0.698, 1)
    elif blinker == _PL_consts.PNCF.FORCE_NO_BLINKER:
        curve_data['curve_color1'] = (0.698, 0.098, 1)

    # priority modifier
    priority_modifier = int(loc0_scs_props.locator_prefab_np_priority_modifier)
    if 0 < priority_modifier < 8:
        curve_data['curve_color0'] = (0.494, 0.6, 0.898)
    elif priority_modifier >= 8:
        curve_data['curve_color0'] = (0, 0, 0.898)

    # allowed vehicles
    allowed_vehicles = int(loc1_scs_props.locator_prefab_np_allowed_veh)
    if allowed_vehicles == _PL_consts.PNCF.SMALL_VEHICLES:
        curve_data['curve_color1'] = (0.898, 0, 0)
    elif allowed_vehicles == _PL_consts.PNCF.LARGE_VEHICLES:
        curve_data['curve_color1'] = (0, 0.898, 0)
    elif allowed_vehicles == 0:
        curve_data['curve_color0'] = (0, 0.898, 0)
        curve_data['curve_color1'] = (0, 0.898, 0)

    curve_data['locrot_0'] = (nav_point_0_loc.x, nav_point_0_loc.y, nav_point_0_loc.z, nav_point_0_rot.x,
                              nav_point_0_rot.y, nav_point_0_rot.z)
    curve_data['locrot_1'] = (nav_point_1_loc.x, nav_point_1_loc.y, nav_point_1_loc.z, nav_point_1_rot.x,
                              nav_point_1_rot.y, nav_point_1_rot.z)

    return curve_data


def collect_map_line_data(loc0_obj, loc1_obj):
    """Recompute map line data, colors and return it in final format prepared for drawing

    :param loc0_obj: out locator object
    :type loc0_obj: bpy.types.Object
    :param loc1_obj: in locator object
    :type loc1_obj: bpy.types.Object
    :return:
    :rtype: {"line_color0": tuple,
             "line_color1": tuple,
             "loc_0": tuple,
             "loc_btw": tuple,
             "loc_1": tuple}
    """

    line_data = {}

    if loc0_obj.scs_props.locator_prefab_mp_road_size == str(_PL_consts.MPVF.ROAD_SIZE_MANUAL):

        if loc0_obj.scs_props.locator_prefab_mp_custom_color == str(_PL_consts.MPVF.CUSTOM_COLOR1):
            line_data['line_color0'] = (0.9, 0.9, 0.9)
        elif loc0_obj.scs_props.locator_prefab_mp_custom_color == str(_PL_consts.MPVF.CUSTOM_COLOR2):
            line_data['line_color0'] = (0.1, 0.1, 0.1)
        elif loc0_obj.scs_props.locator_prefab_mp_custom_color == str(_PL_consts.MPVF.CUSTOM_COLOR3):
            line_data['line_color0'] = (0, 0.4, 0)

    if loc0_obj.scs_props.locator_prefab_mp_prefab_exit:
        line_data['line_color0'] = (0.6, 0, 0)

    if loc1_obj.scs_props.locator_prefab_mp_road_size == str(_PL_consts.MPVF.ROAD_SIZE_MANUAL):

        if loc1_obj.scs_props.locator_prefab_mp_custom_color == str(_PL_consts.MPVF.CUSTOM_COLOR1):
            line_data['line_color1'] = (0.9, 0.9, 0.9)
        elif loc1_obj.scs_props.locator_prefab_mp_custom_color == str(_PL_consts.MPVF.CUSTOM_COLOR2):
            line_data['line_color1'] = (0.1, 0.1, 0.1)
        elif loc1_obj.scs_props.locator_prefab_mp_custom_color == str(_PL_consts.MPVF.CUSTOM_COLOR3):
            line_data['line_color1'] = (0, 0.4, 0)

    if loc1_obj.scs_props.locator_prefab_mp_prefab_exit:
        line_data['line_color1'] = (0.6, 0, 0)

    map_point_0_loc = loc0_obj.matrix_world.translation
    map_point_1_loc = loc1_obj.matrix_world.translation
    line_data['loc_0'] = (map_point_0_loc.x, map_point_0_loc.y, map_point_0_loc.z)
    line_data['loc_btw'] = _math_utils.middle_point(map_point_0_loc, map_point_1_loc)
    line_data['loc_1'] = (map_point_1_loc.x, map_point_1_loc.y, map_point_1_loc.z)

    return line_data


def collect_trigger_line_data(loc0_obj, loc0_conns_count, loc1_obj, loc1_conns_count):
    """Recompute map line data, colors and return it in final format prepared for drawing

    :param loc0_obj: out locator object
    :type loc0_obj: bpy.types.Object
    :param loc1_obj: in locator object
    :type loc1_obj: bpy.types.Object
    :return:
    :rtype: {"line_color0": tuple,
             "line_color1": tuple,
             "loc_0": tuple,
             "loc_btw": tuple,
             "loc_1": tuple}
    """

    line_data = {}

    if loc0_conns_count < 2:
        line_data['line_color0'] = (0.6, 0, 0)

    if loc1_conns_count < 2:
        line_data['line_color1'] = (0.6, 0, 0)

    tp_0_loc = loc0_obj.matrix_world.translation
    tp_1_loc = loc1_obj.matrix_world.translation
    line_data['loc_0'] = (tp_0_loc.x, tp_0_loc.y, tp_0_loc.z)
    line_data['loc_btw'] = _math_utils.middle_point(tp_0_loc, tp_1_loc)
    line_data['loc_1'] = (tp_1_loc.x, tp_1_loc.y, tp_1_loc.z)

    return line_data
