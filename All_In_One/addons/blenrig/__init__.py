# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
#
# ##### ACKNOWLEDGEMENTS #####
#
# BlenRig by: Juan Pablo Bouza
# Initial script programming: Bart Crouch
# Current maintainer and developer: Juan Pablo Bouza, Sav Martin
#
# Synoptic Panel/Rig Picker based on work by: Salvador Artero     
#
# Special thanks on python advice to: Campbell Barton, Bassam Kurdali, Daniel Salazar, CodeManX, Patrick Crawford, Gabriel Caraballo, Ines Almeida
# Special thanks for feedback and ideas to: Jorge Rausch, Gabriel Sabsay, Pablo Vázquez, Hjalti Hjálmarsson, Beorn Leonard, Sarah Laufer
#
# #########################################################################################################



bl_info = {
    'name': 'BlenRig 5',
    'author': 'Juan Pablo Bouza , Sav Martin',
    'version': (1,0,4),
    'blender': (2, 80, 0),
    'location': 'Armature, Object and Lattice properties, View3d tools panel, Armature Add menu',
    'description': 'BlenRig 5 rigging system',
    'wiki_url': 'https://cloud.blender.org/p/blenrig/56966411c379cf44546120e8',
    'tracker_url': 'https://gitlab.com/jpbouza/BlenRig/issues',
    "category": "Learnbgame",
}


import bpy
import os

from bpy.props import FloatProperty, IntProperty, BoolProperty

######### Load Rig Functions ##########
from .rig_functions import (
    bone_auto_hide,
    reproportion_toggle,
    rig_toggles,
    toggle_face_drivers,
    toggle_flex_drivers,
    toggle_body_drivers
)

######### Update Function for Properties ##########

def prop_update(self, context):
    bone_auto_hide(context)

def reprop_update(self, context):
    reproportion_toggle(context)

def rig_toggles_update(self, context):
    rig_toggles(context)

def optimize_face(self, context):
    toggle_face_drivers(context)

def optimize_flex(self, context):
    toggle_flex_drivers(context)

def optimize_body(self, context):
    toggle_body_drivers(context)

######### Handler for update on load and frame change #########

from bpy.app.handlers import persistent

@persistent
def load_reprop_handler(context):  
    bone_auto_hide(context)      
    reproportion_toggle(context)
    rig_toggles(context)  
    
@persistent
def load_handler(context):  
    bone_auto_hide(context)          

bpy.app.handlers.load_post.append(load_reprop_handler)
bpy.app.handlers.frame_change_post.append(load_handler)


######### Properties Creation ############

#FK/IK

bpy.types.PoseBone.ik_head = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="IK/FK Toggle",
    update=prop_update,
    name="ik_head"
)

bpy.types.PoseBone.ik_torso = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,
    options={'ANIMATABLE'},
    description="IK/FK Toggle",
    update=prop_update,
    name="ik_torso"
)
bpy.types.PoseBone.inv_torso = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Invert Torso Hierarchy",
    update=prop_update,
    name="inv_torso"
)
bpy.types.PoseBone.ik_arm_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="IK/FK Toggle",
    update=prop_update,
    name="ik_arm_L"
)
bpy.types.PoseBone.ik_arm_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="IK/FK Toggle",
    update=prop_update,
    name="ik_arm_R"
)
bpy.types.PoseBone.ik_leg_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="IK/FK Toggle",
    update=prop_update,
    name="ik_leg_L"
)
bpy.types.PoseBone.ik_toes_all_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="IK/FK Toggle",
    update=prop_update,
    name="ik_toes_all_L"
)
bpy.types.PoseBone.ik_leg_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="IK/FK Toggle",
    update=prop_update,
    name="ik_leg_R"
)
bpy.types.PoseBone.ik_toes_all_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="IK/FK Toggle",
    update=prop_update,
    name="ik_toes_all_R"
)
bpy.types.PoseBone.ik_fing_ind_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="IK/FK Toggle",
    update=prop_update,
    name="ik_fing_ind_L"
)
bpy.types.PoseBone.ik_fing_mid_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="IK/FK Toggle",
    update=prop_update,
    name="ik_fing_mid_L"
)
bpy.types.PoseBone.ik_fing_ring_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="IK/FK Toggle",
    update=prop_update,
    name="ik_fing_mid_L"
)
bpy.types.PoseBone.ik_fing_lit_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="IK/FK Toggle",
    update=prop_update,
    name="ik_fing_lit_L"
)
bpy.types.PoseBone.ik_fing_thumb_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="IK/FK Toggle",
    update=prop_update,
    name="ik_fing_thumb_L"
)
bpy.types.PoseBone.ik_fing_ind_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="IK/FK Toggle",
    update=prop_update,
    name="ik_fing_ind_R"
)
bpy.types.PoseBone.ik_fing_mid_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="IK/FK Toggle",
    update=prop_update,
    name="ik_fing_mid_R"
)
bpy.types.PoseBone.ik_fing_ring_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="IK/FK Toggle",
    update=prop_update,
    name="ik_fing_mid_R"
)
bpy.types.PoseBone.ik_fing_lit_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="IK/FK Toggle",
    update=prop_update,
    name="ik_fing_lit_R"
)
bpy.types.PoseBone.ik_fing_thumb_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="IK/FK Toggle",
    update=prop_update,
    name="ik_fing_thumb_R"
)
bpy.types.PoseBone.ik_fing_all_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="IK/FK Toggle",
    update=prop_update,
    name="ik_fing_all_R"
)
bpy.types.PoseBone.ik_fing_all_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="IK/FK Toggle",
    update=prop_update,
    name="ik_fing_all_L"
)

# HINGE

bpy.types.PoseBone.hinge_head = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Isolate Rotation",
    update=prop_update,
    name="hinge_head"
)
bpy.types.PoseBone.hinge_neck = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Isolate Rotation",
    update=prop_update,
    name="hinge_neck"
)
bpy.types.PoseBone.hinge_arm_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Isolate Rotation",
    update=prop_update,
    name="hinge_arm_L"
)
bpy.types.PoseBone.hinge_arm_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Isolate Rotation",
    update=prop_update,
    name="hinge_arm_R"
)
bpy.types.PoseBone.hinge_hand_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Isolate Rotation",
    update=prop_update,
    name="hinge_hand_L"
)
bpy.types.PoseBone.hinge_hand_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Isolate Rotation",
    update=prop_update,
    name="hinge_hand_R"
)
bpy.types.PoseBone.hinge_fing_ind_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Isolate Rotation",
    update=prop_update,
    name="hinge_fing_ind_L"
)
bpy.types.PoseBone.hinge_fing_mid_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Isolate Rotation",
    update=prop_update,
    name="hinge_fing_mid_L"
)
bpy.types.PoseBone.hinge_fing_ring_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Isolate Rotation",
    update=prop_update,
    name="hinge_fing_mid_L"
)
bpy.types.PoseBone.hinge_fing_lit_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Isolate Rotation",
    update=prop_update,
    name="hinge_fing_lit_L"
)
bpy.types.PoseBone.hinge_fing_thumb_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Isolate Rotation",
    update=prop_update,
    name="hinge_fing_thumb_L"
)
bpy.types.PoseBone.hinge_fing_ind_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Isolate Rotation",
    update=prop_update,
    name="hinge_fing_ind_R"
)
bpy.types.PoseBone.hinge_fing_mid_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Isolate Rotation",
    update=prop_update,
    name="hinge_fing_mid_R"
)
bpy.types.PoseBone.hinge_fing_ring_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Isolate Rotation",
    update=prop_update,
    name="hinge_fing_mid_R"
)
bpy.types.PoseBone.hinge_fing_lit_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Isolate Rotation",
    update=prop_update,
    name="hinge_fing_lit_R"
)
bpy.types.PoseBone.hinge_fing_thumb_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Isolate Rotation",
    update=prop_update,
    name="hinge_fing_thumb_R"
)
bpy.types.PoseBone.hinge_fing_all_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Isolate Rotation",
    update=prop_update,
    name="hinge_fing_all_R"
)
bpy.types.PoseBone.hinge_fing_all_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Isolate Rotation",
    update=prop_update,
    name="hinge_fing_all_L"
)
bpy.types.PoseBone.hinge_leg_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Isolate Rotation",
    update=prop_update,
    name="hinge_leg_L"
)
bpy.types.PoseBone.hinge_toes_all_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Isolate Rotation",
    update=prop_update,
    name="hinge_toes_all_L"
)
bpy.types.PoseBone.hinge_leg_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Isolate Rotation",
    update=prop_update,
    name="hinge_leg_R"
)           
bpy.types.PoseBone.hinge_toes_all_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Isolate Rotation",
    update=prop_update,
    name="hinge_toes_all_R"
)

