# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 PBRTv3 Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond
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
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
#
from ... import PBRTv3Addon
from ...ui.materials import pbrtv3_material_sub


@PBRTv3Addon.addon_register_class
class ui_material_mirror(pbrtv3_material_sub):
    bl_label = 'PBRTv3 Mirror Material'

    PBRTv3_COMPAT = {'mirror'}

    display_property_groups = [
        ( ('material', 'pbrtv3_material'), 'pbrtv3_mat_mirror' )
    ]

    def draw_ior_menu(self, context):
        """
        This is a draw callback from property_group_renderer, due
        to ef_callback item in pbrtv3_mat_<mat>.properties
        """

        lmg = context.material.pbrtv3_material.pbrtv3_mat_mirror

        if lmg.filmindex_floatvalue == lmg.filmindex_presetvalue:
            menu_text = lmg.filmindex_presetstring
        else:
            menu_text = '-- Choose IOR preset --'

        cl = self.layout.column(align=True)
        cl.menu('PBRTv3_MT_ior_presets', text=menu_text)
