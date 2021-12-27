# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Copyright (C) 2013-2014: SCS Software

import bpy
import os
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.printout import lprint
from io_scs_tools.exp import pia as _pia
from io_scs_tools.exp import pic as _pic
from io_scs_tools.exp import pis as _pis
from io_scs_tools.exp import pit as _pit
from io_scs_tools.exp import pit_ef as _pit_ef
from io_scs_tools.exp.pim import exporter as _pim_exporter
from io_scs_tools.exp.pim_ef import exporter as _pim_ef_exporter
from io_scs_tools.exp.pip import exporter as _pip_exporter
from io_scs_tools.exp.transition_structs.bones import BonesTrans
from io_scs_tools.exp.transition_structs.materials import MaterialsTrans
from io_scs_tools.exp.transition_structs.parts import PartsTrans
from io_scs_tools.exp.transition_structs.terrain_points import TerrainPntsTrans


def _get_objects_by_type(blender_objects, parts):
    """Gets lists for different types of objects used by SCS.
    It actually returns: mesh objects, locators (prefab, model, collision) and armature object.

    :param blender_objects: list of the objects that should be sorted by type
    :type blender_objects: list of bpy.types.Object
    :param parts: transitional parts class instance for adding users (parts without users won't be exported)
    :type parts: io_scs_tools.exp.transition_structs.parts.PartsTrans
    :return: more lists of objects in order: meshes, prefab_locators, model_locators, collision_locators and armutare object as last
    :rtype: list of [list]
    """

    prefab_locator_list = []
    model_locator_list = []
    collision_locator_list = []
    mesh_object_list = []
    armature_object = None

    for obj in blender_objects:

        # LOCATORS
        if obj.type == 'EMPTY':
            if obj.scs_props.locator_type == 'Prefab':
                prefab_locator_list.append(obj)

                if _object_utils.has_part_property(obj):
                    parts.add_user(obj)

            elif obj.scs_props.locator_type == 'Model':
                model_locator_list.append(obj)

                parts.add_user(obj)

            elif obj.scs_props.locator_type == 'Collision':
                collision_locator_list.append(obj)

                parts.add_user(obj)

        # ARMATURES
        elif obj.type == 'ARMATURE':
            if not armature_object:
                armature_object = obj
            else:
                lprint("W More armatures detected on SCS Root object, only first one will be used!")

        # MESHES
        elif obj.type == 'MESH':

            # MESH OBJECTS
            if obj.data.scs_props.locator_preview_model_path == "":  # Export object only if it's not a Preview Model...
                mesh_object_list.append(obj)

                parts.add_user(obj)

        else:
            print('!!! - Unhandled object type: %r' % str(obj.type))

    return mesh_object_list, prefab_locator_list, model_locator_list, collision_locator_list, armature_object


