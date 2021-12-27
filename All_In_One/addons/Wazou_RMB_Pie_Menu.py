﻿# ##### BEGIN GPL LICENSE BLOCK #####
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

bl_info = {
    "name": "Wazou Right clic Pie Menu",
    "author": "Cédric Lepiller",
    "version": (0, 1, 2),
    "blender": (2, 7, 1),
    "location": "View3D > RMB",
    "description": "Right Click Pie Menu",
    "category": "Learnbgame",
}

"""
Right Click Pie Menu
This adds a the Right Click Pie Menu in the View3D.
Left mouse is SELECTION.
Left Alt + Double click sets the 3D cursor.

"""

import bpy
import bmesh
from bpy.types import Menu
from bpy.props import IntProperty, FloatProperty, BoolProperty
from bl_ui.properties_paint_common import (
        UnifiedPaintPanel,
        brush_texture_settings,
        brush_texpaint_common,
        brush_mask_texture_settings,
        )

########################
#      Properties      #               
########################

class WazouRightMenuPiePrefs(bpy.types.AddonPreferences):
    """Creates the tools in a Panel, in the scene context of the properties editor"""
    bl_idname = __name__

    bpy.types.Scene.Enable_Tab_RMB_01 = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.Enable_Tab_RMB_02 = bpy.props.BoolProperty(default=False)
    
    def draw(self, context):
        layout = self.layout
        
        layout.prop(context.scene, "Enable_Tab_RMB_01", text="Shortcuts", icon="QUESTION")  
        if context.scene.Enable_Tab_RMB_01:
            row = layout.row()
            layout.label(text="– Object/Edit mode > RMB")
            layout.label(text="– Cusor > Alt + double clic")
            
        layout.prop(context.scene, "Enable_Tab_RMB_02", text="URL's", icon="URL") 
        if context.scene.Enable_Tab_RMB_02:
            row = layout.row()    
            
            row.operator("wm.url_open", text="Pitiwazou.com").url = "http://www.pitiwazou.com/"
            row.operator("wm.url_open", text="Wazou's Ghitub").url = "https://github.com/pitiwazou/Scripts-Blender"
            row.operator("wm.url_open", text="BlenderLounge Forum ").url = "http://blenderlounge.fr/forum/"      
            
#######################
#       Classes       #               
#######################

# Add Mesh #
class AddMenu(bpy.types.Menu):
    bl_label = "Add Mesh"
    
    def draw(self, context):
        layout = self.layout
        
        layout.operator("mesh.primitive_cube_add", text="Cube", icon='MESH_CUBE')
        layout.operator("mesh.primitive_plane_add", text="Plane", icon='MESH_PLANE')
        layout.operator("mesh.primitive_uv_sphere_add", text="UV Sphere", icon='MESH_UVSPHERE')
        layout.operator("mesh.primitive_cylinder_add", text="Cylinder", icon='MESH_CYLINDER')
        layout.operator("mesh.primitive_grid_add", text="Grid", icon='MESH_GRID')
        layout.operator("mesh.primitive_ico_sphere_add", text="Ico Sphere", icon='MESH_ICOSPHERE')
        layout.operator("mesh.primitive_circle_add", text="Circle", icon='MESH_CIRCLE')
        layout.operator("mesh.primitive_cone_add", text="Cone", icon='MESH_CONE')
        layout.operator("mesh.primitive_torus_add", text="Torus", icon='MESH_TORUS')
        layout.operator("mesh.primitive_monkey_add", text="Monkey", icon='MESH_MONKEY')
        layout.separator()
        layout.operator("object.camera_add", icon='OUTLINER_OB_CAMERA')
        layout.separator()  
        layout.operator("object.lamp_add", text="Area", icon='LAMP_AREA').type = 'AREA'
        layout.operator("object.lamp_add", text="Sun", icon='LAMP_SUN').type = 'SUN'
        layout.operator("object.lamp_add", text="Hemi", icon='LAMP_HEMI').type = 'HEMI'
        layout.operator("object.lamp_add", text="Point", icon='LAMP_POINT').type = 'POINT'
        layout.operator("object.lamp_add", text="Spot", icon='LAMP_SPOT').type = 'SPOT'
        layout.separator()
        layout.operator("curve.primitive_bezier_circle_add", icon='CURVE_BEZCIRCLE')
        layout.operator("curve.primitive_bezier_curve_add", icon='CURVE_BEZCURVE')
        layout.operator("curve.primitive_nurbs_path_add", icon='CURVE_PATH')
        layout.separator()
        layout.operator("object.empty_add", text="Empty AXE", icon='OUTLINER_OB_EMPTY').type = 'PLAIN_AXES'
        layout.operator("object.empty_add", text="Empty CUBE", icon='OUTLINER_OB_EMPTY').type = 'CUBE'
        layout.operator("object.add", text="Lattice", icon='OUTLINER_OB_LATTICE').type = 'LATTICE'
        layout.operator("object.text_add", text="Text", icon='OUTLINER_OB_FONT')
        layout.operator("object.armature_add", text="Armature", icon='OUTLINER_OB_ARMATURE')

#Subsurf 2
class SubSurf2(bpy.types.Operator):  
    bl_idname = "object.subsurf2"  
    bl_label = "SubSurf 2"  
  
    def execute(self, context):
        bpy.ops.object.subdivision_set(level=2)
        bpy.context.object.modifiers["Subsurf"].show_only_control_edges = True
        
        if bpy.context.object.mode == "EDIT":
            bpy.ops.object.subdivision_set(level=2)
            bpy.context.object.modifiers["Subsurf"].show_on_cage = True
            bpy.ops.object.mode_set(mode = 'EDIT')
        return {'FINISHED'} 

#Remove Subsurf
class RemoveSubsurf(bpy.types.Operator):  
    bl_idname = "remove.subsurf"  
    bl_label = "Remove Subsurf"  
  
    def execute(self, context):
        bpy.ops.object.modifier_remove(modifier="Subsurf")
        return {'FINISHED'}     

