from .speed_up_movie_strip import POWER_SEQUENCER_OT_speed_up_movie_strip
from .add_transform import POWER_SEQUENCER_OT_add_transform
from .align_audios import POWER_SEQUENCER_OT_align_audios
from .border_select import POWER_SEQUENCER_OT_border_select
from .playback_speed_set import POWER_SEQUENCER_OT_playback_speed_set
from .channel_offset import POWER_SEQUENCER_OT_channel_offset
from .concatenate_strips import POWER_SEQUENCER_OT_concatenate_strips
from .copy_selected_sequences import POWER_SEQUENCER_OT_copy_selected_sequences
from .crossfade_add import POWER_SEQUENCER_OT_crossfade_add
from .crossfade_edit import POWER_SEQUENCER_OT_crossfade_edit
from .crossfade_remove import POWER_SEQUENCER_OT_crossfade_remove
from .cut_strips_under_cursor import POWER_SEQUENCER_OT_cut_strips_under_cursor
from .playback_speed_decrease import POWER_SEQUENCER_OT_playback_speed_decrease
from .delete_direct import POWER_SEQUENCER_OT_delete_direct
from .deselect_all_left_or_right import POWER_SEQUENCER_OT_deselect_all_strips_left_or_right
from .deselect_handles_and_grab import POWER_SEQUENCER_OT_deselect_handles_and_grab
from .duplicate_move import POWER_SEQUENCER_OT_duplicate_move
from .fade_add import POWER_SEQUENCER_OT_fade_add
from .fade_clear import POWER_SEQUENCER_OT_fade_clear
from .grab_closest_handle_or_cut import POWER_SEQUENCER_OT_grab_closest_cut
from .grab import POWER_SEQUENCER_OT_grab
from .grab_sequence_handles import POWER_SEQUENCER_OT_grab_sequence_handles
from .import_local_footage import POWER_SEQUENCER_OT_import_local_footage
from .playback_speed_increase import POWER_SEQUENCER_OT_playback_speed_increase
from .jump_time_offset import POWER_SEQUENCER_OT_jump_time_offset
from .jump_to_cut import POWER_SEQUENCER_OT_jump_to_cut
from .make_still_image import POWER_SEQUENCER_OT_make_still_image
from .marker_delete_closest import POWER_SEQUENCER_OT_marker_delete_closest
from .marker_delete_direct import POWER_SEQUENCER_OT_marker_delete_direct
from .marker_go_to_next import POWER_SEQUENCER_OT_marker_go_to_next
from .markers_as_timecodes import POWER_SEQUENCER_OT_copy_markers_as_timecodes
from .markers_create_from_selected import POWER_SEQUENCER_OT_markers_create_from_selected_strips
from .marker_snap_to_cursor import POWER_SEQUENCER_OT_marker_snap_to_cursor
from .markers_snap_matching_strips import POWER_SEQUENCER_OT_markers_snap_matching_strips
from .meta_resize_to_content import POWER_SEQUENCER_OT_meta_resize_to_content
from .meta_ungroup_and_trim import POWER_SEQUENCER_OT_meta_ungroup_and_trim
from .meta_trim_content_to_bounds import POWER_SEQUENCER_OT_meta_trim_content_to_bounds
from .mouse_cut import POWER_SEQUENCER_OT_mouse_cut
from .mouse_space_strips import POWER_SEQUENCER_OT_mouse_space_strips
from .mouse_toggle_mute import POWER_SEQUENCER_OT_mouse_toggle_mute
from .mouse_trim import POWER_SEQUENCER_OT_mouse_trim
from .open_project_directory import POWER_SEQUENCER_OT_open_project_directory
from .preview_closest_cut import POWER_SEQUENCER_OT_preview_closest_cut
from .preview_to_selection import POWER_SEQUENCER_OT_preview_to_selection
from .remove_gaps import POWER_SEQUENCER_OT_remove_gaps
from .scene_rename_with_strip import POWER_SEQUENCER_OT_scene_rename_with_strip
from .render_apply_preset import POWER_SEQUENCER_OT_render_apply_preset
from .ripple_delete import POWER_SEQUENCER_OT_ripple_delete
from .save_direct import POWER_SEQUENCER_OT_save_direct
from .scene_create_from_selection import POWER_SEQUENCER_OT_scene_create_from_selection
from .scene_cycle import POWER_SEQUENCER_OT_scene_cycle
from .select_closest_to_mouse import POWER_SEQUENCER_OT_select_closest_to_mouse
from .select_linked_strips import POWER_SEQUENCER_OT_select_linked_strips
from .select_linked_effect import POWER_SEQUENCER_OT_select_linked_effect
from .select_related_strips import POWER_SEQUENCER_OT_select_related_strips
from .select_strips_under_cursor import POWER_SEQUENCER_OT_select_strips_under_cursor
from .markers_set_preview_in_between import POWER_SEQUENCER_OT_set_preview_between_markers
from .set_timeline_range import POWER_SEQUENCER_OT_set_timeline_range
from .trim_left_or_right_handles import POWER_SEQUENCER_OT_trim_left_or_right_handles
from .snap_selection_to_cursor import POWER_SEQUENCER_OT_snap_selection_to_cursor
from .speed_remove_effect import POWER_SEQUENCER_OT_unspeed
from .swap_strips import POWER_SEQUENCER_OT_swap_strips
from .synchronize_titles import POWER_SEQUENCER_OT_synchronize_titles
from .toggle_selected_mute import POWER_SEQUENCER_OT_toggle_selected_mute
from .toggle_waveforms import POWER_SEQUENCER_OT_toggle_waveforms
from .trim_three_point_edit import POWER_SEQUENCER_OT_trim_three_point_edit
from .trim_to_surrounding_cuts import POWER_SEQUENCER_OT_trim_to_surrounding_cuts

