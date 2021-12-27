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

import bpy
import re
import os
import subprocess
import blend_render_info
from sys import platform
from bpy_extras.io_utils import ImportHelper
from numpy import arange, around, isclose
from itertools import count, groupby
import rna_keymap_ui
import webbrowser


bl_info = {
    "name": "Loom",
    "description": "Image sequence rendering, encoding and playback",
    "author": "Christian Brinkmann (p2or)",
    "version": (0, 1),
    "blender": (2, 79, 0),
    "location": "Render Menu or Render Panel (optional)",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "https://github.com/p2or/blender-loom",
    "tracker_url": "https://github.com/p2or/blender-loom/issues",
    "support": "COMMUNITY",
    "category": "Learnbgame",
}

# -------------------------------------------------------------------
#    Preferences & Scene Properties
# -------------------------------------------------------------------

class LoomPreferences(bpy.types.AddonPreferences):

    bl_idname = __name__

    terminal = bpy.props.EnumProperty(
        name="Terminal",
        items=(
            ("win-default", "Windows Default Terminal", "", 1),
            ("osx-default", "OSX Default Terminal", "", 2),
            ("x-terminal-emulator", "X Terminal Emulator", "", 3),
            ("xfce4-terminal", "Xfce4 Terminal", "", 4),
            ("xterm", "xterm", "", 5)))

    xterm_flag = bpy.props.BoolProperty(
        name="Use Xterm (Terminal Fallback)",
        description="Serves as fallback for OSX and others",
        default=False)
        
    bash_file = bpy.props.StringProperty(
        name="Bash file",
        description = "Filepath to temporary bash or bat file")

    bash_flag = bpy.props.BoolProperty(
        name="Force Bash File",
        description="Force using bash file instead of individual arguments",
        default=False)

    render_dialog_width = bpy.props.IntProperty(
        name="Render Dialog Width",
        description = "Width of Image Sequence Render Dialog",
        subtype='PIXEL',
        default=450, min=400)

    encode_dialog_width = bpy.props.IntProperty(
        name="Encoding Dialog Width",
        description = "Width of Encoding Dialog",
        subtype='PIXEL',
        default=650, min=400)

    log_render = bpy.props.BoolProperty(
        name="Logging (Required for Playback)",
        description="If enabled render output properties will be saved",
        default=True)

    log_render_limit = bpy.props.IntProperty(
        name="Log Limit",
        default=3)

    playblast_flag = bpy.props.BoolProperty(
        name="Playblast (Experimental)",
        description="Playback rendered sequences",
        default=False)
    
    user_player = bpy.props.BoolProperty(
        name="Default Animation Player",
        description="Use default player (User Preferences > File > Animation Player)",
        default=False)

    display_ui = bpy.props.BoolProperty(
        name="Display Buttons in Render Panel",
        description = "Displays Buttons in Render Panel",
        default=False)

    ffmpeg_path = bpy.props.StringProperty(
        name="FFmpeg Binary",
        description="Path to ffmpeg",
        maxlen=1024,
        subtype='FILE_PATH')

    default_codec = bpy.props.StringProperty(
        name="User Codec",
        description = "Default user codec")

    batch_dialog_width = bpy.props.IntProperty(
        name="Batch Dialog Width",
        description="Width of Batch Render Dialog",
        subtype='PIXEL',
        default=650, min=600, max=1800)

    batch_dialog_rows = bpy.props.IntProperty(
        name="Number of Rows",
        description="Number of Rows",
        min=7, max=40,
        default=12)
    
    batch_paths_flag = bpy.props.BoolProperty(
        name="Display File Paths",
        description="Display File paths")

    batch_path_col_width = bpy.props.FloatProperty(
        name="Path Column Width",
        description="Width of path column in list",
        default=0.6, min=0.3, max=0.8)

    batch_name_col_width = bpy.props.FloatProperty(
        name="Name Column Width",
        description="Width of name column in list",
        default=0.45, min=0.3, max=0.8)

    render_background = bpy.props.BoolProperty(
        name="Render in Background",
        description="Do not activate the Console",
        default=False)

    def draw(self, context):
        split_width = 0.4
        layout = self.layout
        box = layout.box()
        split = box.split(split_width)
        col = split.column()
        if bpy.app.version < (2, 80, 0): col.prop(self, "display_ui")
        col.prop(self, "playblast_flag")
        up = col.column()
        up.prop(self, "user_player")
        up.enabled = self.playblast_flag
        col = split.column(split_width)
        col.prop(self, "render_dialog_width") 
        col.prop(self, "encode_dialog_width")
        col.prop(self, "batch_dialog_width")

        box = layout.box()
        split = box.split(split_width)
        col = split.column()
        col.label("Path to FFmpeg Binary:")
        txt = "Force generating .bat file" if platform.startswith('win32') else "Force generating .sh file"
        col_sub = col.column()
        col_sub.prop(self, "bash_flag", text=txt)
        
        """ OSX specific properties """
        if platform.startswith('darwin'):
            col_sub.enabled = False
            col.prop(self, "render_background")
            
        """ Linux/OSX specific properties """
        if not platform.startswith('win32'):
            col.prop(self, "xterm_flag")

        col = split.column()
        col.prop(self, "ffmpeg_path", text="")
        sub = col.row(align=True)
        txt = "Delete temporary .bat Files" if platform.startswith('win32') else "Delete temporary .sh files"
        sub.operator(LoomDeleteBashFiles.bl_idname, text=txt, icon="FILE_SCRIPT")
        script_folder = bpy.utils.script_path_user()
        sub.operator(LoomOpenFolder.bl_idname, icon="DISK_DRIVE", text="").folder_path = script_folder
            
        """ Hotkey box """
        box = layout.box()
        split = box.split()
        col = split.column()
        col.label('Hotkeys')
        kc_usr = bpy.context.window_manager.keyconfigs.user
        km_usr = kc_usr.keymaps.get('Screen')

        if not user_keymap_ids: # Ouch, Todo!
            for kmi_usr in km_usr.keymap_items:
                for km_addon, kmi_addon in addon_keymaps:
                    if kmi_addon.compare(kmi_usr):
                        user_keymap_ids.append(kmi_usr.id)
        for kmi_usr in km_usr.keymap_items: # user hotkeys by namespace
            if kmi_usr.idname.startswith("loom."):
                col.context_pointer_set("keymap", km_usr)
                rna_keymap_ui.draw_kmi([], kc_usr, km_usr, kmi_usr, col, 0)

        row = layout.row()
        layout.operator(LoomPreferencesReset.bl_idname, icon='FILE_REFRESH')


class LoomPreferencesReset(bpy.types.Operator):
    """Reset Add-on Preferences"""
    bl_idname = "loom.reset_preferences"
    bl_label = "Reset Preferences"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        prefs = context.user_preferences.addons[__name__].preferences
        prefs.property_unset("terminal")
        prefs.property_unset("xterm_flag")
        prefs.property_unset("render_dialog_width")
        prefs.property_unset("encode_dialog_width")
        prefs.property_unset("bash_flag")
        prefs.property_unset("bash_file")
        prefs.property_unset("display_ui")
        prefs.property_unset("user_player")
        prefs.property_unset("log_render")
        prefs.property_unset("log_render_limit")
        #prefs.property_unset("ffmpeg_path")
        prefs.property_unset("default_codec")
        prefs.property_unset("playblast_flag")

        """ Restore default keys by keymap ids """
        kc_usr = context.window_manager.keyconfigs.user
        km_usr = kc_usr.keymaps.get('Screen')
        for i in user_keymap_ids:
            kmi = km_usr.keymap_items.from_id(i)
            if kmi:
                km_usr.restore_item_to_default(kmi)
        #bpy.ops.wm.save_userpref()
        return {'FINISHED'}


class LoomRenderCollection(bpy.types.PropertyGroup):
    # name = bpy.props.StringProperty()
    render_id = bpy.props.IntProperty()
    start_time = bpy.props.StringProperty()
    start_frame = bpy.props.StringProperty()
    end_frame = bpy.props.StringProperty()
    file_path = bpy.props.StringProperty()
    padded_zeros = bpy.props.IntProperty()
    image_format = bpy.props.StringProperty()


class LoomBatchRenderCollection(bpy.types.PropertyGroup):
    # name = bpy.props.StringProperty()
    rid = bpy.props.IntProperty()
    path = bpy.props.StringProperty()
    frame_start = bpy.props.IntProperty()
    frame_end = bpy.props.IntProperty()
    scene = bpy.props.StringProperty()
    frames = bpy.props.StringProperty(name="Frames")
    encode_flag = bpy.props.BoolProperty(default=False)
    input_filter = bpy.props.BoolProperty(default=False)


class LoomSettings(bpy.types.PropertyGroup):

    frame_input = bpy.props.StringProperty(
        name="Frames to render",
        description="Specify a range or single frames to render")

    filter_input = bpy.props.BoolProperty(
        name="Filter individual elements",
        description="Isolate numbers after exclude chars (^, !)",
        default=False)

    command_line = bpy.props.BoolProperty(
        name="Render using Command Line",
        description="Send frames to Command Line (background process)",
        default=False)

    override_threads = bpy.props.BoolProperty(
        name="Override CPU thread count",
        description="Force to render with specified thread count (CPU)",
        default=False)

    threads = bpy.props.IntProperty(
        name="CPU Threads",
        description="Number of CPU threads to use simultaneously while rendering",
        min = 1)
    
    sequence_encode = bpy.props.StringProperty(
        name="Image Sequence",
        description="Image Sequence",
        maxlen=1024)

    movie_path = bpy.props.StringProperty(
        name="Movie",
        description="Movie File output path",
        maxlen=1024)

    lost_frames = bpy.props.StringProperty(
        name="Missing Frames",
        description="Missing Frames",
        default="",
        options={'SKIP_SAVE'})

    render_collection = bpy.props.CollectionProperty(
        name="Render Collection",
        type=LoomRenderCollection)

    batch_scan_folder = bpy.props.StringProperty(
        name="Folder",
        description="Folder",
        maxlen=1024)

    batch_render_idx = bpy.props.IntProperty(
        name="Collection Index",
        description="Collection Index")
       
    batch_render_coll = bpy.props.CollectionProperty(
        name="Batch Render Collection",
        type=LoomBatchRenderCollection)


# -------------------------------------------------------------------
#    UI Operators
# -------------------------------------------------------------------

class LoomRenderThreads(bpy.types.Operator):
    """Set all available threads"""
    bl_idname = "loom.available_threads"
    bl_label = "Reset Threads"
    bl_description = "Set to all available threads"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        from multiprocessing import cpu_count
        context.scene.loom.threads = cpu_count()
        self.report({'INFO'}, "Set to core maximum")
        return {'FINISHED'}


class LoomRenderFullScale(bpy.types.Operator):
    """Set Resolution Percentage Scale to 100%"""
    bl_idname = "loom.full_scale"
    bl_label = "Full Scale"
    bl_description = "Set Resolution Percentage Scale to 100%"
    bl_options = {'INTERNAL'}

    def execute(self, context): #context.area.tag_redraw()
        context.scene.render.resolution_percentage = 100
        return {'FINISHED'}


class LoomRenderTimelineProperties(bpy.types.Operator):
    """Set timeline range, steps & threads from UI"""
    bl_idname = "loom.timeline_properties"
    bl_label = "Timeline UI Properties"
    bl_description = "Set range based on Timeline"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        scn = context.scene
        lum = scn.loom
        timeline_range = "{start}-{end}".format(start=scn.frame_start, end=scn.frame_end)
        timeline_inc = "{range}x{inc}".format(range=timeline_range, inc=scn.frame_step)
        lum.frame_input = timeline_inc if scn.frame_step != 1 else timeline_range
        return {'FINISHED'}


class LoomRenderVerifyFrames(bpy.types.Operator):
    """Display all frames & the current render location"""
    bl_idname = "loom.verify_frames"
    bl_label = "Verify Input Frames"
    bl_description = "Report all Frames that are going to be rendered"
    bl_options = {'INTERNAL'}

    frame_input = None
    def execute(self, context):
        scn = context.scene
        folder = os.path.realpath(bpy.path.abspath(scn.render.filepath))
        
        if self.frame_input:
            self.report({'INFO'}, ("{} {} [{}] will be rendered to {}".format(
                len(self.frame_input),
                "Frame" if len(self.frame_input) == 1 else "Frames",
                ', '.join('{}'.format(i) for i in self.frame_input), 
                folder)))
        else:
            self.report({'INFO'}, "No frames specified")
        return {'FINISHED'}

    def invoke(self, context, event):
        lum = context.scene.loom
        self.frame_input = filter_frames(
            lum.frame_input, context.scene.frame_step, lum.filter_input)
        return self.execute(context)


