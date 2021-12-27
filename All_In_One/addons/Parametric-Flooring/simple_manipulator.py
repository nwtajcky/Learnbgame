# -*- coding:utf-8 -*-

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

# ----------------------------------------------------------
# Author: Stephen Leger (s-leger)
#
# ----------------------------------------------------------
import bpy
import bgl
import blf
from math import sin, cos, atan2, pi
from mathutils import Vector, Matrix
from mathutils.geometry import intersect_line_plane, intersect_point_line, intersect_line_sphere
from bpy_extras import view3d_utils
from bpy.types import PropertyGroup
from bpy.props import EnumProperty, FloatVectorProperty, StringProperty, CollectionProperty, BoolProperty

# Arrow sizes (world units)
arrow_size = 0.1
# Handle area size (pixels)
handle_size = 10

# ------------------------------------------------------------------
# Define Gl Handle types
# ------------------------------------------------------------------


class Gl():
    """
        handle 3d -> 2d gl drawing
    """
    def __init__(self):
        self.width = 1
        self.pos_2d = Vector((0, 0))
        self.colour_active = (1.0, 0.0, 0.0, 1.0)
        self.colour_hover = (1.0, 1.0, 0.0, 1.0)
        self.colour_normal = (1.0, 1.0, 1.0, 1.0)
        self.colour_inactive = (0.0, 0.0, 0.0, 1.0)

    @property
    def colour(self):
        return self.colour_inactive

    def position_2d_from_coord(self, context, coord):
        """ coord given in local input coordsys
        """
        region = context.region
        rv3d = context.region_data
        loc = view3d_utils.location_3d_to_region_2d(region, rv3d, coord, self.pos_2d)
        return loc

    def _end(self):
        bgl.glEnd()
        bgl.glPopAttrib()
        bgl.glLineWidth(1)
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

    def _start_poly(self, colour):
        bgl.glPushAttrib(bgl.GL_ENABLE_BIT)
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glColor4f(*colour)
        bgl.glBegin(bgl.GL_POLYGON)

    def _start_line(self, colour, width=1):
        bgl.glPushAttrib(bgl.GL_ENABLE_BIT)
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glEnable(bgl.GL_LINE)
        bgl.glColor4f(*colour)
        bgl.glLineWidth(width)
        bgl.glBegin(bgl.GL_LINE_STRIP)

    def draw_text(self, text, x, y, angle, font_height, colour):
        # dirty fast assignment
        dpi, font_id = 72, 0
        bgl.glColor4f(*colour)
        blf.position(font_id, x, y, 0)
        blf.rotation(font_id, angle)
        blf.size(font_id, font_height, dpi)
        blf.draw(font_id, text)

    def draw(self, context):
        gl_type = type(self).__name__
        if 'Handle' in gl_type:
            self._start_poly(self.colour)
        elif gl_type in ['GlLine', 'GlArc']:
            self._start_line(self.colour, self.width)
        if gl_type == 'GlText':
            x, y = self.position_2d_from_coord(context, self.pts[0])
            self.draw_text(self.txt, x, y, self.angle, self.font_height, self.colour)
        else:
            for pt in self.pts:
                x, y = self.position_2d_from_coord(context, pt)
                bgl.glVertex2f(x, y)
            self._end()


class GlText(Gl):

    def __init__(self, round=2, label='', z_axis=Vector((0, 0, 1))):
        self.z_axis = z_axis
        self.value = 0
        self.round = round
        self.label = label
        self.font_height = 16
        Gl.__init__(self)

    @property
    def angle(self):
        return 0

    @property
    def pts(self):
        return [self.pos_3d]

    @property
    def txt(self):
        return self.label + str(round(self.value, self.round))

    def set_pos(self, context, value, pos_3d, direction, normal=Vector((0, 0, 1))):
        self.up_axis = direction.normalized()
        self.c_axis = self.up_axis.cross(normal)
        self.pos_3d = pos_3d
        self.value = value


