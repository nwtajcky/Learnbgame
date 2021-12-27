import bpy

####### BlenRig 5 Rigging Panel

class BlenRig_5_rigging_panel(bpy.types.Panel):
    bl_label = "BlenRig 5 Rigging Panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        if not bpy.context.active_object:
            return False
        if (bpy.context.active_object.type in ["ARMATURE"]):
            for prop in bpy.context.active_object.data.items():
                if prop[0] == 'rig_name' and prop[1] == 'BlenRig_5':
                    return True

    def draw(self, context):
        arm = bpy.context.active_object
        arm_data = bpy.context.active_object.data
        p_bones = arm.pose.bones
        layout = self.layout

####### Body Settings
        if "gui_rig_body" in arm_data:
            props = context.window_manager.blenrig_5_props
            box = layout.column()
            col = box.column()
            row = col.row()
        # expanded box
        if "gui_rig_body" in arm_data and arm_data["gui_rig_body"]:
            row.operator("gui.blenrig_5_tabs", icon="OUTLINER_OB_ARMATURE", emboss = 1).tab = "gui_rig_body"
            row.label(text="BODY SETTINGS")
            col.separator()
            # IK Initial Rotation
            col.prop(props, "gui_body_ik_rot", text = 'IK:')
            if props.gui_body_ik_rot:
                box = col.box()
                box.label(text="IK Initial Rotation:")
                row_props = box.row()
                col_R = row_props.column()
                col_L = row_props.column()
                for b in p_bones:
                    if '_R' in b.name:
                        for C in b.constraints:
                            if C.name == 'Ik_Initial_Rotation':
                                col_R.prop(C, 'to_min_x_rot', text = "{}".format(b.name), toggle=True)
                for b in p_bones:
                    if '_L' in b.name:
                        for C in b.constraints:
                            if C.name == 'Ik_Initial_Rotation':
                                col_L.prop(C, 'to_min_x_rot', text = "{}".format(b.name), toggle=True)
            # Atuomated Movement
            col.prop(props, "gui_body_auto_move", text = 'Automated Movement:')
            if props.gui_body_auto_move:
                box = col.box()
                box.label(text="IK Auto Shoulder:")
                row_props = box.row()
                col_R = row_props.column()
                col_L = row_props.column()
                for b in p_bones:
                    if 'shoulder' in b.name:
                        if '_R' in b.name:
                            for cust_prop in b.keys():
                                if 'SHLDR_AUTO' in cust_prop:
                                    col_R.prop(b, '["{}"]'.format(cust_prop), text = "{} {}".format(b.name, ((cust_prop).replace('SHLDR_AUTO_', '').replace('_R', ''))),  toggle=True)
                for b in p_bones:
                    if 'shoulder' in b.name:
                        if '_L' in b.name:
                            for cust_prop in b.keys():
                                if 'SHLDR_AUTO' in cust_prop:
                                    col_L.prop(b, '["{}"]'.format(cust_prop), text = "{} {}".format(b.name, ((cust_prop).replace('SHLDR_AUTO_', '').replace('_L', ''))),  toggle=True)
                box = col.box()
                row_props = box.row()
                col_R = row_props.column()
                col_L = row_props.column()
                col_R.label(text='Torso FK Ctrl Influence:')
                col_R.prop(p_bones['spine_1_fk'], '["fk_follow_main"]', text="Spine 1", toggle=True)
                col_R.prop(p_bones['spine_2_fk'], '["fk_follow_main"]', text="Spine 2", toggle=True)
                col_R.prop(p_bones['spine_3_fk'], '["fk_follow_main"]', text="Spine 3", toggle=True)
                col_R.label(text='Torso INV Ctrl Influence:')
                col_R.prop(p_bones['spine_2_inv'], '["fk_follow_main"]', text="Spine 2 inv", toggle=True)
                col_R.prop(p_bones['spine_1_inv'], '["fk_follow_main"]', text="Spine 1 inv", toggle=True)
                col_R.prop(p_bones['pelvis_inv'], '["fk_follow_main"]', text="Pelvis inv", toggle=True)
                col_L.label(text='Neck FK Ctrl Influence:')
                col_L.prop(p_bones['neck_1_fk'], '["fk_follow_main"]', text="Neck 1", toggle=True)
                col_L.prop(p_bones['neck_2_fk'], '["fk_follow_main"]', text="Neck 2", toggle=True)
                col_L.prop(p_bones['neck_3_fk'], '["fk_follow_main"]', text="Neck 3", toggle=True)

                box = col.box()
                row_props = box.row()
                col_R = row_props.column()
                col_L = row_props.column()
                col_R.label(text='Foot Roll R:')
                col_L.label(text='Foot Roll L:')
                for b in p_bones:
                    if 'foot_roll_ctrl_R' in b.name:
                        for cust_prop in b.keys():
                            if 'ROLL' in cust_prop:
                                col_R.prop(b, '["{}"]'.format(cust_prop), text = "{}".format((cust_prop).replace('_L', '')),  toggle=True)
                for b in p_bones:
                    if 'foot_roll_ctrl_L' in b.name:
                        for cust_prop in b.keys():
                            if 'ROLL' in cust_prop:
                                col_L.prop(b, '["{}"]'.format(cust_prop), text = "{}".format((cust_prop).replace('_L', '')),  toggle=True)

            # Realistic Joints
            col.prop(props, "gui_body_rj", text = 'Realistic Joints:')
            if props.gui_body_rj:
                box = col.box()
                box.label(text="Bone Movement")
                row_props = box.row()
                col_R = row_props.column()
                col_L = row_props.column()
                for b in p_bones:
                    if 'properties' in b.name:
                        if 'arm' in b.name:
                            if '_R' in b.name:
                                for cust_prop in b.keys():
                                    if 'realistic_joints' in cust_prop:
                                        col_R.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop).replace('realistic_joints_', ''),  toggle=True)
                col_R.separator()
                for b in p_bones:
                    if 'properties' in b.name:
                        if 'leg' in b.name:
                            if '_R' in b.name:
                                for cust_prop in b.keys():
                                    if 'realistic_joints' in cust_prop:
                                        col_R.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop).replace('realistic_joints_', ''),  toggle=True)
                for b in p_bones:
                    if 'properties' in b.name:
                        if 'arm' in b.name:
                            if '_L' in b.name:
                                for cust_prop in b.keys():
                                    if 'realistic_joints' in cust_prop:
                                        col_L.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop).replace('realistic_joints_', ''),  toggle=True)
                col_L.separator()
                for b in p_bones:
                    if 'properties' in b.name:
                        if 'leg' in b.name:
                            if '_L' in b.name:
                                for cust_prop in b.keys():
                                    if 'realistic_joints' in cust_prop:
                                        col_L.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop).replace('realistic_joints_', ''),  toggle=True)
            # Body Toggles
            col.prop(props, "gui_body_toggles", text = 'Toggles:')
            if props.gui_body_toggles:
                box = col.box()
                row_props = box.row()
                col_R = row_props.column()
                col_L = row_props.column()
                for b in p_bones:
                    if 'properties' in b.name:
                        if 'arm' in b.name:
                            if '_R' in b.name:
                                for cust_prop in b.keys():
                                    if 'toggle' in cust_prop:
                                        col_R.prop(b, '{}'.format(cust_prop))
                for b in p_bones:
                    if 'properties' in b.name:
                        if 'leg' in b.name:
                            if '_R' in b.name:
                                for cust_prop in b.keys():
                                    if 'toggle' in cust_prop:
                                        col_R.prop(b, '{}'.format(cust_prop))
                for b in p_bones:
                    if 'properties' in b.name:
                        if 'arm' in b.name:
                            if '_L' in b.name:
                                for cust_prop in b.keys():
                                    if 'toggle' in cust_prop:
                                        col_L.prop(b, '{}'.format(cust_prop))
                for b in p_bones:
                    if 'properties' in b.name:
                        if 'leg' in b.name:
                            if '_L' in b.name:
                                for cust_prop in b.keys():
                                    if 'toggle' in cust_prop:
                                        col_L.prop(b, '{}'.format(cust_prop))

        else:
            row.operator("gui.blenrig_5_tabs", icon="ARMATURE_DATA", emboss = 1).tab = "gui_rig_body"
            row.label(text="BODY SETTINGS")
