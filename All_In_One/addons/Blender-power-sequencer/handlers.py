import bpy
from bpy.app.handlers import persistent
from . import addon_updater_ops
# from .ui import POWER_SEQUENCER_MT_main


@persistent
def load_file_post(arg):
    """
    Called after loading the blend file
    """
    for scene in bpy.data.scenes:
        scene.power_sequencer.frame_pre = bpy.context.scene.frame_current


# TODO: if change speed with mouse, don't process
# TODO: support going back in time with arrow keys and play
# Options: wrap bpy.ops.screen.frame_offset etc.?
@persistent
def playback_speed_post(scene):
    """
    Handler function for faster playback
    Skips keyframes after a frame change based on the playback_speed value
    It steps over frame rather than increase the playback speed smoothly,
    but it's still useful for faster editing
    """
    if bpy.context.screen and not bpy.context.screen.is_animation_playing:
        return

    scene = bpy.context.scene
    playback_speed = scene.power_sequencer.playback_speed
    frame_multipler = 1

    if scene.power_sequencer.frame_pre > scene.frame_current:
        pass
    elif playback_speed == 'normal':
        pass
    elif playback_speed == 'fast' and scene.frame_current % 3 == 0:
        scene.frame_current = scene.frame_current + 1*frame_multipler
    elif playback_speed == 'faster' and scene.frame_current % 2 == 0:
        scene.frame_current = scene.frame_current + 1*frame_multipler
    elif playback_speed == 'double':
        # 2.5x -> skip 5 frames for 2. 2 then 3 then 2 etc.
        scene.frame_current = scene.frame_current + 1*frame_multipler
    elif playback_speed == 'triple':
        scene.frame_current = scene.frame_current + 2*frame_multipler

    # print('Pre {!s} / Post {!s}'.format(frame_pre, scene.frame_current))
    scene.power_sequencer.frame_pre = scene.frame_current


def draw_playback_speed(self, context):
    layout = self.layout
    scene = context.scene
    layout.prop(scene.power_sequencer, 'playback_speed')


def draw_ui_menu(self, context):
    layout = self.layout
    layout.menu('POWER_SEQUENCER_MT_main')


# Add-on updater
def draw_check_for_update(self, context):
    # Call to check for update in background
    # note: built-in checks ensure it runs at most once
    # and will run in the background thread, not blocking
    # or hanging blender
    # Internally also checks to see if auto-check enabled
    # and if the time interval has passed
    addon_updater_ops.check_for_update_background()


def register_handlers():
    # MENUS
    bpy.types.SEQUENCER_HT_header.append(draw_ui_menu)
    bpy.types.SEQUENCER_HT_header.append(draw_playback_speed)
    bpy.types.SEQUENCER_HT_header.append(draw_check_for_update)

    # HANDLERS
    load_post = bpy.app.handlers.load_post
    for handler in load_post:
        if (" load_file_post " in str(handler)):
            load_post.remove(handler)
    load_post.append(load_file_post)

    frame_change_post = bpy.app.handlers.frame_change_post
    for handler in frame_change_post:
        if (" playback_speed_post " in str(handler)):
            frame_change_post.remove(handler)
    frame_change_post.append(playback_speed_post)


def unregister_handlers():
    # MENUS
    bpy.types.SEQUENCER_HT_header.remove(draw_ui_menu)
    bpy.types.SEQUENCER_HT_header.remove(draw_playback_speed)
    bpy.types.SEQUENCER_HT_header.remove(draw_check_for_update)

    # HANDLERS
    load_post = bpy.app.handlers.load_post
    for handler in load_post:
        if (" load_file_post " in str(handler)):
            load_post.remove(handler)

    frame_change_post = bpy.app.handlers.frame_change_post
    for handler in frame_change_post:
        if (" playback_speed_post " in str(handler)):
            frame_change_post.remove(handler)
