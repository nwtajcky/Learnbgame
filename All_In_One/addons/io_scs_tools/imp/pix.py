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
from io_scs_tools.consts import Operators as _OP_consts
from io_scs_tools.imp import pia as _pia
from io_scs_tools.imp import pic as _pic
from io_scs_tools.imp import pim as _pim
from io_scs_tools.imp import pim_ef as _pim_ef
from io_scs_tools.imp import pip as _pip
from io_scs_tools.imp import pis as _pis
from io_scs_tools.imp import pit as _pit
from io_scs_tools.imp.transition_structs.terrain_points import TerrainPntsTrans
from io_scs_tools.internals import inventory as _inventory
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils import material as _material_utils
from io_scs_tools.utils import name as _name_utils
from io_scs_tools.utils import object as _object_utils
from io_scs_tools.utils import path as _path_utils
from io_scs_tools.utils.printout import lprint


def _get_shader_data(material_data):
    """Returns Material's Effect, Attributes and Textures.

    :param material_data: Material data
    :type material_data: list
    :return: Material's Effect, Attributes, Textures
    :rtype: tuple
    """
    material_effect = material_data[0]
    material_attributes = material_data[2]
    material_textures = material_data[3]
    material_section = material_data[4]
    return material_effect, material_attributes, material_textures, material_section


def _are_shader_data_compatible(preset_section, material_attributes, material_textures, material_name):
    """Compares preset section attributes and textures for compatibility with actual given,
    dictionaries of material attributes and textures.
    It returns True if this conditions are meet:
    1. Attribute count is the same
    2. Texture count is the same
    3. All attributes from actual attributes dictonary exists in preset  (tags & value length has to match)
    4. All textures types from actual textures dictionary exists in preset (types have to match)

    :param preset_section: section data of the preset that should be compared with given attributes and textures
    :type preset_section: io_scs_tools.internals.structure.SectionData
    :param material_attributes: dictionary of attributes (key: attribute tag, value: attribute value)
    :type material_attributes: dict[str, float|int|list]
    :param material_textures: dictionary of textures (key: texture type, value: texture path
    :type material_textures: dict[str, str]
    :param material_name: name of the material we are working on, used purely for reporting messages
    :type material_name: str
    :return: True if everything matches, False otherwise
    :rtype: bool
    """

    preset_mat_attributes = {}
    preset_mat_textures = set()

    # collect attributes & texture types from preset
    for item in preset_section.sections:

        if item.type == "Attribute":

            attr_tag = item.get_prop_value("Tag")
            attr_value = item.get_prop_value("Value")

            preset_mat_attributes[attr_tag] = attr_value

        elif item.type == "Texture":

            tex_type = item.get_prop_value("Tag").split(":")[1]
            preset_mat_textures.add(tex_type)

    # we are not saving substance in presets thus add it if found in material attributes
    if "substance" in material_attributes:
        preset_mat_attributes["substance"] = None

    # calculate counters, as we don't keep counts in shader preset
    attr_count = len(preset_mat_attributes)
    tex_count = len(preset_mat_textures)

    # check if all material attributes are in preset
    for mat_attr_tag in material_attributes:

        if mat_attr_tag not in preset_mat_attributes:
            lprint("W Attribute: %r inside material %r not found in the assigned shader preset!", (mat_attr_tag, material_name))
            return False

        preset_attr_value = preset_mat_attributes[mat_attr_tag]
        if isinstance(preset_attr_value, list) and len(preset_attr_value) != len(material_attributes[mat_attr_tag]):
            lprint("W Attribute: %r inside material %r is corrupted (attribute data count mismatch)!",
                   (preset_attr_value, material_name))
            return False

    # check if all material texture types are in preset
    for tex_type in material_textures:

        if tex_type not in preset_mat_textures:
            lprint("W Texture type: %r from material %r not found in the assigned shader preset!", (tex_type, material_name))
            return False

    if attr_count < len(material_attributes):
        lprint("W Material %r has more attributes than needed by assigned shader preset!", (material_name,))
        return False

    if tex_count != len(material_textures):
        lprint("W Texture count mismatch between material %r and it's assigned shader preset!", (material_name,))
        return False

    return True