####### Facial Settings
        if "gui_rig_face" in arm_data:
            props = context.window_manager.blenrig_5_props
            box = layout.column()
            col = box.column()
            row = col.row()
        # expanded box
        if "gui_rig_face" in arm_data and arm_data["gui_rig_face"]:
            row.operator("gui.blenrig_5_tabs", icon="MONKEY", emboss = 1).tab = "gui_rig_face"
            row.label(text="FACIAL SETTINGS")
            col.separator
            # Face movement ranges
            col.prop(props, "gui_face_movement_ranges", text = 'Facial Movement Ranges:')
            if props.gui_face_movement_ranges:
                box = col.box()
                row_props = box.row()
                col_R = row_props.column()
                col_L = row_props.column()
                col_R.label(text="Mouth_Corner_R")
                for b in p_bones:
                    if 'mouth_corner' in b.name:
                        if '_R' in b.name:
                            for cust_prop in b.keys():
                                if '_RNA_UI' not in cust_prop:
                                    if 'ACTION' not in cust_prop:
                                        col_R.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('_LIMIT', '').replace('_R', '')),  toggle=True)
                col_L.label(text="Mouth_Corner_L")
                for b in p_bones:
                    if 'mouth_corner' in b.name:
                        if '_L' in b.name:
                            for cust_prop in b.keys():
                                if '_RNA_UI' not in cust_prop:
                                    if 'ACTION' not in cust_prop:
                                        col_L.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('_LIMIT', '').replace('_L', '')),  toggle=True)
                box = col.box()
                box.label(text="Mouth_Ctrl")
                row_props = box.row()
                col_R = row_props.column()
                col_L = row_props.column()
                for b in p_bones:
                    if 'mouth_ctrl' in b.name:
                        for cust_prop in b.keys():
                            if 'OUT' in cust_prop:
                                col_R.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('_LIMIT', '')),  toggle=True)
                            if 'SMILE' in cust_prop:
                                col_R.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('_LIMIT', '')),  toggle=True)
                            if 'IN' in cust_prop:
                                col_L.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('_LIMIT', '')),  toggle=True)
                            if 'JAW' in cust_prop:
                                col_L.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('_LIMIT', '')),  toggle=True)
                    if 'maxi' in b.name:
                        for cust_prop in b.keys():
                            if 'ACTION' not in cust_prop:
                                if 'UP' in cust_prop:
                                    col_R.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('_LIMIT', '')),  toggle=True)
                                if 'DOWN' in cust_prop:
                                    col_L.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('_LIMIT', '')),  toggle=True)
                box = col.box()
                row_props = box.row()
                col_R = row_props.column()
                col_L = row_props.column()
                col_R.label(text="Mouth_Frown_R")
                for b in p_bones:
                    if 'mouth_frown' in b.name:
                        if '_R' in b.name:
                            for cust_prop in b.keys():
                                if '_RNA_UI' not in cust_prop:
                                    if 'ACTION' not in cust_prop:
                                        col_R.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('_LIMIT_R', '')),  toggle=True)
                col_L.label(text="Mouth_Frown_L")
                for b in p_bones:
                    if 'mouth_frown' in b.name:
                        if '_L' in b.name:
                            for cust_prop in b.keys():
                                if '_RNA_UI' not in cust_prop:
                                    if 'ACTION' not in cust_prop:
                                        col_L.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('_LIMIT_L', '')),  toggle=True)
                box = col.box()
                row_props = box.row()
                col_R = row_props.column()
                col_L = row_props.column()
                col_R.label(text="Cheek_Ctrl_R")
                col_L.label(text="Cheek_Ctrl_L")
                for b in p_bones:
                    if 'cheek_ctrl' in b.name:
                        if '_R'in b.name:
                            for cust_prop in b.keys():
                                if '_RNA_UI' not in cust_prop:
                                    if 'ACTION' not in cust_prop:
                                        col_R.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('_R', '').replace('_LIMIT', '')),  toggle=True)
                        if '_L'in b.name:
                            for cust_prop in b.keys():
                                if '_RNA_UI' not in cust_prop:
                                    if 'ACTION' not in cust_prop:
                                        col_L.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('_LIMIT', '').replace('_L', '')),  toggle=True)
                box = col.box()
                row_props = box.row()
                col_R = row_props.column()
                col_L = row_props.column()
                col_R.label(text="Nose_Frown_R")
                for b in p_bones:
                    if 'nose_frown' in b.name:
                        if '_R' in b.name:
                            for cust_prop in b.keys():
                                if '_RNA_UI' not in cust_prop:
                                    if 'ACTION' not in cust_prop:
                                        col_R.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('_LIMIT_R', '')),  toggle=True)
                col_L.label(text="Nose_Frown_L")
                for b in p_bones:
                    if 'nose_frown' in b.name:
                        if '_L' in b.name:
                            for cust_prop in b.keys():
                                if '_RNA_UI' not in cust_prop:
                                    if 'ACTION' not in cust_prop:
                                        col_L.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('_LIMIT_L', '')),  toggle=True)
                box = col.box()
                row_props = box.row()
                col_R = row_props.column()
                col_L = row_props.column()
                col_R.label(text="Eyelid_Low_R")
                col_L.label(text="Eyelid_Low_L")
                for b in p_bones:
                    if 'eyelid_low_ctrl' in b.name:
                        if '_R'in b.name:
                            for cust_prop in b.keys():
                                if '_RNA_UI' not in cust_prop:
                                    if 'ACTION' not in cust_prop:
                                        col_R.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('_R', '').replace('_LIMIT', '')),  toggle=True)
                        if '_L'in b.name:
                            for cust_prop in b.keys():
                                if '_RNA_UI' not in cust_prop:
                                    if 'ACTION' not in cust_prop:
                                        col_L.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('_LIMIT', '').replace('_L', '')),  toggle=True)
                col_R.label(text="Eyelid_Up_R")
                col_L.label(text="Eyelid_Up_L")
                for b in p_bones:
                    if 'eyelid_up_ctrl' in b.name:
                        if '_R'in b.name:
                            for cust_prop in b.keys():
                                if '_RNA_UI' not in cust_prop:
                                    if 'ACTION' not in cust_prop:
                                        col_R.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('_R', '').replace('_LIMIT', '')),  toggle=True)
                        if '_L'in b.name:
                            for cust_prop in b.keys():
                                if '_RNA_UI' not in cust_prop:
                                    if 'ACTION' not in cust_prop:
                                        col_L.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('_LIMIT', '').replace('_L', '')),  toggle=True)
            # Face action toggles
            col.prop(props, "gui_face_action_toggles", text = 'Action Toggles:')
            if props.gui_face_action_toggles:
                box = col.box()
                row_props = box.row()
                col_R = row_props.column()
                col_L = row_props.column()
                col_R.label(text="Mouth_Corner_R")
                for b in p_bones:
                    if 'mouth_corner' in b.name:
                        if '_R' in b.name:
                            for cust_prop in b.keys():
                                if 'ACTION' in cust_prop:
                                    col_R.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('ACTION_', '').replace('_R', '')),  toggle=True)
                col_L.label(text="Mouth_Corner_L")
                for b in p_bones:
                    if 'mouth_corner' in b.name:
                        if '_L' in b.name:
                            for cust_prop in b.keys():
                                if 'ACTION'in cust_prop:
                                    col_L.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('ACTION_', '').replace('_L', '')),  toggle=True)
                box = col.box()
                box.label(text="Mouth_Ctrl")
                row_props = box.row()
                col_R = row_props.column()
                col_L = row_props.column()
                for b in p_bones:
                    if 'mouth_ctrl' in b.name:
                        for cust_prop in b.keys():
                            if 'ACTION' in cust_prop:
                                col_R.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('ACTION_', '')),  toggle=True)
                    if 'maxi' in b.name:
                        for cust_prop in b.keys():
                            if 'ACTION' in cust_prop:
                                col_L.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('ACTION', 'JAW')),  toggle=True)
                box = col.box()
                row_props = box.row()
                col_R = row_props.column()
                col_L = row_props.column()
                col_R.label(text="Cheek_Ctrl_R")
                col_L.label(text="Cheek_Ctrl_L")
                for b in p_bones:
                    if 'cheek_ctrl' in b.name:
                        if '_R'in b.name:
                            for cust_prop in b.keys():
                                if 'ACTION' in cust_prop:
                                    col_R.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('_R', '').replace('ACTION_', '')),  toggle=True)
                        if '_L'in b.name:
                            for cust_prop in b.keys():
                                if 'ACTION' in cust_prop:
                                    col_L.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('ACTION_', '').replace('_L', '')),  toggle=True)
            # Lip Shaping
            col.prop(props, "gui_face_lip_shaping", text = 'Lip Shaping:')
            if props.gui_face_lip_shaping:
                box = col.box()
                row_props = box.row()
                col_1 = row_props.column()
                col_1.label(text="Follow Left Corner")
                col_2 = row_props.column()
                col_2.scale_x = 0.6
                col_2.label(text="X:")
                col_3 = row_props.column()
                col_3.label(text="Y:")
                col_3.scale_x = 0.6
                col_4 = row_props.column()
                col_4.label(text="Z:")
                col_4.scale_x = 0.6
                for b in p_bones:
                    if 'lip_up_ctrl_1_mstr_L' in b.name:
                        col_1.label(text="{}".format(b.name.replace('_mstr', '')))
                        for cust_prop in b.keys():
                            if '_X_' in cust_prop:
                                col_2.prop(b, '["{}"]'.format(cust_prop), text = '%', toggle=True)
                            if '_Y_' in cust_prop:
                                col_3.prop(b, '["{}"]'.format(cust_prop), text = '%', toggle=True)
                            if '_Z_' in cust_prop:
                                col_4.prop(b, '["{}"]'.format(cust_prop), text = '%', toggle=True)
                for b in p_bones:
                    if 'lip_low_ctrl_1_mstr_L' in b.name:
                        col_1.label(text="{}".format(b.name.replace('_mstr', '')))
                        for cust_prop in b.keys():
                            if '_X_' in cust_prop:
                                col_2.prop(b, '["{}"]'.format(cust_prop), text = '%', toggle=True)
                            if '_Y_' in cust_prop:
                                col_3.prop(b, '["{}"]'.format(cust_prop), text = '%', toggle=True)
                            if '_Z_' in cust_prop:
                                col_4.prop(b, '["{}"]'.format(cust_prop), text = '%', toggle=True)
                for b in p_bones:
                    if 'lip_up_ctrl_2_mstr_L' in b.name:
                        col_1.label(text="{}".format(b.name.replace('_mstr', '')))
                        for cust_prop in b.keys():
                            if '_X_' in cust_prop:
                                col_2.prop(b, '["{}"]'.format(cust_prop), text = '%', toggle=True)
                            if '_Y_' in cust_prop:
                                col_3.prop(b, '["{}"]'.format(cust_prop), text = '%', toggle=True)
                            if '_Z_' in cust_prop:
                                col_4.prop(b, '["{}"]'.format(cust_prop), text = '%', toggle=True)
                for b in p_bones:
                    if 'lip_low_ctrl_2_mstr_L' in b.name:
                        col_1.label(text="{}".format(b.name.replace('_mstr', '')))
                        for cust_prop in b.keys():
                            if '_X_' in cust_prop:
                                col_2.prop(b, '["{}"]'.format(cust_prop), text = '%', toggle=True)
                            if '_Y_' in cust_prop:
                                col_3.prop(b, '["{}"]'.format(cust_prop), text = '%', toggle=True)
                            if '_Z_' in cust_prop:
                                col_4.prop(b, '["{}"]'.format(cust_prop), text = '%', toggle=True)
                for b in p_bones:
                    if 'lip_up_ctrl_3_mstr_L' in b.name:
                        col_1.label(text="{}".format(b.name.replace('_mstr', '')))
                        for cust_prop in b.keys():
                            if '_X_' in cust_prop:
                                col_2.prop(b, '["{}"]'.format(cust_prop), text = '%', toggle=True)
                            if '_Y_' in cust_prop:
                                col_3.prop(b, '["{}"]'.format(cust_prop), text = '%', toggle=True)
                            if '_Z_' in cust_prop:
                                col_4.prop(b, '["{}"]'.format(cust_prop), text = '%', toggle=True)
                for b in p_bones:
                    if 'lip_low_ctrl_3_mstr_L' in b.name:
                        col_1.label(text="{}".format(b.name.replace('_mstr', '')))
                        for cust_prop in b.keys():
                            if '_X_' in cust_prop:
                                col_2.prop(b, '["{}"]'.format(cust_prop), text = '%', toggle=True)
                            if '_Y_' in cust_prop:
                                col_3.prop(b, '["{}"]'.format(cust_prop), text = '%', toggle=True)
                            if '_Z_' in cust_prop:
                                col_4.prop(b, '["{}"]'.format(cust_prop), text = '%', toggle=True)
                row_props = box.row()
                col_1 = row_props.column()
                col_1.label(text="Follow Right Corner")
                col_2 = row_props.column()
                col_2.scale_x = 0.6
                col_2.label(text="X:")
                col_3 = row_props.column()
                col_3.label(text="Y:")
                col_3.scale_x = 0.6
                col_4 = row_props.column()
                col_4.label(text="Z:")
                col_4.scale_x = 0.6
                for b in p_bones:
                    if 'lip_up_ctrl_1_mstr_R' in b.name:
                        col_1.label(text="{}".format(b.name.replace('_mstr', '')))
                        for cust_prop in b.keys():
                            if '_X_' in cust_prop:
                                col_2.prop(b, '["{}"]'.format(cust_prop), text = '%', toggle=True)
                            if '_Y_' in cust_prop:
                                col_3.prop(b, '["{}"]'.format(cust_prop), text = '%',  toggle=True)
                            if '_Z_' in cust_prop:
                                col_4.prop(b, '["{}"]'.format(cust_prop), text = '%',  toggle=True)
                for b in p_bones:
                    if 'lip_low_ctrl_1_mstr_R' in b.name:
                        col_1.label(text="{}".format(b.name.replace('_mstr', '')))
                        for cust_prop in b.keys():
                            if '_X_' in cust_prop:
                                col_2.prop(b, '["{}"]'.format(cust_prop), text = '%', toggle=True)
                            if '_Y_' in cust_prop:
                                col_3.prop(b, '["{}"]'.format(cust_prop), text = '%',  toggle=True)
                            if '_Z_' in cust_prop:
                                col_4.prop(b, '["{}"]'.format(cust_prop), text = '%',  toggle=True)
                for b in p_bones:
                    if 'lip_up_ctrl_2_mstr_R' in b.name:
                        col_1.label(text="{}".format(b.name.replace('_mstr', '')))
                        for cust_prop in b.keys():
                            if '_X_' in cust_prop:
                                col_2.prop(b, '["{}"]'.format(cust_prop), text = '%', toggle=True)
                            if '_Y_' in cust_prop:
                                col_3.prop(b, '["{}"]'.format(cust_prop), text = '%',  toggle=True)
                            if '_Z_' in cust_prop:
                                col_4.prop(b, '["{}"]'.format(cust_prop), text = '%',  toggle=True)
                for b in p_bones:
                    if 'lip_low_ctrl_2_mstr_R' in b.name:
                        col_1.label(text="{}".format(b.name.replace('_mstr', '')))
                        for cust_prop in b.keys():
                            if '_X_' in cust_prop:
                                col_2.prop(b, '["{}"]'.format(cust_prop), text = '%', toggle=True)
                            if '_Y_' in cust_prop:
                                col_3.prop(b, '["{}"]'.format(cust_prop), text = '%',  toggle=True)
                            if '_Z_' in cust_prop:
                                col_4.prop(b, '["{}"]'.format(cust_prop), text = '%',  toggle=True)
                for b in p_bones:
                    if 'lip_up_ctrl_3_mstr_R' in b.name:
                        col_1.label(text="{}".format(b.name.replace('_mstr', '')))
                        for cust_prop in b.keys():
                            if '_X_' in cust_prop:
                                col_2.prop(b, '["{}"]'.format(cust_prop), text = '%', toggle=True)
                            if '_Y_' in cust_prop:
                                col_3.prop(b, '["{}"]'.format(cust_prop), text = '%',  toggle=True)
                            if '_Z_' in cust_prop:
                                col_4.prop(b, '["{}"]'.format(cust_prop), text = '%',  toggle=True)
                for b in p_bones:
                    if 'lip_low_ctrl_3_mstr_R' in b.name:
                        col_1.label(text="{}".format(b.name.replace('_mstr', '')))
                        for cust_prop in b.keys():
                            if '_X_' in cust_prop:
                                col_2.prop(b, '["{}"]'.format(cust_prop), text = '%', toggle=True)
                            if '_Y_' in cust_prop:
                                col_3.prop(b, '["{}"]'.format(cust_prop), text = '%',  toggle=True)
                            if '_Z_' in cust_prop:
                                col_4.prop(b, '["{}"]'.format(cust_prop), text = '%',  toggle=True)
                col.separator

        else:
            row.operator("gui.blenrig_5_tabs", icon="MESH_MONKEY", emboss = 1).tab = "gui_rig_face"
            row.label(text="FACIAL SETTINGS")

