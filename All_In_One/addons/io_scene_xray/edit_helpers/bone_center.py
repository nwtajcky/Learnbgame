import bpy
import mathutils

from io_scene_xray.xray_motions import MATRIX_BONE, MATRIX_BONE_INVERTED
from .base_bone import AbstractBoneEditHelper


class _BoneCenterEditHelper(AbstractBoneEditHelper):
    def draw(self, layout, context):
        if self.is_active(context):
            layout.operator(_ApplyCenter.bl_idname, icon='FILE_TICK')
            layout.operator(_AlignCenter.bl_idname, icon='CURSOR')
            super().draw(layout, context)
            return

        layout.operator(_EditCenter.bl_idname, text='Edit Center')

    def _create_helper(self, name):
        helper = bpy.data.objects.new(name, None)
        helper.empty_draw_size = 0.05
        helper.lock_rotation = helper.lock_scale = (True, True, True)
        return helper

    def _update_helper(self, helper, target):
        super()._update_helper(helper, target)
        bone = target

        global pose_bone
        pose_bone = bpy.context.object.pose.bones[bone.name]
        mat = pose_bone.matrix * MATRIX_BONE_INVERTED
        mat *= mathutils.Matrix.Translation(bone.xray.mass.center)
        helper.location = mat.to_translation()


HELPER = _BoneCenterEditHelper('bone-center-edit')


class _EditCenter(bpy.types.Operator):
    bl_idname = 'io_scene_xray.edit_bone_center'
    bl_label = 'Edit Bone Center'
    bl_description = 'Create a helper object that can be used for adjusting bone center'

    @classmethod
    def poll(cls, context):
        return context.active_bone and not HELPER.is_active(context)

    def execute(self, context):
        target = context.active_object.data.bones[context.active_bone.name]
        HELPER.activate(target)
        return {'FINISHED'}


class _AlignCenter(bpy.types.Operator):
    bl_idname = 'io_scene_xray.edit_bone_center_align'
    bl_label = 'Align Center'

    @classmethod
    def poll(cls, _context):
        _, bone = HELPER.get_target()
        return bone and bone.xray.shape.type != '0'

    def execute(self, _context):
        helper, bone = HELPER.get_target()
        shape = bone.xray.shape
        mat = pose_bone.matrix * MATRIX_BONE_INVERTED
        pos = None
        if shape.type == '1':
            pos = shape.box_trn
        elif shape.type == '2':
            pos = shape.sph_pos
        elif shape.type == '3':
            pos = shape.cyl_pos
        mat *= mathutils.Matrix.Translation((pos[0], pos[2], pos[1]))
        helper.location = mat.to_translation()
        return {'FINISHED'}


class _ApplyCenter(bpy.types.Operator):
    bl_idname = 'io_scene_xray.edit_bone_center_apply'
    bl_label = 'Apply Center'
    bl_options = {'UNDO'}

    def execute(self, _context):
        helper, bone = HELPER.get_target()
        mat = MATRIX_BONE * pose_bone.matrix.inverted() * helper.matrix_local
        bone.xray.mass.center = mat.to_translation()
        HELPER.deactivate()
        bpy.context.scene.update()
        return {'FINISHED'}
