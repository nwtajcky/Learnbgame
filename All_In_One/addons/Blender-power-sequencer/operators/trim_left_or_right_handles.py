from operator import attrgetter

import bpy

from .utils.doc import doc_brief, doc_description, doc_idname, doc_name


class POWER_SEQUENCER_OT_trim_left_or_right_handles(bpy.types.Operator):
    """
    Trims or extends the handle closest to the time cursor for all selected strips.

    If you keep the Shift key down, the edit will ripple through the timeline.

    By pressing A before K, the strips under the cursor are going to be auto selected.
    """
    doc = {
        'name': doc_name(__qualname__),
        'demo': '',
        'description': doc_description(__doc__),
        'shortcuts': [
            ({'type': 'K', 'value': 'PRESS', 'alt': True}, {'side': 'right', 'ripple': False, 'auto_select': False}, 'Smart Snap Right'),
            ({'type': 'K', 'value': 'PRESS', 'alt': True, 'key_modifier': 'A'}, {'side': 'right', 'ripple': False, 'auto_select': True}, 'Auto Select Smart Snap Right'),
            ({'type': 'K', 'value': 'PRESS', 'alt': True, 'shift': True}, {'side': 'right', 'ripple': True, 'auto_select': False}, 'Smart Snap Right With Ripple'),
            ({'type': 'K', 'value': 'PRESS', 'alt': True, 'shift': True, 'key_modifier': 'A'}, {'side': 'right', 'ripple': True, 'auto_select': True}, 'Auto Select Smart Snap Right With Ripple'),
            ({'type': 'K', 'value': 'PRESS', 'ctrl': True}, {'side': 'left', 'ripple': False, 'auto_select': False}, 'Smart Snap Left'),
            ({'type': 'K', 'value': 'PRESS', 'ctrl': True, 'key_modifier': 'A'}, {'side': 'left', 'ripple': False, 'auto_select': True}, 'Auto Select Smart Snap Left'),
            ({'type': 'K', 'value': 'PRESS', 'ctrl': True, 'shift': True}, {'side': 'left', 'ripple': True, 'auto_select': False}, 'Smart Snap Left With Ripple'),
            ({'type': 'K', 'value': 'PRESS', 'ctrl': True, 'shift': True, 'key_modifier': 'A'}, {'side': 'left', 'ripple': True, 'auto_select': True}, 'Auto Select Smart Snap Left With Ripple'),
        ],
        'keymap': 'Sequencer'
    }
    bl_idname = doc_idname(__qualname__)
    bl_label = doc['name']
    bl_description = doc_brief(doc['description'])
    bl_options = {'REGISTER', 'UNDO'}

    side: bpy.props.EnumProperty(
        items=[('left', 'Left', 'Left side'), ('right', 'Right', 'Right side'),
               ('auto', 'Auto', 'Use the side closest to the time cursor')],
        name="Snap side",
        description="Handle side to use for the snap",
        default='auto')
    ripple: bpy.props.BoolProperty(
        name="Ripple",
        default=False)
    auto_select: bpy.props.BoolProperty(
        name="Auto Select",
        default=False)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        frame_current = context.scene.frame_current
        if self.auto_select:
            for sequence in context.sequences:
                sequence.select=sequence.frame_final_start <= frame_current and sequence.frame_final_end >= frame_current

        to_ripple = self.select_strip_handle(context.selected_sequences, self.side, frame_current)

        bpy.ops.sequencer.snap(frame=frame_current)

        if self.ripple:
            for sequence_to_ripple in to_ripple:
                sequence = sequence_to_ripple["sequence"]
                original_frame = sequence_to_ripple["original_frame"]
                gap = original_frame - sequence.frame_final_end if \
                      sequence_to_ripple["side"] == 'RIGHT' else \
                      sequence.frame_final_start - original_frame
                self.ripple_sequences(sequence_to_ripple["sequence"], context,
                                      gap, sequence_to_ripple["side"])

        for sequence in context.selected_sequences:
            sequence.select_right_handle = False
            sequence.select_left_handle = False
        return {"FINISHED"}

    def select_strip_handle(self, sequences, side, frame):
        """
        Select the left or right handles of the strips based on the frame number
        """
        side = side.upper()
        to_ripple = []

        for s in sequences:
            s.select_left_handle = False
            s.select_right_handle = False

            handle_side = ''
            start, end = s.frame_final_start, s.frame_final_end
            if side == 'AUTO' and start <= frame <= end:
                handle_side = 'LEFT' if abs(
                    frame - start) < s.frame_final_duration / 2 else 'RIGHT'
            elif side == 'LEFT' and frame < end or side == 'RIGHT' and frame > start:
                handle_side = side
            else:
                s.select = False
            if handle_side:
                bpy.ops.sequencer.select_handles(side=handle_side)
                original_frame = s.frame_final_end if handle_side == 'RIGHT' else s.frame_final_start
                to_ripple.append({"side": handle_side, "original_frame": original_frame, "sequence": s})
        return to_ripple

    def ripple_sequences(self, sequence, context, gap, side):
        """
        Ripples edit sequences in the same channel of sequence moving them by gap
        """
        ordered_sequences = sorted(context.sequences, key=attrgetter('frame_final_start'))
        for s in ordered_sequences:
            if s.channel != sequence.channel:
                continue
            if s == sequence and side == 'LEFT' or sequence.frame_final_end < s.frame_final_start:
                try:
                    s.frame_start -= gap
                except AttributeError:
                    continue
