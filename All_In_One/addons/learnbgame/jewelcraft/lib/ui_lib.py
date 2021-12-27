# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2019  Mikhail Rachinskiy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


import bpy


def popup_report(self, info, title="", icon="INFO"):

    def draw(self, context):
        self.layout.label(text=info)

    self.report({"INFO"}, f"{title}: {info}")

    bpy.context.window_manager.popup_menu(draw, title, icon)


def popup_report_batch(self, info, title="", icon="INFO"):

    def draw(self_local, context):
        layout = self_local.layout

        for x in info:
            layout.label(text=x)
            self.report({"INFO"}, x)

    self.report({"INFO"}, f"{title}:\n")

    bpy.context.window_manager.popup_menu(draw, title, icon)
