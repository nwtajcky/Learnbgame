# MIT License

# Copyright (c) 2017 GiveMeAllYourCats

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Code author: Hotox
# Repo: https://github.com/michaeldegroot/cats-blender-plugin
# Edits by: GiveMeAllYourCats

import bpy

from . import common as Common
from . import eyetracking as Eyetracking
from .common import version_2_79_or_older
from .register import register_wrap

mmd_tools_installed = False
try:
    import mmd_tools_local
    mmd_tools_installed = True
except:
    pass


@register_wrap
class StartPoseMode(bpy.types.Operator):
    bl_idname = 'cats_manual.start_pose_mode'
    bl_label = 'Start Pose Mode'
    bl_description = 'Starts the pose mode.\n' \
                     'This lets you test how your model will move'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature() is None:
            return False
        return True

    def execute(self, context):
        saved_data = Common.SavedData()

        current = ""
        if bpy.context.active_object and bpy.context.active_object.mode == 'EDIT' and bpy.context.active_object.type == 'ARMATURE' and len(
                bpy.context.selected_editable_bones) > 0:
            current = bpy.context.selected_editable_bones[0].name

        if version_2_79_or_older():
            bpy.context.space_data.use_pivot_point_align = False
            bpy.context.space_data.show_manipulator = True
        else:
            pass
            # TODO

        armature = Common.set_default_stage()
        Common.switch('POSE')
        armature.data.pose_position = 'POSE'

        for mesh in Common.get_meshes_objects():
            if Common.has_shapekeys(mesh):
                for shape_key in mesh.data.shape_keys.key_blocks:
                    shape_key.value = 0

        for pb in armature.data.bones:
            pb.select = True
        bpy.ops.pose.rot_clear()
        bpy.ops.pose.scale_clear()
        bpy.ops.pose.transforms_clear()

        bone = armature.data.bones.get(current)
        if bone is not None:
            for pb in armature.data.bones:
                if bone.name != pb.name:
                    pb.select = False
        else:
            for index, pb in enumerate(armature.data.bones):
                if index != 0:
                    pb.select = False

        if version_2_79_or_older():
            bpy.context.space_data.transform_manipulators = {'ROTATE'}
        else:
            bpy.ops.wm.tool_set_by_id(name="builtin.rotate")

        saved_data.load(hide_only=True)
        Common.hide(armature, False)

        return {'FINISHED'}


@register_wrap
class StopPoseMode(bpy.types.Operator):
    bl_idname = 'cats_manual.stop_pose_mode'
    bl_label = 'Stop Pose Mode'
    bl_description = 'Stops the pose mode and resets the pose to normal'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature() is None:
            return False
        return True

    def execute(self, context):
        saved_data = Common.SavedData()
        armature = Common.get_armature()
        Common.set_active(armature)
        Common.hide(armature, False)

        for pb in armature.data.bones:
            pb.hide = False
            pb.select = True
        bpy.ops.pose.rot_clear()
        bpy.ops.pose.scale_clear()
        bpy.ops.pose.transforms_clear()
        for pb in armature.data.bones:
            pb.select = False

        armature = Common.set_default_stage()
        armature.data.pose_position = 'REST'

        for mesh in Common.get_meshes_objects():
            if Common.has_shapekeys(mesh):
                for shape_key in mesh.data.shape_keys.key_blocks:
                    shape_key.value = 0

        if version_2_79_or_older():
            bpy.context.space_data.transform_manipulators = {'TRANSLATE'}
        else:
            bpy.ops.wm.tool_set_by_id(name="builtin.select_box")

        Eyetracking.eye_left = None

        saved_data.load(hide_only=True)

        return {'FINISHED'}


@register_wrap
class PoseToShape(bpy.types.Operator):
    bl_idname = 'cats_manual.pose_to_shape'
    bl_label = 'Pose to Shape Key'
    bl_description = 'This saves your current pose as a new shape key.' \
                     '\nThe new shape key will be at the bottom of your shape key list of the mesh'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        armature = Common.get_armature()
        return armature and armature.mode == 'POSE'

    def execute(self, context):
        # pose_to_shapekey('Pose')
        bpy.ops.cats_manual.pose_name_popup('INVOKE_DEFAULT')

        return {'FINISHED'}


