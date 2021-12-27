"""Helper functions for nif import and export scripts."""

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
import re

import pyffi
from pyffi.formats.nif import NifFormat
from io_scene_mnif.utility.nif_logging import NifLog
from io_scene_mnif.utility.nif_global import NifOp

class NifCommon:
    """Abstract base class for import and export. Contains utility functions
    that are commonly used in both import and export.
    """
    
    # dictionary of bones that belong to a certain armature
    # maps NIF armature name to list of NIF bone name
    dict_armatures = {}

    # dictionary mapping bhkRigidBody objects to objects imported in Blender; 
    # we use this dictionary to set the physics constraints (ragdoll etc)
    dict_havok_objects = {}
    
    # dictionary of names, to map NIF blocks to correct Blender names
    dict_names = {}

    # dictionary of bones, maps Blender name to NIF block
    dict_blocks = {}
    
    # keeps track of names of exported blocks, to make sure they are unique
    dict_block_names = []

    # bone animation priorities (maps NiNode name to priority number);
    # priorities are set in import_kf_root and are stored into the name
    # of a NULL constraint (for lack of something better) in
    # import_armature
    dict_bone_priorities = {}

    # dictionary of materials, to reuse materials
    dict_materials = {}
    
    # dictionary of texture files, to reuse textures
    dict_textures = {}
    dict_mesh_uvlayers = []

    VERTEX_RESOLUTION = 1000
    NORMAL_RESOLUTION = 100

    EXTRA_SHADER_TEXTURES = [
        "EnvironmentMapIndex",
        "NormalMapIndex",
        "SpecularIntensityIndex",
        "EnvironmentIntensityIndex",
        "LightCubeMapIndex",
        "ShadowTextureIndex"]
    """Names (ordered by default index) of shader texture slots for
    Sid Meier's Railroads and similar games.
    """
    
    HAVOK_SCALE = 6.996

    def __init__(self, operator):
        """Common initialization functions for executing the import/export operators: """
        
        NifOp.init(operator)
        
        # print scripts info
        from . import bl_info
        niftools_ver = (".".join(str(i) for i in bl_info["version"]))
        
        NifLog.info("Executing - Niftools : Blender Nif Plugin v{0} (running on Blender {1}, PyFFI {2})".format(niftools_ver,
                                                                                                bpy.app.version_string,
                                                                                                pyffi.__version__))

        # find and store this list now of selected objects as creating new objects adds them to the selection list
        self.selected_objects = bpy.context.selected_objects[:]




    def get_n_apply_mode_from_b_blend_type(self, b_blend_type):
        if b_blend_type == "LIGHTEN":
            return NifFormat.ApplyMode.APPLY_HILIGHT
        elif b_blend_type == "MULTIPLY":
            return NifFormat.ApplyMode.APPLY_HILIGHT2
        elif b_blend_type == "MIX":
            return NifFormat.ApplyMode.APPLY_MODULATE
        
        NifLog.warn("Unsupported blend type ({0}) in material, using apply mode APPLY_MODULATE".format(b_blend_type))
        return NifFormat.ApplyMode.APPLY_MODULATE