def export(dirpath, name_suffix, root_object, game_object_list):
    """The main export function.

    :param dirpath: The main Filepath where most of the Files will be exported
    :type dirpath: str
    :param name_suffix: files name suffix (exchange format is using .ef)
    :type name_suffix: str
    :param root_object: This is the "SCS Root Object" and parent object of all objects in "game_object_list" and carries many settings for the
    whole "SCS Game Object"
    :type root_object: bpy.types.Object
    :param game_object_list: This is a simple list of all objects belonging to the "SCS Game Object", which can be further reduced of invalid objects
    :type game_object_list: list
    :return: Return state statuses (Usually 'FINISHED')
    :rtype: dict
    """
    import time

    t = time.time()
    context = bpy.context
    context.window.cursor_modal_set('WAIT')

    lprint("I Export started for: %r on: %s", (root_object.name, time.strftime("%b %d, %Y at %H:%M:%S")))

    # TRANSITIONAL STRUCTURES
    terrain_points = TerrainPntsTrans()
    parts = PartsTrans(root_object.scs_object_part_inventory)
    materials = MaterialsTrans()
    bones = BonesTrans()

    # GROUP OBJECTS BY TYPE
    (
        mesh_objects,
        prefab_locators,
        model_locators,
        collision_locators,
        armature_object
    ) = _get_objects_by_type(game_object_list, parts)

    # INITIAL CHECKS
    skeleton_filepath = root_object.name + ".pis" + name_suffix  # NOTE: if no skeleton is exported name of it should be there anyway
    if armature_object and root_object.scs_props.scs_root_animated == "anim":

        skeleton_filepath = _path_utils.get_skeleton_relative_filepath(armature_object, dirpath, root_object.name) + name_suffix

        if len(mesh_objects) == 0:
            context.window.cursor_modal_restore()
            lprint("E Rejecting animated Game Object with SCS Root Object name %r.\n\t   "
                   "Animated Game Object has to have at least one mesh object!",
                   (root_object.name,))
            return False

    if len(mesh_objects) == 0 and len(model_locators) == 0:
        context.window.cursor_modal_restore()
        lprint("E Rejecting empty Game Object with SCS Root Object name: %r\n\t   " +
               "Game Object has to have at least one mesh object or model locator!",
               (root_object.name,))
        return False

    # EXPORT
    scs_globals = _get_scs_globals()
    export_success = True

    # EXPORT PIM
    if scs_globals.export_pim_file:
        in_args = (dirpath, name_suffix, root_object, armature_object, skeleton_filepath, mesh_objects, model_locators)
        trans_structs_args = (parts, materials, bones, terrain_points)

        if scs_globals.export_output_type == "5":
            export_success = _pim_exporter.execute(*(in_args + trans_structs_args))
        elif scs_globals.export_output_type == "EF":
            export_success = _pim_ef_exporter.execute(*(in_args + trans_structs_args))
        else:
            export_success = False

        # EXPORT PIC
        if scs_globals.export_pic_file and export_success:
            if collision_locators:
                in_args = (collision_locators, dirpath + os.sep + root_object.name, name_suffix, root_object.name)
                trans_structs_args = (parts,)
                export_success = _pic.export(*(in_args + trans_structs_args))
            else:
                lprint("I No collider locator objects to export.")

    # EXPORT PIP
    if scs_globals.export_pip_file and prefab_locators and export_success:
        in_args = (dirpath, root_object.name, name_suffix, prefab_locators, root_object.matrix_world)
        trans_structs_args = (parts, terrain_points)
        export_success = _pip_exporter.execute(*(in_args + trans_structs_args))

    # EXPORT PIT
    if scs_globals.export_pit_file and export_success:
        in_args = (root_object, dirpath + os.sep + root_object.name, name_suffix)
        trans_structs_args = (parts, materials)

        if scs_globals.export_output_type == "5":
            export_success = _pit.export(*(in_args + trans_structs_args))
        elif scs_globals.export_output_type == "EF":
            export_success = _pit_ef.export(*(in_args + trans_structs_args))
        else:
            export_success = False

    # PIS, PIA
    if root_object.scs_props.scs_root_animated == 'anim':
        # EXPORT PIS
        if scs_globals.export_pis_file and bones.are_present() and export_success:
            export_success = _pis.export(os.path.join(dirpath, skeleton_filepath), root_object, armature_object, bones.get_as_list())

        # EXPORT PIA
        if scs_globals.export_pia_file and bones.are_present() and export_success:

            anim_dirpath = _path_utils.get_animations_relative_filepath(root_object, dirpath)

            if anim_dirpath is not None:

                anim_dirpath = os.path.join(dirpath, anim_dirpath)
                # make sure to get relative path from PIA to PIS (animations may use custom export path)
                skeleton_filepath = _path_utils.get_skeleton_relative_filepath(armature_object, anim_dirpath, root_object.name) + name_suffix

                exported_anims_names = {}  # store exported animations paths, so we can report duplicates and overwrites

                for scs_anim in root_object.scs_object_animation_inventory:

                    if scs_anim.export:  # check if export is disabled on animation itself

                        # TODO: use bones transitional variable for safety checks
                        export_success = _pia.export(root_object, armature_object, scs_anim, anim_dirpath, name_suffix, skeleton_filepath)

                        if export_success:

                            if scs_anim.name not in exported_anims_names:
                                exported_anims_names[scs_anim.name] = 1
                            else:
                                exported_anims_names[scs_anim.name] += 1

                for anim_name, export_count in exported_anims_names.items():

                    if export_count > 1:

                        lprint("W Detected %s animation instances on SCS Root Object: %r with same name: %r.\n\t   "
                               "Only last one stayed exported as it overwrote previous ones!",
                               (export_count, root_object.name, anim_name))

            else:
                lprint("E Custom animations export path is not relative to SCS Project Base Path.\n\t   " +
                       "Animations won't be exported!")

    elif armature_object and len(root_object.scs_object_animation_inventory) > 0:
        lprint("W Armature and SCS Animations detected but not exported! If you are exporting animated model,\n\t   " +
               "make sure to switch SCS Root Object %r to 'Animated Model'!", (root_object.name,))

    # FINAL FEEDBACK
    context.window.cursor_modal_restore()
    if export_success:
        lprint("I Export completed for: %r in %.3f seconds.\n", (root_object.name, time.time() - t))

    return True
