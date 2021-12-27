# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Commotion motion graphics add-on for Blender.
#  Copyright (C) 2014-2018  Mikhail Rachinskiy
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
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


from bpy.types import Operator
from bpy.props import FloatProperty, BoolProperty


class OBJECT_OT_commotion_slow_parent_offset(Operator):
    bl_label = "Commotion Offset Slow Parent"
    bl_description = "Offset Slow Parent property for selected objects"
    bl_idname = "object.commotion_slow_parent_offset"
    bl_options = {"REGISTER", "UNDO"}

    offset = FloatProperty(name="Offset Factor", default=1, min=0, step=10, precision=3)

    def execute(self, context):
        obs = []
        app = obs.append
        offset = 1.0

        for ob in context.selected_objects:
            if ob.parent:
                distance = (ob.parent.matrix_world.translation - ob.matrix_world.translation).length
                app((ob, distance))

        for ob, _ in sorted(obs, key=lambda x: x[1]):
            ob.use_slow_parent = True
            ob.slow_parent_offset = offset
            offset += self.offset

        return {"FINISHED"}

    def invoke(self, context, event):
        props = context.scene.commotion
        self.offset = props.slow_parent_offset

        return self.execute(context)


class OBJECT_OT_commotion_slow_parent_toggle(Operator):
    bl_label = "Commotion Toggle Slow Parent"
    bl_description = "Toggle Slow Parent property on or off for selected objects"
    bl_idname = "object.commotion_slow_parent_toggle"
    bl_options = {"REGISTER", "UNDO"}

    enable = BoolProperty(name="Enable", options={"SKIP_SAVE"})

    def execute(self, context):
        for ob in context.selected_objects:
            if ob.parent:
                ob.use_slow_parent = self.enable

        return {"FINISHED"}