####### Layers Settings
        if "gui_rig_layers" in arm_data:
            box = layout.column()
            col = box.column()
            row = col.row()
        # expanded box
        if "gui_rig_layers" in arm_data and arm_data["gui_rig_layers"]:
            row.operator("gui.blenrig_5_tabs", icon="RENDERLAYERS", emboss = 1).tab = "gui_rig_layers"
            row.label(text="LAYERS SETTING")
            col.separator
            box = col.box()
            col_2 = box.column()
            row_props = col_2.row()
            row_props.scale_y = 0.75
            row_props.scale_x = 1
            row_props.alignment = 'LEFT'
            row_props.prop(arm_data, '["layers_count"]', text="Layers", toggle=True)
            if arm_data['bone_auto_hide'] == 1:
                row_props.operator("gui.blenrig_5_tabs",text = "  Bone Auto Hiding", icon="CHECKBOX_HLT", emboss = 0).tab = "bone_auto_hide"
            else:
                row_props.operator("gui.blenrig_5_tabs",text = "  Bone Auto Hiding", icon="CHECKBOX_DEHLT", emboss = 0).tab = "bone_auto_hide"
            col_2.label(text='Layers Schemes:')
            row_schemes = col_2.row()
            row_schemes.operator("blenrig5.layers_scheme_compact", text="Compact")
            row_schemes.operator("blenrig5.layers_scheme_expanded", text="Expanded")
            col_2.label(text='Layers Names: (Always keep 32 items)')
            row_layers = col_2.row()
            row_layers.prop(arm_data, '["layer_list"]', text="", toggle=True)
        else:
            row.operator("gui.blenrig_5_tabs", icon="RENDER_RESULT", emboss = 1).tab = "gui_rig_layers"
            row.label(text="LAYERS SETTING")