#Stretchy IK

bpy.types.PoseBone.toon_head = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Stretchy IK Toggle",
    update=prop_update,
    name="toon_head"
)   

bpy.types.PoseBone.toon_torso = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Stretchy IK Toggle",
    update=prop_update,
    name="toon_torso"
) 

bpy.types.PoseBone.toon_arm_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Stretchy IK Toggle",
    update=prop_update,
    name="toon_arm_L"
) 

bpy.types.PoseBone.toon_arm_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Stretchy IK Toggle",
    update=prop_update,
    name="toon_arm_R"
) 

bpy.types.PoseBone.toon_leg_L = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Stretchy IK Toggle",
    update=prop_update,
    name="toon_leg_L"
) 

bpy.types.PoseBone.toon_leg_R = FloatProperty(
    default=0.000,
    min=0.000,
    max=1.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Stretchy IK Toggle",
    update=prop_update,
    name="toon_leg_R"
) 

# LOOK SWITCH
bpy.types.PoseBone.look_switch = FloatProperty(
    default=3.000,
    min=0.000,
    max=3.000,
    precision=0,
    step=100,   
    options={'ANIMATABLE'},
    description="Target of Eyes",
    update=prop_update,
    name="look_switch"
) 

# REPROPORTION
bpy.types.Armature.reproportion = BoolProperty(
    default=0,
    description="Toggle Reproportion Mode",
    update=reprop_update,
    name="reproportion"
) 
# TOGGLE_FACE_DRIVERS
bpy.types.Armature.toggle_face_drivers = BoolProperty(
    default=1,
    description="Toggle Face Riggin Drivers",
    update=optimize_face,
    name="toggle_face_drivers"
) 
# TOGGLE_FLEX_DRIVERS
bpy.types.Armature.toggle_flex_drivers = BoolProperty(
    default=1,
    description="Toggle Flex Scaling",
    update=optimize_flex,
    name="toggle_flex_drivers"
) 
# TOGGLE_BODY_DRIVERS
bpy.types.Armature.toggle_body_drivers = BoolProperty(
    default=1,
    description="Toggle Body Rigging Drivers",
    update=optimize_body,
    name="toggle_body_drivers"
) 
# TOGGLES
bpy.types.PoseBone.toggle_fingers_L = BoolProperty(
    default=0,
    description="Toggle fingers in rig",
    update=rig_toggles_update,
    name="toggle_fingers_L"
) 

bpy.types.PoseBone.toggle_toes_L = BoolProperty(
    default=0,
    description="Toggle toes in rig",
    update=rig_toggles_update,
    name="toggle_toes_L"
) 

bpy.types.PoseBone.toggle_fingers_R = BoolProperty(
    default=0,
    description="Toggle fingers in rig",
    update=rig_toggles_update,
    name="toggle_fingers_R"
) 

bpy.types.PoseBone.toggle_toes_R = BoolProperty(
    default=0,
    description="Toggle toes in rig",
    update=rig_toggles_update,
    name="toggle_toes_R"
) 
                   
####### Load BlenRig 5 Controls Panel
from .ui_panel_controls import BLENRIG_PT_BlenRig_5_Interface

####### Load BlenRig 5 Rigging Panel
from .ui_panel_rigging import (
    BLENRIG_PT_BlenRig_5_rigging_panel,
    BLENRIG_PT_BlenRig_5_mesh_panel,
    BLENRIG_PT_BlenRig_5_lattice_panel
    )

####### Load BlenRig 5 Bake Operators
from .ops_baking import (
    ARMATURE_OT_mesh_pose_baker,
    ARMATURE_OT_reset_hooks,
    ARMATURE_OT_reset_deformers,
    ARMATURE_OT_armature_baker,
    ARMATURE_OT_reset_constraints
    )                          

####### Load BlenRig 5 Alignment Operators
from .ops_alignment import (
    Operator_BlenRig_Fix_Misaligned_Bones,
    Operator_BlenRig_Auto_Bone_Roll,
    Operator_BlenRig_Custom_Bone_Roll,
    Operator_BlenRig_Store_Roll_Angles,
    Operator_BlenRig_Restore_Roll_Angles,
    Operator_BlenRig_Reset_Dynamic
    )                          

####### Load BlenRig 5 Snapping Operators
from .ops_snapping import (
    Operator_Torso_Snap_FK_IK, 
    Operator_Torso_Snap_IK_FK, 
    Operator_Head_Snap_FK_IK,
    Operator_Head_Snap_IK_FK,
    Operator_Torso_Snap_UP_INV,
    Operator_Torso_Snap_INV_UP,
    Operator_Arm_L_Snap_FK_IK,
    Operator_Arm_L_Snap_IK_FK,
    Operator_Arm_R_Snap_FK_IK,
    Operator_Arm_R_Snap_IK_FK,
    Operator_Leg_L_Snap_FK_IK,
    Operator_Leg_L_Snap_IK_FK,
    Operator_Leg_R_Snap_FK_IK,
    Operator_Leg_R_Snap_IK_FK
    )
    