classes = [
    POWER_SEQUENCER_OT_speed_up_movie_strip,
    POWER_SEQUENCER_OT_add_transform,
    POWER_SEQUENCER_OT_align_audios,
    POWER_SEQUENCER_OT_border_select,
    POWER_SEQUENCER_OT_playback_speed_set,
    POWER_SEQUENCER_OT_channel_offset,
    POWER_SEQUENCER_OT_concatenate_strips,
    POWER_SEQUENCER_OT_copy_selected_sequences,
    POWER_SEQUENCER_OT_crossfade_add,
    POWER_SEQUENCER_OT_crossfade_edit,
    POWER_SEQUENCER_OT_crossfade_remove,
    POWER_SEQUENCER_OT_cut_strips_under_cursor,
    POWER_SEQUENCER_OT_playback_speed_decrease,
    POWER_SEQUENCER_OT_delete_direct,
    POWER_SEQUENCER_OT_deselect_all_strips_left_or_right,
    POWER_SEQUENCER_OT_deselect_handles_and_grab,
    POWER_SEQUENCER_OT_duplicate_move,
    POWER_SEQUENCER_OT_fade_add,
    POWER_SEQUENCER_OT_fade_clear,
    POWER_SEQUENCER_OT_grab_closest_cut,
    POWER_SEQUENCER_OT_grab,
    POWER_SEQUENCER_OT_grab_sequence_handles,
    POWER_SEQUENCER_OT_import_local_footage,
    POWER_SEQUENCER_OT_playback_speed_increase,
    POWER_SEQUENCER_OT_jump_time_offset,
    POWER_SEQUENCER_OT_jump_to_cut,
    POWER_SEQUENCER_OT_make_still_image,
    POWER_SEQUENCER_OT_marker_delete_closest,
    POWER_SEQUENCER_OT_marker_delete_direct,
    POWER_SEQUENCER_OT_marker_go_to_next,
    POWER_SEQUENCER_OT_copy_markers_as_timecodes,
    POWER_SEQUENCER_OT_markers_create_from_selected_strips,
    POWER_SEQUENCER_OT_marker_snap_to_cursor,
    POWER_SEQUENCER_OT_markers_snap_matching_strips,
    POWER_SEQUENCER_OT_meta_resize_to_content,
    POWER_SEQUENCER_OT_meta_ungroup_and_trim,
    POWER_SEQUENCER_OT_meta_trim_content_to_bounds,
    POWER_SEQUENCER_OT_mouse_cut,
    POWER_SEQUENCER_OT_mouse_space_strips,
    POWER_SEQUENCER_OT_mouse_toggle_mute,
    POWER_SEQUENCER_OT_mouse_trim,
    POWER_SEQUENCER_OT_open_project_directory,
    POWER_SEQUENCER_OT_preview_closest_cut,
    POWER_SEQUENCER_OT_preview_to_selection,
    POWER_SEQUENCER_OT_remove_gaps,
    POWER_SEQUENCER_OT_scene_rename_with_strip,
    POWER_SEQUENCER_OT_render_apply_preset,
    POWER_SEQUENCER_OT_ripple_delete,
    POWER_SEQUENCER_OT_save_direct,
    POWER_SEQUENCER_OT_scene_create_from_selection,
    POWER_SEQUENCER_OT_scene_cycle,
    POWER_SEQUENCER_OT_select_closest_to_mouse,
    POWER_SEQUENCER_OT_select_linked_strips,
    POWER_SEQUENCER_OT_select_linked_effect,
    POWER_SEQUENCER_OT_select_related_strips,
    POWER_SEQUENCER_OT_select_strips_under_cursor,
    POWER_SEQUENCER_OT_set_preview_between_markers,
    POWER_SEQUENCER_OT_set_timeline_range,
    POWER_SEQUENCER_OT_trim_left_or_right_handles,
    POWER_SEQUENCER_OT_snap_selection_to_cursor,
    POWER_SEQUENCER_OT_unspeed,
    POWER_SEQUENCER_OT_swap_strips,
    POWER_SEQUENCER_OT_synchronize_titles,
    POWER_SEQUENCER_OT_toggle_selected_mute,
    POWER_SEQUENCER_OT_toggle_waveforms,
    POWER_SEQUENCER_OT_trim_three_point_edit,
    POWER_SEQUENCER_OT_trim_to_surrounding_cuts
]

doc = {
    'sequencer.refresh_all': {
        'name': 'Refresh All',
        'description': '',
        'shortcuts': [
            ({'type': 'R', 'value': 'PRESS', 'shift': True}, {}, 'Refresh All')
        ],
        'demo': '',
        'keymap': 'Sequencer'
    }
}