def pose_to_shapekey(name):
    saved_data = Common.SavedData()

    for mesh in Common.get_meshes_objects():
        Common.unselect_all()
        Common.set_active(mesh)

        Common.switch('EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.remove_doubles(threshold=0)
        Common.switch('OBJECT')

        # Apply armature mod
        mod = mesh.modifiers.new(name, 'ARMATURE')
        mod.object = Common.get_armature()
        bpy.ops.object.modifier_apply(apply_as='SHAPE', modifier=mod.name)

    armature = Common.set_default_stage()
    Common.switch('POSE')
    armature.data.pose_position = 'POSE'

    saved_data.load(ignore=armature.name)
    return armature


@register_wrap
class PoseNamePopup(bpy.types.Operator):
    bl_idname = "cats_manual.pose_name_popup"
    bl_label = "Give this shapekey a name:"
    bl_description = 'Sets the shapekey name. Press anywhere outside to skip'

    bpy.types.Scene.pose_to_shapekey_name = bpy.props.StringProperty(name="Pose Name")

    def execute(self, context):
        name = context.scene.pose_to_shapekey_name
        if not name:
            name = 'Pose'
        pose_to_shapekey(name)
        self.report({'INFO'}, 'Pose successfully saved as shape key.')
        return {'FINISHED'}

    def invoke(self, context, event):
        context.scene.pose_to_shapekey_name = 'Pose'
        dpi_value = Common.get_user_preferences().system.dpi
        return context.window_manager.invoke_props_dialog(self, width=dpi_value * 4, height=-550)

    def check(self, context):
        # Important for changing options
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        row.scale_y = 1.3
        row.prop(context.scene, 'pose_to_shapekey_name')


@register_wrap
class PoseToRest(bpy.types.Operator):
    bl_idname = 'cats_manual.pose_to_rest'
    bl_label = 'Apply as Rest Pose'
    bl_description = 'This applies the current pose position as the new rest position.' \
                     '\n' \
                     '\nIf you scale the bones equally on each axis the shape keys will be scaled correctly as well!' \
                     '\nWARNING: This can have unwanted effects on shape keys, so be careful when modifying the head with this'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        armature = Common.get_armature()
        return armature and armature.mode == 'POSE'

    def execute(self, context):
        saved_data = Common.SavedData()

        armature = Common.get_armature()
        scales = {}

        # Find out how much each bone is scaled
        for bone in armature.pose.bones:
            scale_x = bone.scale[0]
            scale_y = bone.scale[1]
            scale_z = bone.scale[2]

            if armature.data.bones.get(bone.name).use_inherit_scale:
                def check_parent(child, scale_x_tmp, scale_y_tmp, scale_z_tmp):
                    if child.parent:
                        parent = child.parent
                        scale_x_tmp *= parent.scale[0]
                        scale_y_tmp *= parent.scale[1]
                        scale_z_tmp *= parent.scale[2]

                        if armature.data.bones.get(parent.name).use_inherit_scale:
                            scale_x_tmp, scale_y_tmp, scale_z_tmp = check_parent(parent, scale_x_tmp, scale_y_tmp,
                                                                                 scale_z_tmp)

                    return scale_x_tmp, scale_y_tmp, scale_z_tmp

                scale_x, scale_y, scale_z = check_parent(bone, scale_x, scale_y, scale_z)

            if scale_x == scale_y == scale_z != 1:
                scales[bone.name] = scale_x

        pose_to_shapekey('PoseToRest')

        bpy.ops.pose.armature_apply()

        for mesh in Common.get_meshes_objects():
            Common.unselect_all()
            Common.set_active(mesh)

            mesh.active_shape_key_index = len(mesh.data.shape_keys.key_blocks) - 1
            bpy.ops.cats_shapekey.shape_key_to_basis()

            # Remove old basis shape key from shape_key_to_basis operation
            for index in range(len(mesh.data.shape_keys.key_blocks) - 1, 0, -1):
                mesh.active_shape_key_index = index
                if 'PoseToRest - Reverted' in mesh.active_shape_key.name:
                    bpy.ops.object.shape_key_remove(all=False)

            mesh.active_shape_key_index = 0

            # Find out which bones scale which shapekeys and set it to the highest scale
            print('\nSCALED BONES:')
            shapekey_scales = {}
            for bone_name, scale in scales.items():
                print(bone_name, scale)
                vg = mesh.vertex_groups.get(bone_name)
                if not vg:
                    continue

                for vertex in mesh.data.vertices:
                    for g in vertex.groups:
                        if g.group == vg.index and g.weight == 1:
                            for i, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
                                if i == 0:
                                    continue

                                if shapekey.data[vertex.index].co != mesh.data.shape_keys.key_blocks[0].data[
                                    vertex.index].co:
                                    if shapekey.name in shapekey_scales:
                                        shapekey_scales[shapekey.name] = max(shapekey_scales[shapekey.name], scale)
                                    else:
                                        shapekey_scales[shapekey.name] = scale
                            break

            # Mix every shape keys with itself with the slider set to the new scale
            for index in range(0, len(mesh.data.shape_keys.key_blocks)):
                mesh.active_shape_key_index = index
                shapekey = mesh.active_shape_key
                if shapekey.name in shapekey_scales:
                    print('Fixed shapekey', shapekey.name)
                    shapekey.slider_max = min(shapekey_scales[shapekey.name], 10)
                    shapekey.value = shapekey.slider_max
                    mesh.shape_key_add(name=shapekey.name + '-New', from_mix=True)
                    shapekey.value = 0

            # Remove all the old shapekeys
            for index in reversed(range(0, len(mesh.data.shape_keys.key_blocks))):
                mesh.active_shape_key_index = index
                shapekey = mesh.active_shape_key
                if shapekey.name in shapekey_scales:
                    bpy.ops.object.shape_key_remove(all=False)

            # Fix the names of the new shapekeys
            for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
                if shapekey and shapekey.name.endswith('-New'):
                    shapekey.name = shapekey.name[:-4]

            # Repair important shape key order
            Common.repair_shapekey_order(mesh.name)

        # Stop pose mode after operation
        bpy.ops.cats_manual.stop_pose_mode()

        saved_data.load(hide_only=True)

        self.report({'INFO'}, 'Pose successfully applied as rest pose.')
        return {'FINISHED'}


@register_wrap
class JoinMeshes(bpy.types.Operator):
    bl_idname = 'cats_manual.join_meshes'
    bl_label = 'Join Meshes'
    bl_description = 'Joins all meshes of this model together.' \
                     '\nIt also:' \
                     '\n  - Reorders all shape keys correctly' \
                     '\n  - Applies all transformations' \
                     '\n  - Repairs broken armature modifiers' \
                     '\n  - Applies all decimation and mirror modifiers' \
                     '\n  - Merges UV maps correctly'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        meshes = Common.get_meshes_objects(check=False)
        return meshes and len(meshes) > 0

    def execute(self, context):
        saved_data = Common.SavedData()
        mesh = Common.join_meshes()
        if not mesh:
            saved_data.load()
            self.report({'ERROR'}, 'Meshes could not be joined!')
            return {'CANCELLED'}

        saved_data.load()
        Common.unselect_all()
        Common.set_active(mesh)
        self.report({'INFO'}, 'Meshes joined.')
        return {'FINISHED'}


@register_wrap
class JoinMeshesSelected(bpy.types.Operator):
    bl_idname = 'cats_manual.join_meshes_selected'
    bl_label = 'Join Selected Meshes'
    bl_description = 'Joins all selected meshes of this model together.' \
                     '\nIt also:' \
                     '\n  - Reorders all shape keys correctly' \
                     '\n  - Applies all transformations' \
                     '\n  - Repairs broken armature modifiers' \
                     '\n  - Applies all decimation and mirror modifiers' \
                     '\n  - Merges UV maps correctly'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        meshes = Common.get_meshes_objects(check=False)
        return meshes and len(meshes) > 0

    def execute(self, context):
        saved_data = Common.SavedData()

        if not Common.get_meshes_objects(mode=3):
            saved_data.load()
            self.report({'ERROR'}, 'No meshes selected! Please select the meshes you want to join in the hierarchy!')
            return {'FINISHED'}

        mesh = Common.join_meshes(mode=1)
        if not mesh:
            saved_data.load()
            self.report({'ERROR'}, 'Selected meshes could not be joined!')
            return {'CANCELLED'}

        saved_data.load()
        Common.unselect_all()
        Common.set_active(mesh)
        self.report({'INFO'}, 'Selected meshes joined.')
        return {'FINISHED'}


@register_wrap
class SeparateByMaterials(bpy.types.Operator):
    bl_idname = 'cats_manual.separate_by_materials'
    bl_label = 'Separate by Materials'
    bl_description = 'Separates selected mesh by materials.\n' \
                     '\n' \
                     'Warning: Never decimate something where you might need the shape keys later (face, mouth, eyes..)'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if obj and obj.type == 'MESH':
            return True

        meshes = Common.get_meshes_objects(check=False)
        return meshes and len(meshes) >= 1

    def execute(self, context):
        saved_data = Common.SavedData()
        obj = context.active_object

        if not obj or (obj and obj.type != 'MESH'):
            Common.unselect_all()
            meshes = Common.get_meshes_objects()
            if len(meshes) == 0:
                saved_data.load()
                self.report({'ERROR'}, 'No meshes found!')
                return {'FINISHED'}
            if len(meshes) > 1:
                saved_data.load()
                self.report({'ERROR'}, 'Multiple meshes found!'
                                       '\nPlease select the mesh you want to separate!')
                return {'FINISHED'}
            obj = meshes[0]

        obj_name = obj.name

        Common.separate_by_materials(context, obj)

        saved_data.load(ignore=[obj_name])
        self.report({'INFO'}, 'Successfully separated by materials.')
        return {'FINISHED'}


@register_wrap
class SeparateByLooseParts(bpy.types.Operator):
    bl_idname = 'cats_manual.separate_by_loose_parts'
    bl_label = 'Separate by Loose Parts'
    bl_description = 'Separates selected mesh by loose parts.\n' \
                     'This acts like separating by materials but creates more meshes for more precision'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if obj and obj.type == 'MESH':
            return True

        meshes = Common.get_meshes_objects(check=False)
        return meshes

    def execute(self, context):
        saved_data = Common.SavedData()
        obj = context.active_object

        if not obj or (obj and obj.type != 'MESH'):
            Common.unselect_all()
            meshes = Common.get_meshes_objects()
            if len(meshes) == 0:
                saved_data.load()
                self.report({'ERROR'}, 'No meshes found!')
                return {'FINISHED'}
            if len(meshes) > 1:
                saved_data.load()
                self.report({'ERROR'}, 'Multiple meshes found!'
                                       '\nPlease select the mesh you want to separate!')
                return {'FINISHED'}
            obj = meshes[0]
        obj_name = obj.name

        Common.separate_by_loose_parts(context, obj)

        saved_data.load(ignore=[obj_name])
        self.report({'INFO'}, 'Successfully separated by loose parts.')
        return {'FINISHED'}


@register_wrap
class SeparateByShapekeys(bpy.types.Operator):
    bl_idname = 'cats_manual.separate_by_shape_keys'
    bl_label = 'Separate by Shape Keys'
    bl_description = 'Separates selected mesh into two parts,' \
                     '\ndepending on whether it is effected by a shape key or not.' \
                     '\n' \
                     '\nVery useful for manual decimation'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if obj and obj.type == 'MESH':
            return True

        meshes = Common.get_meshes_objects(check=False)
        return meshes

    def execute(self, context):
        saved_data = Common.SavedData()
        obj = context.active_object

        if not obj or (obj and obj.type != 'MESH'):
            Common.unselect_all()
            meshes = Common.get_meshes_objects()
            if len(meshes) == 0:
                saved_data.load()
                self.report({'ERROR'}, 'No meshes found!')
                return {'FINISHED'}
            if len(meshes) > 1:
                saved_data.load()
                self.report({'ERROR'}, 'Multiple meshes found!'
                                       '\nPlease select the mesh you want to separate!')
                return {'FINISHED'}
            obj = meshes[0]
        obj_name = obj.name

        Common.separate_by_shape_keys(context, obj)

        saved_data.load(ignore=[obj_name])
        self.report({'INFO'}, 'Successfully separated by shape keys.')
        return {'FINISHED'}


@register_wrap
class MergeWeights(bpy.types.Operator):
    bl_idname = 'cats_manual.merge_weights'
    bl_label = 'Merge Weights'
    bl_description = 'Deletes the selected bones and adds their weight to their respective parents.' \
                     '\n' \
                     '\nOnly available in Edit or Pose Mode with bones selected'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        active_obj = bpy.context.active_object
        if not active_obj or not bpy.context.active_object.type == 'ARMATURE':
            return False
        if active_obj.mode == 'EDIT' and bpy.context.selected_editable_bones:
            return True
        if active_obj.mode == 'POSE' and bpy.context.selected_pose_bones:
            return True

        return False

    def execute(self, context):
        saved_data = Common.SavedData()

        armature = bpy.context.object

        Common.switch('EDIT')

        # Find which bones to work on and put their name and their parent in a list
        parenting_list = {}
        for bone in bpy.context.selected_editable_bones:
            parent = bone.parent
            while parent and parent.parent and parent in bpy.context.selected_editable_bones:
                parent = parent.parent
            if not parent:
                continue
            parenting_list[bone.name] = parent.name

        # Merge all the bones in the parenting list
        merge_weights(armature, parenting_list)

        saved_data.load()

        self.report({'INFO'}, 'Deleted ' + str(len(parenting_list)) + ' bones and added their weights to their parents.')
        return {'FINISHED'}


@register_wrap
class MergeWeightsToActive(bpy.types.Operator):
    bl_idname = 'cats_manual.merge_weights_to_active'
    bl_label = 'Merge Weights'
    bl_description = 'Deletes the selected bones except the active one and adds their weights to the active bone.' \
                     '\nThe active bone is the one you selected last.' \
                     '\n' \
                     '\nOnly available in Edit or Pose Mode with bones selected'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        active_obj = bpy.context.active_object
        if not active_obj or not bpy.context.active_object.type == 'ARMATURE':
            return False
        if active_obj.mode == 'EDIT' and bpy.context.selected_editable_bones and len(bpy.context.selected_editable_bones) > 1:
            if bpy.context.active_bone in bpy.context.selected_editable_bones:
                return True
        elif active_obj.mode == 'POSE' and bpy.context.selected_pose_bones and len(bpy.context.selected_pose_bones) > 1:
            if bpy.context.active_pose_bone in bpy.context.selected_pose_bones:
                return True

        return False

    def execute(self, context):
        saved_data = Common.SavedData()

        armature = bpy.context.object

        Common.switch('EDIT')

        # Find which bones to work on and put their name and their parent in a list and parent the bones to the active one
        parenting_list = {}
        for bone in bpy.context.selected_editable_bones:
            if bone.name == bpy.context.active_bone.name:
                continue
            parenting_list[bone.name] = bpy.context.active_bone.name
            bone.parent = bpy.context.active_bone

        # Merge all the bones in the parenting list
        merge_weights(armature, parenting_list)

        # Load original modes
        saved_data.load()

        self.report({'INFO'}, 'Deleted ' + str(len(parenting_list)) + ' bones and added their weights to the active bone.')
        return {'FINISHED'}


def merge_weights(armature, parenting_list):
    Common.switch('OBJECT')
    # Merge the weights on the meshes
    for mesh in Common.get_meshes_objects(armature_name=armature.name):
        Common.set_active(mesh)

        for bone, parent in parenting_list.items():
            if not mesh.vertex_groups.get(bone):
                continue
            if not mesh.vertex_groups.get(parent):
                mesh.vertex_groups.new(name=parent)
            Common.mix_weights(mesh, bone, parent)

    # Select armature
    Common.unselect_all()
    Common.set_active(armature)
    Common.switch('EDIT')

    # Delete merged bones
    for bone in parenting_list.keys():
        armature.data.edit_bones.remove(armature.data.edit_bones.get(bone))


@register_wrap
class ApplyTransformations(bpy.types.Operator):
    bl_idname = 'cats_manual.apply_transformations'
    bl_label = 'Apply Transformations'
    bl_description = "Applies the position, rotation and scale to the armature and it's meshes"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature():
            return True
        return False

    def execute(self, context):
        saved_data = Common.SavedData()

        Common.apply_transforms()

        saved_data.load()
        self.report({'INFO'}, 'Transformations applied.')
        return {'FINISHED'}


@register_wrap
class RemoveZeroWeight(bpy.types.Operator):
    bl_idname = 'cats_manual.remove_zero_weight'
    bl_label = 'Remove Zero Weight Bones'
    bl_description = "Cleans up the bones hierarchy, deleting all bones that don't directly affect any vertices\n" \
                     "Don't use this if you plan to use 'Fix Model'"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature():
            return True
        return False

    def execute(self, context):
        saved_data = Common.SavedData()

        Common.set_default_stage()
        count = Common.delete_zero_weight()
        Common.set_default_stage()

        saved_data.load()
        self.report({'INFO'}, 'Deleted ' + str(count) + ' zero weight bones.')
        return {'FINISHED'}


@register_wrap
class RemoveConstraints(bpy.types.Operator):
    bl_idname = 'cats_manual.remove_constraints'
    bl_label = 'Remove Bone Constraints'
    bl_description = "Removes constrains between bones causing specific bone movement as these are not used by VRChat"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature():
            return True
        return False

    def execute(self, context):
        saved_data = Common.SavedData()

        Common.set_default_stage()
        Common.delete_bone_constraints()
        Common.set_default_stage()

        saved_data.load()
        self.report({'INFO'}, 'Removed all bone constraints.')
        return {'FINISHED'}


@register_wrap
class RecalculateNormals(bpy.types.Operator):
    bl_idname = 'cats_manual.recalculate_normals'
    bl_label = 'Recalculate Normals'
    bl_description = "Don't use this on good looking meshes as this can screw them up.\n" \
                     "Makes normals point inside of the selected mesh.\n" \
                     "Use this if there are random inverted or darker faces on the mesh"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            return True

        meshes = Common.get_meshes_objects(check=False)
        return meshes

    def execute(self, context):
        saved_data = Common.SavedData()

        obj = context.active_object
        if not obj or (obj and obj.type != 'MESH'):
            Common.unselect_all()
            meshes = Common.get_meshes_objects()
            if len(meshes) == 0:
                saved_data.load()
                return {'FINISHED'}
            obj = meshes[0]
        mesh = obj

        Common.unselect_all()
        Common.set_active(mesh)
        Common.switch('EDIT')
        Common.switch('EDIT')

        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)

        Common.set_default_stage()

        saved_data.load()
        self.report({'INFO'}, 'Recalculated all normals.')
        return {'FINISHED'}


