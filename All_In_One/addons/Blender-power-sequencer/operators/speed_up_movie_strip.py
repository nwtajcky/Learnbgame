import bpy

from .utils.global_settings import SequenceTypes
from .utils.slice_contiguous_sequence_list import slice_selection
from .utils.find_linked_sequences import find_linked
from .utils.doc import doc_name, doc_idname, doc_brief, doc_description


class POWER_SEQUENCER_OT_speed_up_movie_strip(bpy.types.Operator):
    """
    *brief* Add 2x speed, set frame end, wrap both into META


    Add 2x speed to strip and set it's frame end  accordingly.  Wraps both the strip and the speed
    modifier into a META strip.
    """
    doc = {
        'name': doc_name(__qualname__),
        'demo': 'https://i.imgur.com/ZyEd0jD.gif',
        'description': doc_description(__doc__),
        'shortcuts': [
            ({'type': 'PLUS', 'value': 'PRESS', 'shift': True}, {}, 'Add Speed')
        ],
        'keymap': 'Sequencer'
    }
    bl_idname = doc_idname(__qualname__)
    bl_label = doc['name']
    bl_description = doc_brief(doc['description'])
    bl_options = {"REGISTER", "UNDO"}

    speed_factor: bpy.props.IntProperty(
        name="Speed factor",
        description="How many times the footage gets sped up",
        default=2,
        min=0)
    individual_sequences: bpy.props.BoolProperty(
        name="Affect individual strips",
        description="Speed up every VIDEO strip individually",
        default=False)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        sequencer = bpy.ops.sequencer
        scene = context.scene
        active = scene.sequence_editor.active_strip

        # Select linked sequences
        for s in find_linked(context, context.sequences, context.selected_sequences):
            s.select = True
        selection = context.selected_sequences

        video_sequences = [
            s for s in selection if s.type in SequenceTypes.VIDEO
        ]

        if not video_sequences:
            self.report({
                "ERROR_INVALID_INPUT"
            }, "No Movie sequence or Metastrips selected. Operation cancelled")
            return {"CANCELLED"}

        # Slice the selection
        selection_blocks = []
        if self.individual_sequences:
            for s in selection:
                if s.type in SequenceTypes.EFFECT:
                    self.report(
                        {"ERROR_INVALID_INPUT"},
                        ("Can't speed up individual sequences if effect strips"
                         " are selected. Please only select VIDEO or META strips."
                         " Operation cancelled"))
                    return {'CANCELLED'}
            selection_blocks = [[s] for s in video_sequences]
        else:
            selection_blocks = slice_selection(context, selection)

        for block in selection_blocks:
            # start, end = 0, 0
            sequencer.select_all(action='DESELECT')
            if len(block) == 1:
                active = scene.sequence_editor.active_strip = block[0]
                # TODO: Use the full source clip
                # start = active.frame_final_start / self.speed_factor
                # end = start + active.frame_final_duration / self.speed_factor
                # active.frame_offset_start, active.frame_offset_end = 0, 0
            else:
                for s in block:
                    s.select = True
                # SELECT GROUPED ONLY AFFECTS ACTIVE STRIP
                # bpy.ops.sequencer.select_grouped(type='EFFECT_LINK')
                sequencer.meta_make()
                active = scene.sequence_editor.active_strip
            # Add speed effect
            sequencer.effect_strip_add(type='SPEED')
            effect_strip = context.scene.sequence_editor.active_strip
            effect_strip.use_default_fade = False
            effect_strip.speed_factor = self.speed_factor

            sequencer.select_all(action='DESELECT')
            active.select_right_handle = True
            active.select = True
            scene.sequence_editor.active_strip = active
            source_name = active.name

            from math import ceil
            size = ceil(
                active.frame_final_duration / effect_strip.speed_factor)
            endFrame = active.frame_final_start + size
            sequencer.snap(frame=endFrame)

            effect_strip.select = True
            sequencer.meta_make()
            context.selected_sequences[0].name = (source_name
                                                  + " "
                                                  + str(self.speed_factor)
                                                  + 'x')
        self.report({"INFO"}, "Successfully processed " +
                    str(len(selection_blocks)) + " selection blocks")
        return {"FINISHED"}