#Add Mirror Object
class AddMirrorObject(bpy.types.Operator):  
    bl_idname = "add.mirrorobject"  
    bl_label = "Add Mirror Object"  
  
    def execute(self, context):
        bpy.ops.object.modifier_add(type='MIRROR')
        bpy.context.object.modifiers["Mirror"].use_clip = True
        return {'FINISHED'}  
    
#Add Mirror Edit
class AddMirrorEdit(bpy.types.Operator):  
    bl_idname = "add.mirroredit"  
    bl_label = "Add Mirror Edit"  
  
    def execute(self, context):
        bpy.ops.object.modifier_add(type='MIRROR')
        bpy.context.object.modifiers["Mirror"].use_clip = True
        bpy.context.object.modifiers["Mirror"].show_on_cage = True
        return {'FINISHED'}   

#Apply Mirror Edit
class ApplyMirrorEdit(bpy.types.Operator):  
    bl_idname = "apply.mirroredit"  
    bl_label = "Apply Mirror Edit"  
  
    def execute(self, context):
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.modifier_apply(modifier="Mirror")
        bpy.ops.object.mode_set(mode = 'EDIT')
        return {'FINISHED'} 
    
#Apply Subsurf Edit
class ApplySubsurfEdit(bpy.types.Operator):  
    bl_idname = "apply.subsurfedit"  
    bl_label = "Apply Subsurf Edit"  
  
    def execute(self, context):
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.modifier_apply(modifier="Subsurf")
        bpy.ops.object.mode_set(mode = 'EDIT')
        return {'FINISHED'}             

#wazou Symetrize
class WazouSymetrize(bpy.types.Operator):  
    bl_idname = "wazou.symetrize"  
    bl_label = "Wazou Symetrize"  
  
    def execute(self, context):
        bpy.ops.mesh.select_all(action='TOGGLE')
        bpy.ops.mesh.select_all(action='TOGGLE')
        bpy.ops.mesh.symmetrize(direction='POSITIVE_X')
        bpy.ops.mesh.select_all(action='TOGGLE')
        return {'FINISHED'} 

#Looptools    
class VIEW3D_MT_edit_mesh_looptools(bpy.types.Menu):
    bl_idname = "loop.tools" 
    bl_label = "LoopTools"

    def draw(self, context):
        layout = self.layout

        layout.operator("mesh.looptools_bridge", text="Bridge").loft = False
        layout.operator("mesh.looptools_circle")
        layout.operator("mesh.looptools_curve")
        layout.operator("mesh.looptools_flatten")
        layout.operator("mesh.looptools_gstretch")
        layout.operator("mesh.looptools_bridge", text="Loft").loft = True
        layout.operator("mesh.looptools_relax")
        layout.operator("mesh.looptools_space") 

#Apply Transforms
class ApplyTransformAll(bpy.types.Operator):  
    bl_idname = "apply.transformall"  
    bl_label = "Apply Transform All"  
    
    def execute(self, context):
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        return {'FINISHED'}           

#Delete modifiers
class DeleteModifiers(bpy.types.Operator):  
    bl_idname = "delete.modifiers"  
    bl_label = "Delete modifiers" 
    
    def execute(self, context):
        selection = bpy.context.selected_objects
        
        if not(selection):  
            for obj in bpy.data.objects:
                for mod in obj.modifiers:
                    bpy.context.scene.objects.active = obj
                    bpy.ops.object.modifier_remove(modifier = mod.name)
        else:
            for obj in selection:
                for mod in obj.modifiers:
                    bpy.context.scene.objects.active = obj
                    bpy.ops.object.modifier_remove(modifier = mod.name)  
        return {'FINISHED'}  

#Clear All
class ClearAll(bpy.types.Operator):  
    bl_idname = "clear.all"  
    bl_label = "Clear All" 
    
    def execute(self, context):
        selection = bpy.context.selected_objects
        bpy.ops.object.location_clear()
        bpy.ops.object.rotation_clear()
        bpy.ops.object.scale_clear()
        return {'FINISHED'}      

#Separate Loose Parts
class SeparateLooseParts(bpy.types.Operator):  
    bl_idname = "separate.looseparts"  
    bl_label = "Separate Loose Parts" 
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.separate(type='LOOSE')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='TOGGLE')
        return {'FINISHED'}  

#Create Hole
class CreateHole(bpy.types.Operator):                  
    """This Operator create a hole on a selection"""                   
    bl_idname = "object.createhole"                     
    bl_label = "Create Hole on a Selection"        

    @classmethod                                     
    def poll(cls, context):                         
        return context.active_object is not None 

    def execute(self, context):                     
        
        bpy.ops.mesh.extrude_region_move()
        bpy.ops.transform.resize(value=(0.6, 0.6, 0.6))
        bpy.ops.mesh.looptools_circle()
        bpy.ops.mesh.extrude_region_move()
        bpy.ops.transform.resize(value=(0.8, 0.8, 0.8))
        bpy.ops.mesh.delete(type='FACE')
        return {'FINISHED'} 
    
#Symetry Lock X
class SymetryLockX(bpy.types.Operator):
    bl_idname = "object.symetrylockx"
    bl_label = "Symetry Lock X"
    
    def execute(self, context):
        if bpy.context.scene.tool_settings.sculpt.use_symmetry_x == True:
            bpy.context.scene.tool_settings.sculpt.use_symmetry_x = False
        elif bpy.context.scene.tool_settings.sculpt.use_symmetry_x == False:
            bpy.context.scene.tool_settings.sculpt.use_symmetry_x = True   
        return {'FINISHED'}
    
#Symetry Lock Y
class SymetryLockY(bpy.types.Operator):
    bl_idname = "object.symetrylocky"
    bl_label = "Symetry Lock Y"
    
    def execute(self, context):
        if bpy.context.scene.tool_settings.sculpt.use_symmetry_y == True:
            bpy.context.scene.tool_settings.sculpt.use_symmetry_y = False
        elif bpy.context.scene.tool_settings.sculpt.use_symmetry_y == False:
            bpy.context.scene.tool_settings.sculpt.use_symmetry_y = True   
        return {'FINISHED'}
    