####### Load BlenRig 5 Body Picker Operators
# Biped
from .ops_picker_body import (
    Operator_Head_Stretch,
    Operator_Head_Toon,   
    Operator_Head_Top_Ctrl,  
    Operator_Head_Mid_Ctrl,          
    Operator_Head_Mid_Curve, 
    Operator_Mouth_Str_Ctrl,        
    Operator_Head_FK, 
    Operator_Head_IK,   
    Operator_Neck_4_Toon, 
    Operator_Face_Toon_Up,      
    Operator_Face_Toon_Mid, 
    Operator_Face_Toon_Low,  
    Operator_Neck_3, 
    Operator_Neck_2,
    Operator_Neck_1,    
    Operator_Neck_3_Toon,  
    Operator_Neck_2_Toon, 
    Operator_Neck_Ctrl,  
    Operator_Shoulder_L, 
    Operator_Shoulder_R, 
    Operator_Shoulder_Rot_L, 
    Operator_Shoulder_Rot_R, 
    Operator_Clavi_Toon_L, 
    Operator_Clavi_Toon_R, 
    Operator_Head_Scale, 
    Operator_Arm_Toon_L, 
    Operator_Elbow_Pole_L, 
    Operator_Forearm_Toon_L, 
    Operator_Arm_Scale_L, 
    Operator_Arm_FK_L, 
    Operator_Arm_IK_L, 
    Operator_Elbow_Toon_L, 
    Operator_Forearm_FK_L, 
    Operator_Forearm_IK_L, 
    Operator_Hand_Toon_L,    
    Operator_Arm_Toon_R, 
    Operator_Elbow_Pole_R, 
    Operator_Forearm_Toon_R, 
    Operator_Arm_Scale_R, 
    Operator_Arm_FK_R, 
    Operator_Arm_IK_R, 
    Operator_Elbow_Toon_R, 
    Operator_Forearm_FK_R, 
    Operator_Forearm_IK_R, 
    Operator_Hand_Toon_R,  
    Operator_Torso_Ctrl, 
    Operator_Spine_3,   
    Operator_Spine_2,  
    Operator_Spine_1,  
    Operator_Master_Torso_Pivot_Point,   
    Operator_Master_Torso,   
    Operator_Pelvis_Ctrl,                               
    Operator_Spine_4_Toon,                                         
    Operator_Spine_3_Toon,   
    Operator_Spine_2_Toon,   
    Operator_Spine_1_Toon,   
    Operator_Pelvis_Toon,   
    Operator_Spine_3_Inv_Ctrl,  
    Operator_Hand_Roll_L, 
    Operator_Fing_Spread_L,  
    Operator_Hand_IK_Pivot_Point_L,     
    Operator_Hand_IK_Ctrl_L,   
    Operator_Hand_FK_L,                                                   
    Operator_Fing_Lit_Ctrl_L,  
    Operator_Fing_Lit_2_L, 
    Operator_Fing_Lit_3_L,  
    Operator_Fing_Lit_4_L,  
    Operator_Fing_Ring_Ctrl_L,  
    Operator_Fing_Ring_2_L, 
    Operator_Fing_Ring_3_L,  
    Operator_Fing_Ring_4_L,   
    Operator_Fing_Mid_Ctrl_L,  
    Operator_Fing_Mid_2_L, 
    Operator_Fing_Mid_3_L,  
    Operator_Fing_Mid_4_L,  
    Operator_Fing_Ind_Ctrl_L,  
    Operator_Fing_Ind_2_L, 
    Operator_Fing_Ind_3_L,  
    Operator_Fing_Ind_4_L,  
    Operator_Fing_Thumb_Ctrl_L,  
    Operator_Fing_Thumb_2_L, 
    Operator_Fing_Thumb_3_L,  
    Operator_Fing_Thumb_1_L,   
    Operator_Fing_Lit_IK_L,  
    Operator_Fing_Ring_IK_L, 
    Operator_Fing_Mid_IK_L, 
    Operator_Fing_Ind_IK_L, 
    Operator_Fing_Thumb_IK_L,   
    Operator_Hand_Close_L,        
    Operator_Hand_Roll_R, 
    Operator_Fing_Spread_R,  
    Operator_Hand_IK_Pivot_Point_R,     
    Operator_Hand_IK_Ctrl_R,   
    Operator_Hand_FK_R,                                                   
    Operator_Fing_Lit_Ctrl_R,  
    Operator_Fing_Lit_2_R, 
    Operator_Fing_Lit_3_R,  
    Operator_Fing_Lit_4_R,  
    Operator_Fing_Ring_Ctrl_R,  
    Operator_Fing_Ring_2_R, 
    Operator_Fing_Ring_3_R,  
    Operator_Fing_Ring_4_R,   
    Operator_Fing_Mid_Ctrl_R,  
    Operator_Fing_Mid_2_R, 
    Operator_Fing_Mid_3_R,  
    Operator_Fing_Mid_4_R,  
    Operator_Fing_Ind_Ctrl_R,  
    Operator_Fing_Ind_2_R, 
    Operator_Fing_Ind_3_R,  
    Operator_Fing_Ind_4_R,  
    Operator_Fing_Thumb_Ctrl_R,  
    Operator_Fing_Thumb_2_R, 
    Operator_Fing_Thumb_3_R,  
    Operator_Fing_Thumb_1_R,   
    Operator_Fing_Lit_IK_R,  
    Operator_Fing_Ring_IK_R, 
    Operator_Fing_Mid_IK_R, 
    Operator_Fing_Ind_IK_R, 
    Operator_Fing_Thumb_IK_R,  
    Operator_Hand_Close_R,        
    Operator_Thigh_Toon_L,   
    Operator_Knee_Pole_L,  
    Operator_Shin_Toon_L,  
    Operator_Pelvis_Toon_L,  
    Operator_Leg_Scale_L,    
    Operator_Thigh_FK_L,  
    Operator_Thigh_IK_L,  
    Operator_Knee_Toon_L,  
    Operator_Shin_FK_L,  
    Operator_Shin_IK_L,  
    Operator_Foot_Toon_L,    
    Operator_Thigh_Toon_R,   
    Operator_Knee_Pole_R,  
    Operator_Shin_Toon_R,  
    Operator_Pelvis_Toon_R,  
    Operator_Leg_Scale_R,    
    Operator_Thigh_FK_R,  
    Operator_Thigh_IK_R,  
    Operator_Knee_Toon_R,  
    Operator_Shin_FK_R,  
    Operator_Shin_IK_R,  
    Operator_Foot_Toon_R,  
    Operator_Toe_2_FK_L,  
    Operator_Toe_Roll_1_L,   
    Operator_Toe_1_FK_L,   
    Operator_Toe_Roll_2_L,   
    Operator_Foot_L,   
    Operator_Foot_Roll_Ctrl_L,   
    Operator_Toe_Big_Ctrl_L,  
    Operator_Toe_Big_2_L,  
    Operator_Toe_Big_3_L,  
    Operator_Toe_Big_IK_L,  
    Operator_Toe_Ind_Ctrl_L, 
    Operator_Toe_Ind_2_L,  
    Operator_Toe_Ind_3_L,  
    Operator_Toe_Ind_4_L,  
    Operator_Toe_Ind_IK_L,  
    Operator_Toe_Mid_Ctrl_L,  
    Operator_Toe_Mid_2_L,  
    Operator_Toe_Mid_3_L,  
    Operator_Toe_Mid_4_L,  
    Operator_Toe_Mid_IK_L,  
    Operator_Toe_Fourth_Ctrl_L,  
    Operator_Toe_Fourth_2_L,  
    Operator_Toe_Fourth_3_L,  
    Operator_Toe_Fourth_4_L,  
    Operator_Toe_Fourth_IK_L,  
    Operator_Toe_Lit_Ctrl_L,  
    Operator_Toe_Lit_2_L,  
    Operator_Toe_Lit_3_L,   
    Operator_Toe_Lit_IK_L,  
    Operator_Toes_Spread_L,    
    Operator_Toes_IK_Ctrl_Mid_L,     
    Operator_Toes_IK_Ctrl_L,        
    Operator_Sole_Ctrl_L,   
    Operator_Sole_Pivot_Point_L,      
    Operator_Toe_2_FK_R,  
    Operator_Toe_Roll_1_R,   
    Operator_Toe_1_FK_R,   
    Operator_Toe_Roll_2_R,   
    Operator_Foot_R,   
    Operator_Foot_Roll_Ctrl_R,  
    Operator_Toe_Big_Ctrl_R,  
    Operator_Toe_Big_2_R,  
    Operator_Toe_Big_3_R,  
    Operator_Toe_Big_IK_R,  
    Operator_Toe_Ind_Ctrl_R, 
    Operator_Toe_Ind_2_R,  
    Operator_Toe_Ind_3_R,  
    Operator_Toe_Ind_4_R,  
    Operator_Toe_Ind_IK_R,  
    Operator_Toe_Mid_Ctrl_R,  
    Operator_Toe_Mid_2_R,  
    Operator_Toe_Mid_3_R,  
    Operator_Toe_Mid_4_R,  
    Operator_Toe_Mid_IK_R,  
    Operator_Toe_Fourth_Ctrl_R,  
    Operator_Toe_Fourth_2_R,  
    Operator_Toe_Fourth_3_R,  
    Operator_Toe_Fourth_4_R,  
    Operator_Toe_Fourth_IK_R,  
    Operator_Toe_Lit_Ctrl_R,  
    Operator_Toe_Lit_2_R,  
    Operator_Toe_Lit_3_R,   
    Operator_Toe_Lit_IK_R,  
    Operator_Toes_Spread_R,    
    Operator_Toes_IK_Ctrl_Mid_R,     
    Operator_Toes_IK_Ctrl_R,                                                       
    Operator_Sole_Ctrl_R,   
    Operator_Sole_Pivot_Point_R,    
    Operator_Master,   
    Operator_Master_Pivot_Point,                                               
    Operator_Look, 
    Operator_Look_L, 
    Operator_Look_R,        
    Operator_Zoom_Selected
    )
    
