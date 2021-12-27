# Blender FLIP Fluid Add-on
# Copyright (C) 2019 Ryan L. Guy
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "FLIP Fluids",
    "description": "A FLIP Fluid Simulation Tool for Blender (v9.0.5.3 Experimental 01-FEB-2019)",
    "author" : "Ryan Guy <ryan.l.guy[at]gmail.com>, Dennis Fassbaender <info[at]df-videos.de>",
    "version" : (9, 0, 5),
    "blender" : (2, 80, 0),
    "location" : "Properties > Physics > FLIP Fluid",
    "warning" : "",
    "wiki_url" : "https://github.com/rlguy/Blender-FLIP-Fluids/wiki",
    "tracker_url" : "https://github.com/rlguy/Blender-FLIP-Fluids/wiki/Guidelines-for-Reporting-Bugs-and-Issues",
    "category" : "Animation"
}

if "bpy" in locals():
    import importlib
    reloadable_modules = [
        'utils',
        'objects',
        'materials',
        'properties',
        'operators',
        'ui',
        'presets',
        'export',
        'bake',
        'render',
        'exit_handler'
    ]
    for module_name in reloadable_modules:
        if module_name in locals():
            importlib.reload(locals()[module_name])

import bpy, atexit, shutil, os
from bpy.props import (
        PointerProperty,
        StringProperty
        )

from . import (
        utils,
        objects,
        materials,
        properties,
        operators,
        ui,
        presets,
        export,
        bake,
        render,
        exit_handler
        )

from .utils import version_compatibility_utils as vcu


@bpy.app.handlers.persistent
def scene_update_post(scene):
    properties.scene_update_post(scene)
    render.scene_update_post(scene)
    materials.scene_update_post(scene)


@bpy.app.handlers.persistent
def frame_change_pre(scene):
    properties.frame_change_pre(scene)
    render.frame_change_pre(scene)


@bpy.app.handlers.persistent
def render_pre(scene):
    render.render_pre(scene)


@bpy.app.handlers.persistent
def render_post(scene):
    render.render_post(scene)


@bpy.app.handlers.persistent
def render_cancel(scene):
    render.render_cancel(scene)


@bpy.app.handlers.persistent
def render_complete(scene):
    render.render_complete(scene)


@bpy.app.handlers.persistent
def load_pre(nonedata):
    properties.load_pre()


@bpy.app.handlers.persistent
def load_post(nonedata):
    properties.load_post()
    materials.load_post()
    presets.load_post()
    exit_handler.load_post()
    

@bpy.app.handlers.persistent
def save_pre(nonedata):
    properties.save_pre()


@bpy.app.handlers.persistent
def save_post(nonedata):
    properties.save_post()
    exit_handler.save_post()


def on_exit():
    exit_handler.on_exit()


def register():
    objects.register()
    materials.register()
    properties.register()
    operators.register()
    ui.register()
    presets.register()

    if vcu.is_blender_28():
        bpy.app.handlers.depsgraph_update_post.append(scene_update_post)
    else:
        bpy.app.handlers.scene_update_post.append(scene_update_post)

    bpy.app.handlers.frame_change_pre.append(frame_change_pre)
    bpy.app.handlers.render_pre.append(render_pre)
    bpy.app.handlers.render_post.append(render_post)
    bpy.app.handlers.render_cancel.append(render_cancel)
    bpy.app.handlers.render_complete.append(render_complete)
    bpy.app.handlers.load_pre.append(load_pre)
    bpy.app.handlers.load_post.append(load_post)
    bpy.app.handlers.save_pre.append(save_pre)
    bpy.app.handlers.save_post.append(save_post)
    atexit.register(on_exit)


def unregister():
    objects.unregister()
    materials.unregister()
    properties.unregister()
    operators.unregister()
    ui.unregister()
    presets.unregister()

    if vcu.is_blender_28():
        bpy.app.handlers.depsgraph_update_post.remove(scene_update_post)
    else:
        bpy.app.handlers.scene_update_post.remove(scene_update_post)

    bpy.app.handlers.frame_change_pre.remove(frame_change_pre)
    bpy.app.handlers.render_pre.remove(render_pre)
    bpy.app.handlers.render_post.remove(render_post)
    bpy.app.handlers.render_cancel.remove(render_cancel)
    bpy.app.handlers.render_complete.remove(render_complete)
    bpy.app.handlers.load_pre.remove(load_pre)
    bpy.app.handlers.load_post.remove(load_post)
    bpy.app.handlers.save_pre.remove(save_pre)
    bpy.app.handlers.save_post.remove(save_post)
    atexit.unregister(on_exit)