class GlLine(Gl):

    def __init__(self, z_axis=Vector((0, 0, 1))):
        self.z_axis = z_axis
        self.p = Vector((0, 0, 0))
        self.v = Vector((0, 0, 0))
        Gl.__init__(self)

    @property
    def length(self):
        return self.v.length

    @property
    def angle(self):
        return atan2(self.v.y, self.v.x)

    @property
    def cross(self):
        return self.v.cross(self.z_axis)

    def normal(self, t=0):
        # perpendiculaire a droite du segment
        n = GlLine()
        n.p = self.lerp(t)
        n.v = self.cross
        return n

    def sized_normal(self, t, size):
        n = GlLine()
        n.p = self.lerp(t)
        n.v = size * self.cross.normalized()
        return n

    def lerp(self, t):
        return self.p + self.v * t

    def offset(self, offset):
        """
            offset > 0 on the right part
        """
        self.p += offset * self.cross.normalized()

    @property
    def pts(self):
        p0 = self.p
        p1 = self.p + self.v
        return [p0, p1]


class GlCircle(Gl):

    def __init__(self):
        self.r = 0
        self.c = Vector((0, 0, 0))
        Gl.__init__(self)


class GlArc(GlCircle):

    def __init__(self, z_axis=Vector((0, 0, 1))):
        """
            a0 and da arguments are in radians
            a0 = 0   on the right side
            a0 = pi on the left side
            da > 0 CCW contrary-clockwise
            da < 0 CW  clockwise
            stored internally as radians
        """
        GlCircle.__init__(self)
        if z_axis.z < 1:
            x_axis = z_axis.cross(Vector((0, 0, 1)))
            y_axis = x_axis.cross(z_axis)
        else:
            x_axis = Vector((1, 0, 0))
            y_axis = Vector((0, 1, 0))
        self.rM = Matrix([
            x_axis,
            y_axis,
            z_axis
        ])
        self.z_axis = z_axis
        self.a0 = 0
        self.da = 0

    @property
    def length(self):
        return self.r * abs(self.da)

    def normal(self, t=0):
        """
            always on the right side
        """
        n = GlLine(z_axis=self.z_axis)
        n.p = self.lerp(t)
        if self.da < 0:
            n.v = self.c - n.p
        else:
            n.v = n.p - self.c
        return n

    def sized_normal(self, t, size):
        n = GlLine(z_axis=self.z_axis)
        n.p = self.lerp(t)
        if self.da < 0:
            n.v = size * (self.c - n.p).normalized()
        else:
            n.v = size * (n.p - self.c).normalized()
        return n

    def lerp(self, t):
        a = self.a0 + t * self.da
        return self.c + self.rM * Vector((self.r * cos(a), self.r * sin(a), 0))

    def tangeant(self, t, length):
        a = self.a0 + t * self.da
        ca = cos(a)
        sa = sin(a)
        n = GlLine()
        n.p = self.c + self.rM * Vector((self.r * ca, self.r * sa, 0))
        n.v = self.rM * Vector((length * sa, -length * ca, 0))
        if self.da > 0:
            n.v = -n.v
        return n

    def offset(self, offset):
        """
            offset > 0 on the right part
        """
        if self.da > 0:
            radius = self.r + offset
        else:
            radius = self.r - offset
        return GlArc(self.c, radius, self.a0, self.da, z_axis=self.z_axis)

    @property
    def pts(self):
        n_pts = max(1, int(round(abs(self.da) / pi * 30, 0)))
        t_step = 1 / n_pts
        return [self.lerp(i * t_step) for i in range(n_pts + 1)]


class GlHandle(Gl):

    def __init__(self, sensor_size, size, selectable=False):
        """
            sensor_size : 2d size in pixels of sensor area
            size : 3d size of handle
        """
        self.size = size
        self.sensor_size = sensor_size
        self.pos_3d = Vector((0, 0, 0))
        self.up_axis = Vector((0, 0, 0))
        self.c_axis = Vector((0, 0, 0))
        self.hover = False
        self.active = False
        self.selectable = selectable
        Gl.__init__(self)

    def set_pos(self, context, pos_3d, direction, normal=Vector((0, 0, 1))):
        self.up_axis = direction.normalized()
        self.c_axis = self.up_axis.cross(normal)
        self.pos_3d = pos_3d
        self.pos_2d = self.position_2d_from_coord(context, pos_3d)

    def check_hover(self, pos_2d):
        dp = pos_2d - self.pos_2d
        self.hover = abs(dp.x) < self.sensor_size and abs(dp.y) < self.sensor_size

    @property
    def pts(self):
        raise NotImplementedError

    @property
    def colour(self):
        if self.selectable:
            if self.active:
                return self.colour_active
            elif self.hover:
                return self.colour_hover
            return self.colour_normal
        else:
            return self.colour_inactive