#Quadruped
from .ops_picker_body import (
    Operator_Ankle_Toon_L, 
    Operator_Carpal_FK_L, 
    Operator_Carpal_IK_L,  
    Operator_Carpal_Toon_L,      
    Operator_Ankle_Toon_R, 
    Operator_Carpal_FK_R, 
    Operator_Carpal_IK_R, 
    Operator_Carpal_Toon_R,      
    Operator_Hock_Toon_L, 
    Operator_Tarsal_FK_L, 
    Operator_Tarsal_IK_L, 
    Operator_Tarsal_Toon_L,        
    Operator_Hock_Toon_R, 
    Operator_Tarsal_FK_R, 
    Operator_Tarsal_IK_R,
    Operator_Tarsal_Toon_R,  
    Operator_Fing_2_FK_L,     
    Operator_Fing_1_FK_L,   
    Operator_Fing_Roll_2_L,    
    Operator_Fing_Roll_1_L,      
    Operator_Hand_L,    
    Operator_Hand_Roll_Ctrl_L,    
    Operator_Hand_Sole_Ctrl_L,    
    Operator_Hand_Sole_Pivot_Point_L,     
    Operator_Fing_2_FK_R,     
    Operator_Fing_1_FK_R,   
    Operator_Fing_Roll_2_R,    
    Operator_Fing_Roll_1_R,      
    Operator_Hand_R,    
    Operator_Hand_Roll_Ctrl_R,    
    Operator_Hand_Sole_Ctrl_R,    
    Operator_Hand_Sole_Pivot_Point_R
    )       
    
####### Load BlenRig 5 Face Picker Operators
from .ops_picker_face import (
    Operator_Ear_Up_R,
    Operator_Ear_R,
    Operator_Ear_Low_R,
    Operator_Brow_Ctrl_1_R,
    Operator_Brow_Ctrl_2_R,
    Operator_Brow_Ctrl_3_R,
    Operator_Brow_Ctrl_4_R,
    Operator_Brow_Ctrl_R,
    Operator_Toon_Brow_R,
    Operator_Ear_Up_L,
    Operator_Ear_L,
    Operator_Ear_Low_L,
    Operator_Brow_Ctrl_1_L,
    Operator_Brow_Ctrl_2_L,
    Operator_Brow_Ctrl_3_L,
    Operator_Brow_Ctrl_4_L,
    Operator_Brow_Ctrl_L,
    Operator_Toon_Brow_L,
    Operator_Frown_Ctrl,
    Operator_Nose_Bridge_1_Ctrl,
    Operator_Eyelid_Up_Ctrl_R,
    Operator_Eyelid_Up_Ctrl_3_R,
    Operator_Eyelid_Up_Ctrl_2_R,
    Operator_Eyelid_Up_Ctrl_1_R,
    Operator_Toon_Eye_Out_R,
    Operator_Toon_Eye_Up_R,
    Operator_Pupil_Ctrl_R,
    Operator_Eye_Ctrl_R,
    Operator_Iris_Ctrl_R,
    Operator_Toon_Eye_In_R,
    Operator_Toon_Eye_Low_R,
    Operator_Eyelid_Ctrl_Out_R,
    Operator_Eyelid_Low_Ctrl_3_R,
    Operator_Eyelid_Low_Ctrl_2_R,
    Operator_Eyelid_Low_Ctrl_1_R,
    Operator_Eyelid_Ctrl_In_R,
    Operator_Eyelid_Low_Ctrl_R,
    Operator_Eyelid_Up_Ctrl_L,
    Operator_Eyelid_Up_Ctrl_3_L,
    Operator_Eyelid_Up_Ctrl_2_L,
    Operator_Eyelid_Up_Ctrl_1_L,
    Operator_Toon_Eye_Out_L,
    Operator_Toon_Eye_Up_L,
    Operator_Pupil_Ctrl_L,
    Operator_Eye_Ctrl_L,
    Operator_Iris_Ctrl_L,
    Operator_Toon_Eye_In_L,
    Operator_Toon_Eye_Low_L,
    Operator_Eyelid_Ctrl_Out_L,
    Operator_Eyelid_Low_Ctrl_3_L,
    Operator_Eyelid_Low_Ctrl_2_L,
    Operator_Eyelid_Low_Ctrl_1_L,
    Operator_Eyelid_Ctrl_In_L,
    Operator_Eyelid_Low_Ctrl_L,
    Operator_Nose_Bridge_2_Ctrl,
    Operator_Nose_Frown_Ctrl_R,
    Operator_Nose_Frown_Ctrl_L,
    Operator_Cheek_Ctrl_R,
    Operator_Cheek_Ctrl_3_R,
    Operator_Cheek_Ctrl_2_R,
    Operator_Cheek_Ctrl_1_R,
    Operator_Cheek2_Ctrl_3_R,
    Operator_Cheek2_Ctrl_2_R,
    Operator_Cheek2_Ctrl_1_R,
    Operator_Lip_Up3_Ctrl_3_R,
    Operator_Lip_Up3_Ctrl_2_R,
    Operator_Lip_Up3_Ctrl_1_R,
    Operator_Lip_Up2_Ctrl_3_R,
    Operator_Lip_Up2_Ctrl_2_R,
    Operator_Lip_Up2_Ctrl_1_R,
    Operator_Cheek_Ctrl_L,
    Operator_Cheek_Ctrl_3_L,
    Operator_Cheek_Ctrl_2_L,
    Operator_Cheek_Ctrl_1_L,
    Operator_Cheek2_Ctrl_3_L,
    Operator_Cheek2_Ctrl_2_L,
    Operator_Cheek2_Ctrl_1_L,
    Operator_Lip_Up3_Ctrl_3_L,
    Operator_Lip_Up3_Ctrl_2_L,
    Operator_Lip_Up3_Ctrl_1_L,
    Operator_Lip_Up2_Ctrl_3_L,
    Operator_Lip_Up2_Ctrl_2_L,
    Operator_Lip_Up2_Ctrl_1_L,
    Operator_Nostril_Ctrl_R,
    Operator_Nose_Ctrl,
    Operator_Nostril_Ctrl_L,
    Operator_Lip_Up3_Ctrl_Mid,
    Operator_Lip_Up3_Ctrl,
    Operator_Lip_Up2_Ctrl_Mid,
    Operator_lip_up2_ctrl,
    Operator_Cheek_Ctrl_4_R,
    Operator_Cheek2_Ctrl_4_R,
    Operator_Lip_Up3_Ctrl_4_R,
    Operator_Lip_Up2_Ctrl_4_R,
    Operator_Cheek_Ctrl_4_L,
    Operator_Cheek2_Ctrl_4_L,
    Operator_Lip_Up3_Ctrl_4_L,
    Operator_Lip_Up2_Ctrl_4_L,
    Operator_Mouth_Mstr_Up,
    Operator_Mouth_Corner_R,
    Operator_Mouth_Corner_L,
    Operator_Lip_Up_Ctrl,
    Operator_Lip_Up_Ctrl_Collision,
    Operator_Lip_Up_Ctrl_3_R,
    Operator_Lip_Up_Ctrl_2_R,
    Operator_Lip_Up_Ctrl_1_R,
    Operator_Lip_Up_Ctrl_Mid,
    Operator_Lip_Up_Ctrl_3_L,
    Operator_Lip_Up_Ctrl_2_L,
    Operator_Lip_Up_Ctrl_1_L,
    Operator_Mouth_Up_Ctrl,
    Operator_Lip_Up_Ctrl_4_R,
    Operator_Lip_Up_Ctrl_4_L,
    Operator_Mouth_Ctrl,
    Operator_Mouth_Low_Ctrl,
    Operator_Lip_Low_Ctrl_3_R,
    Operator_Lip_Low_Ctrl_2_R,
    Operator_Lip_Low_Ctrl_1_R,
    Operator_Lip_Low_Ctrl_Mid,
    Operator_Lip_Low_Ctrl_1_L,
    Operator_Lip_Low_Ctrl_2_L,
    Operator_Lip_Low_Ctrl_3_L,
    Operator_Lip_Low_Ctrl_Collision,
    Operator_Lip_Low_Ctrl,
    Operator_Mouth_Mstr_Low,
    Operator_Mouth_Mstr_Ctrl,
    Operator_Mouth_Frown_Ctrl_R,
    Operator_Lip_Low2_Ctrl_3_R,
    Operator_Lip_Low2_Ctrl_2_R,
    Operator_Lip_Low2_Ctrl_1_R,
    Operator_Lip_Low3_Ctrl_3_R,
    Operator_Lip_Low3_Ctrl_2_R,
    Operator_Lip_Low3_Ctrl_1_R,
    Operator_Cheek_Ctrl_5_R,
    Operator_Chin_Ctrl_3_R,
    Operator_Chin_Ctrl_2_R,
    Operator_Chin_Ctrl_1_R,
    Operator_Mouth_Frown_Ctrl_L,
    Operator_Lip_Low2_Ctrl_3_L,
    Operator_Lip_Low2_Ctrl_2_L,
    Operator_Lip_Low2_Ctrl_1_L,
    Operator_Lip_Low3_Ctrl_3_L,
    Operator_Lip_Low3_Ctrl_2_L,
    Operator_Lip_Low3_Ctrl_1_L,
    Operator_Cheek_Ctrl_5_L,
    Operator_Chin_Ctrl_3_L,
    Operator_Chin_Ctrl_2_L,
    Operator_Chin_Ctrl_1_L,
    Operator_Lip_Low2_Ctrl_Mid,
    Operator_Lip_Low2_Ctrl,
    Operator_Lip_Low3_Ctrl_Mid,
    Operator_Lip_Low3_Ctrl,
    Operator_Chin_Ctrl_Mid,
    Operator_Chin_Ctrl,
    Operator_Maxi,
    Operator_Head_Mid_Stretch,
    Operator_Head_Low_Stretch,
    Operator_Teeth_Up_Ctrl_R,
    Operator_Teeth_Up_Ctrl_L,
    Operator_Teeth_Up_Ctrl_Mid_R,
    Operator_Teeth_Up_Ctrl_Mid_L,
    Operator_Teeth_Up_Ctrl_Mid,
    Operator_Teeth_Up,
    Operator_Teeth_Low_Ctrl_R,
    Operator_Teeth_Low_Ctrl_L,
    Operator_Teeth_Low_Ctrl_Mid_R,
    Operator_Teeth_Low_Ctrl_Mid_L,
    Operator_Teeth_Low_Ctrl_Mid,
    Operator_Teeth_Low,
    Operator_Uvula_1,
    Operator_Uvula_2,
    Operator_Tongue_1_FK,
    Operator_Tongue_2_FK,
    Operator_Tongue_1_IK,
    Operator_Tongue_2_IK,
    Operator_Tongue_3_IK,
    Operator_Tongue_Mstr
    )

