import bpy

from .utils.doc import doc_name, doc_idname, doc_brief, doc_description


class POWER_SEQUENCER_OT_border_select(bpy.types.Operator):
    """
    *brief* Wrapper around Blender's border select, deselects handles and overrides selection

    Deselects the strips' handles before applying border select, so you don't
    have to deselect manually first.
    """
    doc = {
        'name': doc_name(__qualname__),
        'demo': '',
        'description': doc_description(__doc__),
        'shortcuts': [
            ({'type': 'B', 'value': 'PRESS', 'alt': True}, {}, 'Border Select')
        ],
        'keymap': 'Sequencer'
    }
    bl_idname = doc_idname(__qualname__)
    bl_label = doc['name']
    bl_description = doc_brief(doc['description'])
    bl_options = {'REGISTER', 'UNDO'}

    extend: bpy.props.BoolProperty(
        name="Extend the selection",
        description=("Extend the current selection if checked,"
                     " otherwise clear it"),
        default=False)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        for s in context.selected_sequences:
            s.select_right_handle = False
            s.select_left_handle = False
        bpy.ops.sequencer.select_all(action='DESELECT')
        bpy.ops.sequencer.select_box('INVOKE_DEFAULT')
        return {'FINISHED'}