#Symetry Lock Z
class SymetryLockZ(bpy.types.Operator):
    bl_idname = "object.symetrylockz"
    bl_label = "Symetry Lock Z"
    

    def execute(self, context):
        if bpy.context.scene.tool_settings.sculpt.use_symmetry_z == True:
            bpy.context.scene.tool_settings.sculpt.use_symmetry_z = False
        elif bpy.context.scene.tool_settings.sculpt.use_symmetry_z == False:
            bpy.context.scene.tool_settings.sculpt.use_symmetry_z = True   
        return {'FINISHED'}   
     
#Dyntopo Shading
class DyntopoSmoothShading(bpy.types.Operator):
    bl_idname = "object.dtpsmoothshading"
    bl_label = "Dyntopo Smooth Shading"
    

    def execute(self, context):
        if bpy.context.scene.tool_settings.sculpt.use_smooth_shading == True:
            bpy.context.scene.tool_settings.sculpt.use_smooth_shading = False
        elif bpy.context.scene.tool_settings.sculpt.use_smooth_shading == False:
            bpy.context.scene.tool_settings.sculpt.use_smooth_shading = True   
        return {'FINISHED'} 
    
#detail Variable Constant    
class DetailSizevariable(bpy.types.Operator):
    bl_idname = "object.detailsizevariable"
    bl_label = "Detail Size Variable"
    variable = bpy.props.FloatProperty()

    def execute(self, context):
        bpy.context.scene.tool_settings.sculpt.constant_detail = self.variable
        return {'FINISHED'}  
    
#Detail Variable Relative         
class DetailSizevariableRelative(bpy.types.Operator):
    bl_idname = "object.detailsizevariablerelative"
    bl_label = "Detail Size Variable  Relative"
    variable = bpy.props.FloatProperty()

    def execute(self, context):
        bpy.context.scene.tool_settings.sculpt.detail_size = self.variable
        return {'FINISHED'} 
    
#Detail Type    
class DTPDetailType(bpy.types.Operator):
    bl_idname = "object.detailtype"
    bl_label = "Detail Type"
    variable = bpy.props.StringProperty()

    def execute(self, context):
        bpy.context.scene.tool_settings.sculpt.detail_type_method = self.variable
        return {'FINISHED'} 
    
#Detail Refine
class DTPDetailRefine(bpy.types.Operator):
    bl_idname = "object.detailrefine"
    bl_label = "Detail Refine"
    variable = bpy.props.StringProperty()

    def execute(self, context):
        bpy.context.scene.tool_settings.sculpt.detail_refine_method = self.variable
        return {'FINISHED'} 

#Enable Dyntopo
class EnableDyntopo(bpy.types.Operator):  
    bl_idname = "enable.dyntopo"  
    bl_label = "Enable Dyntopo" 
    
    def execute(self, context):
        bpy.ops.sculpt.dynamic_topology_toggle()
        bpy.context.scene.tool_settings.sculpt.detail_refine_method = 'SUBDIVIDE_COLLAPSE'
        bpy.context.scene.tool_settings.sculpt.detail_type_method = 'CONSTANT'
        bpy.context.scene.tool_settings.sculpt.use_smooth_shading = True
        return {'FINISHED'} 

#Sculpt Symmetrize +X to -X
class SculptSymmetrizePlusX(bpy.types.Operator):  
    bl_idname = "sculpt.symmetrizeplusx"  
    bl_label = "Sculpt Symmetrize +X to -X" 
    
    def execute(self, context):
        bpy.ops.sculpt.symmetrize()
        if bpy.context.scene.tool_settings.sculpt.symmetrize_direction ==  'NEGATIVE_X' :
            bpy.context.scene.tool_settings.sculpt.symmetrize_direction = 'POSITIVE_X'
        return {'FINISHED'}     

#Sculpt Symmetrize -X to +X
class SculptSymmetrizeMoinsX(bpy.types.Operator):  
    bl_idname = "sculpt.symmetrizemoinsx"  
    bl_label = "Sculpt Symmetrize - X to + X" 
    
    def execute(self, context):
        bpy.ops.sculpt.symmetrize()
        if bpy.context.scene.tool_settings.sculpt.symmetrize_direction ==  'POSITIVE_X' :
            bpy.context.scene.tool_settings.sculpt.symmetrize_direction = 'NEGATIVE_X'
        return {'FINISHED'} 

#Sculpt Use symetry X
class SculptUseSymmetryX(bpy.types.Operator):  
    bl_idname = "sculpt.sculptusesymmetryx"  
    bl_label = "Sculpt Use symetry X" 
    
    def execute(self, context):
        if bpy.context.scene.tool_settings.sculpt.use_symmetry_x == (True):
            bpy.context.scene.tool_settings.sculpt.use_symmetry_x = False
            
        elif bpy.context.scene.tool_settings.sculpt.use_symmetry_x == (False) :
             bpy.context.scene.tool_settings.sculpt.use_symmetry_x = True
        return {'FINISHED'}     

#Sculpt Use symetry Y
class SculptUseSymmetryY(bpy.types.Operator):  
    bl_idname = "sculpt.sculptusesymmetryy"  
    bl_label = "Sculpt Use symetry Y" 
    
    def execute(self, context):
        if bpy.context.scene.tool_settings.sculpt.use_symmetry_y == (True):
            bpy.context.scene.tool_settings.sculpt.use_symmetry_y = False
            
        elif bpy.context.scene.tool_settings.sculpt.use_symmetry_y == (False) :
             bpy.context.scene.tool_settings.sculpt.use_symmetry_y = True
        return {'FINISHED'}     

#Sculpt Use symetry Z
class SculptUseSymmetryZ(bpy.types.Operator):  
    bl_idname = "sculpt.sculptusesymmetryz"  
    bl_label = "Sculpt Use symetry Z" 
    
    def execute(self, context):
        if bpy.context.scene.tool_settings.sculpt.use_symmetry_z == (True):
            bpy.context.scene.tool_settings.sculpt.use_symmetry_z = False
            
        elif bpy.context.scene.tool_settings.sculpt.use_symmetry_z == (False) :
             bpy.context.scene.tool_settings.sculpt.use_symmetry_z = True
        return {'FINISHED'} 

