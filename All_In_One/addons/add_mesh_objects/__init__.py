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
# Contributed to by
# meta-androcto #

bl_info = {
    "name": "Mesh Objects",
    "author": "Multiple Authors",
    "version": (0, 1),
    "blender": (2, 6, 3),
    "location": "View3D > Add > Mesh > Mesh Objects",
    "description": "Add extra object types",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}


if "bpy" in locals():
    import imp
    imp.reload(add_naca_airfoil_2)
    imp.reload(add_mesh_ogive)
    imp.reload(add_mesh_teapot)

else:
    from . import add_naca_airfoil_2
    from . import add_mesh_ogive
    from . import add_mesh_teapot

import bpy


class INFO_MT_mesh_objects_add(bpy.types.Menu):
    # Define the "mesh objects" menu
    bl_idname = "INFO_MT_mesh_objects_add"
    bl_label = "Mesh Objects"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("mesh.make_airfoil",
            text="Airfoil")
        layout.operator("mesh.add_ogive",
            text="Ogive")
        layout.operator("mesh.primitive_teapot_add",
            text="Teapot+")

# Register all operators and panels

# Define "Extras" menu
def menu_func(self, context):
    self.layout.menu("INFO_MT_mesh_objects_add", icon="PLUGIN")


def register():
    bpy.utils.register_module(__name__)

    # Add "Extras" menu to the "Add Mesh" menu
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)

    # Remove "Extras" menu from the "Add Mesh" menu.
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()