class LoomRenderDialog(bpy.types.Operator):
    """Render Image Sequence UI"""
    bl_idname = "loom.render_dialog"
    bl_label = "Render Image Sequence"
    bl_description = "Render Image Sequence"
    bl_options = {'REGISTER'}

    show_errors = bpy.props.BoolProperty(
        name="Show Errors",
        description="Displays Errors and Warnings",
        default=False,
        options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return not context.scene.render.is_movie_format

    def check(self, context):
        return True
    
    def write_permission(self, folder): # Hacky, but ok for now
        # https://stackoverflow.com/q/2113427/3091066
        try: # os.access(os.path.realpath(bpy.path.abspath(out_folder)), os.W_OK)
            pf = os.path.join(folder, "permission.txt")
            fh = open(pf, 'w')
            fh.close()
            os.remove(pf)
            return True
        except:
            return False

    def execute(self, context):
        prefs = context.user_preferences.addons[__name__].preferences
        scn = context.scene
        lum = scn.loom
        filter_individual_numbers = lum.filter_input
        user_input = lum.frame_input

        """ Error handling """
        user_error = False

        if not self.options.is_invoke:
            user_error = True

        if not bpy.data.is_saved:
            self.report({'ERROR'}, "Blend-file not saved.")
            user_error = True
        
        if not context.scene.camera:
            self.report({'ERROR'}, "No camera in scene.")
            user_error = True

        if not user_input and not any(char.isdigit() for char in user_input):
            self.report({'ERROR'}, "No frames to render.")
            user_error = True
        
        out_folder, out_filename = os.path.split(scn.render.filepath)
        if not self.write_permission(os.path.realpath(bpy.path.abspath(out_folder))):
            self.report({'ERROR'}, "Specified output folder does not exist (permission denied)")
            user_error = True

        if user_error: #bpy.ops.loom.render_dialog('INVOKE_DEFAULT')
            return {"CANCELLED"}

        """ Start rendering headless or within the UI as usual """
        if lum.command_line:
            bpy.ops.loom.render_terminal(
                frames = user_input,
                threads = lum.threads,
                isolate_numbers = filter_individual_numbers)
        else:
            bpy.ops.render.image_sequence(
                frames = user_input, 
                isolate_numbers = filter_individual_numbers,
                render_silent = False)
        return {"FINISHED"}

    def invoke(self, context, event):
        scn = context.scene
        lum = scn.loom
        prefs = context.user_preferences.addons[__name__].preferences
        if not lum.is_property_set("frame_input") or not lum.frame_input:
            bpy.ops.loom.timeline_properties()

        if not prefs.is_property_set("terminal") or not prefs.terminal:
            bpy.ops.loom.verify_terminal()
        if not lum.is_property_set("threads") or not lum.threads:
            lum.threads = scn.render.threads  # *.5

        return context.window_manager.invoke_props_dialog(self, 
            width=(prefs.render_dialog_width*context.user_preferences.system.pixel_size))

    def draw(self, context):
        scn = context.scene
        lum = scn.loom
        prefs = context.user_preferences.addons[__name__].preferences
        layout = self.layout  # layout.label("Render Image Sequence")

        split = layout.split(.17)
        col = split.column(align=True)
        col.label("Frames:")
        col = split.column(align=True)
        sub = col.row(align=True) #GHOST_ENABLED
        sub.operator(LoomRenderTimelineProperties.bl_idname, icon='PREVIEW_RANGE', text="")
        sub.prop(lum, "frame_input", text="")
        sub.prop(lum, "filter_input", icon='FILTER', icon_only=True)
        #sub.prop(lum, "filter_keyframes", icon='SPACE2', icon_only=True)
        sub.operator(LoomRenderVerifyFrames.bl_idname, icon='GHOST_ENABLED', text="") #SEQ_LUMA_WAVEFORM

        split = layout.split(.17)
        col = split.column(align=True)
        col.active = not lum.command_line
        col.label("Display:")
        col = split.column(align=True)
        sub = col.row(align=True)
        sub.active = not lum.command_line
        sub.prop(scn.render, "display_mode", text="")
        sub.prop(scn.render, "use_lock_interface", icon_only=True)
            
        row = layout.row(align=True)    
        row.prop(lum, "command_line", text="Render using Command Line")
        if scn.render.resolution_percentage < 100:
            row.prop(self, "show_errors", text="", icon='SCRIPT' if self.show_errors else "REC", emboss=False)
        else:
            row.operator(LoomHelp.bl_idname, icon='HELP', text="", emboss=False)
            #row.prop(self, "show_errors", icon='SCRIPT' if self.selection else "HELP", text="", emboss=False)
            
        if lum.command_line:
            row = layout.row(align=True)
            row.prop(lum, "override_threads",  icon='RADIO', icon_only=True)
            thr_elem = row.row(align=True)
            thr_elem.active = bool(lum.command_line and lum.override_threads)
            thr_elem.prop(lum, "threads")
            thr_elem.operator(LoomRenderThreads.bl_idname, icon='LOOP_BACK', text="")
            #thr_elem.prop(lum, "extra_terminal", icon='CONSOLE', icon_only=True)
        
        if self.show_errors:
            res_percentage = scn.render.resolution_percentage
            if res_percentage < 100:
                row = layout.row()
                row.label("Warning: Resolution Percentage Scale is set to {}%".format(res_percentage))
                row.operator(LoomRenderFullScale.bl_idname, icon="RECOVER_AUTO", text="", emboss=False)


"""
# Todo!
# 'real' render button on a wm.invoke_popup()

class RenderButton(bpy.types.Operator):
    bl_idname = "loom.render"
    bl_label = "Render Seqence"
    bl_options = {'REGISTER'}
    
    # row.operator(RenderButton.bl_idname, icon='RENDER_STILL')
    # win = context.window #win.cursor_warp((win.width*.5)-100, (win.height*.5)+100)
    
    def execute(self, context):
        return {'FINISHED'}

"""

class LoomRenderInputDialog(bpy.types.Operator):
    """Allows to pass custom numbers and ranges to the render dialog"""
    bl_idname = "loom.render_input_dialog"
    bl_label = "Render Frames"
    bl_description = "Open up Render Image Sequence dialog"
    bl_options = {'INTERNAL'}

    frame_input = bpy.props.StringProperty()

    def execute(self, context):
        if self.frame_input:
            context.scene.loom.frame_input = self.frame_input
            bpy.ops.loom.render_dialog('INVOKE_DEFAULT')
            return {'FINISHED'}
        else:
            return {'CANCELLED'}
        

class LoomRenderSelectedKeysDialog(bpy.types.Operator):
    """Render selected keys of the dopesheet or graph editor"""
    bl_idname = "loom.render_selected_keys"
    bl_label = "Render Selected Keyframes"
    bl_description = "Render selected keys in the dopesheet"
    bl_options = {'REGISTER'}

    def int_filter(self, flt):
        try:
            return int(flt) if flt.is_integer() else None
        except ValueError:
            return None

    def rangify_frames(self, frames):
        """ Converts a list of integers to range string [1,2,3] -> '1-3' """
        G=(list(x) for _,x in groupby(frames, lambda x,c=count(): next(c)-x))
        return ",".join("-".join(map(str,(g[0],g[-1])[:len(g)])) for g in G)

    def selected_ctrl_points(self, context):
        """ Returns all selected keys in dopesheet """
        # There is a select flag for the handles:
        # key.select_left_handle & key.select_right_handle
        ctrl_points = set()
        for action in bpy.data.actions:
            for channel in action.fcurves: 
                #if channel.select:
                for key in channel.keyframe_points:       
                    if key.select_control_point:
                        ctrl_points.add(key.co.x)
        return sorted(ctrl_points)
    
    def channel_ctrl_points(self, context):
        """Returns all keys of selected channels in dopesheet"""
        ctrl_points = set()
        for action in bpy.data.actions:
            for channel in action.fcurves:
                if channel.select: #print(action, channel.group)
                    for key in channel.keyframe_points:
                        ctrl_points.add(key.co.x)
        return sorted(ctrl_points)
    
    @classmethod
    def poll(cls, context):
         #context.area.spaces[0].mode in ('DOPESHEET', 'SHAPEKEY', ...)
        areas = ('DOPESHEET_EDITOR', 'GRAPH_EDITOR', 'TIMELINE')
        return context.area.type in areas and \
            not context.scene.render.is_movie_format

    def execute(self, context):
        selected_keys = self.selected_ctrl_points(context) 
        if not selected_keys:
            self.report({'ERROR'}, "Nothing selected.")
            return {"CANCELLED"}

        """ Return integers whenever possible """
        int_frames = [self.int_filter(frame) for frame in selected_keys]
        frames = selected_keys if None in int_frames else int_frames

        bpy.ops.loom.render_input_dialog(frame_input=self.rangify_frames(frames))
        return {'FINISHED'}


def codec_callback(scene, context):
    codec = [
        ('PRORES422', "Apple ProRes 422", ""),
        ('PRORES422HQ', "Apple ProRes 422 HQ", ""),
        ('PRORES422LT', "Apple ProRes 422 LT", ""),
        ('PRORES422PR', "Apple ProRes 422 Proxy", ""),
        ('PRORES4444', "Apple ProRes 4444", ""),
        ('PRORES4444XQ', "Apple ProRes 4444 XQ", ""),
        ('DNXHD422-08-036', "Avid DNxHD 422 8-bit 36Mbit", ""),
        ('DNXHD422-08-145', "Avid DNxHD 422 8-bit 145Mbit", ""),
        ('DNXHD422-08-145', "Avid DNxHD 422 8-bit 220Mbit", ""),
        ('DNXHD422-10-185', "Avid DNxHD 422 10-bit 185Mbit", ""),
        #('DNXHD422-10-440', "Avid DNxHD 422 10-bit 440Mbit", ""),
        #('DNXHD444-10-350', "Avid DNxHD 422 10-bit 440Mbit", ""),
        ('DNXHR-444', "Avid DNxHR 444 10bit", ""),
        ('DNXHR-HQX', "Avid DNxHR HQX 10bit", ""),
        ('DNXHR-HQ', "Avid DNxHR HQ 8bit", ""),
        ('DNXHR-SQ', "Avid DNxHR SQ 8bit", "")
    ]
    return codec

def colorspace_callback(scene, context):
    colorspace = [
        ('iec61966_2_1', "sRGB", ""),
        ('bt709', "rec709", ""),
        ('gamma22', "Gamma 2.2", ""),
        ('gamma28', "Gamma 2.8", ""),
        ('linear', "Linear", "")
    ]
    return colorspace


class LoomBatchDisplaySettings(bpy.types.Menu):
    bl_label = "Loom Batch Display Settings"
    bl_idname = "loom_batch_display_settings_menu"

    def draw(self, context):
        prefs = context.user_preferences.addons[__name__].preferences
        layout = self.layout
        layout.label(text="Display Settings", icon="COLOR")
        layout.separator()
        layout.prop(prefs, "batch_paths_flag")
        layout.prop(prefs, "batch_dialog_rows")
        if prefs.batch_paths_flag:
            layout.prop(prefs, "batch_path_col_width")
        else:
            layout.prop(prefs, "batch_name_col_width")
        layout.operator("loom.batch_dialog_reset_display", icon="ANIM")


class LoomBatchListItemDisplay(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        prefs = context.user_preferences.addons[__name__].preferences
        if prefs.batch_paths_flag:
            split = layout.split(prefs.batch_path_col_width, align=True)
            split_left = split.split(0.08)
            split_left.label("{:02d}".format(index+1))
            #split_left.prop(item, "path", text="", emboss=False, icon='FILE_BLEND')
            split_left.label(item.path, icon='FILE_BLEND')
            """
            split_op = split_left.split(0.01)
            split_op.operator("loom.batch_default_frames", icon="FILE_BLEND", text="", emboss=True).item_id = index
            split_op.prop(item, "path", text="", emboss=False)
            """
        else:
            split = layout.split(prefs.batch_name_col_width, align=True)
            split_left = split.split(0.1)
            #split_left.label("{:02d}".format(index+1))
            split_left.operator("loom.batch_default_frames", text="{:02d}".format(index+1), emboss=False).item_id = index
            split_left.label(item.name, icon='FILE_BLEND')
            
        split_right = split.split(.99)
        row = split_right.row(align=True)
        row.operator("loom.batch_default_frames", icon="PREVIEW_RANGE", text="").item_id = index
        row.prop(item, "frames", text="") #, icon='IMAGEFILE'
        #row = split_right.row(align=True) #row.prop(item, "input_filter", text="", icon='FILTER')
        row.prop(item, "input_filter", text="", icon='FILTER')
        row.operator("loom.batch_verify_input", text="", icon='GHOST_ENABLED').item_id = index
        #if prefs.ffmpeg_path:
        row.prop(item, "encode_flag", text="", icon='FILE_MOVIE')
        
    def invoke(self, context, event):
        pass   
    

class LoomBatchDialog(bpy.types.Operator):
    """Loom Batch Render Dialog"""
    bl_idname = "loom.batch_render_dialog"
    bl_label = "Loom Batch"
    bl_options = {'REGISTER'}
   
    colorspace = bpy.props.EnumProperty(
        name="Colorspace",
        description="colorspace",
        items=colorspace_callback)

    codec = bpy.props.EnumProperty(
        name="Codec",
        description="Codec",
        items=codec_callback)
    
    fps = bpy.props.IntProperty(
        name="Frame Rate",
        description="Frame Rate",
        default=25, min=1)

    terminal = bpy.props.BoolProperty(
        name="Terminal Instance",
        description="Render in new Terminal Instance",
        default=True)

    shutdown = bpy.props.BoolProperty(
        name="Shutdown",
        description="Shutdown when done",
        default=False)

    def determine_type(self, val): 
        #val = ast.literal_eval(s)
        if (isinstance(val, int)):
            return ("chi")
        elif (isinstance(val, float)):
            return ("chf")
        if val in ["true", "false"]:
            return ("chb")
        else:
            return ("chs")

    def pack_multiple_cmds(self, dct):
        rna_lst = []
        for key, args in dct.items():
            for i in args:
                rna_lst.append({"idc": key, "name": self.determine_type(i), "value": str(i)})
        return rna_lst

    def pack_arguments(self, lst):
        return [{"idc": 0, "name": self.determine_type(i), "value": str(i)} for i in lst]

    def write_permission(self, folder): # Hacky, but ok for now
        # https://stackoverflow.com/q/2113427/3091066
        try: # os.access(os.path.realpath(bpy.path.abspath(out_folder)), os.W_OK)
            pf = os.path.join(folder, "permission.txt")
            fh = open(pf, 'w')
            fh.close()
            os.remove(pf)
            return True
        except:
            return False

    def missing_frames(self, frames):
        return sorted(set(range(frames[0], frames[-1] + 1)).difference(frames))

    def verify_app(self, cmd):
        try:
            subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                return False
        return True

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        prefs = context.user_preferences.addons[__name__].preferences
        lum = context.scene.loom
        black_list = []

        """ Error handling """
        user_error = False
        ffmpeg_error = False

        if not bool(lum.batch_render_coll):
            self.report({'ERROR'}, "No files to render.")
            user_error = True

        for item in lum.batch_render_coll:
            if not item.frames and not any(char.isdigit() for char in item.frames):
                self.report({'ERROR'}, "{} [wrong frame input]".format(item.name))
                user_error = True

            if not os.path.isfile(item.path):
                self.report({'ERROR'}, "{} does not exist anymore".format(item.name))
                user_error = True

            """ encode errors """
            if item.encode_flag:
                
                """ Verify ffmpeg """
                if not prefs.ffmpeg_path:
                    if self.verify_app(["ffmpeg", "-h"]):
                        prefs.ffmpeg_path = "ffmpeg"
                    else:
                        ffmpeg_error = True
                
                elif prefs.ffmpeg_path and prefs.ffmpeg_path != "ffmpeg":
                    if not os.path.isabs(prefs.ffmpeg_path) or prefs.ffmpeg_path.startswith('//'):
                        ffmpeg_bin = os.path.realpath(bpy.path.abspath(prefs.ffmpeg_path))
                        if os.path.isfile(ffmpeg_bin): 
                            prefs.ffmpeg_path = ffmpeg_bin            
                    if not self.verify_app([prefs.ffmpeg_path, "-h"]):
                        ffmpeg_error = True

                """ verify frames """
                frames_user = filter_frames(frame_input=item.frames, filter_individual=item.input_filter)
                if self.missing_frames(frames_user):
                    black_list.append(item.name)
                    info = "Encoding {} will be skipped [Missing Frames]".format(item.name)
                    self.report({'INFO'}, info)

            out_folder, out_filename = os.path.split(item.path)
            if not self.write_permission(os.path.realpath(bpy.path.abspath(out_folder))):
                self.report({'ERROR'}, "Specified output folder does not exist (permission denied)")
                user_error = True

        if len(black_list) > 1:
            self.report({'ERROR'}, "Can not encode: {} (missing frames)".format(", ".join(black_list)))
            user_error = True

        if user_error or ffmpeg_error:
            if ffmpeg_error:
                self.report({'ERROR'}, "Path to ffmpeg binary not set in Addon preferences")
            bpy.ops.loom.batch_render_dialog('INVOKE_DEFAULT')
            return {"CANCELLED"}

        cli_arg_dict = {}
        for c, item in enumerate(lum.batch_render_coll):
            python_expr = ("import bpy;" +\
                    "bpy.ops.render.image_sequence(" +\
                    "frames='{fns}', isolate_numbers={iel}," +\
                    "render_silent={cli});" +\
                    "bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)").format(
                        fns=item.frames,
                        iel=item.input_filter, 
                        cli=True)

            cli_args = [bpy.app.binary_path, "-b", item.path, "--python-expr", python_expr]
            cli_arg_dict[c] = cli_args

        coll_len = len(cli_arg_dict)
        for c, item in enumerate(lum.batch_render_coll):
            if item.encode_flag and item.name not in black_list:
                python_expr = ("import bpy;" +\
                            "seq_path=bpy.context.scene.render.frame_path(frame=1);" +\
                            #"seq_path=bpy.context.scene.render.filepath;" +\
                            "bpy.ops.loom.encode_sequence(" +\
                            "sequence=seq_path, terminal_instance=False, pause=False)")
                
                cli_args = [bpy.app.binary_path, "-b", item.path, "--python-expr", python_expr]
                cli_arg_dict[c+coll_len] = cli_args

        """ Start headless batch encoding """
        bpy.ops.loom.run_terminal(
            #debug_arguments=True,
            binary="",
            terminal_instance=self.terminal,
            argument_collection=self.pack_multiple_cmds(cli_arg_dict),
            bash_name="loom-batch-temp",
            force_bash=True,
            shutdown=self.shutdown)

        ### TEST - MULTILINE
        '''
        s = ""
        for key, value in cli_arg_dict.items():
            s += " ".join(value) + "\n"
        bpy.ops.loom.run_terminal(
            #debug_arguments=True,
            binary="",
            terminal_instance=self.terminal,
            arguments=s,
            bash_name="loom-batch-temp",
            force_bash=True,
            shutdown=self.shutdown)
        '''
        ### TEST - RUN COMMANDS IN A LOOP
        ''' 
        for item in lum.batch_render_coll:          
            if item.encode_flag:
                python_expr = ('import bpy;'
                                'seq_path=bpy.context.scene.render.frame_path(frame=1);'
                                'bpy.ops.loom.encode_sequence(sequence=seq_path)')
                
                cli_args = ["-b", item.path, "--python-expr", python_expr]
                bpy.ops.loom.run_terminal(
                    debug_arguments=True,
                    terminal_instance=self.terminal,
                    argument_collection=self.pack_arguments(cli_args),
                    bash_name="loom-batch-temp",
                    force_bash = prefs.bash_flag,
                    communicate=True)
        '''
        return {'FINISHED'}

    def invoke(self, context, event):
        prefs = context.user_preferences.addons[__name__].preferences
        return context.window_manager.invoke_props_dialog(self, 
            width=(prefs.batch_dialog_width*context.user_preferences.system.pixel_size))

    def check(self, context):
        return True
        
    def draw(self, context):
        prefs = context.user_preferences.addons[__name__].preferences
        scn = context.scene
        lum = scn.loom

        layout = self.layout
        row = layout.row()
        row.template_list(
            "LoomBatchListItemDisplay", "", 
            lum, "batch_render_coll", 
            lum, "batch_render_idx", 
            rows=prefs.batch_dialog_rows)

        col = row.column(align=True)
        col.operator("loom.batch_select_blends", icon='ZOOMIN', text="")
        col.operator("loom.batch_dialog_action", icon='ZOOMOUT', text="").action = 'REMOVE'
        col.menu("loom_batch_display_settings_menu", icon='DOWNARROW_HLT', text="")
        col.separator()
        col.separator()
        col.operator("loom.batch_dialog_action", icon='TRIA_UP', text="").action = 'UP'
        col.operator("loom.batch_dialog_action", icon='TRIA_DOWN', text="").action = 'DOWN'
        
        row = layout.row(align=True)
        row = row.column(align=True)
        row.operator("loom.batch_scandir_blends", icon='ZOOM_SELECTED') #VIEWZOOM
        col = row.row(align=True)
        col.operator("loom.batch_remove_doubles", text="Remove Duplicates", icon="SEQ_SPLITVIEW")
        col.operator("loom.batch_clear_list", text="Clear List", icon="PANEL_CLOSE")
        
        if any(i.encode_flag for i in lum.batch_render_coll):
            split_perc = 0.3
            row = layout.row()
            split = row.split(split_perc)
            split.label("Colorspace")
            split.prop(self, "colorspace", text="")
            row = layout.row()
            split = row.split(split_perc)
            split.label("Frame Rate")
            split.prop(self, "fps", text="")
            row = layout.row()
            split = row.split(split_perc)
            split.label("Codec")
            split.prop(self, "codec", text="")
            row = layout.row()
            row.separator()
            
        #if platform.startswith('win32'):
        row = layout.row()
        row.prop(self, "shutdown", text="Shutdown when done")
        row = layout.row()

        '''
        try:
            current_item = lum.batch_render_coll[lum.batch_render_idx]
            current_item_default = "{}-{}".format(current_item.frame_start, current_item.frame_end)
            current_item_name = current_item.name
        except IndexError:
            current_item = None

        if current_item:
            row = layout.row()
            row.label("Blend: {} | Default Range: {}".format(
                    current_item_name.replace(".blend", ""), 
                    current_item_default))
        '''

class LoomBatchSelectBlends(bpy.types.Operator, ImportHelper):
    """Select Blend Files via File Browser"""
    bl_idname = "loom.batch_select_blends"
    bl_label = "Select Blend Files"
    bl_description = "Select Blend Files in File Browser"

    # ImportHelper mixin class uses this
    filename_ext = ".blend"

    filter_glob = bpy.props.StringProperty(
            default="*.blend",
            options={'HIDDEN'},
            maxlen=255)

    files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)        
    cursor_pos = [0,0]
    
    def display_popup(self, context):
        win = context.window #win.cursor_warp((win.width*.5)-100, (win.height*.5)+100)
        win.cursor_warp(self.cursor_pos[0]-100, self.cursor_pos[1]+70) # re-invoke the dialog
        bpy.ops.loom.batch_render_dialog('INVOKE_DEFAULT')

    def cancel(self, context):
        self.display_popup(context)

    def invoke(self, context, event):
        self.cursor_pos = [event.mouse_x, event.mouse_y]
        self.filename = ""
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        scn = context.scene
        lum = scn.loom
        folder = (os.path.dirname(self.filepath))
        
        added = []
        for i in self.files:
            try: # https://blender.stackexchange.com/a/55503/3710
                path_to_file = (os.path.join(folder, i.name))
                data = blend_render_info.read_blend_rend_chunk(path_to_file)
                start, end, sc = data[0]
                item = lum.batch_render_coll.add()
                item.rid = len(lum.batch_render_coll)
                item.name = i.name
                item.path = path_to_file
                item.frame_start = start
                item.frame_end = end
                item.scene = sc
                item.frames = "{}-{}".format(item.frame_start, item.frame_end)
                if i.name: added.append(i.name)
            except:
                self.report({'INFO'}, "Can't read {}".format(i.name))
        if added:
            self.report({'INFO'}, "Added {} to the list".format(", ".join(added)))
        else:
            self.report({'INFO'}, "Nothing selected")
            
        lum.batch_render_idx = len(lum.batch_render_coll)-1
        self.display_popup(context)
        return {'FINISHED'}
    

class LoomBatchScanBlends(bpy.types.Operator, ImportHelper):
    """Scan directory for blend files and add to list"""
    bl_idname = "loom.batch_scandir_blends"
    bl_label = "Scan Directory for Blend Files"
    bl_options = {'INTERNAL'}

    # ImportHelper mixin class uses this
    filename_ext = ".blend"

    filter_glob = bpy.props.StringProperty(
            default="*.blend",
            options={'HIDDEN'},
            maxlen=255)

    directory = bpy.props.StringProperty(subtype='DIR_PATH')
    sub_folders = bpy.props.BoolProperty(default=True, name="Scan Subfolders")
    cursor_pos = [0,0]

    def blend_files(self, base_dir, recursive):
        # Limitation: https://bugs.python.org/issue26111
        # https://stackoverflow.com/q/14710708/3091066
        for entry in os.scandir(base_dir):
            try:
                if entry.is_file() and entry.name.endswith(".blend"):
                    yield entry
                elif entry.is_dir() and recursive:
                    yield from self.blend_files(entry.path, recursive)
            except WindowsError:
                self.report({'WARNING'},"Access denied: {} (not a real directory)".format(entry.name))

    def display_popup(self, context):
        win = context.window #win.cursor_warp((win.width*.5)-100, (win.height*.5)+100)
        win.cursor_warp(self.cursor_pos[0]-100, self.cursor_pos[1]+70) # re-invoke the dialog
        bpy.ops.loom.batch_render_dialog('INVOKE_DEFAULT')
        
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scn = context.scene
        lum = scn.loom
        lum.batch_scan_folder = self.directory
        
        if not self.directory:
            return {'CANCELLED'}

        blend_files = self.blend_files(self.directory, self.sub_folders)
        if not blend_files:
            self.display_popup(context)
            self.report({'WARNING'},"No blend files found in {}".format(self.directory))
            return {'CANCELLED'}
        
        added = []
        for i in blend_files:
            try:
                path_to_file = (i.path)
                data = blend_render_info.read_blend_rend_chunk(path_to_file)
                start, end, sc = data[0]
                item = lum.batch_render_coll.add()
                item.rid = len(lum.batch_render_coll)
                item.name = i.name
                item.path = path_to_file
                item.frame_start = start
                item.frame_end = end
                item.scene = sc
                item.frames = "{}-{}".format(item.frame_start, item.frame_end)
                if i.name:
                    added.append(i.name)
            except:
                  self.report({'INFO'}, "Can't read {}".format(i.name))
        if added:
            self.report({'INFO'}, "Added {} to the list".format(", ".join(added)))
        
        lum.batch_render_idx = len(lum.batch_render_coll)-1
        self.display_popup(context)
        return {'FINISHED'}
    
    def cancel(self, context):
        self.display_popup(context)

    def invoke(self, context, event):
        self.cursor_pos = [event.mouse_x, event.mouse_y]
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class LoomBatchDialogListActions(bpy.types.Operator):
    """Loom Batch Dialog Action"""
    bl_idname = "loom.batch_dialog_action"
    bl_label = "Loom Batch Dialog Action"
    bl_description = "Loom Batch Dialog Action"
    bl_options = {'INTERNAL'}
    
    action = bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))

    def invoke(self, context, event):
        scn = context.scene
        lum = scn.loom
        idx = lum.batch_render_idx
        try:
            item = lum.batch_render_coll[idx]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and idx < len(lum.batch_render_coll) - 1:
                item_next = lum.batch_render_coll[idx+1].name
                lum.batch_render_coll.move(idx, idx + 1)
                lum.batch_render_idx += 1

            elif self.action == 'UP' and idx >= 1:
                item_prev = lum.batch_render_coll[idx-1].name
                lum.batch_render_coll.move(idx, idx-1)
                lum.batch_render_idx -= 1

            elif self.action == 'REMOVE':
                info = '"{}" removed from list'.format(lum.batch_render_coll[lum.batch_render_idx].name)
                lum.batch_render_idx -= 1
                if lum.batch_render_idx < 0: lum.batch_render_idx = 0
                self.report({'INFO'}, info)
                lum.batch_render_coll.remove(idx)

        if self.action == 'ADD':
            bpy.ops.loom.batch_select_blends('INVOKE_DEFAULT')       
            lum.batch_render_idx = (len(lum.batch_render_coll))

        return {"FINISHED"}