#Pivot to selection
class PivotToSelection(bpy.types.Operator):  
    bl_idname = "object.pivot2selection"  
    bl_label = "Pivot To Selection"  
  
    def execute(self, context):  
        saved_location = bpy.context.scene.cursor_location.copy()
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.context.scene.cursor_location = saved_location 
        return {'FINISHED'}  
    
#Pivot to Bottom
class PivotBottom(bpy.types.Operator):  
    bl_idname = "object.pivotobottom"  
    bl_label = "Pivot To Bottom"  
  
    def execute(self, context):
        
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        o=bpy.context.active_object
        init=0
        for x in o.data.vertices:
             if init==0:
                 a=x.co.z
                 init=1
             elif x.co.z<a:
                 a=x.co.z
                 
        for x in o.data.vertices:
             x.co.z-=a

        o.location.z+=a 
        bpy.ops.object.mode_set(mode = 'EDIT')
        return {'FINISHED'} 
                                                  
######################
#        Pies        #               
######################  
#Pie Sculpt Constant/Relative
class PieSculptConstantRelative(Menu):
    bl_idname = "pie.sculptconstantrelative"
    bl_label = "Pie Sculpt Constant/Relative"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        #4 - LEFT
        pie.operator("object.detailrefine", text="Subdiv Collapse").variable = 'SUBDIVIDE_COLLAPSE'
        #6 - RIGHT
        pie.operator("object.detailrefine", text="Collapse").variable = 'COLLAPSE'
        #2 - BOTTOM
        pie.operator("object.detailrefine", text="Subdivide").variable = 'SUBDIVIDE'
        #8 - TOP
        pie.operator("object.detailtype", text="Relative").variable = 'RELATIVE'
        #7 - TOP - LEFT
        pie.operator("object.detailtype", text="Constant").variable = 'CONSTANT'
        #9 - TOP - RIGHT
        pie.operator("object.detailtype", text="Brush").variable = 'BRUSH'
        #1 - BOTTOM - LEFT
        #3 - BOTTOM - RIGHT
        
#Pie Sculpt Detail Size Variable Constant
class PieSculptDetailSizeVariableConstant(Menu):
    bl_idname = "pie.sculptdetailsizevariableconstant"
    bl_label = "Detail Size Values"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        #4 - LEFT
        pie.operator("object.detailsizevariable", text="1").variable = 1
        #6 - RIGHT
        pie.operator("object.detailsizevariable", text="15").variable = 15
        #2 - BOTTOM
        pie.operator("object.detailsizevariable", text="25").variable = 25
        #8 - TOP
        pie.operator("object.detailsizevariable", text="5").variable = 5
        #7 - TOP - LEFT 
        pie.operator("object.detailsizevariable", text="2").variable = 2
        #9 - TOP - RIGHT
        pie.operator("object.detailsizevariable", text="10").variable = 10
        #1 - BOTTOM - LEFT
        pie.operator("object.detailsizevariablerelative", text="30").variable = 30
        #3 - BOTTOM - RIGHT
        pie.operator("object.detailsizevariable", text="20").variable = 20
        
#Pie Sculpt Detail Size Variable Relative
class PieSculptDetailSizeVariableRelative(Menu):
    bl_idname = "pie.sculptdetailsizevariablerelative"
    bl_label = "Detail Size Values"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        
        pie.operator("object.detailsizevariablerelative", text="1").variable = 1
        #6 - RIGHT
        pie.operator("object.detailsizevariablerelative", text="15").variable = 15
        #2 - BOTTOM
        pie.operator("object.detailsizevariablerelative", text="25").variable = 25
        #8 - TOP
        pie.operator("object.detailsizevariablerelative", text="5").variable = 5
        #7 - TOP - LEFT 
        pie.operator("object.detailsizevariablerelative", text="2").variable = 2
        #9 - TOP - RIGHT
        pie.operator("object.detailsizevariablerelative", text="10").variable = 10
        #1 - BOTTOM - LEFT
        pie.operator("object.detailsizevariablerelative", text="30").variable = 30
        #3 - BOTTOM - RIGHT
        pie.operator("object.detailsizevariablerelative", text="20").variable = 20
        
#Pie Sculpt Mirror
class PieSculptMirror(Menu):
    bl_idname = "pie.sculptmirror"
    bl_label = "Pie Sculpt Mirror"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        sculpt = context.tool_settings.sculpt
        #4 - LEFT
        pie.operator("sculpt.symmetrizemoinsx", text="-X to +X", icon='TRIA_RIGHT')
        #6 - RIGHT
        pie.operator("sculpt.symmetrizeplusx", text="+X to -X", icon='TRIA_LEFT')
        #2 - BOTTOM
        if bpy.context.scene.tool_settings.sculpt.use_symmetry_y == (True):
            pie.operator("sculpt.sculptusesymmetryy", text="Unlock Y", icon='LOCKED')
        else:
            pie.operator("sculpt.sculptusesymmetryy", text="Lock Y", icon='UNLOCKED')
        #8 - TOP
        pie.operator("object.symetrylocky", text="Symmetrize Y", icon='MOD_MIRROR')
        #7 - TOP - LEFT 
        pie.operator("object.symetrylockx", text="Symmetrize X", icon='MOD_MIRROR')
        #9 - TOP - RIGHT
        pie.operator("object.symetrylockz", text="Symmetrize Z", icon='MOD_MIRROR')
        #1 - BOTTOM - LEFT
        if bpy.context.scene.tool_settings.sculpt.use_symmetry_x == (True):
            pie.operator("sculpt.sculptusesymmetryx", text="Unlock X", icon='LOCKED')
        else:
            pie.operator("sculpt.sculptusesymmetryx", text="Lock X", icon='UNLOCKED')    
        #3 - BOTTOM - RIGHT
        if bpy.context.scene.tool_settings.sculpt.use_symmetry_z == (True):
            pie.operator("sculpt.sculptusesymmetryz", text="Unlock Z", icon='LOCKED')
        else:
            pie.operator("sculpt.sculptusesymmetryz", text="Lock Z", icon='UNLOCKED') 