####### Dynamic Shaping
        if "gui_rig_flex" in arm_data:
            box = layout.column()
            col = box.column()
            row = col.row()
        # expanded box
        if "gui_rig_flex" in arm_data and arm_data["gui_rig_flex"]:
            row.operator("gui.blenrig_5_tabs", icon="OUTLINER_OB_ARMATURE", emboss = 1).tab = "gui_rig_flex"
            row.label(text="DYNAMIC SHAPING (Flex Rig Way)")
            col.separator
            box = col.box()
            row_props = box.row()
            col_1 = row_props.column()
            col_1.scale_x = 0.5
            col_2 = row_props.column()
            col_2.label(text="Head:")
            col_2.scale_x = 2
            col_3 = row_props.column()
            col_3.scale_x = 0.5
            for b in p_bones:
                if 'properties_head' in b.name:
                    for cust_prop in b.keys():
                        if 'flex' in cust_prop:
                            if 'head' in cust_prop:
                                col_2.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('flex_head_', '')),  toggle=True)
            col_2.label(text="Neck:")
            for b in p_bones:
                if 'properties_head' in b.name:
                    for cust_prop in b.keys():
                        if 'flex' in cust_prop:
                            if 'neck' in cust_prop:
                                col_2.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('flex_neck_', '')),  toggle=True)
            row_props = box.row()
            col_1 = row_props.column()
            col_1.label(text="Arm_R:")
            col_2 = row_props.column()
            col_2.label(text="Torso:")
            col_3 = row_props.column()
            col_3.label(text="Arm_L:")
            for b in p_bones:
                if 'properties_arm_R' in b.name:
                    for cust_prop in b.keys():
                        if 'flex' in cust_prop:
                            if 'forearm' not in cust_prop:
                                if 'hand' not in  cust_prop:
                                    col_1.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('flex_arm_', '')),  toggle=True)
            col_1.label(text="Forearm_R:")
            for b in p_bones:
                if 'properties_arm_R' in b.name:
                    for cust_prop in b.keys():
                        if 'flex' in cust_prop:
                            if 'forearm' in cust_prop:
                                col_1.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('flex_forearm_', '')),  toggle=True)
            col_1.label(text="Hand_R:")
            for b in p_bones:
                if 'properties_arm_R' in b.name:
                    for cust_prop in b.keys():
                        if 'flex' in cust_prop:
                            if 'hand' in cust_prop:
                                col_1.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('flex_hand_', '')),  toggle=True)
            for b in p_bones:
                if 'properties_torso' in b.name:
                    for cust_prop in b.keys():
                        if 'flex' in cust_prop:
                            if 'torso' in cust_prop:
                                col_2.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('flex_torso_', '')),  toggle=True)
            col_2.label(text="Chest:")
            for b in p_bones:
                if 'properties_torso' in b.name:
                    for cust_prop in b.keys():
                        if 'flex' in cust_prop:
                            if 'chest' in cust_prop:
                                col_2.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('flex_chest_', '')),  toggle=True)
            col_2.label(text="Ribs:")
            for b in p_bones:
                if 'properties_torso' in b.name:
                    for cust_prop in b.keys():
                        if 'flex' in cust_prop:
                            if 'ribs' in cust_prop:
                                col_2.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('flex_ribs_', '')),  toggle=True)
            col_2.label(text="waist:")
            for b in p_bones:
                if 'properties_torso' in b.name:
                    for cust_prop in b.keys():
                        if 'flex' in cust_prop:
                            if 'waist' in cust_prop:
                                col_2.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('flex_waist_', '')),  toggle=True)
            col_2.label(text="pelvis:")
            for b in p_bones:
                if 'properties_torso' in b.name:
                    for cust_prop in b.keys():
                        if 'flex' in cust_prop:
                            if 'pelvis' in cust_prop:
                                col_2.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('flex_pelvis_', '')),  toggle=True)
            for b in p_bones:
                if 'properties_arm_L' in b.name:
                    for cust_prop in b.keys():
                        if 'flex' in cust_prop:
                            if 'forearm' not in cust_prop:
                                if 'hand' not in  cust_prop:
                                    col_3.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('flex_arm_', '')),  toggle=True)
            col_3.label(text="Forearm_L:")
            for b in p_bones:
                if 'properties_arm_L' in b.name:
                    for cust_prop in b.keys():
                        if 'flex' in cust_prop:
                            if 'forearm' in cust_prop:
                                col_3.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('flex_forearm_', '')),  toggle=True)
            col_3.label(text="Hand_L:")
            for b in p_bones:
                if 'properties_arm_L' in b.name:
                    for cust_prop in b.keys():
                        if 'flex' in cust_prop:
                            if 'hand' in cust_prop:
                                col_3.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('flex_hand_', '')),  toggle=True)
            row_props = box.row()
            col_1 = row_props.column()
            col_2 = row_props.column()
            col_2.label(text="Leg_R:")
            col_2.scale_x = 4
            col_3 = row_props.column()
            col_3.label(text="Leg_L:")
            col_3.scale_x = 4
            col_4 = row_props.column()
            for b in p_bones:
                if 'properties_leg_R' in b.name:
                    for cust_prop in b.keys():
                        if 'flex' in cust_prop:
                            if 'leg' in  cust_prop:
                                col_2.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('flex_leg_', '')),  toggle=True)
                            if 'thigh' in  cust_prop:
                                col_2.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('flex_thigh_', '')),  toggle=True)
            col_2.label(text="Shin_R:")
            for b in p_bones:
                if 'properties_leg_R' in b.name:
                    for cust_prop in b.keys():
                        if 'flex' in cust_prop:
                            if 'shin' in cust_prop:
                                col_2.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('flex_shin_', '')),  toggle=True)
            col_2.label(text="Foot_R:")
            for b in p_bones:
                if 'properties_leg_R' in b.name:
                    for cust_prop in b.keys():
                        if 'flex' in cust_prop:
                            if 'foot' in cust_prop:
                                col_2.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('flex_foot_', '')),  toggle=True)
            for b in p_bones:
                if 'properties_leg_L' in b.name:
                    for cust_prop in b.keys():
                        if 'flex' in cust_prop:
                            if 'leg' in  cust_prop:
                                col_3.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('flex_leg_', '')),  toggle=True)
                            if 'thigh' in  cust_prop:
                                col_3.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('flex_thigh_', '')),  toggle=True)
            col_3.label(text="Shin_L:")
            for b in p_bones:
                if 'properties_leg_L' in b.name:
                    for cust_prop in b.keys():
                        if 'flex' in cust_prop:
                            if 'shin' in cust_prop:
                                col_3.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('flex_shin_', '')),  toggle=True)
            col_3.label(text="Foot_L:")
            for b in p_bones:
                if 'properties_leg_L' in b.name:
                    for cust_prop in b.keys():
                        if 'flex' in cust_prop:
                            if 'foot' in cust_prop:
                                col_3.prop(b, '["{}"]'.format(cust_prop), text = "{}".format(cust_prop.replace('flex_foot_', '')),  toggle=True)
            box.separator()
            row_reset = box.row()
            row_reset.alignment =  'CENTER'
            row_reset.scale_x = 1
            row_reset.operator("blenrig5.reset_dynamic_shaping")

        else:
            row.operator("gui.blenrig_5_tabs", icon="OUTLINER_DATA_ARMATURE", emboss = 1).tab = "gui_rig_flex"
            row.label(text="DYNAMIC SHAPING (Flex Rig Way)")
