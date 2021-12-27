import bpy
from bpy.types import Operator

from bpy.props import *

import bgl
import blf

import bmesh

import gpu
from gpu_extras.batch import batch_for_shader

from .utils.fc_bool_util import select_active, execute_boolean_op, execute_slice_op, is_apply_immediate
from .utils.fc_view_3d_utils import *

from .types.shape import *
from .types.rectangle_shape import *
from .types.polyline_shape import *
from .types.circle_shape import *

from .types.enums import *

# Primitive mode operator
class FC_Primitive_Mode_Operator(bpy.types.Operator):
    bl_idname = "object.fc_immediate_mode_op"
    bl_label = "Primitive Mode Operator"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO", "BLOCKING"}

    @classmethod
    def poll(cls, context): 
        if context.object is None:
            return False
            
        return context.object.mode == "OBJECT"
		
    def __init__(self):
        self.draw_handle_2d = None
        self.draw_handle_3d = None
        self.draw_event  = None
        self.shape = Polyline_Shape()

        self.create_batch(None)
                
    def invoke(self, context, event):
        args = (self, context)  

        target_obj = context.scene.carver_target
        snap_to_target = context.scene.snap_to_target

        if target_obj is None:
            self.report({'ERROR'}, 'Please define a target object.')
            context.scene.in_primitive_mode = False
            return {"FINISHED"}

        context.scene.in_primitive_mode = True

        self.create_shape(context, target_obj, snap_to_target)                 

        self.register_handlers(args, context)
                   
        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}
    
    def register_handlers(self, args, context):
        self.draw_handle_3d = bpy.types.SpaceView3D.draw_handler_add(
            self.draw_callback_3d, args, "WINDOW", "POST_VIEW")

        self.draw_handle_2d = bpy.types.SpaceView3D.draw_handler_add(
            self.draw_callback_2d, args, "WINDOW", "POST_PIXEL")

        self.draw_event = context.window_manager.event_timer_add(0.1, window=context.window)
        
    def unregister_handlers(self, context):
        
        context.window_manager.event_timer_remove(self.draw_event)
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle_2d, "WINDOW")
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handle_3d, "WINDOW")
        
        self.draw_handle_2d = None
        self.draw_handle_3d = None
        self.draw_event  = None

    def get_3d_for_mouse(self, mouse_pos_2d, context):
        if context.scene.snap_to_target:
            mouse_pos_3d = self.shape.get_3d_for_2d(mouse_pos_2d, context)
        else:
            mouse_pos_3d = get_3d_vertex(context, mouse_pos_2d)
        return mouse_pos_3d

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()

        target_obj = context.scene.carver_target
        snap_to_target = context.scene.snap_to_target
                               
        if event.type == "ESC" and event.value == "PRESS":

            was_none = self.shape.is_none()

            self.shape.reset()
            self.create_batch(None)

            if was_none:

                context.scene.in_primitive_mode = False
                self.unregister_handlers(context)

                return {'FINISHED'}

        # The mouse is moved
        if event.type == "MOUSEMOVE" and not self.shape.is_none():

            mouse_pos_2d = (event.mouse_region_x, event.mouse_region_y)

            mouse_pos_3d = self.get_3d_for_mouse(mouse_pos_2d, context)

            if context.scene.use_snapping and mouse_pos_3d is not None:
                mouse_pos_3d = get_snap_3d_vertex(context, mouse_pos_3d)
                mouse_pos_2d = get_2d_vertex(context, mouse_pos_3d)

            if self.shape.handle_mouse_move(mouse_pos_2d, mouse_pos_3d, event, context):
                self.create_batch(mouse_pos_3d)
        
        # Left mouse button is pressed
        if event.value == "PRESS" and event.type == "LEFTMOUSE":

            if target_obj is None:
                self.report({'ERROR'}, 'Please define a target object.')
                return {"PASS_THROUGH"}

            self.create_shape(context, target_obj, snap_to_target)

            mouse_pos_2d = (event.mouse_region_x, event.mouse_region_y)

            mouse_pos_3d = self.get_3d_for_mouse(mouse_pos_2d, context)
                
            if context.scene.use_snapping and mouse_pos_3d is not None:
                mouse_pos_3d = get_snap_3d_vertex(context, mouse_pos_3d)
                mouse_pos_2d = get_2d_vertex(context, mouse_pos_3d)

            if self.shape.is_moving():
                self.shape.stop_move(context)

            if self.shape.is_extruding():
                self.shape.stop_extrude(context)

            if self.shape.is_rotating():
                self.shape.stop_rotate(context)

            if self.shape.handle_mouse_press(mouse_pos_2d, mouse_pos_3d, event, context):
                self.create_object(context)
            else:
                # So that the direction is defined during shape
                # creation, not when it is extruded
                if self.shape.is_processing():
                    view_context = ViewContext(context)
                    self.shape.set_view_context(view_context)
                
            self.create_batch(mouse_pos_3d)

        # Keyboard
        if event.value == "PRESS":

            # try to move the shape
            if event.type == "G":
                mouse_pos_2d = (event.mouse_region_x, event.mouse_region_y)

                mouse_pos_3d = self.get_3d_for_mouse(mouse_pos_2d, context)

                if self.shape.start_move(mouse_pos_3d):
                    return {"RUNNING_MODAL"}

            # try to rotate the shape
            if event.type == "R":
                mouse_pos_2d = (event.mouse_region_x, event.mouse_region_y)

                mouse_pos_3d = self.get_3d_for_mouse(mouse_pos_2d, context)

                if self.shape.start_rotate(mouse_pos_3d, context):
                    self.create_batch()
                    return {"RUNNING_MODAL"}               

            # try to extrude the shape
            if event.type == "E":
                mouse_pos_2d = (event.mouse_region_x, event.mouse_region_y)

                if self.shape.start_extrude(mouse_pos_2d, context):
                    self.create_batch()
                    return {"RUNNING_MODAL"}  

            # toggle bool mode
            if event.type == "M":
                context.scene.bool_mode = next_enum(context.scene.bool_mode, 
                                                    context.scene, "bool_mode")

                return {"RUNNING_MODAL"}

            # toggle primitve  
            if event.type == "P":
                if self.shape.is_none():
                    context.scene.primitive_type = next_enum(context.scene.primitive_type, 
                                                        context.scene, "primitive_type")

                    self.create_shape(context, target_obj, snap_to_target)
                    return {"RUNNING_MODAL"}
             
        return {"PASS_THROUGH"}

    def create_shape(self, context, target_obj, snap_to_target):
        if self.shape.is_none():
            if context.scene.primitive_type == "Circle":
                self.shape = Circle_Shape()
            elif context.scene.primitive_type == "Polyline":
                self.shape = Polyline_Shape()
            else:
                self.shape = Rectangle_Shape()

            self.shape.initialize(context, target_obj, snap_to_target)

    def create_object(self, context):

        # Create a mesh and an object and 
        # add the object to the scene collection
        mesh = bpy.data.meshes.new("MyMesh")
        obj  = bpy.data.objects.new("MyObject", mesh)

        bpy.context.scene.collection.objects.link(obj)
        
        bpy.ops.object.select_all(action='DESELECT')

        bpy.context.view_layer.objects.active = obj
        obj.select_set(state=True)

        # Create a bmesh and add the vertices
        # added by mouse clicks
        bm = bmesh.new()
        bm.from_mesh(mesh) 

        for v in self.shape.vertices:
            bm.verts.new(v)
        
        bm.verts.index_update()

        bm.faces.new(bm.verts)

        # Extrude mesh if extrude mesh option is enabled
        self.extrude_mesh(context, bm)

        bm.to_mesh(mesh)  
        bm.free()

        bpy.context.view_layer.objects.active = obj
        obj.select_set(state=True)

        self.remove_doubles()

       
        # set origin to geometry
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

        # Fast bool modes
        if context.scene.bool_mode != "Create":

            target_obj = bpy.context.scene.carver_target
            if target_obj is not None:

                bool_mode_id = self.get_bool_mode_id(context.scene.bool_mode)
                if bool_mode_id != 3:
                    execute_boolean_op(context, target_obj, bool_mode_id)
                else:
                    execute_slice_op(context, target_obj)

                # delete the bool object if apply immediate is checked
                if is_apply_immediate():
                    bpy.ops.object.delete()
                    select_active(target_obj)

    def get_bool_mode_id(self, bool_name):
        if bool_name == "Difference":
            return 0
        elif bool_name == "Union":
            return 1
        elif bool_name == "Intersect":
            return 2
        elif bool_name == "Slice":
            return 3
        return -1

    def remove_doubles(self):
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles()       

    def extrude_mesh(self, context, bm):
        if context.scene.extrude_mesh:
            
            dir = self.shape.get_dir() * context.scene.draw_distance * 2

            if self.shape.is_extruded():
                dir = self.shape.get_dir() * self.shape.extrusion

            r = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
            verts = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
            bmesh.ops.translate(bm, vec=dir, verts=verts)


    def finish(self):
        self.unregister_handlers(bpy.context)
        return {"FINISHED"}

    def create_batch(self, mouse_pos = None):
        
        points = self.shape.get_vertices_copy(mouse_pos)

        extrude_points = self.shape.get_vertices_extruded_copy(mouse_pos)

        extrude_lines = []
        for index, vertex in enumerate(extrude_points):
            extrude_lines.append(points[index])
            extrude_lines.append(vertex)

        self.shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
         
        self.batch = batch_for_shader(self.shader, 'LINE_LOOP', 
            {"pos": points})

        self.batch_extruded = batch_for_shader(self.shader, 'LINE_LOOP', 
            {"pos": extrude_points})

        self.batch_lines_extruded = batch_for_shader(self.shader, 'LINES', 
            {"pos": extrude_lines})

        self.batch_points = batch_for_shader(self.shader, 'POINTS', {"pos": points})

	# Draw handler to paint in pixels
    def draw_callback_2d(self, op, context):

        # Draw text for primitive mode
        region = context.region
        text = "- Primitive mode -"

        subtext = self.shape.get_text(context)

        xt = int(region.width / 2.0)
        
        blf.size(0, 24, 72)
        blf.position(0, xt - blf.dimensions(0, text)[0] / 2, 60 , 0)
        blf.draw(0, text) 

        blf.size(1, 16, 72)
        blf.color(1, 1, 1, 1, 1)
        blf.position(1, xt - blf.dimensions(1, subtext)[0] / 2, 30 , 1)
        blf.draw(1, subtext) 

	# Draw handler to paint onto the screen
    def draw_callback_3d(self, op, context):

        # Draw lines
        bgl.glEnable(bgl.GL_LINE_SMOOTH)
        self.shader.bind()

        self.shader.uniform_float("color", (0.2, 0.5, 0.8, 1.0))
        bgl.glLineWidth(2)
        self.batch_extruded.draw(self.shader)

        bgl.glLineWidth(1)
        self.batch_lines_extruded.draw(self.shader)

        bgl.glLineWidth(3)
        self.shader.uniform_float("color", (0.1, 0.3, 0.7, 1.0))
        self.batch.draw(self.shader)

        if self.shape.draw_points():
            bgl.glPointSize(10)
            self.batch_points.draw(self.shader)