#Pie Sculpt Curves
class PieSculptCurves(Menu):
    bl_idname = "pie.sculptcurves"
    bl_label = "Pie Sculpt Curves"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        #4 - LEFT
        pie.operator("brush.curve_preset", icon='SMOOTHCURVE', text="Smooth").shape = 'SMOOTH'
        #6 - RIGHT
        pie.operator("brush.curve_preset", icon='SPHERECURVE', text="Rounde").shape = 'ROUND'
        #2 - BOTTOM
        pie.operator("brush.curve_preset", icon='ROOTCURVE', text="Root").shape = 'ROOT'
        #8 - TOP
        pie.operator("brush.curve_preset", icon='SHARPCURVE', text="Sharp").shape = 'SHARP'
        #7 - TOP - LEFT 
        pie.operator("brush.curve_preset", icon='LINCURVE', text="Line").shape = 'LINE'
        #9 - TOP - RIGHT
        pie.operator("brush.curve_preset", icon='NOCURVE', text="Max").shape = 'MAX'
        #1 - BOTTOM - LEFT
        #3 - BOTTOM - RIGHT
########################################################################

########################################################################
#RMB          
class View3dRightClicMenu(Menu):
    bl_idname = "pie.rightclicmenu"
    bl_label = "Right Clic Menu"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        
        ################################################
        # No Objects                                   #
        ################################################
        if bpy.context.area.type == 'VIEW_3D' and not bpy.context.object:
            
            #4 - LEFT
            pie.operator("wm.read_homefile", text="New", icon='NEW')
            #6 - RIGHT
            box = pie.split().column()
            row = box.split(align=True)
            box.operator("wm.recover_last_session", text="Recover Last Session", icon='RECOVER_LAST')
            box.operator("wm.recover_auto_save", text="Recover auto Save", icon='RECOVER_AUTO')
            #2 - BOTTOM
            box = pie.split().column()
            row = box.split(align=True)
            row.operator("mesh.primitive_cube_add", text="", icon='MESH_CUBE')
            row.operator("mesh.primitive_plane_add", text="", icon='MESH_PLANE')
            row.operator("mesh.primitive_uv_sphere_add", text="", icon='MESH_UVSPHERE')
            row.operator("mesh.primitive_cylinder_add", text="", icon='MESH_CYLINDER')
            row = box.row(align=True)
            row = box.split(align=True)
            row.operator("mesh.primitive_grid_add", text=" ", icon='MESH_GRID')
            row.operator("mesh.primitive_circle_add", text=" ", icon='MESH_CIRCLE')
            row.operator("mesh.primitive_cone_add", text=" ", icon='MESH_CONE')
            row.operator("mesh.primitive_torus_add", text=" ", icon='MESH_TORUS')
            row = box.row(align=True)
            row = box.split(align=True)
            row.operator("object.camera_add", text="", icon='OUTLINER_OB_CAMERA')
            row.operator("object.lamp_add", text="", icon='LAMP_AREA').type = 'AREA'
            row.operator("object.lamp_add", text="", icon='LAMP_SUN').type = 'SUN'
            row.operator("object.lamp_add", text="", icon='LAMP_HEMI').type = 'HEMI'
            box.menu("AddMenu", text="Objects", icon="OBJECT_DATA")
            #8 - TOP
            pie.operator("wm.save_mainfile", text="Save", icon='FILE_TICK')
            #7 - TOP - LEFT 
            pie.operator("wm.open_mainfile", text="Open file", icon='FILE_FOLDER')
            #9 - TOP - RIGHT
            pie.operator("wm.save_as_mainfile", text="Save As...", icon='SAVE_AS')
            #1 - BOTTOM - LEFT
            box = pie.split().column()
            row = box.split(align=True)
            row.operator("import_scene.obj", text="Imp OBJ", icon='IMPORT')
            row.operator("export_scene.obj", text="Exp OBJ", icon='EXPORT')
            row = box.row(align=True)
            row = box.split(align=True)
            row.operator("import_scene.fbx", text="Imp FBX", icon='IMPORT')
            row.operator("export_scene.fbx", text="Exp FBX", icon='EXPORT')
            #3 - BOTTOM - RIGHT
            box = pie.split().column()
            row = box.split(align=True)
            row.operator("wm.link", text="Link", icon='LINK_BLEND')
            row.operator("wm.append", text="Append", icon='APPEND_BLEND')
        
        ################################################
        # Object Mode                                  #
        ################################################    
        elif bpy.context.area.type == 'VIEW_3D' and bpy.context.object.mode == 'OBJECT':
            #4 - LEFT
            box = pie.split().column()
            row = box.split(align=True)
            row.operator("Object.join", text="Join", icon='FULLSCREEN_EXIT')
            row.operator("separate.looseparts", text="Separate", icon='FULLSCREEN_ENTER')
            #6 - RIGHT
            is_subsurf = False
            for mode in bpy.context.object.modifiers :
                if mode.type == 'SUBSURF' :
                    is_subsurf = True
            if is_subsurf == True :
                pie.operator("remove.subsurf", text="Remove Subsurf", icon='X')
            else :
               pie.operator("object.subsurf2", text="Add Subsurf", icon='MOD_SUBSURF')
                
            #2 - BOTTOM
            box = pie.split().column()
            row = box.split(align=True)
            row.operator("mesh.primitive_cube_add", text="", icon='MESH_CUBE')
            row.operator("mesh.primitive_plane_add", text="", icon='MESH_PLANE')
            row.operator("mesh.primitive_uv_sphere_add", text="", icon='MESH_UVSPHERE')
            row.operator("mesh.primitive_cylinder_add", text="", icon='MESH_CYLINDER')
            row = box.row(align=True)
            row = box.split(align=True)
            row.operator("mesh.primitive_grid_add", text=" ", icon='MESH_GRID')
            row.operator("mesh.primitive_circle_add", text=" ", icon='MESH_CIRCLE')
            row.operator("mesh.primitive_cone_add", text=" ", icon='MESH_CONE')
            row.operator("mesh.primitive_torus_add", text=" ", icon='MESH_TORUS')
            row = box.row(align=True)
            row = box.split(align=True)
            row.operator("object.camera_add", text="", icon='OUTLINER_OB_CAMERA')
            row.operator("object.lamp_add", text="", icon='LAMP_AREA').type = 'AREA'
            row.operator("object.lamp_add", text="", icon='LAMP_SUN').type = 'SUN'
            row.operator("object.lamp_add", text="", icon='LAMP_HEMI').type = 'HEMI'
            box.menu("AddMenu", text="Objects", icon="OBJECT_DATA")
            #8 - TOP
            pie.operator("screen.redo_last", text="F6", icon='SCRIPTWIN')
            #7 - TOP - LEFT 
            box = pie.split().column()
            row = box.split(align=True)
            is_mirror = False
            for mode in bpy.context.object.modifiers :
                if mode.type == 'MIRROR' :
                    is_mirror = True
            if is_mirror == True :
                row.operator("object.modifier_remove", text="Del Mirror",icon='X').modifier="Mirror"   
            else:
                row.operator("add.mirrorobject", text="Add Mirror", icon='MOD_MIRROR')
                  
            row.operator("object.automirror", icon = 'MOD_MIRROR')
            row = box.row(align=True)
            row = box.split(align=True)
            row.operator("object.modifier_apply", text="Apply Mirror", icon='FILE_TICK').modifier="Mirror"
            row.operator("delete.modifiers", text="Del Modifiers", icon='X')
            row = box.row(align=True)
            row = box.split(align=True)
            row.operator("object.modifier_apply", text="Apply Subsurf", icon='FILE_TICK').modifier="Subsurf"
            #9 - TOP - RIGHT
            box = pie.split().column()
            row = box.row(align=True)
            row.operator("object.origin_set", text="O To Cursor", icon='CURSOR').type ='ORIGIN_CURSOR'
            row.operator("object.origin_set", text="O To COM", icon='CLIPUV_HLT').type ='ORIGIN_CENTER_OF_MASS'
            row = box.row(align=True)
            row.operator("object.origin_set", text="Origin To Geo", icon='ROTATE').type ='ORIGIN_GEOMETRY'
            row.operator("object.origin_set", text="Geo To Origin", icon='BBOX').type ='GEOMETRY_ORIGIN'
            row = box.row(align=True)
            row.operator("view3d.snap_selected_to_cursor", text="Sel to Cursor", icon='CLIPUV_HLT').use_offset = False
            row.operator("view3d.snap_cursor_to_selected", text="Cursor to Sel", icon='ROTACTIVE')  
            row = box.row(align=True)
            row.operator("object.pivot2selection", text="Origin To Sel", icon='SNAP_INCREMENT')
            row.operator("object.pivotobottom", text="Origin To Bottom", icon='TRIA_DOWN') 
            #1 - BOTTOM - LEFT
            box = pie.split().column()
            row = box.row(align=True)
            row.operator("apply.transformall", text="Freeze T", icon='FREEZE')
            row.operator("clear.all", text="Clear All", icon='MANIPUL')
            #3 - BOTTOM - RIGHT
            pie.operator("object.delete", text="Delete", icon='CANCEL').use_global=False
        
        ################################################
        # Edit Mode                                    #
        ################################################    
        elif bpy.context.object.mode == 'EDIT':    

            #4 - LEFT
            box = pie.split().column()
            row = box.split(align=True)
            row.operator("mesh.subdivide", text="Subdivide", icon='GRID').smoothness=0
            row.operator("mesh.vertices_smooth", text="Smooth", icon='UV_VERTEXSEL')
            row = box.row(align=True)
            row = box.split(align=True)
            row.operator("wm.context_toggle", text="Mirror X ", icon='MOD_MIRROR').data_path = "object.data.use_mirror_x"
            row.operator("wazou.symetrize", text="Symetrize", icon='UV_EDGESEL')

            #6 - RIGHT
            is_subsurf1 = False
            for mode in bpy.context.object.modifiers :
                if mode.type == 'SUBSURF' :
                    is_subsurf1 = True
            if is_subsurf1 == True :
                pie.operator("remove.subsurf", text="Remove Subsurf", icon='X')
            else :
               pie.operator("object.subsurf2", text="Add Subsurf", icon='MOD_SUBSURF')
            #2 - BOTTOM
            box = pie.split().column()
            row = box.row(align=True) 
            #Vertex
            if tuple (bpy.context.tool_settings.mesh_select_mode) == (True, False, False) :
                box.label("Merge at :")
                row = box.row(align=True)
                row = box.split(align=True)
                row.operator("mesh.merge", text="First", icon='AUTOMERGE_ON').type='FIRST'
                row.operator("mesh.merge", text="Center", icon='AUTOMERGE_ON').type='CENTER'
                row.operator("mesh.merge", text="Last", icon='AUTOMERGE_ON').type='LAST'
            #Edges    
            if tuple (bpy.context.tool_settings.mesh_select_mode) == (False, True, False):
                box.label("Merge at :")
                row = box.row(align=True)
                row = box.split(align=True)
                row.operator("mesh.merge", text="Cursor", icon='CURSOR').type='CURSOR'
                row.operator("mesh.merge", text="Center", icon='AUTOMERGE_ON').type='CENTER'
                row.operator("mesh.merge", text="Collapse", icon='AUTOMERGE_ON').type='COLLAPSE'
            #Faces
            if tuple (bpy.context.tool_settings.mesh_select_mode) == (False, False, True):
                box.label("Merge at :")
                row = box.row(align=True)
                row = box.split(align=True)
                row.operator("mesh.merge", text="Cursor", icon='CURSOR').type='CURSOR'
                row.operator("mesh.merge", text="Center", icon='AUTOMERGE_ON').type='CENTER'
                row.operator("mesh.merge", text="Collapse", icon='AUTOMERGE_ON').type='COLLAPSE'
            #8 - TOP
            pie.operator("screen.redo_last", text="F6", icon='SCRIPTWIN')
            #7 - TOP - LEFT 
            box = pie.split().column()
            row = box.split(align=True)
            is_mirror1 = False
            for mode in bpy.context.object.modifiers :
                if mode.type == 'MIRROR' :
                    is_mirror1 = True
            if is_mirror1 == True :
                row.operator("object.modifier_remove", text="Del Mirror", icon='X_VEC').modifier="Mirror"
                
            else:
                row.operator("add.mirroredit", text="Add Mirror", icon='MOD_MIRROR')
            
            row.operator("object.automirror", icon = 'MOD_MIRROR')
            row = box.row(align=True)
            row = box.split(align=True)
            row.operator("apply.mirroredit", text="Apply Mirror", icon='FILE_TICK')
            row.operator("apply.subsurfedit", text="Apply Sub", icon='FILE_TICK')
            #9 - TOP - RIGHT
            box = pie.split().column()
            row = box.split(percentage=0.6)
            row.operator("mesh.offset_edges", text="Offset Edges", icon='UV_EDGESEL')
            row.menu("loop.tools")
            row = box.row(align=True)
            row = box.split(align=True)
            row.operator("mesh.poke", text="Poke Faces")
            row.operator("mesh.fill_grid", text="Grid Fill")
            #1 - BOTTOM - LEFT
            box = pie.split().column()
            row = box.split(align=True)
            row.operator("mesh.loopcut", text="Loopcut", icon='EDIT_VEC').smoothness=1
            row.operator("mesh.inset",text="Inset  ", icon='EDIT_VEC').use_select_inset=False
            row = box.row(align=True)
            row = box.split(align=True)
            row.operator("mesh.bevel",text="Bevel  ", icon='MOD_BEVEL')
            row.operator("object.createhole",text="Hole", icon='CLIPUV_DEHLT')
            #3 - BOTTOM - RIGHT
            box = pie.split().column()
            row = box.split(align=True)
            row.operator("mesh.flip_normals",text="Flip N", icon = 'FILE_REFRESH')
            row.operator("mesh.normals_make_consistent",text="consistant", icon = 'MATCUBE')
            row = box.row(align=True)
            row = box.split(align=True)
            row.operator("wm.context_toggle", text="Show Norms", icon='FACESEL').data_path = "object.data.show_normal_face"
            row.operator("mesh.remove_doubles", text="rem D2l",icon='X')
            row = pie.split().column()
            row = box.split(align=True)
            row.operator("mesh.separate")
            row.menu("AddMenu", text="Add Obj", icon="OBJECT_DATA")
        
        ################################################
        # Sculpt                                       #
        ################################################    
        elif bpy.context.area.type == 'VIEW_3D' and bpy.context.object.mode == 'SCULPT':

            sculpt = context.tool_settings.sculpt
            brush = context.tool_settings.sculpt.brush
            if context.sculpt_object.use_dynamic_topology_sculpting:
                #4 - LEFT
                pie.operator("sculpt.dynamic_topology_toggle", icon='X', text="Disable Dyntopo")
                #6 - RIGHT
                #pie.operator("sculpt.detail_flood_fill", text="Detail flood Fill") 
                box = pie.split().column()
                row = box.split(align=True)
                box.operator("sculpt.sample_detail_size", text="Sample Detail Size", icon='EYEDROPPER')
                box.operator("sculpt.detail_flood_fill", text="Detail flood Fill")
                #2 - BOTTOM
                if bpy.context.scene.tool_settings.sculpt.use_smooth_shading == True:
                    pie.operator("object.dtpsmoothshading", text="flat Shading", icon='MESH_ICOSPHERE')
                else:
                    pie.operator("object.dtpsmoothshading", text="Smooth Shading", icon='SOLID')
                #8 - TOP
                #brush = context.tool_settings.sculpt.brush
                col = pie.column(align=True)        
                col.prop(brush, "auto_smooth_factor",  slider=True)
                #7 - TOP - LEFT 
                pie.operator("wm.call_menu_pie", text="Contant/Relative", icon='MOD_MIRROR').name="pie.sculptconstantrelative"
                #9 - TOP - RIGHT
                if bpy.context.tool_settings.sculpt.detail_type_method == 'CONSTANT':
                    col = pie.column(align=True)        
                    col.prop(sculpt, "constant_detail",  slider=True)
                elif bpy.context.tool_settings.sculpt.detail_type_method == 'RELATIVE':
                    col = pie.column(align=True)        
                    col.prop(sculpt, "detail_size",  slider=True)
                elif bpy.context.tool_settings.sculpt.detail_type_method == 'BRUSH':
                    col = pie.column(align=True)        
                    col.prop(sculpt, "detail_percent",  slider=True)
                #1 - BOTTOM - LEFT
                box = pie.split().column()
                row = box.split(align=True)
                box.operator("wm.call_menu_pie", text="Curves", icon='SHARPCURVE').name="pie.sculptcurves"
                box.operator("wm.call_menu_pie", text="Symmetrize/Lock", icon='MOD_MIRROR').name="pie.sculptmirror" 
                #3 - BOTTOM - RIGHT
                pie.operator("sculpt.optimize", text="Optimize")
                
            else:
                #4 - LEFT
                pie.operator("enable.dyntopo", text="Enable Dyntopo", icon='LINE_DATA')
                #6 - RIGHT
                pie.operator("wm.call_menu_pie", text="Curves", icon='SHARPCURVE').name="pie.sculptcurves"
                #2 - BOTTOM
                pie.operator("wm.call_menu_pie", text="Symmetrize/Lock", icon='MOD_MIRROR').name="pie.sculptmirror"
                #8 - TOP
                brush = context.tool_settings.sculpt.brush
                col = pie.column(align=True)        
                col.prop(brush, "auto_smooth_factor",  slider=True)
                #7 - TOP - LEFT 
                #9 - TOP - RIGHT
                #1 - BOTTOM - LEFT
                #3 - BOTTOM - RIGHT
  

