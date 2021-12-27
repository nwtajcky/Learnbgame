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

from bgl import (glColor3f, glVertex3f, glLineWidth, glBegin, glEnd, GL_LINES)
from io_scs_tools.internals.open_gl import primitive as _primitive
from mathutils import Vector, Matrix


def draw_shape_model_locator(mat, scs_globals):
    """
    Draws shape for "Model Locator" type.
    :param mat:
    :param scs_globals:
    :return:
    """
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glColor3f(scs_globals.locator_model_wire_color.r, scs_globals.locator_model_wire_color.g,
              scs_globals.locator_model_wire_color.b)
    glVertex3f(*(mat * Vector((0.0, scs_globals.locator_empty_size * 1, 0.0))))
    glVertex3f(*(mat * Vector((0.0, 0.75, 0.0))))
    glVertex3f(*(mat * Vector((-0.15, 0.45, 0.0))))
    glVertex3f(*(mat * Vector((0.0, 0.75, 0.0))))
    glVertex3f(*(mat * Vector((0.0, 0.75, 0.0))))
    glVertex3f(*(mat * Vector((0.15, 0.45, 0.0))))
    glEnd()
    glLineWidth(1.0)


def draw_model_box(mat, scs_globals):
    """
    Draw Cube for Model locator.
    :param mat:
    :param scs_globals:
    :return:
    """

    mat1 = mat * (Matrix.Translation((0.0, 0.0, 0.0)) *
                  Matrix.Scale(scs_globals.locator_size / 5, 4, (1.0, 0.0, 0.0)) *
                  Matrix.Scale(scs_globals.locator_size / 5, 4, (0.0, 1.0, 0.0)) *
                  Matrix.Scale(scs_globals.locator_size / 5, 4, (0.0, 0.0, 1.0)))

    cube_vertices, cube_faces, cube_wire_lines = _primitive.get_box_data()

    _primitive.draw_polygon_object(mat1,
                                   cube_vertices,
                                   cube_faces,
                                   scs_globals.locator_coll_face_color,
                                   False,
                                   True,
                                   cube_wire_lines,
                                   scs_globals.locator_model_wire_color)


def draw_model_locator(obj, scs_globals):
    """
    Draw Model locator.
    :param obj:
    :return:
    """
    import mathutils

    size = scs_globals.locator_size
    empty_size = scs_globals.locator_empty_size
    mat_sca = mathutils.Matrix.Scale(size, 4)
    mat_orig = obj.matrix_world
    mat = mat_orig * mat_sca
    _primitive.draw_shape_x_axis(mat, empty_size)
    _primitive.draw_shape_y_axis_neg(mat, empty_size)
    _primitive.draw_shape_z_axis(mat, empty_size)
    draw_shape_model_locator(mat, scs_globals)
    if not obj.scs_props.locator_preview_model_present:
        draw_model_box(mat_orig, scs_globals)
