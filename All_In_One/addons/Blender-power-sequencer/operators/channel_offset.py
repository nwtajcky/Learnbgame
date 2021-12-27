import bpy
from operator import attrgetter

from .utils.doc import doc_name, doc_idname, doc_brief, doc_description


class POWER_SEQUENCER_OT_channel_offset(bpy.types.Operator):
    """
    Move selected strip to the nearest open channel above/down
    """
    doc = {
        'name': doc_name(__qualname__),
        'demo': '',
        'description': doc_description(__doc__),
        'shortcuts': [
            ({'type': 'UP_ARROW', 'value': 'PRESS', 'alt': True},
             {'direction': 'up'},
             'Move to Open Channel Above'),
            ({'type': 'DOWN_ARROW', 'value': 'PRESS', 'alt': True},
             {'direction': 'down'},
             'Move to Open Channel Below')
        ],
        'keymap': 'Sequencer'
    }
    bl_idname = doc_idname(__qualname__)
    bl_label = doc['name']
    bl_description = doc_brief(doc['description'])
    bl_options = {'REGISTER', 'UNDO'}

    direction: bpy.props.EnumProperty(
        items=[('up', 'up', 'Move the selection 1 channel up'),
               ('down', 'down', 'Move the selection 1 channel down')],
        name='Direction',
        description='Move the sequences up or down',
        default='up')

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        selection = context.selected_sequences
        if not selection:
            return {'CANCELLED'}

        selection = sorted(
            selection, key=attrgetter('channel', 'frame_final_start'))

        if self.direction == 'up':
            for s in reversed(selection):
                s.channel += 1
        elif self.direction == 'down':
            for s in selection:
                if (s.channel > 1):
                    s.channel -= 1
        return {'FINISHED'}