@register_wrap
class FlipNormals(bpy.types.Operator):
    bl_idname = 'cats_manual.flip_normals'
    bl_label = 'Flip Normals'
    bl_description = "Flips the direction of the faces' normals of the selected mesh.\n" \
                     "Use this if all normals are inverted"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            return True

        meshes = Common.get_meshes_objects(check=False)
        return meshes

    def execute(self, context):
        saved_data = Common.SavedData()

        obj = context.active_object
        if not obj or (obj and obj.type != 'MESH'):
            Common.unselect_all()
            meshes = Common.get_meshes_objects()
            if len(meshes) == 0:
                saved_data.load()
                return {'FINISHED'}
            obj = meshes[0]
        mesh = obj

        Common.unselect_all()
        Common.set_active(mesh)
        Common.switch('EDIT')
        Common.switch('EDIT')

        bpy.ops.mesh.select_all(action='SELECT')

        bpy.ops.mesh.flip_normals()

        Common.set_default_stage()

        saved_data.load()
        self.report({'INFO'}, 'Flipped all normals.')
        return {'FINISHED'}


@register_wrap
class RemoveDoubles(bpy.types.Operator):
    bl_idname = 'cats_manual.remove_doubles'
    bl_label = 'Remove Doubles'
    bl_description = "Merges duplicated faces and vertices of the selected meshes." \
                     "\nThis is more save than doing it manually:" \
                     "\n  - leaves shape keys completely untouched" \
                     "\n  - but removes less doubles overall"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            return True

        meshes = Common.get_meshes_objects(check=False)
        return meshes

    def execute(self, context):
        saved_data = Common.SavedData()

        removed_tris = 0
        meshes = Common.get_meshes_objects(mode=3)
        if not meshes:
            meshes = [Common.get_meshes_objects()[0]]

        Common.set_default_stage()

        for mesh in meshes:
            removed_tris += Common.remove_doubles(mesh, 0.0001, save_shapes=True)

        Common.set_default_stage()

        saved_data.load()

        self.report({'INFO'}, 'Removed ' + str(removed_tris) + ' vertices.')
        return {'FINISHED'}