class SquareHandle(GlHandle):

    def __init__(self, sensor_size, size, selectable=False):
        GlHandle.__init__(self, sensor_size, size, selectable)

    @property
    def pts(self):
        n = self.up_axis
        c = self.c_axis
        x = n * self.size / 2
        y = c * self.size / 2
        return [self.pos_3d - x - y, self.pos_3d + x - y, self.pos_3d + x + y, self.pos_3d - x + y]


class TriHandle(GlHandle):

    def __init__(self, sensor_size, size, selectable=False):
        GlHandle.__init__(self, sensor_size, size, selectable)

    @property
    def pts(self):
        n = self.up_axis
        c = self.c_axis
        x = n * self.size
        y = c * self.size / 2
        return [self.pos_3d - x + y, self.pos_3d - x - y, self.pos_3d]


# ------------------------------------------------------------------
# Define Manipulators
# ------------------------------------------------------------------


class Manipulator():

    def __init__(self, context, o, datablock, glprovider):
        """
            o : object to manipulate
            datablock : object data to manipulate
            glprovider: object simple_manipulator datablock (tM)
        """
        self.o = o
        self.datablock = datablock
        self.glprovider = glprovider
        self.origin = Vector((0, 0, 1))
        self.mouse_pos = Vector((0, 0))
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback, args, 'WINDOW', 'POST_PIXEL')

    def exit(self):
        # print("Manipulator.exit() %s" % (type(self).__name__))
        if self._handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        self.o = None
        self.datablock = None
        self.glprovider = None
        self._handle = None

    def press(self):
        raise NotImplementedError

    def release(self):
        raise NotImplementedError

    def mouse_move(self):
        raise NotImplementedError

    def modal(self, context, event):
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            return self.press(context, event)
        elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            return self.release(context, event)
        elif event.type == 'MOUSEMOVE':
            return self.mouse_move(context, event)
        return False

    def mouse_position(self, event):
        self.mouse_pos.x, self.mouse_pos.y = event.mouse_region_x, event.mouse_region_y

    def get_pos3d(self, context):
        """
            convert mouse pos to 3d point over plane defined by origin and normal
        """
        region = context.region
        rv3d = context.region_data
        rM = context.active_object.matrix_world.to_3x3()
        view_vector_mouse = view3d_utils.region_2d_to_vector_3d(region, rv3d, self.mouse_pos)
        ray_origin_mouse = view3d_utils.region_2d_to_origin_3d(region, rv3d, self.mouse_pos)
        pt = intersect_line_plane(ray_origin_mouse, ray_origin_mouse + view_vector_mouse,
            self.origin, rM * self.glprovider.normal, False)
        # attempt to fix issue with parallel plane
        if pt is None:
            pt = intersect_line_plane(ray_origin_mouse, ray_origin_mouse + view_vector_mouse,
                self.origin, view_vector_mouse, False)
        return pt

    def get_value(self, data, attr, index=-1):
        try:
            if index > -1:
                return getattr(data, attr)[index]
            else:
                return getattr(data, attr)
        except:
            return 0

    def set_value(self, context, data, attr, value, index=-1):
        try:
            if self.get_value(data, attr, index) != value:
                # switch context so unselected object may be manipulable too
                old = context.active_object
                state = self.o.select
                self.o.select = True
                context.scene.objects.active = self.o
                if index > -1:
                    getattr(data, attr)[index] = value
                else:
                    setattr(data, attr, value)
                self.o.select = state
                old.select = True
                context.scene.objects.active = old
        except:
            pass

    def preTranslate(self, tM, vec):
        return tM * Matrix([
        [1, 0, 0, vec.x],
        [0, 1, 0, vec.y],
        [0, 0, 1, vec.z],
        [0, 0, 0, 1]])

    def move(self, axis, value):
        if axis == 'x':
            tM = self.preTranslate(self.o.matrix_world, Vector((value, 0, 0)))
        elif axis == 'y':
            tM = self.preTranslate(self.o.matrix_world, Vector((0, value, 0)))
        else:
            tM = self.preTranslate(self.o.matrix_world, Vector((0, 0, value)))
        self.o.matrix_world = tM


