# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
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
from ... import LuxRenderAddon
from ...ui.materials import luxrender_material_base


@LuxRenderAddon.addon_register_class
class ui_luxrender_mat_compositing(luxrender_material_base):
    bl_label = 'LuxRender Material Compositing'

    display_property_groups = [
        ( ('material', 'luxrender_material'), 'luxrender_mat_compositing' )
    ]

    @classmethod
    def poll(cls, context):
        if not hasattr(context.scene, 'luxrender_integrator'):
            return False
        return context.scene.luxrender_integrator.surfaceintegrator == 'distributedpath' and super().poll(context)