@register_wrap
class RemoveDoublesNormal(bpy.types.Operator):
    bl_idname = 'cats_manual.remove_doubles_normal'
    bl_label = 'Remove Doubles Normally'
    bl_description = "Merges duplicated faces and vertices of the selected meshes." \
                     "\nThis is exactly like doing it manually"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            return True

        meshes = Common.get_meshes_objects(check=False)
        return meshes

    def execute(self, context):
        saved_data = Common.SavedData()

        removed_tris = 0
        meshes = Common.get_meshes_objects(mode=3)
        if not meshes:
            meshes = [Common.get_meshes_objects()[0]]

        Common.set_default_stage()

        for mesh in meshes:
            removed_tris += Common.remove_doubles(mesh, 0.0001, save_shapes=True)

        Common.set_default_stage()

        saved_data.load()

        self.report({'INFO'}, 'Removed ' + str(removed_tris) + ' vertices.')
        return {'FINISHED'}


@register_wrap
class FixVRMShapesButton(bpy.types.Operator):
    bl_idname = 'cats_manual.fix_vrm_shapes'
    bl_label = 'Fix Koikatsu Shapekeys'
    bl_description = "Fixes the shapekeys of Koikatsu models"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return Common.get_meshes_objects(check=False)

    def execute(self, context):
        saved_data = Common.SavedData()

        mesh = Common.get_meshes_objects()[0]
        slider_max_eyes = 0.33333
        slider_max_mouth = 0.94

        if not Common.has_shapekeys(mesh):
            self.report({'INFO'}, 'No shapekeys detected!')
            saved_data.load()
            return {'CANCELLED'}

        Common.set_active(mesh)
        bpy.ops.object.shape_key_clear()

        shapekeys = enumerate(mesh.data.shape_keys.key_blocks)

        # Find shapekeys to merge
        shapekeys_to_merge_eyes = {}
        shapekeys_to_merge_mouth = {}
        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            if index == 0:
                continue

            # Set max slider
            if shapekey.name.startswith('eye_'):
                shapekey.slider_max = slider_max_eyes
            else:
                shapekey.slider_max = slider_max_mouth

            # Split name
            name_split = shapekey.name.split('00')
            if len(name_split) < 2:
                continue
            pre_name = name_split[0]
            post_name = name_split[1]

            # Put shapekey in corresponding list
            if pre_name == "eye_face.f":
                shapekeys_to_merge_eyes[post_name] = []
            elif pre_name == "kuti_face.f":
                shapekeys_to_merge_mouth[post_name] = []

        # Add all matching shapekeys to the merge list
        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            if index == 0:
                continue

            name_split = shapekey.name.split('00')
            if len(name_split) < 2:
                continue
            pre_name = name_split[0]
            post_name = name_split[1]

            if post_name in shapekeys_to_merge_eyes.keys():
                if pre_name == 'eye_face.f' or pre_name == 'eye_siroL.sL' or pre_name == 'eye_line_u.elu':
                    shapekeys_to_merge_eyes[post_name].append(shapekey.name)

            elif post_name in shapekeys_to_merge_mouth.keys():
                if pre_name == 'kuti_face.f' or pre_name == 'kuti_ha.ha' or pre_name == 'kuti_sita.t':
                    shapekeys_to_merge_mouth[post_name].append(shapekey.name)

        # Merge all the shape keys
        shapekeys_used = []
        for name, shapekeys_merge in shapekeys_to_merge_eyes.items():
            if len(shapekeys_merge) <= 1:
                continue

            for shapekey_name in shapekeys_merge:
                mesh.data.shape_keys.key_blocks[shapekey_name].value = slider_max_eyes
                shapekeys_used.append(shapekey_name)

            mesh.shape_key_add(name='eyes_' + name[1:], from_mix=True)
            mesh.active_shape_key_index = len(mesh.data.shape_keys.key_blocks) - 1
            bpy.ops.object.shape_key_move(type='TOP')
            bpy.ops.object.shape_key_clear()

        for name, shapekeys_merge in shapekeys_to_merge_mouth.items():
            if len(shapekeys_merge) <= 1:
                continue

            for shapekey_name in shapekeys_merge:
                mesh.data.shape_keys.key_blocks[shapekey_name].value = slider_max_mouth
                shapekeys_used.append(shapekey_name)

            mesh.shape_key_add(name='mouth_' + name[1:], from_mix=True)
            mesh.active_shape_key_index = len(mesh.data.shape_keys.key_blocks) - 1
            bpy.ops.object.shape_key_move(type='TOP')
            bpy.ops.object.shape_key_clear()

        # Remove all the used shapekeys
        for index in reversed(range(0, len(mesh.data.shape_keys.key_blocks))):
            mesh.active_shape_key_index = index
            shapekey = mesh.active_shape_key
            if shapekey.name in shapekeys_used:
                bpy.ops.object.shape_key_remove(all=False)

        saved_data.load()

        self.report({'INFO'}, 'Fixed VRM shapekeys.')
        return {'FINISHED'}