class SizeManipulator(Manipulator):

    def __init__(self, context, o, datablock, glprovider, handle_size):
        self.handle_left = TriHandle(handle_size, arrow_size)
        self.handle_right = TriHandle(handle_size, arrow_size, selectable=True)
        self.line_0 = GlLine()
        self.line_1 = GlLine()
        self.line_2 = GlLine()
        self.label = GlText()
        Manipulator.__init__(self, context, o, datablock, glprovider)

    def check_hover(self):
        self.handle_right.check_hover(self.mouse_pos)

    def press(self, context, event):
        if self.handle_right.hover:
            self.handle_right.active = True
            return True
        return False

    def release(self, context, event):
        self.check_hover()
        self.handle_right.active = False
        return False

    def mouse_move(self, context, event):
        self.mouse_position(event)
        if self.handle_right.active:
            self.update(context, event)
            return True
        else:
            self.check_hover()
        return False

    def update(self, context, event):
        # 0  1  2
        # |_____|
        #
        pt = self.get_pos3d(context)
        pt, t = intersect_point_line(pt, self.line_0.p, self.line_2.p)
        length = (self.line_0.p - pt).length
        if event.alt:
            length = round(length, 1)
        self.set_value(context, self.datablock, self.glprovider.prop1_name, length)

    def draw_callback(self, _self, context):
        """
            draw on screen feedback using gl.
        """
        left, right, side, normal = self.glprovider.get_pts(self.o.matrix_world)
        self.origin = left
        self.line_1.p = left
        self.line_1.v = right - left
        self.line_0.z_axis = normal
        self.line_1.z_axis = normal
        self.line_2.z_axis = normal
        self.label.z_axis = normal
        self.line_0 = self.line_1.sized_normal(0, side.x * 1.1)
        self.line_2 = self.line_1.sized_normal(1, side.x * 1.1)
        self.line_1.offset(side.x * 1.0)
        self.handle_left.set_pos(context, self.line_1.p, -self.line_1.v, normal=normal)
        self.handle_right.set_pos(context, self.line_1.lerp(1), self.line_1.v, normal=normal)
        self.label.set_pos(context, self.line_1.length, self.line_1.lerp(0.5), self.line_1.v, normal=normal)
        self.label.draw(context)
        self.line_0.draw(context)
        self.line_1.draw(context)
        self.line_2.draw(context)
        self.handle_left.draw(context)
        self.handle_right.draw(context)


# ------------------------------------------------------------------
# Define a single Manipulator Properties to store on object
# ------------------------------------------------------------------


