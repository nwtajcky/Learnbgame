#  ***** GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
#  ***** GPL LICENSE BLOCK *****

import bpy
from . import internal

class Fillet(bpy.types.Operator):
    bl_idname = 'curve.bezier_cad_fillet'
    bl_description = bl_label = 'Fillet'
    bl_options = {'REGISTER', 'UNDO'}

    radius: bpy.props.FloatProperty(name='Radius', description='Radius of the rounded corners', unit='LENGTH', default=0.1)

    @classmethod
    def poll(cls, context):
        return internal.curveObject()

    def execute(self, context):
        splines = internal.bezierSelectedSplines(True, True, True)
        if len(splines) == 0:
            self.report({'WARNING'}, 'Nothing selected')
            return {'CANCELLED'}
        for spline in splines:
            internal.filletSpline(spline, self.radius)
            bpy.context.object.data.splines.remove(spline)
        return {'FINISHED'}

class Boolean(bpy.types.Operator):
    bl_idname = 'curve.bezier_cad_boolean'
    bl_description = bl_label = 'Boolean'
    bl_options = {'REGISTER', 'UNDO'}

    operation: bpy.props.EnumProperty(name='Type', items=[
        ('UNION', 'Union', 'Boolean OR', 0),
        ('INTERSECTION', 'Intersection', 'Boolean AND', 1),
        ('DIFFERENCE', 'Difference', 'Active minus Selected', 2)
    ])

    @classmethod
    def poll(cls, context):
        return internal.curveObject()

    def execute(self, context):
        if bpy.context.object.data.dimensions != '2D':
            self.report({'WARNING'}, 'Can only be applied in 2D')
            return {'CANCELLED'}
        splines = internal.bezierSelectedSplines(True, True)
        if len(splines) != 2:
            self.report({'WARNING'}, 'Invalid selection')
            return {'CANCELLED'}
        bpy.ops.curve.spline_type_set(type='BEZIER')
        splineA = bpy.context.object.data.splines.active
        splineB = splines[0] if (splines[1] == splineA) else splines[1]
        if not internal.bezierBooleanGeometry(splineA, splineB, self.operation):
            self.report({'WARNING'}, 'Invalid selection')
            return {'CANCELLED'}
        return {'FINISHED'}

class Intersection(bpy.types.Operator):
    bl_idname = 'curve.bezier_cad_intersection'
    bl_description = bl_label = 'Intersection'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return internal.curveObject()

    def execute(self, context):
        segments = internal.bezierSegments(bpy.context.object.data.splines, True)
        if len(segments) < 2:
            self.report({'WARNING'}, 'Invalid selection')
            return {'CANCELLED'}

        internal.bezierMultiIntersection(segments)
        return {'FINISHED'}

class MergeEnds(bpy.types.Operator):
    bl_idname = 'curve.bezier_cad_merge_ends'
    bl_description = bl_label = 'Merge Ends'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return internal.curveObject()

    def execute(self, context):
        points = []
        selected_splines = []
        is_last_point = []
        for spline in bpy.context.object.data.splines:
            if spline.type != 'BEZIER' or spline.use_cyclic_u:
                continue
            if spline.bezier_points[0].select_control_point:
                points.append(spline.bezier_points[0])
                selected_splines.append(spline)
                is_last_point.append(False)
            if spline.bezier_points[-1].select_control_point:
                points.append(spline.bezier_points[-1])
                selected_splines.append(spline)
                is_last_point.append(True)

        if len(points) != 2:
            self.report({'WARNING'}, 'Invalid selection')
            return {'CANCELLED'}

        points[0].handle_left_type = 'FREE'
        points[0].handle_right_type = 'FREE'
        new_co = (points[0].co+points[1].co)*0.5

        handle = (points[1].handle_left if is_last_point[1] else points[1].handle_right)+new_co-points[1].co
        if is_last_point[0]:
            points[0].handle_left += new_co-points[0].co
            points[0].handle_right = handle
        else:
            points[0].handle_right += new_co-points[0].co
            points[0].handle_left = handle
        points[0].co = new_co

        bpy.ops.curve.select_all(action='DESELECT')
        points[1].select_control_point = True
        bpy.ops.curve.delete()
        selected_splines[0].bezier_points[-1 if is_last_point[0] else 0].select_control_point = True
        selected_splines[1].bezier_points[-1 if is_last_point[1] else 0].select_control_point = True
        bpy.ops.curve.make_segment()
        bpy.ops.curve.select_all(action='DESELECT')
        return {'FINISHED'}

