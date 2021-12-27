bl_info = {
	"name": "Pie Save",
	"description": "Save import export Pie",
	"author": "Vaughan Ling",
	"version": (0, 1, 0),
	"blender": (2, 80, 0),
	"location": "",
	"warning": "",
	"category": "Learnbgame",
	}

import bpy
from bpy.types import (
		Menu,
		Operator,
		)
import os

class VIEW3D_PIE_SAVE(Menu):
	bl_idname = "pie.save"
	bl_label = "Save"

	def draw(self, context):
		layout = self.layout
		pie = layout.menu_pie()
		pie.operator("wm.link", text = "Link/Reference", icon='LINK_BLEND')
		pie.operator("wm.save_without_prompt", text="Save", icon='FILE_TICK')
		pie.operator("wm.save_as_mainfile", text="Save As...", icon='NONE')
		pie.operator("wm.open_mainfile", text="Open file", icon='FILE_FOLDER')
		pie.operator("wm.read_homefile", text="New", icon='FILE_NEW')
		pie.separator()
		pie.menu("TOPBAR_MT_file_open_recent")

def register():
	bpy.utils.register_class(VIEW3D_PIE_SAVE)


def unregister():
	bpy.utils.unregister_class(VIEW3D_PIE_SAVE)

if __name__ == "__main__":
	register()