class simple_manipulator(PropertyGroup):
    """
        A property group to add to manipulable objects
        type: type of manipulator
        prop1_name = the property name of object to modify
        prop2_name = another property name of object to modify (angle and radius)
        p0, p1, p2 3d Vectors as base points to represent manipulators on screen
        normal Vector normal of plane on with draw manipulator
    """
    type = EnumProperty(
        items=(
            ('SIZE', 'Size', 'Generic size manipulator', 0),
            ('SIZE_LOC', 'Size Location', 'Generic size from border manipulator', 1),
            ('ANGLE', 'Angle', 'Angle between two vectors', 2),
            ('ARC_ANGLE_RADIUS', 'Arc based angle', '', 3),
            ('COUNTER', 'Counter increase and decrease', '', 4),
            ('DUMB_SIZE', 'Dumb Size', 'Generic size not editable', 5),
            ('DELTA_LOC', 'Delta location', 'Move object on an axis', 6)
        ),
        default='SIZE'
    )
    prop1_name = StringProperty()
    prop2_name = StringProperty()
    p0 = FloatVectorProperty(subtype='XYZ')
    p1 = FloatVectorProperty(subtype='XYZ')
    p2 = FloatVectorProperty(subtype='XYZ')
    normal = FloatVectorProperty(subtype='XYZ', default=(0, 0, 1))

    def set_pts(self, pts):
        self.p0, self.p1, self.p2 = pts

    def get_pts(self, tM):
        rM = tM.to_3x3()
        if self.type in ['SIZE', 'COUNTER', 'SIZE_LOC', 'DUMB_SIZE', 'DELTA_LOC']:
            return tM * self.p0, tM * self.p1, self.p2, rM * self.normal
        else:
            return tM * self.p0, rM * self.p1, rM * self.p2, rM * self.normal

    def setup(self, context, o, datablock):
        """
            Factory return a manipulator object
            o:         object
            datablock: datablock to modify
        """
        global handle_size
        if self.type == 'SIZE':
            return SizeManipulator(context, o, datablock, self, handle_size)
        elif self.type == 'SIZE_LOC':
            return SizeLocationManipulator(context, o, datablock, self, handle_size)
        elif self.type == 'ANGLE':
            return AngleManipulator(context, o, datablock, self, handle_size)
        elif self.type == 'ARC_ANGLE_RADIUS':
            return ArcAngleRadiusManipulator(context, o, datablock, self, handle_size)
        elif self.type == 'COUNTER':
            return CounterManipulator(context, o, datablock, self, handle_size)
        elif self.type == 'DUMB_SIZE':
            return DumbSizeManipulator(context, o, datablock, self, handle_size)
        elif self.type == 'DELTA_LOC':
            return DeltaLocationManipulator(context, o, datablock, self, handle_size)


bpy.utils.register_class(simple_manipulator)

# a global manipulator stack reference for use
# as fallback when internal one loose reference.
# prevent Blender "ACCESS_VIOLATION" crashes
# NOTE: use a dict here to prevent potential
# collisions between many objects being in
# manipulate mode (at create time)
manip_stack = []

# ------------------------------------------------------------------
# Define Manipulable to make a PropertyGroup manipulable
# ------------------------------------------------------------------


class Manipulable():
    """
        A class extending PropertyGroup to setup gl manipulators
        Beware : prevent crash calling manipulable_disable()
                 before changing manipulated data
    """
    manipulators = CollectionProperty(
            type=simple_manipulator,
            description="store 3d points to draw gl manipulators"
            )
    manipulable_refresh = BoolProperty(
            default=False,
            description="Flag enable to rebuild manipulators when data model change"
            )

    def manipulable_disable(self, context):
        """
            disable gl draw handlers
        """
        global manip_stack

        if not hasattr(self, "manip_stack"):
            # prevent blender crash by loosing reference on this one
            self.manip_stack = manip_stack

        for m in self.manip_stack:
            m.exit()

        self.manip_stack = []
        manip_stack = self.manip_stack

    def manipulable_setup(self, context):
        """
            TODO: Implement the setup part as per parent object basis
        """
        self.manipulable_disable(context)
        o = context.active_object
        for m in self.manipulators:
            self.manip_stack.append(m.setup(context, o, self))

    def manipulable_invoke(self, context):
        """
            call this in operator invoke()
        """
        self.manip_stack = []
        self.manipulable_setup(context)

    def manipulable_modal(self, context, event):
        """
            call in operator modal()
        """
        # setup again when manipulators type change
        if self.manipulable_refresh:
            self.manipulable_refresh = False
            self.manipulable_setup(context)

        context.area.tag_redraw()

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.manipulable_disable(context)
            self.manipulable_exit(context)
            return {'FINISHED'}

        for m in self.manip_stack:
            if m.modal(context, event):
                self.manipulable_manipulate(context, type=type(m).__name__)
                return {'RUNNING_MODAL'}

        # allow any action on release
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            self.manipulable_release(context)

        return {'PASS_THROUGH'}

    # Callbacks
    def manipulable_release(self, context):
        """
            Override with action to do on mouse release
            eg: big update
        """
        return

    def manipulable_exit(self, context):
        """
            Override with action to do when modal exit
        """
        return

    def manipulable_manipulate(self, context, type='None'):
        """
            Override with action to do when a handle is active (pressed and mousemove)
        """
        return