addon_keymaps = []
def register():
    bpy.utils.register_class(View3dRightClicMenu)
    bpy.utils.register_class(WazouRightMenuPiePrefs)
    #Object
    bpy.utils.register_class(AddMenu)
    bpy.utils.register_class(SubSurf2)
    bpy.utils.register_class(RemoveSubsurf)
    bpy.utils.register_class(AddMirrorObject)
    bpy.utils.register_class(ApplySubsurfEdit)
    bpy.utils.register_class(VIEW3D_MT_edit_mesh_looptools)
    bpy.utils.register_class(ApplyTransformAll)
    bpy.utils.register_class(DeleteModifiers)
    bpy.utils.register_class(ClearAll)
    bpy.utils.register_class(SeparateLooseParts)
    bpy.utils.register_class(PivotToSelection)
    bpy.utils.register_class(PivotBottom)
    #Edit
    bpy.utils.register_class(AddMirrorEdit)
    bpy.utils.register_class(ApplyMirrorEdit)
    bpy.utils.register_class(WazouSymetrize)
    bpy.utils.register_class(CreateHole)
    #Sculpt
    bpy.utils.register_class(EnableDyntopo)
    bpy.utils.register_class(SculptSymmetrizePlusX)
    bpy.utils.register_class(SculptSymmetrizeMoinsX)
    bpy.utils.register_class(DetailSizevariable)
    bpy.utils.register_class(SymetryLockX)
    bpy.utils.register_class(SymetryLockY)
    bpy.utils.register_class(SymetryLockZ)
    bpy.utils.register_class(DyntopoSmoothShading)
    bpy.utils.register_class(DTPDetailType)
    bpy.utils.register_class(DTPDetailRefine)
    bpy.utils.register_class(DetailSizevariableRelative)
    bpy.utils.register_class(PieSculptMirror)
    bpy.utils.register_class(SculptUseSymmetryX)
    bpy.utils.register_class(SculptUseSymmetryY)
    bpy.utils.register_class(SculptUseSymmetryZ)
    bpy.utils.register_class(PieSculptCurves)
    bpy.utils.register_class(PieSculptDetailSizeVariableRelative)
    bpy.utils.register_class(PieSculptDetailSizeVariableConstant)
    bpy.utils.register_class(PieSculptConstantRelative)
    
    
    