class LoomBatchClearList(bpy.types.Operator):
    bl_idname = "loom.batch_clear_list"
    bl_label = "Delete all items of the list?"
    bl_description = "Clear all items"
    bl_options = {'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        return bool(bpy.context.scene.loom.batch_render_coll)
    
    def execute(self, context):
        context.scene.loom.batch_render_coll.clear()
        self.report({'INFO'}, "All items removed")
        return {"FINISHED"}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    

class LoomBatchDialogReset(bpy.types.Operator):
    bl_idname = "loom.batch_dialog_reset_display"
    bl_label = "Reset Display Settings"
    bl_description = "Reset Batch Dialog Display Settings"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        prefs = context.user_preferences.addons[__name__].preferences
        prefs.property_unset("batch_dialog_rows")
        prefs.property_unset("batch_paths_flag")
        prefs.property_unset("batch_path_col_width")
        prefs.property_unset("batch_name_col_width")       
        return {'FINISHED'}


class LoomBatchRemoveDoubles(bpy.types.Operator):
    bl_idname = "loom.batch_remove_doubles"
    bl_label = "Remove All Duplicates?"
    bl_description = "Remove Duplicates in List based on the filename"
    bl_options = {'INTERNAL'}
    
    doubles = []

    def find_duplicates(self, context):
        path_lookup = {}
        for c, i in enumerate(context.scene.loom.batch_render_coll):
            path_lookup.setdefault(i.path, []).append(i.name)

        for path, names in path_lookup.items():
            for i in names[1:]:
                self.doubles.append(i)
        return len(self.doubles)

    @classmethod
    def poll(cls, context):
        return bool(context.scene.loom.batch_render_coll)
    
    def execute(self, context):
        lum = context.scene.loom
        removed_items = []
        for i in self.doubles:
            item_id = lum.batch_render_coll.find(i)
            lum.batch_render_coll.remove(item_id)
            removed_items.append(i)

        lum.batch_render_idx = (len(lum.batch_render_coll)-1)
        self.report({'INFO'}, "{} {} removed: {}".format(
                    len(removed_items),
                    "items" if len(removed_items) > 1 else "item",
                    ', '.join(set(removed_items))))
        return {'FINISHED'}

    def invoke(self, context, event):
        self.doubles.clear()
        if self.find_duplicates(context):
            return context.window_manager.invoke_confirm(self, event)
        else:
            self.report({'INFO'}, "No doubles in list, nothing to do.")
            return {'FINISHED'}


class LoomBatchActiveItem(bpy.types.Operator):
    bl_idname = "loom.batch_active_item"
    bl_label = "Print Active Item to Console"
    bl_description = "Print active Item"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        lum = context.scene.loom
        try:
            print (lum.batch_render_coll[lum.batch_render_idx].name)
        except IndexError:
            print ("No active item")
        return{'FINISHED'}
    

class LoomBatchDefaultRange(bpy.types.Operator):
    bl_idname = "loom.batch_default_frames"
    bl_label = "Revert to default frame range"
    bl_description = "Revert to default frame range"
    bl_options = {'INTERNAL'}
    
    item_id = bpy.props.IntProperty()
    
    def execute(self, context):
        try:
            item = context.scene.loom.batch_render_coll[self.item_id]
            default_range = "{}-{}".format(item.frame_start, item.frame_end)
            item.frames = default_range
        except IndexError:
            self.report({'INFO'}, "No active item")
        return{'FINISHED'}


class LoomBatchVerifyInput(bpy.types.Operator):
    bl_idname = "loom.batch_verify_input"
    bl_label = "Verify Input Frame Range"
    bl_description = "Verify Input Frame Range"
    bl_options = {'INTERNAL'}
    
    item_id = bpy.props.IntProperty()
    
    def execute(self, context):
        try:
            item = context.scene.loom.batch_render_coll[self.item_id]
        except IndexError:
            self.report({'INFO'}, "No active item") # redundant?
            return{'CANCELLED'}
        
        folder = os.path.realpath(bpy.path.abspath(item.path))
        frame_input = filter_frames(
            frame_input = item.frames, 
            filter_individual = item.input_filter)
        
        if frame_input:
            self.report({'INFO'}, ("{} {} [{}] will be rendered to {}".format(
                len(frame_input),
                "Frame" if len(frame_input) == 1 else "Frames",
                ', '.join('{}'.format(i) for i in frame_input), 
                folder)))
        else:
            self.report({'INFO'}, "No frames specified")
        return {'FINISHED'}


class LoomEncodeSequence(bpy.types.Operator):
    """Encode Image Sequence to ProRes or DNxHD"""
    bl_idname = "loom.encode_sequence"
    bl_label = "Encode Image Sequence"
    bl_description = "Encode Image Sequence"
    bl_options = {'REGISTER'}

    sequence = bpy.props.StringProperty(
        name="Path to sequence",
        description="Path to sequence",
        maxlen=1024,
        subtype='FILE_PATH')
    
    movie = bpy.props.StringProperty(
        name="Path to movie",
        description="Path to movie",
        maxlen=1024,
        subtype='FILE_PATH')

    fps = bpy.props.IntProperty(
        name="Frame Rate",
        description="Frame Rate",
        default=25, min=1)

    missing_frames = bpy.props.BoolProperty(
        name="Missing Frames",
        description="Missing Frames")

    codec = bpy.props.EnumProperty(
        name="Codec",
        description="Codec",
        items=codec_callback)

    colorspace = bpy.props.EnumProperty(
        name="Colorspace",
        description="colorspace",
        items=colorspace_callback)
    
    terminal_instance = bpy.props.BoolProperty(
        name="New Terminal Instance",
        description="Opens Blender in a new Terminal Window",
        default=True)

    pause = bpy.props.BoolProperty(
        name="Confirm when done",
        description="Confirm when done",
        default=True)

    # https://avpres.net/FFmpeg/sq_ProRes.html, 
    # https://trac.ffmpeg.org/wiki/Encode/VFX
    encode_presets = {
        "PRORES422PR" : ["-c:v", "prores", "-profile:v", 0],
        "PRORES422LT" : ["-c:v", "prores", "-profile:v", 1],
        "PRORES422" : ["-c:v", "prores", "-profile:v", 2],
        "PRORES422HQ" : ["-c:v", "prores", "-profile:v", 3],
        "PRORES4444" : ["-c:v", "prores_ks", "-profile:v", 4, "-quant_mat", "hq", "-pix_fmt", "yuva444p10le"],
        "PRORES4444XQ" : ["-c:v", "prores_ks", "-profile:v", 5, "-quant_mat", "hq", "-pix_fmt", "yuva444p10le"],
        "DNXHD422-08-036" : ["-c:v", "dnxhd", "-vf", "scale=1920x1080,fps=25/1,format=yuv422p", "-b:v", "36M"],
        "DNXHD422-08-145" : ["-c:v", "dnxhd", "-vf", "scale=1920x1080,fps=25/1,format=yuv422p", "-b:v", "145M"],
        "DNXHD422-08-145" : ["-c:v", "dnxhd", "-vf", "scale=1920x1080,fps=25/1,format=yuv422p", "-b:v", "220M"],
        "DNXHD422-10-185" : ["-c:v", "dnxhd", "-vf", "scale=1920x1080,fps=25/1,format=yuv422p10", "-b:v", "185M"],
        #"DNXHD422-10-440" : ["-c:v", "dnxhd", "-vf", "scale=1920x1080,fps=25/1,format=yuv422p10", "-b:v", "440M"],
        #"DNXHD444-10-350" : ["-c:v", "dnxhd", "-profile:v", "dnxhr_444", "-vf", "format=yuv444p10" "-b:v", "350M"],
        "DNXHR-444" : ["-c:v", "dnxhd", "-profile:v", "dnxhr_444", "-vf", "format=yuv444p10"],
        "DNXHR-HQX" : ["-c:v", "dnxhd", "-profile:v", "dnxhr_hqx", "-vf", "format=yuv422p10"],
        "DNXHR-HQ" : ["-c:v", "dnxhd", "-profile:v", "dnxhr_hq", "-vf", "format=yuv422p"],
        "DNXHR-SQ" : ["-c:v", "dnxhd", "-profile:v", "dnxhr_sq", "-vf", "format=yuv422p"],
        }
    
    def missing_frames(self, frames):
        return sorted(set(range(frames[0], frames[-1] + 1)).difference(frames))

    def rangify_frames(self, frames):
        """ Convert list of integers to Range string [1,2,3] -> '1-3' """
        G=(list(x) for _,x in groupby(frames, lambda x,c=count(): next(c)-x))
        return ",".join("-".join(map(str,(g[0],g[-1])[:len(g)])) for g in G)

    def verify_app(self, cmd):
        try:
            subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                return False
        return True

    def determine_type(self, val): 
        #val = ast.literal_eval(s)
        if (isinstance(val, int)):
            return ("chi")
        elif (isinstance(val, float)):
            return ("chf")
        if val in ["true", "false"]:
            return ("chb")
        else:
            return ("chs")

    def number_suffix(self, filename):
        regex = re.compile(r'\d+\b')
        digits = ([x for x in regex.findall(filename)])
        return next(reversed(digits), None)

    def pack_arguments(self, lst):
        return [{"idc": 0, "name": self.determine_type(i), "value": str(i)} for i in lst]

    def check(self, context):
        return True        

    def execute(self, context):
        prefs = context.user_preferences.addons[__name__].preferences
        prefs.default_codec = self.codec
        lum = context.scene.loom
        image_sequence = {}
        
        """ Verify ffmpeg """
        ffmpeg_error = False
        if not prefs.ffmpeg_path:
            if self.verify_app(["ffmpeg", "-h"]):
                prefs.ffmpeg_path = "ffmpeg"
            else:
                ffmpeg_error = True
        
        elif prefs.ffmpeg_path and prefs.ffmpeg_path != "ffmpeg":
            if not os.path.isabs(prefs.ffmpeg_path) or prefs.ffmpeg_path.startswith('//'):
                ffmpeg_bin = os.path.realpath(bpy.path.abspath(prefs.ffmpeg_path))
                if os.path.isfile(ffmpeg_bin): 
                    prefs.ffmpeg_path = ffmpeg_bin            
            if not self.verify_app([prefs.ffmpeg_path, "-h"]):
                ffmpeg_error = True
        
        if ffmpeg_error:
            error_message = "Path to ffmpeg binary not set in addon preferences"
            if not self.options.is_invoke:
                print (error_message)
                return {"CANCELLED"}
            else:
                self.report({'ERROR'},error_message)
                bpy.ops.loom.encode_sequence('INVOKE_DEFAULT')
                return {"CANCELLED"}

        #if not self.properties.is_property_set("sequence"): # call via commandline?
        seq_path = lum.sequence_encode if not self.sequence else self.sequence
        mov_path = lum.movie_path if not self.movie else self.movie

        path_error = False
        if not seq_path:
            self.report({'ERROR'}, "No image sequence specified")
            path_error = True

        if path_error:
            bpy.ops.loom.encode_sequence('INVOKE_DEFAULT')
            return {"CANCELLED"}

        """ Verify image sequence """
        basedir, filename = os.path.split(seq_path)
        basedir = os.path.realpath(bpy.path.abspath(basedir))
        filename_noext, extension = os.path.splitext(filename)

        seq_error = False
        if '#' not in filename_noext:
            num_suff = self.number_suffix(filename_noext)
            if not num_suff:
                self.report({'ERROR'}, "No valid image sequence")
                seq_error = True
            else:
                filename_noext = filename_noext.replace(num_suff, "#"*len(num_suff))
        
        if not extension: # Sequence file format
            self.report({'ERROR'}, "File format not set (missing extension)")
            seq_error = True

        if seq_error:
            bpy.ops.loom.encode_sequence('INVOKE_DEFAULT')
            return {"CANCELLED"}

        hashes = filename_noext.count('#')
        name_real = filename_noext.replace("#", "")
        file_pattern = r"{fn}(\d{{{ds}}})\.?{ex}$".format(fn=name_real, ds=hashes, ex=extension)

        for f in os.scandir(basedir):
            if f.name.endswith(extension) and f.is_file():
                match = re.match(file_pattern, f.name, re.IGNORECASE)
                if match: image_sequence[int(match.group(1))] = os.path.join(basedir, f.name)

        if not len(image_sequence) > 1:
            self.report({'WARNING'},"No valid image sequence")
            bpy.ops.loom.encode_sequence('INVOKE_DEFAULT')
            return {"CANCELLED"}

        if not mov_path:
            mov_path = next(iter(image_sequence.values()))

        """ Verify movie file name and extension """
        mov_basedir, mov_filename = os.path.split(mov_path)
        mov_filename_noext, mov_extension = os.path.splitext(mov_filename)
        mov_extension = ".mov"

        mov_num_suff = self.number_suffix(mov_filename_noext)
        if mov_num_suff:
            mov_filename_noext = mov_filename_noext.replace(mov_num_suff, "")

        if mov_filename_noext.endswith(("-", "_", ".")):
            mov_filename_noext = mov_filename_noext[:-1]

        mov_path = os.path.join(mov_basedir, "{}{}".format(mov_filename_noext, mov_extension))
        if os.path.isfile(mov_path):
            from time import strftime
            time_stamp = strftime("_%Y%m%d-%H%M%S")
            mov_filename_noext = "{}{}".format(mov_filename_noext, time_stamp)
        
        mov_path = os.path.join(mov_basedir, "{}{}".format(mov_filename_noext, mov_extension))

        """ Detect missing frames """
        frame_numbers = sorted(list(image_sequence.keys())) #start_frame, end_frame = fn[0], fn[-1]
        missing_frames = self.missing_frames(frame_numbers)

        if missing_frames:
            lum.lost_frames = self.rangify_frames(missing_frames)
            error = "Missing frames detected: {}".format(lum.lost_frames)
            if not self.options.is_invoke:
                print ("ERROR: ", error)
                return {"CANCELLED"}
            else:
                self.report({'ERROR_INVALID_INPUT'}, error)
                self.report({'ERROR'},"Frame list copied to clipboard.")
                context.window_manager.clipboard = "{}".format(
                    ','.join(map(str, missing_frames)))
                bpy.ops.loom.encode_sequence('INVOKE_DEFAULT') # re-invoke the dialog
                return {"CANCELLED"}
        else:
            lum.lost_frames = ""
            
        """ Format image sequence for ffmpeg """
        fn_ffmpeg = filename_noext.replace("#"*hashes, "%0{}d{}".format(hashes, extension))
        fp_ffmpeg = os.path.join(basedir, fn_ffmpeg) # "{}%0{}d{}".format(filename_noext, 4, ext)
        cli_args = ["-start_number", frame_numbers[0], "-apply_trc", self.colorspace, "-i", fp_ffmpeg] 
        cli_args += self.encode_presets[self.codec]
        cli_args += [mov_path] if self.fps == 25 else ["-r", self.fps, mov_path]

        """ Run ffmpeg """
        bpy.ops.loom.run_terminal(
            #debug_arguments=True,
            binary=prefs.ffmpeg_path,
            terminal_instance=self.terminal_instance,
            argument_collection=self.pack_arguments(cli_args),
            bash_name="loom-ffmpeg-temp",
            force_bash=prefs.bash_flag,
            pause=self.pause)

        self.report({'INFO'}, "Encoding {}{} to {}".format(filename_noext, extension, mov_path))
        return {"FINISHED"}

    def invoke(self, context, event):
        lum = context.scene.loom
        prefs = context.user_preferences.addons[__name__].preferences

        if not self.properties.is_property_set("codec"):
            if prefs.default_codec:
                try:
                    self.codec = prefs.default_codec
                except:
                    pass

        return context.window_manager.invoke_props_dialog(self, 
            width=(prefs.encode_dialog_width*context.user_preferences.system.pixel_size))

    def draw(self, context):
        lum = context.scene.loom
        prefs = context.user_preferences.addons[__name__].preferences
        layout = self.layout

        split_width = .2
        split = layout.split(split_width)
        col = split.column(align=True)
        col.label("Sequence:")
        col = split.column(align=True)
        sub = col.row(align=True)          
        sub.prop(lum, "sequence_encode", text="")
        if lum.sequence_encode:
            sub.operator(LoomEncodeVerifyImageSequence.bl_idname, icon='GHOST_ENABLED', text="")
            sub.operator(LoomOpenFolder.bl_idname, 
                icon="DISK_DRIVE", text="").folder_path = os.path.dirname(lum.sequence_encode)
        else:
            sub.operator(LoomEncodeAutoPaths.bl_idname, text="", icon='AUTO') #GHOST #GHOST_ENABLED, SEQUENCE
        sel_sequence = sub.operator(LoomEncodeLoadImageSequence.bl_idname, text="", icon='FILESEL')
        sel_sequence.verify_sequence = False

        split = layout.split(split_width)
        col = split.column(align=True)
        col.label("Colorspace:")
        col = split.column(align=True)
        col.prop(self, "colorspace", text="")

        split = layout.split(split_width)
        col = split.column(align=True)
        col.label("Frame Rate:")
        col = split.column(align=True)
        col.prop(self, "fps", text="")

        split = layout.split(split_width)
        col = split.column(align=True)
        col.label("Codec:")
        col = split.column(align=True)
        col.prop(self, "codec", text="")

        split = layout.split(split_width)
        col = split.column(align=True)
        col.label("Movie File:")
        col = split.column(align=True)
        sub = col.row(align=True)
        sub.prop(lum, "movie_path", text="")
        if lum.movie_path:
            sub.operator(LoomOpenFolder.bl_idname, 
                icon="DISK_DRIVE", text="").folder_path = os.path.dirname(lum.movie_path)
        sub.operator(LoomEncodeSelectMovie.bl_idname, text="", icon='FILESEL')
        
        if lum.lost_frames:
            row = layout.row()
            row = layout.row(align=True)
            fg = row.operator(LoomFillSequenceGaps.bl_idname, icon='GHOST', text="Fill Gaps with Copies")
            fg.sequence_path = lum.sequence_encode
            txt = "Render Missing Frames"
            di = row.operator(LoomRenderInputDialog.bl_idname, icon='RENDER_STILL', text=txt)
            di.frame_input = lum.lost_frames

        row = layout.row()


class LoomEncodeLoadImageSequence(bpy.types.Operator, ImportHelper):
    """Select File of Image Sequence"""
    bl_idname = "loom.load_sequence"
    bl_label = "Select File of Image Sequence"
    bl_options = {'INTERNAL'}
    
    cursor_pos = [0,0]
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    
    filter_glob = bpy.props.StringProperty(
        default="*.png;*.jpg;*.jpeg;*.jpg;*.exr;*dpx;*tga;*tif;*tiff;",
        #default="*" + ";*".join(bpy.path.extensions_image),
        options={'HIDDEN'})

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    verify_sequence = bpy.props.BoolProperty(
            name="Verify Image Sequence",
            description="Detects missing frames",
            default=True)

    def number_suffix(self, filename):
        regex = re.compile(r'\d+\b')
        digits = ([x for x in regex.findall(filename)])
        return next(reversed(digits), None)
    
    def bound_frame(self, frame_path, frame_iter):
        folder, filename = os.path.split(frame_path)
        digits = self.number_suffix(filename)
        frame = re.sub('\d(?!\d)', lambda x: str(int(x.group(0)) + frame_iter), digits)
        return os.path.exists(os.path.join(folder, frame.join(filename.rsplit(digits))))

    def is_sequence(self, filepath):
        folder, filename = os.path.split(filepath) # any(char.isdigit() for char in filename)
        filename_noext, ext = os.path.splitext(filename)
        if not filename_noext[-1].isdigit(): return False
        next_frame = self.bound_frame(filepath, 1)
        prev_frame = self.bound_frame(filepath, -1)
        return True if next_frame or prev_frame else False

    def missing_frames(self, frames):
        return sorted(set(range(frames[0], frames[-1] + 1)).difference(frames))
    
    def rangify_frames(self, frames):
        """ Convert list of integers to Range string [1,2,3] -> '1-3' """
        G=(list(x) for _,x in groupby(frames, lambda x,c=count(): next(c)-x))
        #G=([list(x) for _,x in groupby(L, lambda x,c=count(): next(c)-x)])
        return ",".join("-".join(map(str,(g[0],g[-1])[:len(g)])) for g in G)

    def display_popup(self, context):
        win = context.window #win.cursor_warp((win.width*.5)-100, (win.height*.5)+100)
        win.cursor_warp(self.cursor_pos[0]-100, self.cursor_pos[1]+70)
        bpy.ops.loom.encode_sequence('INVOKE_DEFAULT') # re-invoke the dialog
        
    @classmethod
    def poll(cls, context):
        return True #context.object is not None

    def execute(self, context):
        lum = context.scene.loom
        image_sequence = {}

        basedir, filename = os.path.split(self.filepath)
        basedir = os.path.realpath(bpy.path.abspath(basedir))
        filename_noext, ext = os.path.splitext(filename)
        frame_suff = self.number_suffix(filename)

        if not frame_suff:
            self.report({'WARNING'},"No valid image sequence")
            self.display_popup(context)
            return {"CANCELLED"}

        sequence_name = filename.replace(frame_suff,'#'*len(frame_suff))
        sequence_path = os.path.join(basedir, sequence_name)
        name_real = filename_noext.replace(frame_suff, "")

        """ Verify image sequence on disk (Scan directory) """
        if self.verify_sequence:
            hashes = sequence_name.count('#')
            file_pattern = r"{fn}(\d{{{ds}}})\.?{ex}$".format(fn=name_real, ds=hashes, ex=ext)
            for f in os.scandir(basedir):
                if f.name.endswith(ext) and f.is_file():
                    match = re.match(file_pattern, f.name, re.IGNORECASE)
                    if match: image_sequence[int(match.group(1))] = os.path.join(basedir, f.name)

            if not len(image_sequence) > 1:
                self.report({'WARNING'},"No valid image sequence")
                return {"CANCELLED"}

            """ Detect missing frames """  #start_frame, end_frame = fn[0], fn[-1]
            frame_numbers = sorted(list(image_sequence.keys()))
            missing_frames = self.missing_frames(frame_numbers)

            if missing_frames:
                lum.lost_frames = self.rangify_frames(missing_frames)
                context.window_manager.clipboard = "{}".format(
                    ','.join(map(str, missing_frames)))
                error_massage = "Missing frames detected: {}".format(self.rangify_frames(missing_frames))
                self.report({'ERROR_INVALID_INPUT'}, error_massage)
                self.report({'ERROR'},"Frame list copied to clipboard.")
            else:
                lum.lost_frames = ""
                self.report({'INFO'},"Valid image sequence, Frame range: {}".format(
                    self.rangify_frames(frame_numbers)))

        else:
            """ Quick test whether single image or not """
            if not self.is_sequence(self.filepath):
                self.report({'WARNING'},"No valid image sequence") #return {"CANCELLED"}
            else:
                lum.lost_frames = ""

        if not name_real: name_real = "untitled"
        name_real = name_real[:-1] if name_real.endswith(("-", "_")) else name_real
        lum.movie_path = os.path.join(basedir, name_real + ".mov")
        lum.sequence_encode = sequence_path

        self.display_popup(context)
        return {'FINISHED'}
    
    def cancel(self, context):
        self.display_popup(context)

    def invoke(self, context, event):
        self.cursor_pos = [event.mouse_x, event.mouse_y]
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class LoomEncodeSelectMovie(bpy.types.Operator, ImportHelper):
    """Movie file path"""
    bl_idname = "loom.save_movie"
    bl_label = "Save Movie File"
    bl_options = {'INTERNAL'}
    
    cursor_pos = [0,0]
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")    
    filename = bpy.props.StringProperty()    
    
    filename_ext = ".mov"
    filter_glob = bpy.props.StringProperty(
            default="*.mov;",
            options={'HIDDEN'})
    
    def name_from_sequence(self, context):
        lum = context.scene.loom
        basedir, filename = os.path.split(lum.sequence_encode)
        filename_noext, ext = os.path.splitext(filename)
        name_real = filename_noext.replace('#', "")
        if name_real.endswith(("-", "_")):
            name_real = name_real[:-1]
        return "{}.mov".format(name_real)

    def display_popup(self, context):
        win = context.window #win.cursor_warp((win.width*.5)-100, (win.height*.5)+100)
        win.cursor_warp(self.cursor_pos[0]-100, self.cursor_pos[1]+70)
        bpy.ops.loom.encode_sequence('INVOKE_DEFAULT') # re-invoke the dialog
        
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        lum = context.scene.loom
        folder, file = os.path.split(self.filepath)
        filename, ext = os.path.splitext(file)
        if os.path.isdir(self.filepath):
            filename = "untitled"
        if ext != ".mov":
            lum.movie_path = os.path.join(folder, "{}{}.mov".format(filename,ext))
        else:
            lum.movie_path = self.filepath #self.report({'WARNING'},"No valid file type")
        self.display_popup(context)
        return {'FINISHED'}
    
    def cancel(self, context):
        self.display_popup(context)

    def invoke(self, context, event):
        self.filename = self.name_from_sequence(context)
        self.cursor_pos = [event.mouse_x, event.mouse_y]
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class LoomEncodeVerifyImageSequence(bpy.types.Operator):
    """Verify & Refresh Image Sequence"""
    bl_idname = "loom.image_sequence_verify"
    bl_label = "Verify Image Sequence"
    bl_options = {'INTERNAL'}

    def rangify_frames(self, frames):
        """ Convert list of integers to Range string [1,2,3] -> '1-3' """
        G=(list(x) for _,x in groupby(frames, lambda x,c=count(): next(c)-x))
        return ",".join("-".join(map(str,(g[0],g[-1])[:len(g)])) for g in G)

    def missing_frames(self, frames):
        return sorted(set(range(frames[0], frames[-1] + 1)).difference(frames))

    def number_suffix(self, filename):
        regex = re.compile(r'\d+\b')
        digits = ([x for x in regex.findall(filename)])
        return next(reversed(digits), None)

    def execute(self, context):
        lum = context.scene.loom
        image_sequence = {}

        if not lum.sequence_encode:
            self.report({'WARNING'},"No image sequence specified")
            return {"CANCELLED"}

        basedir, filename = os.path.split(lum.sequence_encode)
        basedir = os.path.realpath(bpy.path.abspath(basedir))
        filename_noext, ext = os.path.splitext(filename)
        
        seq_error = False
        if '#' not in filename_noext:
            num_suff = self.number_suffix(filename_noext)
            if num_suff:
                filename_noext = filename_noext.replace(num_suff, "#"*len(num_suff))
                sequence_name = "{}{}".format(filename_noext, ext)
                lum.sequence_encode = "{}".format(os.path.join(basedir, sequence_name))
            else:
                seq_error = True

        if seq_error:
            self.report({'ERROR'},"No valid image sequence")
            return {"CANCELLED"}
        if not ext:
            self.report({'ERROR'}, "File format not set (missing extension)")
            return {"CANCELLED"}

        hashes = filename_noext.count('#')
        name_real = filename_noext.replace("#", "")
        file_pattern = r"{fn}(\d{{{ds}}})\.?{ex}$".format(fn=name_real, ds=hashes, ex=ext)

        for f in os.scandir(basedir):
            if f.name.endswith(ext) and f.is_file():
                match = re.match(file_pattern, f.name, re.IGNORECASE)
                if match: image_sequence[int(match.group(1))] = os.path.join(basedir, f.name)

        if not len(image_sequence) > 1:
            self.report({'ERROR'},"Specified image sequence not found on disk")
            return {"CANCELLED"}

        """ Detect missing frames """
        frame_numbers = sorted(list(image_sequence.keys()))
        missing_frames = self.missing_frames(frame_numbers)

        if missing_frames:
            lum.lost_frames = self.rangify_frames(missing_frames)
            context.window_manager.clipboard = "{}".format(
                ','.join(map(str, missing_frames)))
            error_massage = "Missing frames detected: {}".format(self.rangify_frames(missing_frames))
            self.report({'ERROR'}, error_massage)
            self.report({'ERROR'},"Frame list copied to clipboard.")
        else:
            self.report({'INFO'},'Sequence: "{}{}" found on disk, Frame range: {}'.format(
                filename_noext, ext, self.rangify_frames(frame_numbers)))
            lum.lost_frames = ""
        return {'FINISHED'}


class LoomEncodeAutoPaths(bpy.types.Operator):
    """Auto Paths (based on default output)"""
    bl_idname = "loom.encode_auto_paths"
    bl_label = "Set sequence and movie path based on default output"
    bl_options = {'INTERNAL'}

    def number_suffix(self, filename):
        regex = re.compile(r'\d+\b')
        digits = ([x for x in regex.findall(filename)])
        return next(reversed(digits), None)

    @classmethod
    def poll(cls, context):
        return not context.scene.loom.sequence_encode

    def execute(self, context):
        lum = context.scene.loom
        '''
        if len(lum.render_collection) > 0:
        lum_rd = lum.render_collection[-1]
        lum.sequence_encode = "{}{}.{}".format(lum_rd.file_path, lum_rd.padded_zeros*"#", lum_rd.image_format)
        movie_file = lum_rd.file_path[:-1] if lum_rd.file_path.endswith(("-", "_", ".")) else lum_rd.file_path
        lum.movie_path = "{}.mov".format(movie_file)
        '''
        basedir, filename = os.path.split(context.scene.render.frame_path(frame=0))
        basedir = os.path.realpath(bpy.path.abspath(basedir))
        filename_noext, ext = os.path.splitext(filename)
        num_suff = self.number_suffix(filename_noext)
        
        if not lum.movie_path:
            movie_noext = filename_noext.replace(num_suff, "")
            movie_noext = movie_noext[:-1] if movie_noext.endswith(("-", "_", ".")) else movie_noext
            lum.movie_path = "{}.mov".format(os.path.join(basedir, movie_noext))

        filename_noext = filename_noext.replace(num_suff, "#"*len(num_suff))
        sequence_name = "{}{}".format(filename_noext, ext)
        lum.sequence_encode = "{}".format(os.path.join(basedir, sequence_name))
        self.report({'INFO'}, "Sequence path set (based on default output path)")   
        
        return {'FINISHED'}


class LoomFillSequenceGaps(bpy.types.Operator):
    """Fill gaps in sequence with copies"""
    bl_idname = "loom.fill_image_sequence"
    bl_label = "Fill gaps in image sequence with copies of previous frames?"
    bl_description = "Fill gaps in image sequence with copies of existing frames"
    bl_options = {'INTERNAL'}
    
    sequence_path = bpy.props.StringProperty()

    def missing_frames(self, frames):
        return sorted(set(range(frames[0], frames[-1] + 1)).difference(frames))

    def execute(self, context):
        lum = context.scene.loom
        image_sequence = {}

        basedir, filename = os.path.split(self.sequence_path)
        basedir = os.path.realpath(bpy.path.abspath(basedir))
        filename_noext, ext = os.path.splitext(filename)

        if "#" not in filename_noext:
            self.report({'WARNING'},"No valid image sequence")
            return {"CANCELLED"}

        """ Scan directory """
        hashes = filename_noext.count('#')
        name_real = filename_noext.replace("#", "")
        file_pattern = r"{fn}(\d{{{ds}}})\.?{ex}$".format(fn=name_real, ds=hashes, ex=ext)
        for f in os.scandir(basedir):
            if f.name.endswith(ext) and f.is_file():
                match = re.match(file_pattern, f.name, re.IGNORECASE)
                if match: image_sequence[int(match.group(1))] = os.path.join(basedir, f.name)

        if not len(image_sequence) > 1:
            self.report({'WARNING'},"No valid image sequence")
            return {"CANCELLED"}

        """ Detect missing frames """
        frame_numbers = sorted(list(image_sequence.keys())) #start_frame, end_frame = fn[0], fn[-1]
        missing_frames = self.missing_frames(frame_numbers)

        """ Copy images """
        if missing_frames:
            frames_to_copy = {}
            f_prev = frame_numbers[0]
            for f in range(frame_numbers[0], frame_numbers[-1]+1):
                if f not in image_sequence:
                    path_copy = os.path.join(basedir, 
                        "{name}{frame:0{digits}d}{extension}".format(
                            name=name_real, frame=f, digits=hashes, extension=ext))
                    frames_to_copy.setdefault(image_sequence[f_prev], []).append(path_copy)
                else:
                    f_prev = f
            try:
                from shutil import copyfile
                for src, dest in frames_to_copy.items():
                        for ff in dest:
                            copyfile(src, ff)
                self.report({'INFO'},"Successfully copied all missing frames")
                #if self.options.is_invoke:
                lum.lost_frames = ""
            except OSError:
                self.report({'ERROR'}, "Error while trying to copy frames")
        else:
            self.report({'INFO'},"Nothing to do")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class LoomOpenFolder(bpy.types.Operator):
    """Opens a certain Folder in the File Browser"""
    bl_idname = "loom.open_folder"
    bl_label = "Open Folder"
    bl_description = "Open folder in file browser"
    bl_options = {'INTERNAL'}
    
    folder_path = bpy.props.StringProperty()
    
    def execute(self, context):
        try:
            if platform.startswith('darwin'):
                webbrowser.open("file://{}".format(self.folder_path))
            else:
                webbrowser.open(self.folder_path)
        except OSError:
            self.report({'INFO'}, "No Folder")
        return {'FINISHED'}

        
class LoomHelp(bpy.types.Operator):
    """Open up readme.md on github"""
    bl_idname = "loom.open_docs"
    bl_label = "Documentation"
    bl_description= "Loom Documentation"
    bl_options = {'INTERNAL'}
    
    def execute(self, context): #self.report({'INFO'}, "")
        webbrowser.open_new("https://github.com/p2or/blender-loom")
        return {'FINISHED'}


# -------------------------------------------------------------------
#    Rendering Operators
# -------------------------------------------------------------------

class LoomRenderTerminal(bpy.types.Operator):
    """Render image sequence in terminal instance"""
    bl_idname = "loom.render_terminal"
    bl_label = "Render Image Sequence in Terminal Instance"
    bl_options = {'REGISTER', 'INTERNAL'}

    frames = bpy.props.StringProperty(
        name="Frames",
        description="Specify a range or frames to render")

    threads = bpy.props.IntProperty(
        name="CPU Threads",
        description="Number of CPU threads to use simultaneously while rendering",
        min = 1)

    digits = bpy.props.IntProperty(
        name="Digits",
        description="Specify digits in filename",
        default=4)

    isolate_numbers = bpy.props.BoolProperty(
        name="Filter Raw Items",
        description="Filter raw elements in frame input",
        default=False)

    debug = bpy.props.BoolProperty(
        name="Debug Arguments",
        description="Print full argument list",
        default=False)

    def determine_type(self, val):
        if (isinstance(val, int)):
            return ("chi")
        elif (isinstance(val, float)):
            return ("chf")
        if val in ["true", "false"]:
            return ("chb")
        else:
            return ("chs")

    def pack_arguments(self, lst):
        return [{"idc": 0, "name": self.determine_type(i), "value": str(i)} for i in lst]

    @classmethod
    def poll(cls, context):
        return not context.scene.render.is_movie_format

    def execute(self, context):
        prefs = context.user_preferences.addons[__name__].preferences

        if bpy.data.is_dirty:  # Save latest changes
            bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

        python_expr = ("import bpy;" +\
                "bpy.ops.render.image_sequence(" +\
                "frames='{fns}', isolate_numbers={iel}," +\
                "render_silent={cli}, digits={lzs})").format(
                    fns=self.frames,
                    iel=self.isolate_numbers, 
                    cli=True, 
                    lzs=self.digits)

        cli_args = ["-b", bpy.data.filepath, "--python-expr", python_expr]
        
        if self.properties.is_property_set("threads"):
            cli_args = cli_args + ["-t", "{}".format(self.threads)]

        bpy.ops.loom.run_terminal( 
            debug_arguments=self.debug,
            terminal_instance=True,
            argument_collection=self.pack_arguments(cli_args), 
            bash_name="loom-render-temp",
            force_bash = prefs.bash_flag)

        return {"FINISHED"}


class LoomRenderImageSequence(bpy.types.Operator):
    """Render image sequence either in background or within the UI"""
    bl_idname = "render.image_sequence"
    bl_label = "Render Image Sequence"
    bl_options = {'REGISTER', 'INTERNAL'}

    frames = bpy.props.StringProperty(
        name="Frames",
        description="Specify a range or single frames to render")

    isolate_numbers = bpy.props.BoolProperty(
        name="Filter Raw Items",
        description="Filter raw elements in frame input",
        default=False)

    render_silent = bpy.props.BoolProperty(
        name="Render silent",
        description="Render without displaying the progress within the UI",
        default=False)

    digits = bpy.props.IntProperty(
        name="Digits",
        description="Specify digits in filename",
        default=4)

    _image_formats = {'BMP': 'bmp', 'IRIS': 'iris', 'PNG': 'png', 'JPEG': 'jpg', 
        'JPEG2000': 'jp2', 'TARGA': 'tga', 'TARGA_RAW': 'tga', 'CINEON': 'cin', 
        'DPX': 'dpx', 'OPEN_EXR_MULTILAYER': 'exr', 'OPEN_EXR': 'exr', 'HDR': 'hdr', 
        'TIFF': 'tif', 'SUPPLEMENT1': 'tiff', 'SUPPLEMENT2': 'jpeg'}

    _rendered_frames, _skipped_frames = [], []
    _timer = _frames = _stop = _rendering = _dec = _log = None
    _output_path = _folder = _filename = _extension = None
    _subframe_flag = False
    
    @classmethod
    def poll(cls, context):
        return not context.scene.render.is_movie_format

    def pre_render(self, scene):
        self._rendering = True

    def cancel_render(self, scene):
        self._stop = True
        scene.render.filepath = self._output_path       
        self._rendered_frames.pop()

    def post_render(self, scene):
        #lum.latest_render = scene.render.filepath
        self._frames.pop(0)
        self._rendering = False
        
    def file_extension(self, file_format):
        return self._image_formats[file_format]
    
    def subframes(self, sub_frames):
        subs = []
        for frame in sub_frames:
            main_frame, sub_frame = repr(frame).split('.')
            subs.append((int(main_frame), float('.' + sub_frame)))
        return subs

    def format_frame(self, frame):
        return "{f}{fn:0{lz}d}.{ext}".format(
            f=self._filename, fn=frame, lz=self.digits, ext=self._extension)

    def format_subframe(self, frame):
        sub_frame = "{sf:.{dec}f}".format(sf = frame[1], dec=self._dec).split('.')[1]
        return "{f}{mf:0{lz}d}{sf}.{ext}".format(
            f=self._filename, mf=frame[0], lz=self.digits, 
            sf=sub_frame, ext=self._extension)

    def log_sequence(self, scene, limit):
        from time import ctime #lum.render_collection.clear()
        lum = scene.loom
        if len(lum.render_collection) == limit:
            lum.render_collection.remove(0)
        render = lum.render_collection.add()
        render.render_id = len(lum.render_collection)
        render.start_time = ctime()
        render.start_frame = str(self._frames[0])
        render.end_frame = str(self._frames[-1])
        render.name = self._filename
        render.file_path = self._output_path
        render.padded_zeros = self.digits if not self._dec else self.digits + self._dec
        render.image_format = self._extension

    def final_report(self):
        if self._rendered_frames:
            frame_count = len(self._rendered_frames)
            if isinstance(self._rendered_frames[0], tuple):
                rendered = ', '.join("{mf}.{sf}".format(
                    mf=i[0], sf=str(i[1]).split(".")[1]) for i in self._rendered_frames)
            else:
                rendered = ','.join(map(str, self._rendered_frames))
            self.report({'INFO'}, "{} {} rendered.".format(
                "Frames:" if frame_count > 1 else "Frame:", rendered))
            self.report({'INFO'}, "{} saved to {}".format(
                "Images" if frame_count > 1 else "Image", self._folder))
                
        if self._skipped_frames:
            skip_count = len(self._skipped_frames)
            if isinstance(self._skipped_frames[0], tuple):
                skipped = ', '.join("{mf}.{sf}".format(
                    mf=i[0], sf=str(i[1]).split(".")[1]) for i in self._skipped_frames)
            else:
                skipped = ','.join(map(str, self._skipped_frames))
            self.report({'WARNING'}, "{} skipped (to not overwrite existing file)".format(skipped))

    def execute(self, context):
        scn = context.scene
        prefs = context.user_preferences.addons[__name__].preferences

        """ Filter user input """
        self._frames = filter_frames(self.frames, scn.frame_step, self.isolate_numbers)

        if not self._frames:
            self.report({'INFO'}, "No frames to render")
            return {"CANCELLED"}
        
        if not self.render_silent:
            self.report({'INFO'}, "Rendering Image Sequence...\n")

        """ Format output string """
        self._output_path = scn.render.filepath
        output_folder, self._filename = os.path.split(self._output_path)
        self._folder = os.path.realpath(bpy.path.abspath(output_folder))
        self._extension = self.file_extension(scn.render.image_settings.file_format)
               
        if self._filename:
            if self._filename.lower().endswith(tuple(self._image_formats.values())):
                name_real, ext = os.path.splitext(self._filename)
            else:
                name_real = self._filename
            if "#" in name_real:
                hashes = re.findall("#+$", name_real)
                name_real = re.sub("#", '', name_real)
                self.digits = len(hashes[0]) 
            self._filename = name_real + "_" if name_real[-1].isdigit() else name_real

        else: # If filename not specified, use blend-file name instead
            self._filename, ext = os.path.splitext(os.path.basename(bpy.data.filepath))
            self._filename += "_"
            self._output_path = os.path.join(self._folder, self._filename)

        """ Clear assigned frame numbers """
        self._skipped_frames.clear(), self._rendered_frames.clear()

        """ Determine whether given frames are subframes """
        if isinstance(self._frames[0], float):
            self._frames = self.subframes(self._frames)
            self._dec = max(map(lambda x: len(str(x[1]).split('.')[1]), self._frames))
            self._subframe_flag = True

        """ Logging  """
        if prefs.log_render: self.log_sequence(scn, prefs.log_render_limit)
        
        """ Render silent """
        if self.render_silent:
            for frame_number in self._frames:

                """ Assemble filename & set output """
                scn.render.filepath = os.path.join(
                    self._folder, self.format_subframe(frame_number) if self._subframe_flag \
                    else self.format_frame(frame_number))
                
                # Skip frame, if already rendered
                if not scn.render.use_overwrite and os.path.isfile(scn.render.filepath):
                    self._skipped_frames.append(frame_number)
                
                else: # Set the frame & render
                    if self._subframe_flag:
                        scn.frame_set(frame_number[0], subframe=frame_number[1])
                    else:
                        scn.frame_set(frame_number)
                        
                    bpy.ops.render.render(write_still=True)

                    if frame_number not in self._rendered_frames:
                        self._rendered_frames.append(frame_number)

            """ Reset output path & display results """
            scn.render.filepath = self._output_path #self.final_report() Prints it twice for whatever reason
            return {"FINISHED"}

        """ Add timer & handlers for modal """
        if not self.render_silent:
            self._stop = False
            self._rendering = False
            bpy.app.handlers.render_pre.append(self.pre_render)
            bpy.app.handlers.render_post.append(self.post_render)
            bpy.app.handlers.render_cancel.append(self.cancel_render)
            wm = context.window_manager
            self._timer = wm.event_timer_add(0.3, context.window)
            wm.modal_handler_add(self)
            return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.type == 'TIMER':
            scn = context.scene

            """ Determine whether frame list is empty or process is interrupted by the user """
            if not self._frames or self._stop: #if True in (not self._frames, self._stop is True):
                context.window_manager.event_timer_remove(self._timer)
                bpy.app.handlers.render_pre.remove(self.pre_render)
                bpy.app.handlers.render_post.remove(self.post_render)
                bpy.app.handlers.render_cancel.remove(self.cancel_render)

                """ Reset output path & display results """
                scn.render.filepath = self._output_path #self._extension
                self.final_report()
                return {"FINISHED"}

            elif self._rendering is False:
                """ Render within UI & show the progress as usual """
                if self._frames:
                    frame_number = self._frames[0]
                    scn.render.filepath = os.path.join(
                        self._folder, self.format_subframe(frame_number) if self._subframe_flag \
                        else self.format_frame(frame_number))

                    if not scn.render.use_overwrite and os.path.isfile(scn.render.filepath):
                        # Skip frame if file already rendered
                        self._skipped_frames.append(frame_number)
                        self.post_render(scn)
                    
                    else: # Set the frame & render
                        if self._subframe_flag:
                            scn.frame_set(frame_number[0], subframe=frame_number[1])
                        else:
                            scn.frame_set(frame_number)

                        bpy.ops.render.render("INVOKE_DEFAULT", write_still=True)
                        if frame_number not in self._rendered_frames:
                            self._rendered_frames.append(frame_number)
                        
        return {"PASS_THROUGH"}


# -------------------------------------------------------------------
#    Playblast (Experimental)
# -------------------------------------------------------------------

class LoomPlayBlast(bpy.types.Operator):
    """Playback rendered image sequence using the default or blender player"""
    bl_idname = "loom.playblast"
    bl_label = "Playblast Sequence"
    bl_description = "Playback rendered image sequence"
    bl_options = {'REGISTER'}
    
    # Todo! Just a temporary solution.
    # Might be a better idea trying to implement properties
    # for bpy.ops.render.play_rendered_anim() operator,
    # /startup/bl_operators/screen_play_rendered.py
    _image_sequence = {}

    def is_sequence(self, filepath):
        next_frame = re.sub('\d(?!\d)', lambda x: str(int(x.group(0)) + 1), filepath)
        return True if os.path.exists(next_frame) else False

    def number_suffix(self, filename):
        # test whether last char is digit?
        regex = re.compile(r'\d+\b')
        digits = ([x for x in regex.findall(filename)])
        return next(reversed(digits), None)

    def missing_frames(self, frames):
        return sorted(set(range(frames[0], frames[-1] + 1)).difference(frames))

    def file_sequence(self, filepath, digits=None, extension=None):
        basedir, filename = os.path.split(filepath)
        basedir = os.path.realpath(bpy.path.abspath(basedir))
        filename_noext, ext = os.path.splitext(filename)
        num_suffix = self.number_suffix(filename_noext)
        filename = filename_noext.replace(num_suffix,'') if num_suffix else filename_noext
        if extension: ext = extension
        if digits:
            file_pattern = r"{fn}(\d{{{ds}}})\.?{ex}$".format(fn=filename, ds=digits, ex=ext)
        else:
            file_pattern = r"{fn}(\d+)\.?{ex}".format(fn=filename, ex=ext)
        
        for f in os.scandir(basedir):
            if f.name.endswith(ext) and f.is_file():
                match = re.match(file_pattern, f.name, re.IGNORECASE)
                if match: self._image_sequence[int(match.group(1))] = os.path.join(basedir, f.name)

    def determine_type(self, val): 
        #val = ast.literal_eval(s)
        if (isinstance(val, int)):
            return ("chi")
        elif (isinstance(val, float)):
            return ("chf")
        if val in ["true", "false"]:
            return ("chb")
        else:
            return ("chs")

    def pack_arguments(self, lst):
        return [{"idc": 0, "name": self.determine_type(i), "value": str(i)} for i in lst]

    def execute(self, context):
        scn = context.scene
        lum = context.scene.loom
        prefs = context.user_preferences.addons[__name__].preferences #prefs.user_player = True
        preview_filetype = "jpg" if scn.render.image_settings.use_preview else None
        default_flag = False
        sequence_name = None

        if len(lum.render_collection) > 0 and prefs.log_render:

            seq = lum.render_collection[len(lum.render_collection)-1]
            seq_dir = os.path.realpath(bpy.path.abspath(os.path.split(seq.file_path)[0]))
            seq_ext = seq.image_format if not preview_filetype else preview_filetype
            sequence_name = "{}.{}".format(seq.file_path, seq_ext)

            self.file_sequence(
                filepath = os.path.join(seq_dir,"{}.{}".format(seq.name, seq.image_format)), 
                digits = seq.padded_zeros, 
                extension = preview_filetype)
            
        else:
            frame_path = bpy.path.abspath(scn.render.frame_path(frame=scn.frame_start, preview=False))
            default_flag = True
            """ Try default operator in the first place """ 
            if self.is_sequence(frame_path):
                bpy.ops.render.play_rendered_anim()
            else:
                self.file_sequence(filepath = frame_path, extension = preview_filetype)
                if self._image_sequence:
                    start = next(iter(self._image_sequence.keys()))
                    frame_path = next(iter(self._image_sequence.values()))
                    self.report({'WARNING'},"Sequence has offset and starts at {}".format(start))
                seq_dir, output_filename = os.path.split(frame_path)
                num_suffix = self.number_suffix(output_filename) #os.path.splitext(output_filename)[0]
                sequence_name = output_filename.replace(num_suffix,'#'*len(num_suffix))
        
        if not self._image_sequence:
            self.report({'WARNING'},"No sequence in loom cache")
            return {'CANCELLED'}
        else:
            if preview_filetype: 
                self.report({'WARNING'},"Preview Playback")
            if not default_flag:
                self.report({'INFO'},"Sequence from loom cache")
            else:
                self.report({'INFO'}, "Matching sequence ({}) found in {}".format(sequence_name, seq_dir))

        frames = sorted(list(self._image_sequence.keys()))
        start_frame = frames[0] 
        end_frame = frames[-1]

        """ Use preview range if enabled """
        if scn.use_preview_range:
            preview_start = scn.frame_preview_start
            preview_end = scn.frame_preview_end
            if all(x in frames for x in (preview_start, preview_end)):
                start_frame, end_frame = preview_start, preview_end
                frames = frames[frames.index(start_frame):frames.index(end_frame)]

        start_frame_path = self._image_sequence[frames[0]] # next(iter(self._image_sequence.values()))
        start_frame_suff = self.number_suffix(start_frame_path)
        start_frame_format = start_frame_path.replace(start_frame_suff,'#'*len(start_frame_suff))

        """ Detect missing frames """
        missing_frames = self.missing_frames(frames)
        if missing_frames:
            end_frame = missing_frames[0]-1
            self.report({'WARNING'}, "Missing Frames: {}".format(', '.join(map(str, missing_frames))))
            
        if not prefs.user_player:
            """ Assemble arguments and run the command """
            self.report({'INFO'}, "[Loom-OP Playback] {} {}-{}".format(sequence_name, start_frame, end_frame))
            self.report({'INFO'}, "Playblast Frame {}-{}".format(start_frame, end_frame))
            args = ["-a", "-f", str(scn.render.fps), str(scn.render.fps_base), "-s", str(start_frame), 
                    "-e", str(end_frame), "-j", str(scn.frame_step), start_frame_path]

            #bpy.ops.loom.run_terminal(arguments=" ".join(args), terminal_instance=False)
            bpy.ops.loom.run_terminal( 
                #debug_arguments=self.debug,
                terminal_instance=False,
                argument_collection=self.pack_arguments(args),
                force_bash=False)

        else: 
            """ Changes some scenes properties temporary... Bullshit!
            However, the only way using the default operator at the moment """
            outfile = scn.render.filepath
            file_format = scn.render.image_settings.file_format
            scn.render.filepath = start_frame_format
            timeline = (scn.frame_start, scn.frame_end)
            
            scn.frame_start = start_frame
            scn.frame_end = end_frame
            if preview_filetype: scn.render.image_settings.file_format = 'JPEG'

            self.report({'INFO'}, "[Default-OP Playback] {}".format(sequence_name))
            self.report({'INFO'}, "Playblast {}-{}".format(start_frame, end_frame))

            bpy.ops.render.play_rendered_anim() # Try it again!

            scn.frame_start = timeline[0]
            scn.frame_end = timeline[1]
            scn.render.filepath = outfile
            scn.render.image_settings.file_format = file_format

        return {'FINISHED'}


# -------------------------------------------------------------------
#    Utilities
# -------------------------------------------------------------------


class LoomRenderClearLog(bpy.types.Operator):
    """Clear Log Collection"""
    bl_idname = "loom.clear_log"
    bl_label = "Clear Log"
    bl_description = "Clear logging properties"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        context.scene.loom.render_collection.clear()
        return {'FINISHED'}


class LoomVerifyTerminal(bpy.types.Operator):
    """Search for system terminal"""
    bl_idname = "loom.verify_terminal"
    bl_label = "Verify Terminal"
    bl_description = "Verifies the terminal installed on the system"
    bl_options = {'INTERNAL'}

    def verify_app(self, cmd):
        try:
            subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                return False
        return True

    def execute(self, context):
        prefs = context.user_preferences.addons[__name__].preferences

        if platform.startswith('win32'):
            prefs.terminal = 'win-default'

        elif platform.startswith('darwin'):
            prefs.terminal = 'osx-default'
            prefs.bash_flag = True

        elif platform.startswith('linux'):

            if self.verify_app(["x-terminal-emulator", "--help"]):
                prefs.terminal = 'x-terminal-emulator'
            elif self.verify_app(["xfce4-terminal", "--help"]):
                prefs.terminal = 'xfce4-terminal'
            elif self.verify_app(["xterm", "--help"]):
                prefs.terminal = 'xterm'

        elif platform.startswith('freebsd'):
            if self.verify_app(["xterm", "--help"]):
                prefs.terminal = 'xterm'

        else:
            if self.verify_app(["xterm", "--help"]):
                prefs.terminal = 'xterm'
            else:
                self.report({'INFO'}, "Terminal not supported.")

        self.report({'INFO'}, "Terminal is '{}'".format(prefs.terminal))
        bpy.ops.wm.save_userpref()
        return {'FINISHED'}


class LoomGenericArgumentCollection(bpy.types.PropertyGroup):
    # name = bpy.props.StringProperty()
    value = bpy.props.StringProperty()
    idc = bpy.props.IntProperty()

class LoomRunTerminal(bpy.types.Operator):
    """Run an instance of an application in a new terminal"""
    bl_idname = "loom.run_terminal"
    bl_label = "Run Application in Terminal"
    bl_description = "Run Application in a new Terminal"
    bl_options = {'INTERNAL'}

    binary = bpy.props.StringProperty(
        name="Binary Path",
        description="Binary Path",
        maxlen=1024,
        subtype='FILE_PATH',
        default=bpy.app.binary_path)

    arguments = bpy.props.StringProperty(
        name="Command Line Arguments",
        description='[args …] "[file]" [args …]')

    argument_collection = bpy.props.CollectionProperty(
        name="Command Line Arguments",
        description="Allows passing a dictionary",
        type=LoomGenericArgumentCollection)

    debug_arguments = bpy.props.BoolProperty(
        name="Debug Arguments",
        description="Print full argument list",
        default=False)

    terminal_instance = bpy.props.BoolProperty(
        name="New Terminal Instance",
        description="Opens Blender in a new Terminal Window",
        default=True)

    force_bash = bpy.props.BoolProperty(
        name="Force Bash File",
        description="Use bash file instead of passing the arguments",
        default=False)

    bash_name = bpy.props.StringProperty(
        name="Name of bash file",
        description="Name of bash file")

    communicate = bpy.props.BoolProperty(
        name="Batch process",
        description="Wait for other process",
        default=False)
    
    shutdown = bpy.props.BoolProperty(
        name="Hibernate when done",
        description="Hibernate when done",
        default=False)

    pause = bpy.props.BoolProperty(
        name="Confirm when done",
        description="Confirm when done",
        default=True)

    def single_bash_cmd(self, arg_list):
        #l = [i for s in arg_list for i in s]
        return ["{b}{e}{b}".format(b='\"', e=x) \
            if x.startswith("import") else x for x in arg_list]

    def write_bat(self, bat_path, bat_args):
        try:
            fp = open(bat_path, "w")
            fp.write("@ECHO OFF\n") #fp.write('COLOR 7F\n')
            if isinstance(bat_args[0], list):
                bat_args = [[self.binary] + i if self.binary else i for i in bat_args]
                # Double quotes and double percentage %%
                bat_args = [["{b}{e}{b}".format(b='\"', e=x) \
                    if x.startswith("import") or '\\' in x else x for x in args] \
                    for args in bat_args] #  or os.path.isfile(x)
                bat_args = [[x.replace("%", "%%") for x in args] for args in bat_args]
                for i in bat_args:
                    fp.write(" ".join(i) + "\n")
            else:
                bat_args = [self.binary] + bat_args if self.binary else bat_args
                bat_args = ["{b}{e}{b}".format(b='\"', e=x) \
                    if '\\' in x or x.startswith("import") else x for x in bat_args] # or os.path.isfile(x)
                bat_args = [x.replace("%", "%%") for x in bat_args]
                fp.write(" ".join(bat_args) + "\n")

            if self.shutdown:
                fp.write('shutdown -s\n')
            if self.pause:
                fp.write('pause\n')
            fp.write('echo Loom Rendering and Encoding done.\n')
            fp.close()
        except:
            self.report({'INFO'}, "Something went wrong while writing the bat file")
            return {'CANCELLED'}

    def write_bash(self, bash_path, bash_args):
        try:
            fp = open(bash_path, 'w')
            fp.write('#! /bin/sh\n')
            if isinstance(bash_args[0], list):
                bash_args = [[self.binary] + i if self.binary else i for i in bash_args]
                bash_args = [["{b}{e}{b}".format(b='\"', e=x) \
                    if x.startswith("import") else x for x in args] for args in bash_args]
                for i in bash_args:
                    fp.write(" ".join(i) + "\n")
            else:
                bash_args = [self.binary] + bash_args if self.binary else bash_args
                bash_args = ["{b}{e}{b}".format(b='\"', e=x) \
                    if x.startswith("import") else x for x in bash_args]
                fp.write(" ".join(bash_args) + "\n")
            
            if self.pause: # https://stackoverflow.com/a/17778773
                fp.write('read -n1 -r -p "Press any key to continue..." key\n')
            if self.shutdown:
                fp.write('shutdown\n')
            fp.write('exit')
            fp.close()
            os.chmod(bash_path, 0o777)
        except:
            self.report({'INFO'}, "Something went wrong while writing the bash file")
            return {'CANCELLED'}

    def execute(self, context):
        prefs = context.user_preferences.addons[__name__].preferences
        args_user = []

        if not prefs.is_property_set("terminal") or not prefs.terminal:
            bpy.ops.loom.verify_terminal()

        if not prefs.terminal:
            self.report({'INFO'}, "Terminal not supported")
            return {'CANCELLED'}

        if self.arguments:
            '''
            Limitation: Splits the string by any whitspace, single or double quotes
            Could be improved with a regex to find the 'actual paths'
            '''
            pattern = r"""('[^']+'|"[^"]+"|[^\s']+)"""
            args_filter = re.compile(pattern, re.VERBOSE)
            lines = self.arguments.splitlines()
            for c, line in enumerate(lines):
                args_user.append(args_filter.findall(" ".join(lines)))
        
        elif len(self.argument_collection) > 0:
            #idcs = set([item.idc for item in self.argument_collection]) 
            arg_dict = {}
            for item in self.argument_collection:
                arg_dict.setdefault(item.idc, []).append(item.value)
            for key, args in arg_dict.items():
                args_user.append(args)

        if not args_user:
            self.report({'INFO'}, "No Arguments")
            return {'CANCELLED'}

        if self.bash_name:
            addon_folder = bpy.utils.script_path_user() # tempfile module?
            ext = ".bat" if prefs.terminal == 'win-default' else ".sh"
            prefs.bash_file = os.path.join(addon_folder, "{}{}".format(self.bash_name, ext))
        
        # Allow command stacking
        if len(args_user) > 1 and not self.communicate:
            self.force_bash = True

        """ Compile arguments for each terminal """
        if prefs.terminal == 'win-default':
            # ['start', 'cmd /k', self.binary, '-h', '&& TIMEOUT 1']
            args = [self.binary] + args_user[0] if self.binary else args_user[0]
            if self.force_bash:
                args = prefs.bash_file 

        elif prefs.xterm_flag:
            """ Xterm Fallback """ # https://bugs.python.org/issue12247
            xterm = ['xterm'] if not platform.startswith('darwin') else ['/usr/X11/bin/xterm']
            args = xterm + ["-e", self.binary] if self.binary else xterm + ["-e"]
            if self.force_bash:
                args = xterm + ["-e", prefs.bash_file]
            else:
                args += args_user[0] # Single command

        elif prefs.terminal == 'osx-default':
            """ OSX """
            #args = ["open", "-n", "-a", "Terminal", "--args", prefs.bash_file]
            #args = ["osascript", "-e", 'Tell application "Terminal" to do script "{} ;exit"'.format(quote(prefs.bash_file))]
            from shlex import quote
            activate = ["-e", 'Tell application "Terminal" to activate'] if not prefs.render_background else []
            run_bash = ["-e", 'Tell application "Terminal" to do script "{} ;exit"'.format(quote(prefs.bash_file))]
            args = ["osascript"] + activate + run_bash
            self.force_bash = True
            
        elif prefs.terminal in ['x-terminal-emulator', 'xterm']:
            """ Debian & FreeBSD """
            args = [prefs.terminal, "-e", self.binary] if self.binary else [prefs.terminal, "-e"]
            if self.force_bash:
                args = [prefs.terminal, "-e", prefs.bash_file]
            else:
                args += args_user[0] # Single command

        elif prefs.terminal in ['xfce4-terminal']: 
            """ Arch """
            args = [prefs.terminal, "-e"]
            if self.force_bash:
                args += [prefs.bash_file]
            else:
                args_xfce = self.single_bash_cmd(args_user[0])
                args_xfce = [self.binary] + args_xfce if self.binary else args_xfce
                args.append(" ".join(str(i) for i in args_xfce)) # Needs to be a string!               

        """ Print all compiled arguments """
        if self.debug_arguments:
            
            debug_list = args_user if not isinstance(args_user[0], list) \
                else [" ".join(i) for i in args_user] #else [i for sl in args_user for i in sl]
            '''
            if not any(os.path.isfile(x) and (x.endswith(".blend")) for x in debug_list):
                self.report({'INFO'}, "No blend-file provided")
            '''
            self.report({'INFO'}, "User Arguments: {}\n".format(
                ' '.join('\n{}: {}'.format(*k) for k in enumerate(debug_list))))
            if self.force_bash:
                self.report({'INFO'}, "Commands will be written to Bash: {}".format(args))
            else:
                self.report({'INFO'}, "Command: {}".format(args))
            return {'CANCELLED'}

        """ Write the file """ 
        if self.force_bash:
            if not platform.startswith('win32'):
                self.write_bash(prefs.bash_file, args_user)
            else:
                self.write_bat(prefs.bash_file, args_user)
        
        """ Open Terminal & pass all argements """
        try:
            if not self.terminal_instance:
                env_copy = os.environ.copy()
                subprocess.Popen(args, env=env_copy)
            
            elif platform.startswith('win32'):
                p = subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE)
                if self.communicate: p.communicate()

            else:
                # subprocess.call(args), same as Popen().wait(), print ("PID", p.pid)
                p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if self.communicate: p.communicate()

            return {'FINISHED'}
        
        except Exception as e:
            self.report({'ERROR'}, "Couldn't run command {} \nError: {}".format(
                        ' '.join('\n{}: {}'.format(*k) for k in enumerate(args)), str(e)))
            return {'CANCELLED'}