####### Load BlenRig 5 Layers Schemes Operators
from .blenrig_biped.ops_biped_layers_scheme import (
    Operator_BlenRig_Layers_Scheme_Compact,
    Operator_BlenRig_Layers_Scheme_Expanded
)

####### Load BlenRig 5 Rig Updater Operators
from .ops_rig_updater import (
    Operator_Biped_Updater
)
  
####### Load BlenRig 5 Rig Presets Operators
from .blenrig_biped.ops_blenrig_biped_add import (
    Operator_BlenRig5_Add_Biped
)

#################### Blenrig Object Add Menu ###############

class INFO_MT_blenrig5_add_rig(bpy.types.Menu):
    # Define the menu
    bl_idname = "BlenRig 5 add rigs"
    bl_label = "BlenRig 5 add rigs"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("blenrig5.add_biped_rig", text="BlenRig 5 Biped Rig", icon='POSE_HLT')

# Define menu
def blenrig5_add_menu_func(self, context):
    self.layout.operator("blenrig5.add_biped_rig", text="BlenRig 5 Biped Rig", icon='POSE_HLT')

######### GUI OPERATORS ########################################### 

# Display or hide tabs (sets the appropriate id-property)
class ARMATURE_OT_blenrig_5_gui(bpy.types.Operator):
    "Display tab"
    bl_label = ""
    bl_idname = "gui.blenrig_5_tabs"

    tab : bpy.props.StringProperty(name="Tab", description="Tab of the gui to expand")
    
    def invoke(self, context, event):
        arm = bpy.context.active_object.data
        if self.properties.tab in arm:
            arm[self.properties.tab] = not arm[self.properties.tab]
        return{'FINISHED'}

####### REGISTRATION ##############################################

# Needed for property registration
class Blenrig_5_Props(bpy.types.PropertyGroup):
    gui_picker_body_props : bpy.props.BoolProperty(default=True, description="Toggle properties display")
    gui_snap_all : bpy.props.BoolProperty(default=False, description="Display ALL Snapping Buttons")
    gui_snap : bpy.props.BoolProperty(default=False, description="Display Snapping Buttons")
    gui_cust_props_all : bpy.props.BoolProperty(default=False, description="Show ALL Custom Properties")
    gui_extra_props_head : bpy.props.BoolProperty(default=False, description="Tweak head extra options")
    gui_extra_props_arms : bpy.props.BoolProperty(default=False, description="Tweak arms extra options")
    gui_extra_props_fingers : bpy.props.BoolProperty(default=False, description="Tweak fingers extra options")
    gui_extra_props_legs : bpy.props.BoolProperty(default=False, description="Tweak legs extra options")
    gui_extra_props_accessories : bpy.props.BoolProperty(default=False, description="Tweak accessories options")
    gui_face_movement_ranges : bpy.props.BoolProperty(default=False, description="Set limits to facial movement")
    gui_face_lip_shaping : bpy.props.BoolProperty(default=False, description="Parameters to define lips curvature")
    gui_face_action_toggles : bpy.props.BoolProperty(default=False, description="Toggle facial actions off for editing")
    gui_body_ik_rot : bpy.props.BoolProperty(default=False, description="Set the initial rotation of IK bones")
    gui_body_auto_move : bpy.props.BoolProperty(default=False, description="Parameters for automated movement")
    gui_body_rj : bpy.props.BoolProperty(default=False, description="Simulate how bone thickness affects joint rotation")
    gui_body_toggles : bpy.props.BoolProperty(default=False, description="Toggle body parts")
    bake_to_shape : bpy.props.BoolProperty(name="Bake to Shape Key", default=False, description="Bake the mesh into a separate Shape Key")
    align_selected_only : bpy.props.BoolProperty(name="Selected Bones Only", default=False, description="Perform aligning only on selected bones")

