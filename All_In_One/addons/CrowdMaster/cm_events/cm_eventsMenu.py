# Copyright 2019 CrowdMaster Development Team
#
# ##### BEGIN GPL LICENSE BLOCK ######
# This file is part of CrowdMaster.
#
# CrowdMaster is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CrowdMaster is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CrowdMaster.  If not, see <http://www.gnu.org/licenses/>.
# ##### END GPL LICENSE BLOCK #####

import bpy
from bpy.props import (CollectionProperty, EnumProperty, IntProperty,
                       PointerProperty, StringProperty)
from bpy.types import Operator, Panel, PropertyGroup, UIList


class event_entry(PropertyGroup):
    """The data structure for the event entries"""
    eventname = StringProperty()
    timeMin = IntProperty(name="Time Min", min=0, default=1)
    timeMax = IntProperty(name="Time Max", min=0, default=10)
    index = IntProperty(min=0)
    category = EnumProperty(items=(
        ("Time", "Time", "Time"),
        ("Volume", "Volume", "Volume"),
        ("Time+Volume", "Time+Volume", "Time+Volume"))
                           )
    volumeType = EnumProperty(name="Volume Type",
                              items=(("Object", "Object", "Object"),
                                     ("Group", "Group", "Group")),
                              default="Object")
    volume = StringProperty(name="Volume")


class events_collection(PropertyGroup):
    coll: CollectionProperty(type=event_entry)
    index: IntProperty()


class SCENE_OT_cm_events_populate(Operator):
    bl_idname = "scene.cm_events_populate"
    bl_label = "Populate CM events list"

    def execute(self, context):
        context.scene.cm_events.coll.add()
        return {'FINISHED'}


class SCENE_OT_event_remove(Operator):
    bl_idname = "scene.cm_events_remove"
    bl_label = "Remove"

    @classmethod
    def poll(cls, context):
        s = context.scene
        return len(s.cm_events.coll) > s.cm_events.index >= 0

    def execute(self, context):
        s = context.scene
        s.cm_events.coll.remove(s.cm_events.index)
        if s.cm_events.index > 0:
            s.cm_events.index -= 1
        return {'FINISHED'}


class SCENE_OT_event_move(Operator):
    bl_idname = "scene.cm_events_move"
    bl_label = "Move"

    direction: EnumProperty(items=(
        ('UP', "Up", "Move up"),
        ('DOWN', "Down", "Move down"))
                            )

    @classmethod
    def poll(cls, context):
        s = context.scene
        return len(s.cm_events.coll) > s.cm_events.index >= 0

    def execute(self, context):
        s = context.scene
        d = -1 if self.direction == 'UP' else 1
        new_index = (s.cm_events.index + d) % len(s.cm_events.coll)
        s.cm_events.coll.move(s.cm_events.index, new_index)
        s.cm_events.index = new_index
        return {'FINISHED'}


class SCENE_UL_event(UIList):
    """for drawing each row"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "eventname", text="")
            layout.prop(item, "category", text="")
            if item.category == "Time" or item.category == "Time+Volume":
                layout.prop(item, "timeMin", text="Start")
                layout.prop(item, "timeMax", text="End")
            if item.category == "Volume" or item.category == "Time+Volume":
                layout.prop(item, "volumeType")
                if item.volumeType == "Object":
                    layout.prop_search(item, "volume", bpy.data, "objects")
                elif item.volumeType == "Group":
                    layout.prop_search(
                        item, "volume", bpy.data, "groups", text="Volumes")
            # this draws each row in the list. Each line is a widget
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)
            # no idea when this is actually used


class SCENE_PT_event(Panel):
    """Creates CrowdMaster Panel in the node editor"""
    bl_label = "Events"
    bl_idname = "SCENE_PT_event"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Simulation"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        try:
            return context.space_data.tree_type == 'CrowdMasterTreeType', context.space_data.tree_type == 'CrowdMasterGenTreeType'
        except (AttributeError, KeyError, TypeError):
            return False

    def draw(self, context):
        layout = self.layout
        sce = context.scene

        row = layout.row()
        row.template_list("SCENE_UL_event", "", sce.cm_events,
                          "coll", sce.cm_events, "index")

        col = row.column()
        sub = col.column(align=True)
        blid_ap = SCENE_OT_cm_events_populate.bl_idname
        sub.operator(blid_ap, text="", icon="ADD")
        blid_ar = SCENE_OT_event_remove.bl_idname
        sub.operator(blid_ar, text="", icon="REMOVE")

        sub = col.column(align=True)
        sub.separator()
        blid_am = SCENE_OT_event_move.bl_idname
        sub.operator(blid_am, text="", icon="TRIA_UP").direction = 'UP'
        sub.operator(blid_am, text="", icon="TRIA_DOWN").direction = 'DOWN'


def event_register():
    bpy.utils.register_class(event_entry)
    bpy.utils.register_class(SCENE_OT_cm_events_populate)
    bpy.utils.register_class(SCENE_OT_event_remove)
    bpy.utils.register_class(SCENE_OT_event_move)
    bpy.utils.register_class(events_collection)
    bpy.utils.register_class(SCENE_UL_event)
    bpy.utils.register_class(SCENE_PT_event)
    bpy.types.Scene.cm_events = PointerProperty(type=events_collection)


def event_unregister():
    bpy.utils.unregister_class(SCENE_UL_event)
    bpy.utils.unregister_class(SCENE_PT_event)
    bpy.utils.unregister_class(SCENE_OT_event_move)
    bpy.utils.unregister_class(SCENE_OT_event_remove)
    bpy.utils.unregister_class(SCENE_OT_cm_events_populate)
    bpy.utils.unregister_class(events_collection)
    bpy.utils.unregister_class(event_entry)