class LoomDeleteBashFiles(bpy.types.Operator):
    """Delete temporary bash file"""
    bl_idname = "loom.delete_bashfiles"
    bl_label = "Delete temporary Bash File"
    bl_description = "Deletes temporary bash file"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        prefs = context.user_preferences.addons[__name__].preferences
        bash_file = prefs.bash_file

        rem_lst = []
        for f in os.scandir(bpy.utils.script_path_user()):
            if f.name.endswith((".sh", ".bat")) and \
                f.name.startswith("loom-") and f.is_file():
                    try:
                        os.remove(f.path)
                        rem_lst.append(f.name)
                    except:
                        pass
        if rem_lst:
            self.report({'INFO'}, "{} removed.".format(", ".join(rem_lst)))
            prefs.bash_file = ""
        else:
            self.report({'INFO'}, "Nothing to remove")
        return {'FINISHED'}


class LoomDeleteFile(bpy.types.Operator):
    """Deletes a file by given path"""
    bl_idname = "loom.delete_file"
    bl_label = "Remove a File"
    bl_description = "Delete file by given path"
    bl_options = {'INTERNAL'}
    
    file_path = bpy.props.StringProperty()
    message_success = bpy.props.StringProperty(default="File removed")
    message_error = bpy.props.StringProperty(default="No file")
    
    def execute(self, context):
        try:
            os.remove(self.file_path)
            self.report({'INFO'}, self.message_success)
            return {'FINISHED'}
        except:
            self.report({'WARNING'}, self.message_error)
            return {'CANCELLED'}