class Subdivide(bpy.types.Operator):
    bl_idname = 'curve.bezier_cad_subdivide'
    bl_description = bl_label = 'Subdivide'
    bl_options = {'REGISTER', 'UNDO'}

    params: bpy.props.StringProperty(name='Params', default='0.25 0.5 0.75')

    @classmethod
    def poll(cls, context):
        return internal.curveObject()

    def execute(self, context):
        segments = internal.bezierSegments(bpy.context.object.data.splines, True)
        if len(segments) == 0:
            self.report({'WARNING'}, 'Nothing selected')
            return {'CANCELLED'}

        cuts = []
        for param in self.params.split(' '):
            cuts.append({'param': max(0.0, min(float(param), 1.0))})
        cuts.sort(key=(lambda cut: cut['param']))
        for segment in segments:
            segment['cuts'].extend(cuts)
        internal.subdivideBezierSegments(segments)
        return {'FINISHED'}

class Array(bpy.types.Operator):
    bl_idname = 'curve.bezier_cad_array'
    bl_description = bl_label = 'Array'
    bl_options = {'REGISTER', 'UNDO'}

    offset: bpy.props.FloatVectorProperty(name='Offset', unit='LENGTH', description='Vector between to copies', subtype='DIRECTION', default=(0.0, 0.0, -1.0), size=3)
    count: bpy.props.IntProperty(name='Count', description='Number of copies', min=1, default=2)
    connect: bpy.props.BoolProperty(name='Connect', description='Concatenate individual copies', default=False)
    serpentine: bpy.props.BoolProperty(name='Serpentine', description='Switch direction of every second copy', default=False)

    @classmethod
    def poll(cls, context):
        return internal.curveObject()

    def execute(self, context):
        splines = internal.bezierSelectedSplines(True, True)
        if len(splines) == 0:
            self.report({'WARNING'}, 'Nothing selected')
            return {'CANCELLED'}
        internal.arrayModifier(splines, self.offset, self.count, self.connect, self.serpentine)
        return {'FINISHED'}

class Circle(bpy.types.Operator):
    bl_idname = 'curve.bezier_cad_circle'
    bl_description = bl_label = 'Circle'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return internal.curveObject()

    def execute(self, context):
        segments = internal.bezierSegments(bpy.context.object.data.splines, True)
        if len(segments) != 1:
            self.report({'WARNING'}, 'Invalid selection')
            return {'CANCELLED'}

        circle = internal.circleOfBezier(internal.bezierSegmentPoints(segments[0]['beginPoint'], segments[0]['endPoint']))
        if circle == None:
            self.report({'WARNING'}, 'Not a circle')
            return {'CANCELLED'}

        bpy.ops.curve.primitive_bezier_circle_add(radius=circle.radius, location=circle.center, rotation=circle.plane.normal.to_track_quat('Z', 'X').to_euler())
        return {'FINISHED'}

class Length(bpy.types.Operator):
    bl_idname = 'curve.bezier_cad_length'
    bl_description = bl_label = 'Length'

    @classmethod
    def poll(cls, context):
        return internal.curveObject()

    def execute(self, context):
        segments = internal.bezierSegments(bpy.context.object.data.splines, True)
        if len(segments) == 0:
            self.report({'WARNING'}, 'Nothing selected')
            return {'CANCELLED'}

        length = 0
        for segment in segments:
            length += internal.bezierLength(internal.bezierSegmentPoints(segment['beginPoint'], segment['endPoint']))
        self.report({'INFO'}, bpy.utils.units.to_string(bpy.context.scene.unit_settings.system, 'LENGTH', length))
        return {'FINISHED'}

operators = [Fillet, Boolean, Intersection, MergeEnds, Subdivide, Array, Circle, Length]
