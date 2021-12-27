import bpy
import datetime as dt
import operator as op
from .utils import pyperclip

from .utils.doc import doc_name, doc_idname, doc_brief, doc_description


class POWER_SEQUENCER_OT_copy_markers_as_timecodes(bpy.types.Operator):
    """
    Formats and copies all the markers as timecodes to put in a Youtube video's description
    """
    doc = {
        'name': doc_name(__qualname__),
        'demo': '',
        'description': doc_description(__doc__),
        'shortcuts': [],
        'keymap': 'Sequencer'
    }
    bl_idname = doc_idname(__qualname__)
    bl_label = doc['name']
    bl_description = doc_brief(doc['description'])

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        render = context.scene.render

        if len(context.scene.timeline_markers) == 0:
            self.report({'INFO'}, "No markers found")
            return {'CANCELLED'}

        sorted_markers = sorted(context.scene.timeline_markers, key=op.attrgetter('frame'))

        markers_as_timecodes = []
        for marker in sorted_markers:
            framerate = render.fps / render.fps_base
            time = (dt.datetime(year=1, month=1, day=1)
                    + dt.timedelta(seconds=marker.frame/framerate))
            markers_as_timecodes.append(time.strftime('%H:%M:%S {}'.format(marker.name)))

        pyperclip.copy('\n'.join(markers_as_timecodes))
        return {'FINISHED'}