# BlenRig Armature Tools Operator
armature_classes = [
    ARMATURE_OT_reset_constraints,
    ARMATURE_OT_armature_baker,
    ARMATURE_OT_mesh_pose_baker,
    ARMATURE_OT_reset_hooks,
    ARMATURE_OT_reset_deformers,
    ARMATURE_OT_blenrig_5_gui,
    BLENRIG_PT_BlenRig_5_Interface,
    Blenrig_5_Props,
    BLENRIG_PT_BlenRig_5_rigging_panel,
    BLENRIG_PT_BlenRig_5_mesh_panel,
    BLENRIG_PT_BlenRig_5_lattice_panel
]
# BlenRig Align Operators
alignment_classes = [
    Operator_BlenRig_Fix_Misaligned_Bones,
    Operator_BlenRig_Auto_Bone_Roll,
    Operator_BlenRig_Custom_Bone_Roll,
    Operator_BlenRig_Store_Roll_Angles,
    Operator_BlenRig_Restore_Roll_Angles,
    Operator_BlenRig_Reset_Dynamic
]
# BlenRig Layers Schemes Operators
schemes_classes = [
    Operator_BlenRig_Layers_Scheme_Compact,
    Operator_BlenRig_Layers_Scheme_Expanded
]
# BlenRig Rig Updater Operators
rig_updater_classes = [
    Operator_Biped_Updater
]
# BlenRig IK/FK Snapping Operators
snapping_classes = [
    Operator_Torso_Snap_FK_IK,
    Operator_Torso_Snap_IK_FK,
    Operator_Head_Snap_FK_IK,
    Operator_Head_Snap_IK_FK,
    Operator_Torso_Snap_UP_INV,
    Operator_Torso_Snap_INV_UP,
    Operator_Arm_L_Snap_FK_IK,
    Operator_Arm_L_Snap_IK_FK,
    Operator_Arm_R_Snap_FK_IK,
    Operator_Arm_R_Snap_IK_FK,
    Operator_Leg_L_Snap_FK_IK,
    Operator_Leg_L_Snap_IK_FK,
    Operator_Leg_R_Snap_FK_IK,
    Operator_Leg_R_Snap_IK_FK
]
# BlenRig Picker Operators
body_picker_biped_classes = [
    Operator_Head_Stretch,
    Operator_Head_Toon,
    Operator_Head_Top_Ctrl,
    Operator_Head_Mid_Ctrl,
    Operator_Head_Mid_Curve,
    Operator_Mouth_Str_Ctrl,
    Operator_Head_FK,
    Operator_Head_IK,
    Operator_Neck_4_Toon,
    Operator_Face_Toon_Up,
    Operator_Face_Toon_Mid,
    Operator_Face_Toon_Low,
    Operator_Neck_3,
    Operator_Neck_2,
    Operator_Neck_1,
    Operator_Neck_3_Toon,
    Operator_Neck_2_Toon,
    Operator_Neck_Ctrl,
    Operator_Shoulder_L,
    Operator_Shoulder_R,
    Operator_Shoulder_Rot_L,
    Operator_Shoulder_Rot_R,
    Operator_Clavi_Toon_L,
    Operator_Clavi_Toon_R,
    Operator_Head_Scale,
    Operator_Arm_Toon_L,
    Operator_Elbow_Pole_L,
    Operator_Forearm_Toon_L,
    Operator_Arm_Scale_L,
    Operator_Arm_FK_L,
    Operator_Arm_IK_L,
    Operator_Elbow_Toon_L,
    Operator_Forearm_FK_L,
    Operator_Forearm_IK_L,
    Operator_Hand_Toon_L,
    Operator_Arm_Toon_R,
    Operator_Elbow_Pole_R,
    Operator_Forearm_Toon_R,
    Operator_Arm_Scale_R,
    Operator_Arm_FK_R,
    Operator_Arm_IK_R,
    Operator_Elbow_Toon_R,
    Operator_Forearm_FK_R,
    Operator_Forearm_IK_R,
    Operator_Hand_Toon_R,
    Operator_Torso_Ctrl,
    Operator_Spine_3,
    Operator_Spine_2,
    Operator_Spine_1,
    Operator_Master_Torso_Pivot_Point,
    Operator_Master_Torso,
    Operator_Pelvis_Ctrl,
    Operator_Spine_4_Toon,
    Operator_Spine_3_Toon,
    Operator_Spine_2_Toon,
    Operator_Spine_1_Toon,
    Operator_Pelvis_Toon,
    Operator_Spine_3_Inv_Ctrl,
    Operator_Hand_Roll_L,
    Operator_Fing_Spread_L,
    Operator_Hand_IK_Pivot_Point_L,
    Operator_Hand_IK_Ctrl_L,
    Operator_Hand_FK_L,
    Operator_Fing_Lit_Ctrl_L,
    Operator_Fing_Lit_2_L,
    Operator_Fing_Lit_3_L,
    Operator_Fing_Lit_4_L,
    Operator_Fing_Ring_Ctrl_L,
    Operator_Fing_Ring_2_L,
    Operator_Fing_Ring_3_L,
    Operator_Fing_Ring_4_L,
    Operator_Fing_Mid_Ctrl_L,
    Operator_Fing_Mid_2_L,
    Operator_Fing_Mid_3_L,
    Operator_Fing_Mid_4_L,
    Operator_Fing_Ind_Ctrl_L,
    Operator_Fing_Ind_2_L,
    Operator_Fing_Ind_3_L,
    Operator_Fing_Ind_4_L,
    Operator_Fing_Thumb_Ctrl_L,
    Operator_Fing_Thumb_2_L,
    Operator_Fing_Thumb_3_L,
    Operator_Fing_Thumb_1_L,
    Operator_Fing_Lit_IK_L,
    Operator_Fing_Ring_IK_L,
    Operator_Fing_Mid_IK_L,
    Operator_Fing_Ind_IK_L,
    Operator_Fing_Thumb_IK_L,
    Operator_Hand_Close_L,
    Operator_Hand_Roll_R,
    Operator_Fing_Spread_R,
    Operator_Hand_IK_Pivot_Point_R,
    Operator_Hand_IK_Ctrl_R,
    Operator_Hand_FK_R,
    Operator_Fing_Lit_Ctrl_R,
    Operator_Fing_Lit_2_R,
    Operator_Fing_Lit_3_R,
    Operator_Fing_Lit_4_R,
    Operator_Fing_Ring_Ctrl_R,
    Operator_Fing_Ring_2_R,
    Operator_Fing_Ring_3_R,
    Operator_Fing_Ring_4_R,
    Operator_Fing_Mid_Ctrl_R,
    Operator_Fing_Mid_2_R,
    Operator_Fing_Mid_3_R,
    Operator_Fing_Mid_4_R,
    Operator_Fing_Ind_Ctrl_R,
    Operator_Fing_Ind_2_R,
    Operator_Fing_Ind_3_R,
    Operator_Fing_Ind_4_R,
    Operator_Fing_Thumb_Ctrl_R,
    Operator_Fing_Thumb_2_R,
    Operator_Fing_Thumb_3_R,
    Operator_Fing_Thumb_1_R,
    Operator_Fing_Lit_IK_R,
    Operator_Fing_Ring_IK_R,
    Operator_Fing_Mid_IK_R,
    Operator_Fing_Ind_IK_R,
    Operator_Fing_Thumb_IK_R,
    Operator_Hand_Close_R,
    Operator_Thigh_Toon_L,
    Operator_Knee_Pole_L,
    Operator_Shin_Toon_L,
    Operator_Pelvis_Toon_L,
    Operator_Leg_Scale_L,
    Operator_Thigh_FK_L,
    Operator_Thigh_IK_L,
    Operator_Knee_Toon_L,
    Operator_Shin_FK_L,
    Operator_Shin_IK_L,
    Operator_Foot_Toon_L,
    Operator_Thigh_Toon_R,
    Operator_Knee_Pole_R,
    Operator_Shin_Toon_R,
    Operator_Pelvis_Toon_R,
    Operator_Leg_Scale_R,
    Operator_Thigh_FK_R,
    Operator_Thigh_IK_R,
    Operator_Knee_Toon_R,
    Operator_Shin_FK_R,
    Operator_Shin_IK_R,
    Operator_Foot_Toon_R,
    Operator_Toe_2_FK_L,
    Operator_Toe_Roll_1_L,
    Operator_Toe_1_FK_L,
    Operator_Toe_Roll_2_L,
    Operator_Foot_L,
    Operator_Foot_Roll_Ctrl_L,
    Operator_Toe_Big_Ctrl_L,
    Operator_Toe_Big_2_L,
    Operator_Toe_Big_3_L,
    Operator_Toe_Big_IK_L,
    Operator_Toe_Ind_Ctrl_L, 
    Operator_Toe_Ind_2_L,
    Operator_Toe_Ind_3_L,
    Operator_Toe_Ind_4_L,
    Operator_Toe_Ind_IK_L,
    Operator_Toe_Mid_Ctrl_L,
    Operator_Toe_Mid_2_L,
    Operator_Toe_Mid_3_L,
    Operator_Toe_Mid_4_L,
    Operator_Toe_Mid_IK_L,
    Operator_Toe_Fourth_Ctrl_L,
    Operator_Toe_Fourth_2_L,
    Operator_Toe_Fourth_3_L,
    Operator_Toe_Fourth_4_L,
    Operator_Toe_Fourth_IK_L,
    Operator_Toe_Lit_Ctrl_L,
    Operator_Toe_Lit_2_L,
    Operator_Toe_Lit_3_L,
    Operator_Toe_Lit_IK_L,
    Operator_Toes_Spread_L,
    Operator_Toes_IK_Ctrl_Mid_L,
    Operator_Toes_IK_Ctrl_L,
    Operator_Sole_Ctrl_L,
    Operator_Sole_Pivot_Point_L,
    Operator_Toe_2_FK_R,
    Operator_Toe_Roll_1_R,
    Operator_Toe_1_FK_R,
    Operator_Toe_Roll_2_R,
    Operator_Foot_R,
    Operator_Foot_Roll_Ctrl_R,
    Operator_Toe_Big_Ctrl_R,
    Operator_Toe_Big_2_R,
    Operator_Toe_Big_3_R,
    Operator_Toe_Big_IK_R,
    Operator_Toe_Ind_Ctrl_R,
    Operator_Toe_Ind_2_R,
    Operator_Toe_Ind_3_R,
    Operator_Toe_Ind_4_R,
    Operator_Toe_Ind_IK_R,
    Operator_Toe_Mid_Ctrl_R,
    Operator_Toe_Mid_2_R,
    Operator_Toe_Mid_3_R,
    Operator_Toe_Mid_4_R,
    Operator_Toe_Mid_IK_R,
    Operator_Toe_Fourth_Ctrl_R,
    Operator_Toe_Fourth_2_R,
    Operator_Toe_Fourth_3_R,
    Operator_Toe_Fourth_4_R,
    Operator_Toe_Fourth_IK_R,
    Operator_Toe_Lit_Ctrl_R,
    Operator_Toe_Lit_2_R,
    Operator_Toe_Lit_3_R,
    Operator_Toe_Lit_IK_R,
    Operator_Toes_Spread_R,
    Operator_Toes_IK_Ctrl_Mid_R,
    Operator_Toes_IK_Ctrl_R,
    Operator_Sole_Ctrl_R,
    Operator_Sole_Pivot_Point_R,
    Operator_Master,
    Operator_Master_Pivot_Point,
    Operator_Look,
    Operator_Look_L,
    Operator_Look_R,
    Operator_Zoom_Selected
]