@register_wrap
class FixFBTButton(bpy.types.Operator):
    bl_idname = 'cats_manual.fix_fbt'
    bl_label = 'Fix Full Body Tracking'
    bl_description = "Applies a general fix for Full Body Tracking." \
                     "\n" \
                     '\nCan potentially reduce the knee bending of this avatar in VRChat.' \
                     '\nIgnore the "Spine length zero" warning in Unity.' \
                     '\n' \
                     '\nRequires bones:' \
                     '\n - Hips, Spine, Left leg, Right leg'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return Common.get_armature()

    def execute(self, context):
        saved_data = Common.SavedData()

        armature = Common.set_default_stage()
        Common.switch('EDIT')

        x_cord, y_cord, z_cord, fbx = Common.get_bone_orientations(armature)

        hips = armature.data.edit_bones.get('Hips')
        spine = armature.data.edit_bones.get('Spine')
        left_leg = armature.data.edit_bones.get('Left leg')
        right_leg = armature.data.edit_bones.get('Right leg')
        left_leg_new = armature.data.edit_bones.get('Left leg 2')
        right_leg_new = armature.data.edit_bones.get('Right leg 2')
        left_leg_new_alt = armature.data.edit_bones.get('Left_Leg_2')
        right_leg_new_alt = armature.data.edit_bones.get('Right_Leg_2')

        if not hips or not spine or not left_leg or not right_leg:
            self.report({'ERROR'}, 'Required bones could not be found!'
                                   '\nPlease make sure that your armature contains the following bones:'
                                   '\n - Hips, Spine, Left leg, Right leg'
                                   '\nExact names are required!')
            saved_data.load()
            return {'CANCELLED'}

        # FBT Fix
        # Disconnect bones
        for child in hips.children:
            child.use_connect = False
        for child in left_leg.children:
            child.use_connect = False
        for child in right_leg.children:
            child.use_connect = False

        # Flip hips
        hips.head = spine.head
        hips.tail = spine.head
        hips.tail[z_cord] = left_leg.head[z_cord]

        if hips.tail[z_cord] > hips.head[z_cord]:
            hips.tail[z_cord] -= 0.1

        # Create new leg bones and put them at the old location
        if not left_leg_new:
            print("DEBUG 1")
            if left_leg_new_alt:
                left_leg_new = left_leg_new_alt
                left_leg_new.name = 'Left leg 2'
                print("DEBUG 1.1")
            else:
                left_leg_new = armature.data.edit_bones.new('Left leg 2')
                print("DEBUG 1.2")
        if not right_leg_new:
            print("DEBUG 2")
            if right_leg_new_alt:
                right_leg_new = right_leg_new_alt
                right_leg_new.name = 'Right leg 2'
                print("DEBUG 2.1")
            else:
                right_leg_new = armature.data.edit_bones.new('Right leg 2')
                print("DEBUG 2.2")

        left_leg_new.head = left_leg.head
        left_leg_new.tail = left_leg.tail

        right_leg_new.head = right_leg.head
        right_leg_new.tail = right_leg.tail

        # Set new location for old leg bones
        left_leg.tail = left_leg.head
        left_leg.tail[z_cord] = left_leg.head[z_cord] + 0.1

        right_leg.tail = right_leg.head
        right_leg.tail[z_cord] = right_leg.head[z_cord] + 0.1

        left_leg_new.parent = left_leg
        right_leg_new.parent = right_leg

        # Fixes bones disappearing, prevents bones from having their tail and head at the exact same position
        for bone in armature.data.edit_bones:
            if round(bone.head[x_cord], 5) == round(bone.tail[x_cord], 5) \
                    and round(bone.head[y_cord], 5) == round(bone.tail[y_cord], 5) \
                    and round(bone.head[z_cord], 5) == round(bone.tail[z_cord], 5):
                if bone.name == 'Hips':
                    bone.tail[z_cord] -= 0.1
                else:
                    bone.tail[z_cord] += 0.1

        Common.switch('OBJECT')

        context.scene.full_body = True

        saved_data.load()

        self.report({'INFO'}, 'Successfully applied the Full Body Tracking fix.')
        return {'FINISHED'}