# Keympa Config   
    
    wm = bpy.context.window_manager
    
    if wm.keyconfigs.addon:
        
        # Set 3d cursor with double click LMB
        #km = bpy.context.window_manager.keyconfigs.addon.keymaps.new("3D View", space_type="VIEW_3D")
        #kmi = km.keymap_items.new('view3d.cursor3d', 'LEFTMOUSE', 'DOUBLE_CLICK', alt=True)

        #Right Clic
        km = wm.keyconfigs.addon.keymaps.new(name = '3D View Generic', space_type = 'VIEW_3D')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'ACTIONMOUSE', 'PRESS')
        kmi.properties.name = "pie.rightclicmenu"
        
        #Right Clic
        km = wm.keyconfigs.addon.keymaps.new(name='Sculpt')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'RIGHTMOUSE', 'PRESS', shift=True)
        kmi.properties.name = "pie.rightclicmenu"  
        
def unregister():
    bpy.utils.unregister_class(View3dRightClicMenu)
    bpy.utils.unregister_class(WazouRightMenuPiePrefs)
    #Object
    bpy.utils.unregister_class(AddMenu)
    bpy.utils.unregister_class(SubSurf2)
    bpy.utils.unregister_class(RemoveSubsurf)
    bpy.utils.unregister_class(AddMirrorObject)
    bpy.utils.unregister_class(ApplySubsurfEdit)
    bpy.utils.unregister_class(VIEW3D_MT_edit_mesh_looptools)
    bpy.utils.unregister_class(ApplyTransformAll)
    bpy.utils.unregister_class(DeleteModifiers)
    bpy.utils.unregister_class(ClearAll)
    bpy.utils.unregister_class(SeparateLooseParts)
    bpy.utils.unregister_class(PivotToSelection)
    bpy.utils.unregister_class(PivotBottom)
    #Edit
    bpy.utils.unregister_class(AddMirrorEdit)
    bpy.utils.unregister_class(ApplyMirrorEdit)
    bpy.utils.unregister_class(WazouSymetrize)
    bpy.utils.unregister_class(CreateHole)
    #Sculpt
    bpy.utils.unregister_class(EnableDyntopo)
    bpy.utils.unregister_class(SculptSymmetrizePlusX)
    bpy.utils.unregister_class(SculptSymmetrizeMoinsX)
    bpy.utils.unregister_class(DetailSizevariable)
    bpy.utils.unregister_class(SymetryLockX)
    bpy.utils.unregister_class(SymetryLockY)
    bpy.utils.unregister_class(SymetryLockZ)
    bpy.utils.unregister_class(DyntopoSmoothShading)
    bpy.utils.unregister_class(DTPDetailType)
    bpy.utils.unregister_class(DTPDetailRefine)
    bpy.utils.unregister_class(DetailSizevariableRelative)
    bpy.utils.unregister_class(PieSculptMirror)
    bpy.utils.unregister_class(SculptUseSymmetryX)
    bpy.utils.unregister_class(SculptUseSymmetryY)
    bpy.utils.unregister_class(SculptUseSymmetryZ)
    bpy.utils.unregister_class(PieSculptCurves)
    bpy.utils.unregister_class(PieSculptDetailSizeVariableRelative)
    bpy.utils.unregister_class(PieSculptDetailSizeVariableConstant)
    bpy.utils.unregister_class(PieSculptConstantRelative)
    
    
    
    
    
    
    
if __name__ == "__main__":
    register()

    #bpy.ops.wm.call_menu_pie(name="View3dRightClicMenu")