body_picker_quadruped_classes = [
    Operator_Ankle_Toon_L,
    Operator_Carpal_FK_L,
    Operator_Carpal_IK_L,
    Operator_Carpal_Toon_L,
    Operator_Ankle_Toon_R,
    Operator_Carpal_FK_R,
    Operator_Carpal_IK_R,
    Operator_Carpal_Toon_R,
    Operator_Hock_Toon_L,
    Operator_Tarsal_FK_L,
    Operator_Tarsal_IK_L,
    Operator_Tarsal_Toon_L,
    Operator_Hock_Toon_R,
    Operator_Tarsal_FK_R,
    Operator_Tarsal_IK_R,
    Operator_Tarsal_Toon_R,
    Operator_Fing_2_FK_L,
    Operator_Fing_1_FK_L,
    Operator_Fing_Roll_2_L,
    Operator_Fing_Roll_1_L,
    Operator_Hand_L,
    Operator_Hand_Roll_Ctrl_L,
    Operator_Hand_Sole_Ctrl_L,
    Operator_Hand_Sole_Pivot_Point_L,
    Operator_Fing_2_FK_R,
    Operator_Fing_1_FK_R,
    Operator_Fing_Roll_2_R,
    Operator_Fing_Roll_1_R,
    Operator_Hand_R,
    Operator_Hand_Roll_Ctrl_R,
    Operator_Hand_Sole_Ctrl_R,
    Operator_Hand_Sole_Pivot_Point_R
]

