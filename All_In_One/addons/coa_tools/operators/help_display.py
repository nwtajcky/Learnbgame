import bpy
import blf, bgl
from .. functions import get_sprite_object


class ShowHelp(bpy.types.Operator):
    bl_idname = "coa_tools.show_help"
    bl_label = "Show Help"
    bl_description = "Show Help"
    bl_options = {"REGISTER"}

    region_offset = 0
    region_height = 0
    region_width = 0
    _timer = None
    alpha = 1.0
    alpha_current = 0.0
    global_pos = 0.0
    i = 0
    fade_in = False
    scale_y = .7
    scale_x = 1.0
    display_height = 1060 # display height before scaling starts
    display_width = 1000
    
    @classmethod
    def poll(cls, context):
        return True

    def write_text(self,text,size=20,pos_y=0,color=(1,1,1,1)):
        start_pos = self.region_height - 60*self.scale_y
        lines = text.split("\n")
        
        pos_y = start_pos - (pos_y * self.scale_y)
        size = int(size * self.scale_y)
        
        bgl.glColor4f(color[0],color[1],color[2],color[3]*self.alpha_current)
        line_height = (size + size*.5) * self.scale_y
        for i,line in enumerate(lines):
            
            blf.position(self.font_id, 15+self.region_offset, pos_y-(line_height*i), 0)
            blf.size(self.font_id, size, 72)
            blf.draw(self.font_id, line)
            
    def invoke(self, context, event):
        wm = context.window_manager
        wm.coa_show_help = True
        args = ()
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_px, args, "WINDOW", "POST_PIXEL")
        self._timer = wm.event_timer_add(0.1, context.window)
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}
    
    def fade(self):
        self.alpha_current = self.alpha_current*.55 + self.alpha*.45
            
    def modal(self, context, event):
        wm = context.window_manager
        context.area.tag_redraw()
        for region in context.area.regions:
            if region.type == "TOOLS":
                self.region_offset = region.width
            if region.type == "WINDOW":    
                self.region_height = region.height
                self.region_width = region.width
                #self.scale_y = self.region_height/920
                self.scale_y = self.region_height/self.display_height
                self.scale_y = min(1.0,max(.7,self.scale_y))
                self.scale_x = self.region_width/self.display_width
                self.scale_x = min(1.0,max(.0,self.scale_x))
        
        if context.user_preferences.system.use_region_overlap:
            pass
        else:
            self.region_offset = 0
        
        if not wm.coa_show_help:
            self.alpha = 0.0
            
        if not wm.coa_show_help and round(self.alpha_current,1) == 0:#event.type in {"RIGHTMOUSE", "ESC"}:
            return self.finish()
        
        if self.alpha != round(self.alpha_current,1):
            self.fade()  
        return {"PASS_THROUGH"}

    def finish(self):
        context = bpy.context
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
        
        return {"FINISHED"}

    def draw_callback_px(self):
        self.sprite_object = get_sprite_object(bpy.context.active_object)
        
        self.font_id = 0  # XXX, need to find out how best to get this.
        global_pos = self.region_height - 60
        # draw some text
        headline_color = [1.0, 0.9, 0.6, 1.0]
        headline_color2 = [0.692584, 1.000000, 0.781936, 1.000000]
        headline_color3 = [0.707686, 1.000000, 0.969626, 1.000000]
        
        ### draw gradient overlay
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glBegin(bgl.GL_QUAD_STRIP)
        color_black = [0.0,0.0,0.0]
        x_coord1 = self.region_offset
        x_coord2 = 525 * self.scale_x
        y_coord1 = self.region_height
        alpha1 = self.alpha_current * 0.7
        alpha2 = self.alpha_current * 0.0
        
        bgl.glColor4f(color_black[0],color_black[1],color_black[2],alpha1)
        bgl.glVertex2f(x_coord1,0)
        
        bgl.glColor4f(color_black[0],color_black[1],color_black[2],alpha1)
        bgl.glVertex2f(x_coord1,y_coord1)
        
        bgl.glColor4f(color_black[0],color_black[1],color_black[2],alpha2)
        bgl.glVertex2f(x_coord2,0)
        
        bgl.glColor4f(color_black[0],color_black[1],color_black[2],alpha2)
        bgl.glVertex2f(x_coord2,y_coord1)
        bgl.glEnd()
        
        
        
        ### draw hotkeys help
        texts = []
        
        text_headline = [["COA Tools Hotkeys Overview",25]]
        
        text_general = [
                ["Pie Menu",20],
                ["      F   -   Contextual Pie Menu",15],
                
                ["Sprite Outliner",20],
                ["      Ctrl + Click    -   Add Item to Selection",15],
                ["      Shift + Click   -   Multi Selection",15],
                
                ["Keyframes",20],
                ["      Ctrl + Click on Key Operator    -   Opens Curve Interpolation Options",15],
                ["      I    -   Keyframe Menu",15]]
        
        text_armature = [        
                ["Edit Armature Mode",20],
                ["  Create",17],
                ["      Click + Drag    -   Draw Bone",15],
                ["      Shift + Click + Drag    -   Draw Bone locked to 45 Angle",15],

                ["",15],
                ["  Hierarchy",17],                
                ["      Ctrl + P    -    Parent selected Bones to Active",15],
                ["      Alt + P    -    Clear parenting",15],
                
                ["",15],
                ["  Select",17],
                ["      Right Click   -   Select Bone",15],
                ["      Shift + Right Click   -   Add to Selection",15],
                ["      A   -   Select / Deselect All",15],
                ["      B   -   Border Selection",15],
                ["      C   -   Paint Selection",15],
                ["      L   -   Select Hovered Mesh",15],
                ["      Ctrl + Draw    -   Draw Selection Outline",15],
                
                ["",15],
                ["  Bind Mesh",17],
                ["      Alt + Click    -    Click on Sprite or Layer in Outliner.",15],
                ["                              Binds Bone with Sprite.",15],

                ["",15],
                ["  General",17],
                ["      Tab    -    Exit Edit Armature Mode",15]]
        
        text_mesh = [        
                ["Edit Mesh Mode",20],
                ["  Create",17],
                ["      Click + Drag    -   Add/Draw Points",15],
                ["      Alt + Click    -   Delete Vertex or Edge",15],
                ["      Shift + Click on Edge    -   Set Edge Length for drawing Edges",15],

                ["",15],
                ["  Connect / Fill Shortcuts",17],
                ["      F   -   Connect Verts, Edges and Faces",15],
                ["      Alt + F   -   Fill Edge Loop",15],
                
                ["",15],
                ["  Select",17],
                ["      Right Click   -   Select Object",15],
                ["      Shift + Right Click   -   Add to Selection",15],
                ["      A   -   Select / Deselect All",15],
                ["      B   -   Border Selection",15],
                ["      C   -   Paint Selection",15],
                ["      L   -   Select Hovered Mesh",15],
                ["      Ctrl + Draw    -   Draw Selection Outline",15],
                
                ["",15],
                ["  Manipulate",17],
                ["      S   -   Scale Selection",15],
                ["      G   -   Move Selection",15],
                ["      R   -   Rotate Selection",15],
                
                ["",15],
                ["  General",17],                
                ["      Ctrl + V    -    Vertex Menu",15],
                ["      Ctrl + E    -    Edge Menu",15],
                ["      Ctrl + F    -    Face Menu",15],
                ["      W    -    Specials Menu",15],
                ["      Tab    -    Exit Edit Mesh Mode",15]]
        
        text_shapekey = [        
                ["Edit Shapkey Mode",20],
                ["      G       -   Select Grab Brush",15],
                ["      F       -   Change Brush Size",15],
                ["      Shift + F   -   Change Brush Strength",15]]
                
        text_weights = [        
                ["Edit Weights Mode",20],
                ["  Brush Settings",17],  
                ["      1       -   Add Brush",15],
                ["      2       -   Blur Brush",15],
                ["      8       -   Subtract Brush",15],
                ["",15],
                ["      F       -   Change Brush Size",15],
                ["      Shift + F   -   Change Brush Strength",15],
                
                ["",15],
                ["  General",17],  
                ["      Tab    -    Exit Edit Weights Mode",15]]
                
        
        text_blender = [        
                ["Blender General",20],
                ["  Mouse",17],  
                ["      Right Click   -   Select Object",15],
                ["      Left Click   -   Confirm / Edit Values in UI",15],
                ["      Shift + Right Click   -   Add to Selection",15],
                
                ["",15],
                ["  Select",17],  
                ["      A   -   Select / Deselect All",15],
                ["      B   -   Border Selection",15],
                ["      C   -   Paint Selection",15],
                ["      L   -   Select Hovered Mesh",15],
                ["      Ctrl + Draw    -   Draw Selection Outline",15],
                
                ["",15],
                ["  Manipulate",17],  
                ["      S   -   Set Scale",15],
                ["      G   -   Set Location",15],
                ["      R   -   Set Rotation",15],
                ["",15],
                ["      Alt + S   -   Reset Scale",15],
                ["      Alt + G   -   Reset Location",15],
                ["      Alt + R   -   Reset Rotation",15],
                
                
                ["",15],
                ["  Menues",17],
                ["      W   -   Specials Menu",15]]
        
        texts += text_headline
        if self.sprite_object == None or (self.sprite_object != None and self.sprite_object.coa_edit_mode in ["OBJECT"]):
            texts += text_general
        if self.sprite_object == None or (self.sprite_object != None and self.sprite_object.coa_edit_mode in ["OBJECT"]):    
            texts += text_blender
        if self.sprite_object == None or (self.sprite_object != None and self.sprite_object.coa_edit_mode in ["ARMATURE"]):
            texts += text_armature
        if self.sprite_object == None or (self.sprite_object != None and self.sprite_object.coa_edit_mode in ["SHAPEKEY"]):
            texts += text_shapekey
        if self.sprite_object == None or (self.sprite_object != None and self.sprite_object.coa_edit_mode in ["WEIGHTS"]):
            texts += text_weights
        if self.sprite_object == None or (self.sprite_object != None and self.sprite_object.coa_edit_mode in ["MESH"]):
            texts += text_mesh
        
        linebreak_size = 0
        for i,text in enumerate(texts):
            line = text[0]
            lineheight = text[1]
            if i > 0:
                linebreak_size += 20
                if lineheight == 20:
                    linebreak_size += 30
        
            color = [1.0,1.0,1.0,1.0]
            if lineheight == 20:
                color = headline_color
            elif lineheight == 25:
                color = headline_color2
            elif lineheight == 17:
                color = headline_color3    
            ### custom color
            if len(text) == 3:
                color = text[2]
            self.write_text(line,size=lineheight,pos_y=linebreak_size,color=color)
        
        
        # restore opengl defaults
        bgl.glLineWidth(1)
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
        