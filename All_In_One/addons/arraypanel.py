bl_info = {
    "name": "Cursor Array",
    "category": "Learnbgame",
}

import bpy
from bpy import *


class ObjectCursorArray(bpy.types.Operator):
    """Object Cursor Array"""
    bl_idname = "object.cursor_array"
    bl_label = "Linear Array"
    bl_options = {'REGISTER', 'UNDO'}
    
    scn = context.window_manager
    
    ''' IDK WHY BUT THIS WORKS ONLY IF YOU UNCOMMENT THE # below and comment the code of total below that, run it like that. And then undo the steps and run.   '''
    #total = bpy.props.IntProperty(name="Steps", default=2, min=1, max=100)
    total = bpy.context.window_manager.num

    def execute(self, context):
        scene = context.scene
        cursor = scene.cursor_location
       
        obj = scene.objects.active

        for i in range(self.total):
            obj_new = obj.copy()
            scene.objects.link(obj_new)

            factor = i / self.total
            #obj_new.location = (obj.location * factor) + (cursor * (1.0 - factor))
            obj_new.location = obj.location 
            obj_new.location.x += context.window_manager.Space[0]*factor
            obj_new.location.y += context.window_manager.Space[1]*factor
            obj_new.location.z += context.window_manager.Space[2]*factor

        return {'FINISHED'}
    
    
class HelloWorldPanel(bpy.types.Panel):
    bl_label = "MoGraph: LinearArray Cloner"
    bl_idname = "OBJECT_PT_hello"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        scn = context.window_manager
        
        layout = self.layout

        obj = context.object
        
        row = layout.row()
        row.prop(scn, "num")
 
        
        row=layout.row()
        row.prop(scn, "Space")
        
        row = layout.row()
        row.operator("object.cursor_array")



def menu_func(self, context):
    self.layout.operator(ObjectCursorArray.bl_idname)


def register():
    bpy.utils.register_class(ObjectCursorArray)
    bpy.utils.register_class(HelloWorldPanel)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
  

    bpy.utils.unregister_class(ObjectCursorArray)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    bpy.utils.unregister_class(HelloWorldPanel)

if __name__ == "__main__":
    bpy.types.WindowManager.num = bpy.props.IntProperty(name="Number of instances:", description = "Number of Cloner Objects to be created", default = 3, min = 1)
   
    bpy.types.WindowManager.Space = bpy.props.FloatVectorProperty(name="Spacing")

    register()