# -------------------------------------------------------------------
#    Helper
# -------------------------------------------------------------------

def filter_frames(frame_input, increment=1, filter_individual=False):
    """ Filter frame input & convert it to a set of frames """
    def float_filter(st):
        try:
            return float(st)
        except ValueError:
            return None

    def int_filter(flt):
        try:
            return int(flt) if flt.is_integer() else None
        except ValueError:
            return None

    numeric_pattern = r"""
        [\^\!]? \s*? # Exclude option
        [-+]?        # Negative or positive number 
        (?:
            # Range & increment 1-2x2, 0.0-0.1x.02
            (?: \d* \.? \d+ \s? \- \s? \d* \.? \d+ \s? [x%] \s? [-+]? \d* \.? \d+ )
            |
            # Range 1-2, 0.0-0.1 etc
            (?: \d* \.? \d+ \s? \- \s? [-+]? \d* \.? \d+ )
            |
            # .1 .12 .123 etc 9.1 etc 98.1 etc
            (?: \d* \. \d+ )
            |
            # 1. 12. 123. etc 1 12 123 etc
            (?: \d+ \.? )
        )
        """
    range_pattern = r"""
        ([-+]? \d*? \.? [0-9]+ \b) # Start frame
        (\s*? \- \s*?)             # Minus
        ([-+]? \d* \.? [0-9]+)     # End frame
        ( (\s*? [x%] \s*? )( [-+]? \d* \.? [0-9]+ \b ) )? # Increment
        """
    exclude_pattern = r"""
        [\^\!] \s*?             # Exclude option
        ([-+]? \d* \.? \d+)$    # Int or Float
        """

    rx_filter = re.compile(numeric_pattern, re.VERBOSE)
    rx_group = re.compile(range_pattern, re.VERBOSE)
    rx_exclude = re.compile(exclude_pattern, re.VERBOSE)

    input_filtered = rx_filter.findall(frame_input)
    if not input_filtered: return None

    """ Option to add a ^ or ! at the beginning to exclude frames """
    if not filter_individual:
        first_exclude_item = next((i for i, v in enumerate(input_filtered) if "^" in v or "!" in v), None)
        if first_exclude_item:
            input_filtered = input_filtered[:first_exclude_item] + \
                             [elem if elem.startswith(("^", "!")) else "^" + elem.lstrip(' ') \
                              for elem in input_filtered[first_exclude_item:]]

    """ Find single values as well as all ranges & compile frame list """
    frame_list, exclude_list, conform_list  = [], [], []

    conform_flag = False
    for item in input_filtered:
        frame = float_filter(item)
        
        if frame is not None: # Single floats
            frame_list.append(frame)
            if conform_flag: conform_list.append(frame)

        else:  # Ranges & items to exclude
            exclude_item = rx_exclude.search(item)
            range_item = rx_group.search(item)

            if exclude_item:  # Single exclude items like ^-3 or ^10
                exclude_list.append(float_filter(exclude_item.group(1)))
                if filter_individual: conform_flag = True

            elif range_item:  # Ranges like 1-10, 20-10, 1-3x0.1, ^2-7 or ^-3--1
                start = min(float_filter(range_item.group(1)), float_filter(range_item.group(3)))
                end = max(float_filter(range_item.group(1)), float_filter(range_item.group(3)))
                step = increment if not range_item.group(4) else float_filter(range_item.group(6))

                if start < end:  # Build the range & add all items to list
                    frame_range = around(arange(start, end, step), decimals=5).tolist()
                    if item.startswith(("^", "!")):
                        if filter_individual: conform_flag = True
                        exclude_list.extend(frame_range)
                        if isclose(step, (end - frame_range[-1])):
                            exclude_list.append(end)
                    else:
                        frame_list.extend(frame_range)
                        if isclose(step, (end - frame_range[-1])):
                            frame_list.append(end)

                        if conform_flag:
                            conform_list.extend(frame_range)
                            if isclose(step, (end - frame_range[-1])):
                                conform_list.append(end)

                elif start == end:  # Not a range, add start frame
                    if not item.startswith(("^", "!")):
                        frame_list.append(start)
                    else:
                        exclude_list.append(start)

    if filter_individual:
        exclude_list = sorted(set(exclude_list).difference(conform_list))
    float_frames = sorted(set(frame_list).difference(exclude_list))

    """ Return integers whenever possible """
    int_frames = [int_filter(frame) for frame in float_frames]
    return float_frames if None in int_frames else int_frames


