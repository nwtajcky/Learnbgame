bl_info = {
    "name": "OpenStreetMap Georeferencing",
    "author": "Vladimir Elistratov <vladimir.elistratov@gmail.com>",
    "version": (1, 0, 2),
    "blender": (2, 7, 8),
    "location": "View 3D > Object Mode > Tool Shelf",
    "description": "OpenStreetMap based object georeferencing",
    "warning": "",
    "wiki_url": "https://github.com/vvoovv/blender-tools/wiki/OpenStreetMap-Georeferencing",
    "tracker_url": "https://github.com/vvoovv/blender-tools/issues",
    "support": "COMMUNITY",
    "category": "Learnbgame",
}

import bpy
import math
from mathutils import Vector

# see conversion formulas at
# http://en.wikipedia.org/wiki/Transverse_Mercator_projection
# and
# http://mathworld.wolfram.com/MercatorProjection.html
class TransverseMercator:
    radius = 6378137.

    def __init__(self, **kwargs):
        # setting default values
        self.lat = 0. # in degrees
        self.lon = 0. # in degrees
        self.k = 1. # scale factor
        
        for attr in kwargs:
            setattr(self, attr, kwargs[attr])
        self.latInRadians = math.radians(self.lat)

    def fromGeographic(self, lat, lon):
        lat = math.radians(lat)
        lon = math.radians(lon-self.lon)
        B = math.sin(lon) * math.cos(lat)
        x = 0.5 * self.k * self.radius * math.log((1.+B)/(1.-B))
        y = self.k * self.radius * ( math.atan(math.tan(lat)/math.cos(lon)) - self.latInRadians )
        return (x,y)

    def toGeographic(self, x, y):
        x = x/(self.k * self.radius)
        y = y/(self.k * self.radius)
        D = y + self.latInRadians
        lon = math.atan(math.sinh(x)/math.cos(D))
        lat = math.asin(math.sin(D)/math.cosh(x))

        lon = self.lon + math.degrees(lon)
        lat = math.degrees(lat)
        return (lat, lon)


class OsmGeoreferencingPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Geo"
    bl_label = "Georeferencing"
    
    def draw(self, context):
        wm = context.window_manager
        layout = self.layout
        
        layout.row().operator("object.set_original_position")
        row = layout.row()
        if not (
            # the original position is set
            "_x" in wm and "_y" in wm and "_h" in wm and
            # custom properties "lat" and "lon" are set for the active scene
            "lat" in context.scene and "lon" in context.scene and
            # objects belonging to the model are selected
            len(context.selected_objects)>0
        ):
            row.enabled = False
        row.operator("object.do_georeferencing")

class SetOriginalPosition(bpy.types.Operator):
    bl_idname = "object.set_original_position"
    bl_label = "Set original position"
    bl_description = "Remember original position"

    def execute(self, context):
        if len(context.selected_objects)==0:
            self.report({"ERROR"}, "Select objects belonging to your model")
            return {"FINISHED"}
        wm = context.window_manager
        # remember the location and orientation of the active object
        o = context.scene.objects.active
        wm["_x"] = o.location.x
        wm["_y"] = o.location.y
        wm["_h"] = o.rotation_euler[2]
        return {"FINISHED"}

class DoGeoreferencing(bpy.types.Operator):
    bl_idname = "object.do_georeferencing"    
    bl_label = "Perform georeferencing"
    bl_description = "Perform georeferencing"
    bl_options = {"UNDO"}

    def execute(self, context):
        wm = context.window_manager
        scene = context.scene
        o = scene.objects.active
        # calculationg the new position of the active object center
        v = -Vector((wm["_x"], wm["_y"], o.location.z))
        p = o.matrix_world * v
        projection = TransverseMercator(lat=scene["lat"], lon=scene["lon"])
        (lat, lon) = projection.toGeographic(p[0], p[1])
        scene["lat"] = lat
        scene["lon"] = lon
        scene["heading"] = (o.rotation_euler[2]-wm["_h"])*180/math.pi
        
        # restoring original objects location and orientation
        bpy.ops.transform.rotate(value=-(o.rotation_euler[2]-wm["_h"]), axis=(0,0,1))
        bpy.ops.transform.translate(value=-(o.location+v))
        # cleaning up
        del wm["_x"], wm["_y"], wm["_h"]
        return {"FINISHED"}


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