####### Rig Optimizations
        if "gui_rig_optimize" in arm_data:
            box = layout.column()
            col = box.column()
            row = col.row()
        # expanded box
        if "gui_rig_optimize" in arm_data and arm_data["gui_rig_optimize"]:
            row.operator("gui.blenrig_5_tabs", icon="POSE_HLT", emboss = 1).tab = "gui_rig_optimize"
            row.label(text="RIG OPTIMIZATIONS")
            col.separator
            box = col.box()
            row_props = box.row()
            col_R = row_props.column()
            col_L = row_props.column()
            col_R.prop(arm_data, 'toggle_face_drivers', text="Enable Face Drivers",)
            col_L.prop(arm_data, 'toggle_body_drivers', text="Enable Body Drivers",)
            col_R.prop(arm_data, 'toggle_flex_drivers', text="Enable Flex Scaling",)

        else:
            row.operator("gui.blenrig_5_tabs", icon="POSE_DATA", emboss = 1).tab = "gui_rig_optimize"
            row.label(text="RIG OPTIMIZATIONS")
####### Rigging & Baking
        if "gui_rig_bake" in arm_data:
            props = context.window_manager.blenrig_5_props
            box = layout.column()
            col = box.column()
            row = col.row()
        # expanded box
        if "gui_rig_bake" in arm_data and arm_data["gui_rig_bake"]:
            row.operator("gui.blenrig_5_tabs", icon="PREFERENCES", emboss = 1).tab = "gui_rig_bake"
            row.label(text="RIGGING & BAKING")
            col.separator()
            box = col.box()
            box.prop(arm_data, 'reproportion', text="Reproportion Mode", toggle=True, icon='PREFERENCES')
            col.separator()
            col.label(text="Baking:")
            box = col.box()
            row = box.row()
            row.operator("blenrig5.armature_baker", text="Bake Armature")
            box.label(text="Fix Alignment (Edit Mode):")
            row = box.row()
            row.operator("blenrig5.fix_misaligned_bones", text="Fix Joints")
            row.operator("blenrig5.auto_bone_roll", text="Calc Rolls")
            row.operator("blenrig5.custom_bone_roll", text="Custom Aligns")
            row = box.row()
            row.operator("blenrig5.store_roll_angles", text="Store Roll Angles")
            row.operator("blenrig5.restore_roll_angles", text="Restore Roll Angles")
            row = box.row()
            row.prop(props, "align_selected_only")
            row.prop(arm_data, "use_mirror_x")
            col.label(text="Extras:")
            box = col.box()
            split = box.split()
            row = split.row()
            row.operator("blenrig5.reset_constraints")
            row.operator("blenrig5.reset_deformers", text="Reset Deformers")
            col.separator()
        else:
            row.operator("gui.blenrig_5_tabs", icon="PREFERENCES", emboss = 1).tab = "gui_rig_bake"
            row.label(text="RIGGING & BAKING")