@register_wrap
class RemoveFBTButton(bpy.types.Operator):
    bl_idname = 'cats_manual.remove_fbt'
    bl_label = 'Remove Full Body Tracking'
    bl_description = "Removes the fix for Full Body Tracking." \
                     '\n' \
                     '\nRequires bones:' \
                     '\n - Hips, Spine, Left leg, Right leg, Left leg 2, Right leg 2'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return Common.get_armature()

    def execute(self, context):
        saved_data = Common.SavedData()

        armature = Common.set_default_stage()
        Common.switch('EDIT')

        x_cord, y_cord, z_cord, fbx = Common.get_bone_orientations(armature)

        hips = armature.data.edit_bones.get('Hips')
        spine = armature.data.edit_bones.get('Spine')
        left_leg = armature.data.edit_bones.get('Left leg')
        right_leg = armature.data.edit_bones.get('Right leg')
        left_leg_new = armature.data.edit_bones.get('Left leg 2')
        right_leg_new = armature.data.edit_bones.get('Right leg 2')

        if not hips or not spine or not left_leg or not right_leg:
            saved_data.load()
            self.report({'ERROR'}, 'Required bones could not be found!'
                                   '\nPlease make sure that your armature contains the following bones:'
                                   '\n - Hips, Spine, Left leg, Right leg, Left leg 2, Right leg 2'
                                   '\nExact names are required!')
            saved_data.load()
            return {'CANCELLED'}

        if not left_leg_new or not right_leg_new:
            saved_data.load()
            self.report({'ERROR'}, 'The Full Body Tracking Fix is not applied!')
            return {'CANCELLED'}

        # Remove FBT Fix
        # Corrects hips
        if hips.head[z_cord] > hips.tail[z_cord]:
            middle_x = (right_leg.head[x_cord] + left_leg.head[x_cord]) / 2
            hips.head[x_cord] = middle_x
            hips.tail[x_cord] = middle_x

            hips.head[y_cord] = right_leg.head[y_cord]
            hips.tail[y_cord] = right_leg.head[y_cord]

            hips.head[z_cord] = right_leg.head[z_cord]
            hips.tail[z_cord] = spine.head[z_cord]

        # Put the original legs at their old location
        left_leg.head = left_leg_new.head
        left_leg.tail = left_leg_new.tail

        right_leg.head = right_leg_new.head
        right_leg.tail = right_leg_new.tail

        # Remove second leg bones
        armature.data.edit_bones.remove(left_leg_new)
        armature.data.edit_bones.remove(right_leg_new)

        # Fixes bones disappearing, prevents bones from having their tail and head at the exact same position
        for bone in armature.data.edit_bones:
            if round(bone.head[x_cord], 5) == round(bone.tail[x_cord], 5) \
                    and round(bone.head[y_cord], 5) == round(bone.tail[y_cord], 5) \
                    and round(bone.head[z_cord], 5) == round(bone.tail[z_cord], 5):
                bone.tail[z_cord] += 0.1

        Common.switch('OBJECT')

        context.scene.full_body = False

        saved_data.load()

        self.report({'INFO'}, 'Successfully removed the Full Body Tracking fix.')
        return {'FINISHED'}