def _create_scs_root_object(name, loaded_variants, loaded_looks, mats_info, objects, locators, armature):
    """Creates an 'SCS Root Object' (Empty Object) for currently imported
    'SCS Game Object' and parent all import content to it.

    :param name:
    :type name: str
    :param loaded_variants: X
    :type loaded_variants: list
    :param loaded_looks: X
    :type loaded_looks: list
    :param mats_info: list of material info, one material info consists of list: [ blend_mat_name, mat_effect, original_mat_alias ]
    :type mats_info: list of list
    :param objects: X
    :type objects: list
    :param locators: X
    :type locators: list
    :param armature: Armature Object
    :type armature: bpy.types.Object
    :return: SCS Root Object
    :rtype: bpy.types.Object
    """

    context = bpy.context

    # MAKE THE 'SCS ROOT OBJECT' NAME UNIQUE
    name = _name_utils.get_unique(name, bpy.data.objects)

    # CREATE EMPTY OBJECT
    bpy.ops.object.empty_add(
        view_align=False,
        location=(0.0, 0.0, 0.0),
        # rotation=rot,
    )  # , layers=(False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,
    # False, False))

    # MAKE A PROPER SETTINGS TO THE 'SCS Game Object' OBJECT
    scs_root_object = context.active_object
    scs_root_object.name = name
    scs_root_object.scs_props.scs_root_object_export_enabled = True
    scs_root_object.scs_props.empty_object_type = 'SCS_Root'

    # print('LOD.pos: %s' % str(scs_root_object.location))
    # print('CUR.pos: %s' % str(context.space_data.cursor_location))

    # PARENTING
    if armature:

        # if armature is present we can specify our game object as animated
        scs_root_object.scs_props.scs_root_animated = "anim"

        # print('ARM.pos: %s' % str(armature.location))
        bpy.ops.object.select_all(action='DESELECT')
        armature.select = True
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
        armature.scs_props.parent_identity = scs_root_object.name

    for obj in objects:
        # print('OBJ.pos: %s' % str(object.location))
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
        obj.scs_props.parent_identity = scs_root_object.name

    for obj in locators:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
        obj.scs_props.parent_identity = scs_root_object.name

    # LOCATION
    scs_root_object.location = context.scene.cursor_location

    # MAKE ONLY 'SCS GAME OBJECT' SELECTED
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        obj.select = False
    scs_root_object.select = True
    context.scene.objects.active = scs_root_object

    # MAKE PART RECORD
    part_inventory = scs_root_object.scs_object_part_inventory
    parts_dict = _object_utils.collect_parts_on_root(scs_root_object)
    for part_name in parts_dict:
        _inventory.add_item(part_inventory, part_name)

    # MAKE VARIANT RECORD
    variant_inventory = scs_root_object.scs_object_variant_inventory
    for variant_i, variant_record in enumerate(loaded_variants):
        variant_name = variant_record[0]
        variantparts = variant_record[1]

        variant = _inventory.add_item(variant_inventory, variant_name)

        # for every variant create all of the part entries and mark them included properly
        for part in part_inventory:

            part = _inventory.add_item(variant.parts, part.name)
            if part.name in variantparts:
                part.include = True

                # cleanup generated terrain points vertex layers by variant
                for obj in parts_dict[part.name]:

                    if obj.type != "MESH":
                        continue

                    vg_to_delete = []
                    accepted_vg_nodes = {}
                    for vertex_group in obj.vertex_groups:

                        # ignore any vertex group which isn't from terrain points
                        # (others might come from skinning)
                        if _OP_consts.TerrainPoints.vg_name_prefix not in vertex_group.name:
                            continue

                        # ignore already fixed vertex group
                        if vertex_group.name.startswith(_OP_consts.TerrainPoints.vg_name_prefix):
                            continue

                        # get variant index from first 6 chars -> check PIM importer for more info
                        vg_var_index = int(vertex_group.name[:6])
                        # ignore other variant vertex groups and add them to delete list
                        if vg_var_index >= 0 and vg_var_index != variant_i:
                            vg_to_delete.append(vertex_group)
                            continue

                        # finally remove variant prefixing name if variant is not defined (-1)
                        # or index matches current one
                        vertex_group.name = vertex_group.name[6:]

                        # log accepted node index for identifying which vertex groups
                        # really have to be deleted
                        accepted_vg_nodes[vertex_group.name[-1]] = 1

                    # cleanup possible duplicates for the same node
                    # because one object anyway can not have terrain points vertex groups for multiple variants
                    while len(vg_to_delete) > 0 and len(accepted_vg_nodes) > 0:
                        curr_vg = vg_to_delete.pop()

                        # extra caution step where group can be deleted
                        # only if one of vertex groups for this node was accepted
                        if curr_vg.name[-1] in accepted_vg_nodes:
                            obj.vertex_groups.remove(curr_vg)

            else:
                part.include = False

    # MAKE LOOK RECORDS
    for look_i, look in enumerate(loaded_looks):

        look_name = look[0]
        look_mat_settings = look[1]

        # setup all the materials. NOTE: They should be already created by PIM import.
        for mat_info in mats_info:
            mat = bpy.data.materials[mat_info[0]]
            if mat_info[2] in look_mat_settings:

                # extract imported shader data
                material_effect, material_attributes, material_textures, material_section = _get_shader_data(look_mat_settings[mat_info[2]])

                # try to find suitable preset
                (preset_name, preset_section) = _material_utils.find_preset(material_effect, material_textures)

                # preset name is found & shader data are compatible with found preset
                if preset_name and _are_shader_data_compatible(preset_section, material_attributes, material_textures, mat_info[0]):

                    mat.scs_props.active_shader_preset_name = preset_name

                    if preset_section:

                        preset_effect = preset_section.get_prop_value("Effect")
                        mat.scs_props.mat_effect_name = preset_effect

                        if look_i == 0:
                            # apply default shader settings
                            _material_utils.set_shader_data_to_material(mat, preset_section, is_import=True)

                        # reapply settings from material
                        _material_utils.set_shader_data_to_material(mat, material_section, is_import=True, override_back_data=False)

                        lprint("D Using shader preset on material %r.", (mat.name,))

                    else:
                        print('''NO "preset_section"! (Shouldn't happen!)''')

                else:  # import shader directly from material and mark it as imported

                    mat.scs_props.active_shader_preset_name = "<imported>"
                    _material_utils.set_shader_data_to_material(mat, material_section, is_import=True)

                    lprint("W Using imported shader on material %r, effect: %r.", (mat.name, mat.scs_props.mat_effect_name))

                if look_i == len(loaded_looks) - 1:
                    # delete not needed data on material
                    if "scs_tex_aliases" in mat:
                        del mat["scs_tex_aliases"]

        # create new look entry on root
        bpy.ops.object.add_scs_look(look_name=look_name, instant_apply=False)

    # apply first look after everything is done
    scs_root_object.scs_props.active_scs_look = 0

    # fix scs root children objects count so it won't trigger persistent cycle
    scs_root_object.scs_cached_num_children = len(scs_root_object.children)

    return scs_root_object