####### Rig Version Info
        col = layout.column()
        row = col.row()
        row.label(text="Armature Ver. " + str(arm_data['rig_version']))

####### Object Baking Panel

class BlenRig_5_mesh_panel(bpy.types.Panel):
    bl_label = "BlenRig 5 Mesh Baking Panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        if not bpy.context.active_object:
            return False
        if (bpy.context.active_object.type in ["MESH"]):
            for mod in bpy.context.active_object.modifiers:
                if (mod.type in ["ARMATURE", "MESH_DEFORM"]):
                    return True

    def draw(self, context):
        props = context.window_manager.blenrig_5_props
        layout = self.layout

        box = layout.column()
        col = box.column()
        row = col.row()
    # expanded box
        col.separator
        row = col.row()
        row.operator("blenrig5.mesh_pose_baker", text="Bake Mesh")
        row.prop(props, "bake_to_shape")

####### Lattice & Curves Panel

class BlenRig_5_lattice_panel(bpy.types.Panel):
    bl_label = "BlenRig 5 Lattice & Curves Panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        if not bpy.context.active_object:
            return False
        if (bpy.context.active_object.type in ["LATTICE", "CURVE"]):
            for mod in bpy.context.active_object.modifiers:
                if (mod.type in ["HOOK"]):
                    return True

    def draw(self, context):
        layout = self.layout

        box = layout.column()
        col = box.column()
        row = col.row()
    # expanded box
        col.separator
        row = col.row()
        row.operator("blenrig5.reset_hooks", text="Reset Hooks")