face_picker_classes = [
    Operator_Ear_Up_R,
    Operator_Ear_R,
    Operator_Ear_Low_R,
    Operator_Brow_Ctrl_1_R,
    Operator_Brow_Ctrl_2_R,
    Operator_Brow_Ctrl_3_R,
    Operator_Brow_Ctrl_4_R,
    Operator_Brow_Ctrl_R,
    Operator_Toon_Brow_R,
    Operator_Ear_Up_L,
    Operator_Ear_L,
    Operator_Ear_Low_L,
    Operator_Brow_Ctrl_1_L,
    Operator_Brow_Ctrl_2_L,
    Operator_Brow_Ctrl_3_L,
    Operator_Brow_Ctrl_4_L,
    Operator_Brow_Ctrl_L,
    Operator_Toon_Brow_L,
    Operator_Frown_Ctrl,
    Operator_Nose_Bridge_1_Ctrl,
    Operator_Eyelid_Up_Ctrl_R,
    Operator_Eyelid_Up_Ctrl_3_R,
    Operator_Eyelid_Up_Ctrl_2_R,
    Operator_Eyelid_Up_Ctrl_1_R,
    Operator_Toon_Eye_Out_R,
    Operator_Toon_Eye_Up_R,
    Operator_Pupil_Ctrl_R,
    Operator_Eye_Ctrl_R,
    Operator_Iris_Ctrl_R,
    Operator_Toon_Eye_In_R,
    Operator_Toon_Eye_Low_R,
    Operator_Eyelid_Ctrl_Out_R,
    Operator_Eyelid_Low_Ctrl_3_R,
    Operator_Eyelid_Low_Ctrl_2_R,
    Operator_Eyelid_Low_Ctrl_1_R,
    Operator_Eyelid_Ctrl_In_R,
    Operator_Eyelid_Low_Ctrl_R,
    Operator_Eyelid_Up_Ctrl_L,
    Operator_Eyelid_Up_Ctrl_3_L,
    Operator_Eyelid_Up_Ctrl_2_L,
    Operator_Eyelid_Up_Ctrl_1_L,
    Operator_Toon_Eye_Out_L,
    Operator_Toon_Eye_Up_L,
    Operator_Pupil_Ctrl_L,
    Operator_Eye_Ctrl_L,
    Operator_Iris_Ctrl_L,
    Operator_Toon_Eye_In_L,
    Operator_Toon_Eye_Low_L,
    Operator_Eyelid_Ctrl_Out_L,
    Operator_Eyelid_Low_Ctrl_3_L,
    Operator_Eyelid_Low_Ctrl_2_L,
    Operator_Eyelid_Low_Ctrl_1_L,
    Operator_Eyelid_Ctrl_In_L,
    Operator_Eyelid_Low_Ctrl_L,
    Operator_Nose_Bridge_2_Ctrl,
    Operator_Nose_Frown_Ctrl_R,
    Operator_Nose_Frown_Ctrl_L,
    Operator_Cheek_Ctrl_R,
    Operator_Cheek_Ctrl_3_R,
    Operator_Cheek_Ctrl_2_R,
    Operator_Cheek_Ctrl_1_R,
    Operator_Cheek2_Ctrl_3_R,
    Operator_Cheek2_Ctrl_2_R,
    Operator_Cheek2_Ctrl_1_R,
    Operator_Lip_Up3_Ctrl_3_R,
    Operator_Lip_Up3_Ctrl_2_R,
    Operator_Lip_Up3_Ctrl_1_R,
    Operator_Lip_Up2_Ctrl_3_R,
    Operator_Lip_Up2_Ctrl_2_R,
    Operator_Lip_Up2_Ctrl_1_R,
    Operator_Cheek_Ctrl_L,
    Operator_Cheek_Ctrl_3_L,
    Operator_Cheek_Ctrl_2_L,
    Operator_Cheek_Ctrl_1_L,
    Operator_Cheek2_Ctrl_3_L,
    Operator_Cheek2_Ctrl_2_L,
    Operator_Cheek2_Ctrl_1_L,
    Operator_Lip_Up3_Ctrl_3_L,
    Operator_Lip_Up3_Ctrl_2_L,
    Operator_Lip_Up3_Ctrl_1_L,
    Operator_Lip_Up2_Ctrl_3_L,
    Operator_Lip_Up2_Ctrl_2_L,
    Operator_Lip_Up2_Ctrl_1_L,
    Operator_Nostril_Ctrl_R,
    Operator_Nose_Ctrl,
    Operator_Nostril_Ctrl_L,
    Operator_Lip_Up3_Ctrl_Mid,
    Operator_Lip_Up3_Ctrl,
    Operator_Lip_Up2_Ctrl_Mid,
    Operator_lip_up2_ctrl,
    Operator_Cheek_Ctrl_4_R,
    Operator_Cheek2_Ctrl_4_R,
    Operator_Lip_Up3_Ctrl_4_R,
    Operator_Lip_Up2_Ctrl_4_R,
    Operator_Cheek_Ctrl_4_L,
    Operator_Cheek2_Ctrl_4_L,
    Operator_Lip_Up3_Ctrl_4_L,
    Operator_Lip_Up2_Ctrl_4_L,
    Operator_Mouth_Mstr_Up,
    Operator_Mouth_Corner_R,
    Operator_Mouth_Corner_L,
    Operator_Lip_Up_Ctrl,
    Operator_Lip_Up_Ctrl_Collision,
    Operator_Lip_Up_Ctrl_3_R,
    Operator_Lip_Up_Ctrl_2_R,
    Operator_Lip_Up_Ctrl_1_R,
    Operator_Lip_Up_Ctrl_Mid,
    Operator_Lip_Up_Ctrl_3_L,
    Operator_Lip_Up_Ctrl_2_L,
    Operator_Lip_Up_Ctrl_1_L,
    Operator_Mouth_Up_Ctrl,
    Operator_Lip_Up_Ctrl_4_R,
    Operator_Lip_Up_Ctrl_4_L,
    Operator_Mouth_Ctrl,
    Operator_Mouth_Low_Ctrl,
    Operator_Lip_Low_Ctrl_3_R,
    Operator_Lip_Low_Ctrl_2_R,
    Operator_Lip_Low_Ctrl_1_R,
    Operator_Lip_Low_Ctrl_Mid,
    Operator_Lip_Low_Ctrl_1_L,
    Operator_Lip_Low_Ctrl_2_L,
    Operator_Lip_Low_Ctrl_3_L,
    Operator_Lip_Low_Ctrl_Collision,
    Operator_Lip_Low_Ctrl,
    Operator_Mouth_Mstr_Low,
    Operator_Mouth_Mstr_Ctrl,
    Operator_Mouth_Frown_Ctrl_R,
    Operator_Lip_Low2_Ctrl_3_R,
    Operator_Lip_Low2_Ctrl_2_R,
    Operator_Lip_Low2_Ctrl_1_R,
    Operator_Lip_Low3_Ctrl_3_R,
    Operator_Lip_Low3_Ctrl_2_R,
    Operator_Lip_Low3_Ctrl_1_R,
    Operator_Cheek_Ctrl_5_R,
    Operator_Chin_Ctrl_3_R,
    Operator_Chin_Ctrl_2_R,
    Operator_Chin_Ctrl_1_R,
    Operator_Mouth_Frown_Ctrl_L,
    Operator_Lip_Low2_Ctrl_3_L,
    Operator_Lip_Low2_Ctrl_2_L,
    Operator_Lip_Low2_Ctrl_1_L,
    Operator_Lip_Low3_Ctrl_3_L,
    Operator_Lip_Low3_Ctrl_2_L,
    Operator_Lip_Low3_Ctrl_1_L,
    Operator_Cheek_Ctrl_5_L,
    Operator_Chin_Ctrl_3_L,
    Operator_Chin_Ctrl_2_L,
    Operator_Chin_Ctrl_1_L,
    Operator_Lip_Low2_Ctrl_Mid,
    Operator_Lip_Low2_Ctrl,
    Operator_Lip_Low3_Ctrl_Mid,
    Operator_Lip_Low3_Ctrl,
    Operator_Chin_Ctrl_Mid,
    Operator_Chin_Ctrl,
    Operator_Maxi,
    Operator_Head_Mid_Stretch,
    Operator_Head_Low_Stretch,
    Operator_Teeth_Up_Ctrl_R,
    Operator_Teeth_Up_Ctrl_L,
    Operator_Teeth_Up_Ctrl_Mid_R,
    Operator_Teeth_Up_Ctrl_Mid_L,
    Operator_Teeth_Up_Ctrl_Mid,
    Operator_Teeth_Up,
    Operator_Teeth_Low_Ctrl_R,
    Operator_Teeth_Low_Ctrl_L,
    Operator_Teeth_Low_Ctrl_Mid_R,
    Operator_Teeth_Low_Ctrl_Mid_L,
    Operator_Teeth_Low_Ctrl_Mid,
    Operator_Teeth_Low,
    Operator_Uvula_1,
    Operator_Uvula_2,
    Operator_Tongue_1_FK,
    Operator_Tongue_2_FK,
    Operator_Tongue_1_IK,
    Operator_Tongue_2_IK,
    Operator_Tongue_3_IK,
    Operator_Tongue_Mstr
]

blenrig_rigs_classes = [
    Operator_BlenRig5_Add_Biped
]

addon_dependencies = ["space_view3d_copy_attributes"]


def register():

    # load dependency add-ons
    import addon_utils
    for addon_id in addon_dependencies:
        default_state, loaded_state = addon_utils.check(addon_id)
        if not loaded_state:
            addon_utils.enable(addon_id, default_set=False, persistent=True)

    # load BlenRig internal classes
    for c in armature_classes:
        bpy.utils.register_class(c)
    for c in alignment_classes:
        bpy.utils.register_class(c)
    for c in schemes_classes:
        bpy.utils.register_class(c)   
    for c in rig_updater_classes:
        bpy.utils.register_class(c)                
    for c in snapping_classes:
        bpy.utils.register_class(c)
    for c in body_picker_biped_classes:
        bpy.utils.register_class(c)
    for c in body_picker_quadruped_classes:
        bpy.utils.register_class(c)
    for c in face_picker_classes:
        bpy.utils.register_class(c)
    for c in blenrig_rigs_classes:
        bpy.utils.register_class(c)

    # BlenRig Props
    bpy.types.WindowManager.blenrig_5_props = bpy.props.PointerProperty(type = Blenrig_5_Props)
    # BlenRig Object Add Panel
    bpy.types.VIEW3D_MT_armature_add.append(blenrig5_add_menu_func)


def unregister():

    # BlenRig Props
    del bpy.types.WindowManager.blenrig_5_props
    # BlenRig Object Add Panel
    bpy.types.VIEW3D_MT_armature_add.remove(blenrig5_add_menu_func)

    # unload BlenRig internal classes
    for c in armature_classes:
        bpy.utils.unregister_class(c)
    for c in alignment_classes:
        bpy.utils.unregister_class(c)
    for c in schemes_classes:
        bpy.utils.unregister_class(c)  
    for c in rig_updater_classes:
        bpy.utils.unregister_class(c)                  
    for c in snapping_classes:
        bpy.utils.unregister_class(c)
    for c in body_picker_biped_classes:
        bpy.utils.unregister_class(c)
    for c in body_picker_quadruped_classes:
        bpy.utils.unregister_class(c)
    for c in face_picker_classes:
        bpy.utils.unregister_class(c)
    for c in blenrig_rigs_classes:
        bpy.utils.unregister_class(c)

    # unload add-on dependencies
    import addon_utils
    for addon_id in addon_dependencies:
        addon_utils.disable(addon_id, default_set=False)


if __name__ == "__main__":
    register()