def draw_loom_render_panel(self, context):
    prefs = context.user_preferences.addons[__name__].preferences
    if prefs.display_ui:
        layout = self.layout
        row = layout.row()
        col = row.column(align=True)
        col.operator(LoomRenderDialog.bl_idname, icon="RENDER_ANIMATION")
        if prefs.playblast_flag:
            split = col.split(align=True, percentage=0.5)
            split.operator(LoomPlayBlast.bl_idname, icon="PLAY", text="Playblast")
            split.operator(LoomEncodeSequence.bl_idname, icon="FILE_MOVIE", text="Encode")
        else:
            col.operator(LoomEncodeSequence.bl_idname, icon="FILE_MOVIE", text="Encode Image Sequence")
        row = layout.row(align=True)


def draw_loom_render_menu(self, context):
    prefs = context.user_preferences.addons[__name__].preferences
    layout = self.layout
    layout.separator()
    layout.operator(LoomRenderDialog.bl_idname, icon='RENDER_ANIMATION')
    layout.operator(LoomEncodeSequence.bl_idname, icon='FILE_MOVIE', text="Encode Image Sequence")
    layout.operator(LoomBatchDialog.bl_idname, icon='SEQ_LUMA_WAVEFORM', text="Batch Render and Encode")
    if prefs.playblast_flag:
        layout.operator(LoomPlayBlast.bl_idname, icon='PLAY', text="Loom Playblast")


