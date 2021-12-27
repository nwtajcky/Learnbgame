'''Script to import/export all the skeleton related objects.'''

# ***** BEGIN LICENSE BLOCK *****
# 
# Copyright © 2005-2015, NIF File Format Library and Tools contributors.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
# 
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
# 
#    * Neither the name of the NIF File Format Library and Tools
#      project nor the names of its contributors may be used to endorse
#      or promote products derived from this software without specific
#      prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# ***** END LICENSE BLOCK *****

import bpy
import mathutils
from io_scene_mnif.modules import armature
from io_scene_mnif.utility import nif_utils
from io_scene_mnif.utility.nif_global import NifOp
from io_scene_mnif.utility.nif_logging import NifLog

from pyffi.formats.nif import NifFormat


class Armature():
    

    def __init__(self, parent):
        self.nif_export = parent
    
    def export_bones(self, arm, parent_block):
        """Export the bones of an armature."""
        # the armature was already exported as a NiNode
        # now we must export the armature's bones
        assert( arm.type == 'ARMATURE' )
        
        # find the root bones
        # list of all bones
        bones = arm.data.bones.values()
        
        # maps bone names to NiNode blocks
        bones_node = {}

        # here all the bones are added
        # first create all bones with their keyframes
        # and then fix the links in a second run

        # ok, let's create the bone NiNode blocks
        for bone in bones:
            # create a new block for this bone
            node = self.nif_export.objecthelper.create_ninode(bone)
            # doing bone map now makes linkage very easy in second run
            bones_node[bone.name] = node

            # add the node and the keyframe for this bone
            node.name = self.nif_export.objecthelper.get_full_name(bone.name)
            
            if (bone.niftools_bone.boneflags != 0):
                node.flags = bone.niftools_bone.boneflags
            else:
                if NifOp.props.game in ('OBLIVION', 'FALLOUT_3', 'SKYRIM'):
                    # default for Oblivion bones
                    # note: bodies have 0x000E, clothing has 0x000F
                    node.flags = 0x000E
                elif NifOp.props.game in ('CIVILIZATION_IV', 'EMPIRE_EARTH_II'):
                    if bone.children:
                        # default for Civ IV/EE II bones with children
                        node.flags = 0x0006
                    else:
                        # default for Civ IV/EE II final bones
                        node.flags = 0x0016
                elif NifOp.props.game in ('DIVINITY_2',):
                    if bone.children:
                        # default for Div 2 bones with children
                        node.flags = 0x0186
                    elif bone.name.lower()[-9:] == 'footsteps':
                        node.flags = 0x0116
                    else:
                        # default for Div 2 final bones
                        node.flags = 0x0196
                else:
                    node.flags = 0x0002 # default for Morrowind bones
            # rest pose
            self.nif_export.objecthelper.set_object_matrix(bone, node)

            # per-node animation
            self.nif_export.animationhelper.export_keyframes(node, arm, bone)

            # does bone have priority value in NULL constraint?
            for constr in arm.pose.bones[bone.name].constraints:
                # yes! store it for reference when creating the kf file
                if constr.name[:9].lower() == "priority:":
                    self.nif_export.dict_bone_priorities[
                        armature.get_bone_name_for_nif(bone.name)
                        ] = int(constr.name[9:])

        # now fix the linkage between the blocks
        for bone in bones:
            # link the bone's children to the bone
            NifLog.debug("Linking children of bone {0}".format(bone.name))
            for child in bone.children:
                bones_node[bone.name].add_child(bones_node[child.name])
            # if it is a root bone, link it to the armature
            if not bone.parent:
                parent_block.add_child(bones_node[bone.name])
                
    
    def export_children(self, b_obj, parent_block):
        """Export all children of blender object b_obj as children of
        parent_block."""
        # loop over all obj's children
        for b_obj_child in b_obj.children:
            # is it a regular node?
            if b_obj_child.type in ['MESH', 'EMPTY', 'ARMATURE']:
                if (b_obj.type != 'ARMATURE'):
                    # not parented to an armature
                    self.nif_export.objecthelper.export_node(b_obj_child, parent_block, b_obj_child.name)
                else:
                    # this object is parented to an armature
                    # we should check whether it is really parented to the
                    # armature using vertex weights
                    # or whether it is parented to some bone of the armature
                    parent_bone_name = b_obj_child.parent_bone
                    if parent_bone_name == "":
                        self.nif_export.objecthelper.export_node(b_obj_child, parent_block, b_obj_child.name)
                    else:
                        # we should parent the object to the bone instead of
                        # to the armature
                        # so let's find that bone!
                        nif_bone_name = self.nif_export.objecthelper.get_full_name(parent_bone_name)
                        for bone_block in self.nif_export.dict_blocks:
                            if isinstance(bone_block, NifFormat.NiNode) and \
                                bone_block.name.decode() == nif_bone_name:
                                # ok, we should parent to block
                                # instead of to parent_block
                                # two problems to resolve:
                                #   - blender bone matrix is not the exported
                                #     bone matrix!
                                #   - blender objects parented to bone have
                                #     extra translation along the Y axis
                                #     with length of the bone ("tail")
                                # this is handled in the get_object_srt function
                                self.nif_export.objecthelper.export_node(b_obj_child, bone_block, b_obj_child.name)
                                break
                        else:
                            assert(False) # BUG!
   
