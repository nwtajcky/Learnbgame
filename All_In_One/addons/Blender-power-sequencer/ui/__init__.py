import bpy
from .panel import POWER_SEQUENCER_PT_Panel
from .change_panel_tab import POWER_SEQUENCER_OT_change_panel_tab
from .menu_contextual import POWER_SEQUENCER_MT_contextual
from .menu_toolbar import (
    POWER_SEQUENCER_MT_main,
    POWER_SEQUENCER_MT_playback,
    POWER_SEQUENCER_MT_strips,
    POWER_SEQUENCER_MT_strips_fades,
    POWER_SEQUENCER_MT_select,
    POWER_SEQUENCER_MT_deselect,
    POWER_SEQUENCER_MT_grab,
    POWER_SEQUENCER_MT_snap,
    POWER_SEQUENCER_MT_edit,
    POWER_SEQUENCER_MT_delete,
    POWER_SEQUENCER_MT_markers,
    POWER_SEQUENCER_MT_marker_delete,
    POWER_SEQUENCER_MT_render,
    POWER_SEQUENCER_MT_file,
    POWER_SEQUENCER_MT_trim,
    POWER_SEQUENCER_MT_mouse,
    POWER_SEQUENCER_MT_preview,
    POWER_SEQUENCER_MT_audio,
    POWER_SEQUENCER_MT_crossfade
)

classes = [
    POWER_SEQUENCER_PT_Panel,
    POWER_SEQUENCER_OT_change_panel_tab,
    POWER_SEQUENCER_MT_contextual,
    POWER_SEQUENCER_MT_main,
    POWER_SEQUENCER_MT_playback,
    POWER_SEQUENCER_MT_strips,
    POWER_SEQUENCER_MT_strips_fades,
    POWER_SEQUENCER_MT_select,
    POWER_SEQUENCER_MT_deselect,
    POWER_SEQUENCER_MT_grab,
    POWER_SEQUENCER_MT_snap,
    POWER_SEQUENCER_MT_edit,
    POWER_SEQUENCER_MT_delete,
    POWER_SEQUENCER_MT_markers,
    POWER_SEQUENCER_MT_marker_delete,
    POWER_SEQUENCER_MT_render,
    POWER_SEQUENCER_MT_file,
    POWER_SEQUENCER_MT_trim,
    POWER_SEQUENCER_MT_mouse,
    POWER_SEQUENCER_MT_preview,
    POWER_SEQUENCER_MT_audio,
    POWER_SEQUENCER_MT_crossfade
]

register_ui, unregister_ui = bpy.utils.register_classes_factory(classes)