def load(context, filepath, name_suffix="", suppress_reports=False):
    """

    :param context: Blender Context currently used for window_manager.update_progress and bpy_object_utils.object_data_add
    :type context: bpy.types.Context
    :param filepath: File path to be imported
    :type filepath: str
    :param name_suffix: files name suffix (exchange format is using .ef)
    :type name_suffix: str
    :param suppress_reports: True if you don't want for reports to be flushed & summaries to be printed out; False otherwise
    :type suppress_reports: bool
    :return: Return state statuses (Usually 'FINISHED')
    :rtype: set
    """
    import time

    t = time.time()
    bpy.context.window.cursor_modal_set('WAIT')
    scs_globals = _get_scs_globals()

    if not suppress_reports:
        lprint("", report_errors=-1, report_warnings=-1)  # Clear the 'error_messages' and 'warning_messages'

    collision_locators = []
    prefab_locators = []
    loaded_variants = []
    loaded_looks = []
    objects = []
    locators = []
    mats_info = []
    scs_root_object = skeleton = bones = armature = None

    # TRANSITIONAL STRUCTURES
    terrain_points = TerrainPntsTrans()

    # IMPORT PIP -> has to be loaded before PIM because of terrain points
    if scs_globals.import_pip_file:
        pip_filepath = filepath + ".pip" + name_suffix
        if os.path.isfile(pip_filepath):
            lprint('\nD PIP filepath:\n  %s', (pip_filepath,))
            # print('PIP filepath:\n  %s' % pip_filepath)
            result, prefab_locators = _pip.load(pip_filepath, terrain_points)
        else:
            lprint('\nI No PIP file.')
            # print('INFO - No PIP file.')

    # IMPORT PIM
    if scs_globals.import_pim_file or scs_globals.import_pis_file:
        pim_filepath = filepath + ".pim" + name_suffix
        if pim_filepath:
            if os.path.isfile(pim_filepath):
                lprint('\nD PIM filepath:\n  %s', (_path_utils.readable_norm(pim_filepath),))

                if pim_filepath.endswith(".pim"):
                    result, objects, locators, armature, skeleton, mats_info = _pim.load(
                        context,
                        pim_filepath,
                        terrain_points_trans=terrain_points
                    )
                elif pim_filepath.endswith(".pim.ef"):
                    result, objects, locators, armature, skeleton, mats_info = _pim_ef.load(
                        context,
                        pim_filepath,
                        terrain_points_trans=terrain_points
                    )
                else:
                    lprint("\nE Unknown PIM file extension! Shouldn't happen...")
            else:
                lprint('\nI No file found at %r!' % (_path_utils.readable_norm(pim_filepath),))
        else:
            lprint('\nI No filepath provided!')

    # IMPORT PIT
    bpy.context.scene.objects.active = None
    if scs_globals.import_pit_file:
        pit_filepath = filepath + ".pit" + name_suffix
        if os.path.isfile(pit_filepath):
            lprint('\nD PIT filepath:\n  %s', (pit_filepath,))
            # print('PIT filepath:\n  %s' % pit_filepath)
            result, loaded_variants, loaded_looks = _pit.load(pit_filepath)
        else:
            lprint('\nI No PIT file.')
            # print('INFO - No PIT file.')

    # IMPORT PIC
    if scs_globals.import_pic_file:
        pic_filepath = filepath + ".pic" + name_suffix
        if os.path.isfile(pic_filepath):
            lprint('\nD PIC filepath:\n  %s', (pic_filepath,))
            # print('PIC filepath:\n  %s' % pic_filepath)
            result, collision_locators = _pic.load(pic_filepath)
        else:
            lprint('\nI No PIC file.')
            # print('INFO - No PIC file.')

    # SETUP 'SCS GAME OBJECTS'
    for item in collision_locators:
        locators.append(item)
    for item in prefab_locators:
        locators.append(item)
    path, filename = os.path.split(filepath)
    if objects or locators or (armature and skeleton):
        scs_root_object = _create_scs_root_object(filename, loaded_variants, loaded_looks, mats_info, objects, locators, armature)

        # Additionally if user wants to have automatically set custom export path, then let him have it :P
        if scs_globals.import_preserve_path_for_export:
            relative_export_path = _path_utils.relative_path(scs_globals.scs_project_path, path)
            if path.startswith(scs_globals.scs_project_path) and relative_export_path != path:
                scs_root_object.scs_props.scs_root_object_export_filepath = relative_export_path
                scs_root_object.scs_props.scs_root_object_allow_custom_path = True
            else:
                lprint("W Can not preserve import path for export on import SCS Root %r, "
                       "as import was done from outside of current SCS Project Base Path!",
                       (scs_root_object.name,))

    # IMPORT PIS
    if scs_globals.import_pis_file:
        # pis file path is created from directory of pim file and skeleton definition inside pim header
        pis_filepath = os.path.dirname(filepath) + os.sep + skeleton
        if os.path.isfile(pis_filepath):
            lprint('\nD PIS filepath:\n  %s', (pis_filepath,))

            # strip off name suffix from skeleton path
            skeleton = skeleton[:-len(name_suffix)]

            # fill in custom data if PIS file is from other directory
            if skeleton[:-4] != scs_root_object.name:
                armature.scs_props.scs_skeleton_custom_export_dirpath = "//" + os.path.relpath(os.path.dirname(pis_filepath),
                                                                                               scs_globals.scs_project_path)
                armature.scs_props.scs_skeleton_custom_name = os.path.basename(skeleton[:-4])

            bones = _pis.load(pis_filepath, armature)
        else:
            bones = None
            lprint('\nI No PIS file.')

        # IMPORT PIA
        if scs_globals.import_pia_file and bones:
            basepath = os.path.dirname(filepath)
            # Search for PIA files in model's directory and its subdirectiories...
            lprint('\nD Searching the directory for PIA files:\n   %s', (basepath,))
            # print('\nSearching the directory for PIA files:\n   %s' % str(basepath))
            pia_files = []
            index = 0
            for root, dirs, files in os.walk(basepath):
                if not scs_globals.import_include_subdirs_for_pia:
                    if index > 0:
                        break
                # print('  root: %s - dirs: %s - files: %s' % (str(root), str(dirs), str(files)))
                for file in files:
                    if file.endswith(".pia" + name_suffix):
                        pia_filepath = os.path.join(root, file)
                        pia_files.append(pia_filepath)
                index += 1

            if len(pia_files) > 0:
                lprint('D PIA files found:')
                for pia_filepath in pia_files:
                    lprint('D %r', pia_filepath)
                # print('armature: %s\nskeleton: %r\nbones: %s\n' % (str(armature), str(skeleton), str(bones)))
                _pia.load(scs_root_object, pia_files, armature, pis_filepath, bones)
            else:
                lprint('\nI No PIA files.')

    # fix scene objects count so it won't trigger copy cycle
    bpy.context.scene.scs_cached_num_objects = len(bpy.context.scene.objects)

    # Turn on Textured Solid in 3D view...
    for bl_screen in bpy.data.screens:
        for bl_area in bl_screen.areas:
            for bl_space in bl_area.spaces:
                if bl_space.type == 'VIEW_3D':
                    bl_space.show_textured_solid = True

    # Turn on GLSL in 3D view...
    bpy.context.scene.game_settings.material_mode = 'GLSL'

    # Turn on "Frame Dropping" for animation playback...
    bpy.context.scene.use_frame_drop = True

    # FINAL FEEDBACK
    bpy.context.window.cursor_modal_restore()
    if suppress_reports:
        lprint('\nI Import compleeted in %.3f sec.', time.time() - t)
    else:
        lprint('\nI Import compleeted in %.3f sec.', time.time() - t, report_errors=True, report_warnings=True)

    return True