# -------------------------------------------------------------------
#    Registration & Shortcuts
# -------------------------------------------------------------------

addon_keymaps = []
user_keymap_ids = []

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.loom = bpy.props.PointerProperty(type=LoomSettings)

    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="Screen", space_type='EMPTY')
        
        if bpy.context.user_preferences.addons[__name__].preferences.playblast_flag:
            kmi = km.keymap_items.new("loom.playblast", 'F11', 'PRESS', ctrl=True, shift=True)
            kmi.active = True
            addon_keymaps.append((km, kmi))
        
        kmi = km.keymap_items.new("loom.encode_sequence", 'F9', 'PRESS', ctrl=True, shift=True)
        kmi.active = True
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("loom.batch_render_dialog", 'F12', 'PRESS', ctrl=True, shift=True, alt=True)
        kmi.active = True
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("loom.render_dialog", 'F12', 'PRESS', ctrl=True, shift=True)
        kmi.active = True
        addon_keymaps.append((km, kmi))
    
    if bpy.app.version < (2, 80, 0): bpy.types.RENDER_PT_render.prepend(draw_loom_render_panel)
    bpy.types.INFO_MT_render.append(draw_loom_render_menu)

def unregister():
    if bpy.app.version < (2, 80, 0): bpy.types.RENDER_PT_render.remove(draw_loom_render_panel)
    bpy.types.INFO_MT_render.remove(draw_loom_render_menu)
    bpy.utils.unregister_module(__name__)

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    del bpy.types.Scene.loom
    
    
if __name__ == "__main__":
    register()