@register_wrap
class DuplicateBonesButton(bpy.types.Operator):
    bl_idname = 'cats_manual.duplicate_bones'
    bl_label = 'Duplicate Bones'
    bl_description = "Duplicates the selected bones including their weight and renames them to _L and _R"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        active_obj = bpy.context.active_object
        if not active_obj or not bpy.context.active_object.type == 'ARMATURE':
            return False
        if active_obj.mode == 'EDIT' and bpy.context.selected_editable_bones:
            return True
        elif active_obj.mode == 'POSE' and bpy.context.selected_pose_bones:
            return True

        return False

    def execute(self, context):
        saved_data = Common.SavedData()

        armature = bpy.context.object

        Common.switch('EDIT')

        bone_count = len(bpy.context.selected_editable_bones)

        # Create the duplicate bones
        duplicate_vertex_groups = {}
        for bone in bpy.context.selected_editable_bones:
            separator = '_'
            if bone.name.endswith('_'):
                separator = ''
            bone_new = armature.data.edit_bones.new(bone.name + separator + 'copy')
            bone_new.parent = bone.parent

            bone_new.head = bone.head
            bone_new.tail = bone.tail
            duplicate_vertex_groups[bone.name] = bone_new.name

        # Fix bone parenting
        for bone_name in duplicate_vertex_groups.values():
            bone = armature.data.edit_bones.get(bone_name)
            if bone.parent.name in duplicate_vertex_groups.keys():
                bone.parent = armature.data.edit_bones.get(duplicate_vertex_groups[bone.parent.name])

        # Create the missing vertex groups and duplicate the weight
        Common.switch('OBJECT')
        for mesh in Common.get_meshes_objects(armature_name=armature.name):
            Common.set_active(mesh)

            for bone_from, bone_to in duplicate_vertex_groups.items():
                mesh.vertex_groups.new(name=bone_to)
                Common.mix_weights(mesh, bone_from, bone_to, delete_old_vg=False)

        saved_data.load()

        self.report({'INFO'}, 'Successfully duplicated ' + str(bone_count) + ' bones.')
        return {'FINISHED'}
