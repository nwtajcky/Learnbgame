import bpy

from .utils.doc import doc_name, doc_idname, doc_brief, doc_description


class POWER_SEQUENCER_OT_playback_speed_decrease(bpy.types.Operator):
    """
    *brief* Decrease playback speed incrementally down to normal


    Playback speed may be set to any of the following speeds:

    * Normal (1x)
    * Fast (1.33x)
    * Faster (1.66x)
    * Double (2x)
    * Triple (3x)

    Activating this operator will decrease playback speed through each
    of these steps until minimum speed is reached.
    """
    doc = {
        'name': doc_name(__qualname__),
        'demo': '',
        'description': doc_description(__doc__),
        'shortcuts': [
            ({'type': 'LEFT_BRACKET', 'value': 'PRESS'}, {}, 'Decrease Playback Speed')
        ],
        'keymap': 'Sequencer'
    }
    bl_idname = doc_idname(__qualname__)
    bl_label = doc['name']
    bl_description = doc_brief(doc['description'])

    def execute(self, context):
        scene = context.scene

        speeds = ["normal", "fast", "faster", "double", "triple"]
        current_speed = scene.power_sequencer.playback_speed

        index = speeds.index(current_speed) - 1
        if index < 0:
            index = 0
        new_speed = speeds[index]

        scene.power_sequencer.playback_speed = new_speed

        return {"FINISHED"}
