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

import bpy, os, math
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty
        )

from .. import types
from ..utils import export_utils
from ..objects.flip_fluid_aabb import AABB


class DomainWorldProperties(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        cls.enable_real_world_size = BoolProperty(
                name="Real World Size",
                description="Enable domain to be scaled to a size in meters",
                default = False,
                options = {'HIDDEN'},
                )
        cls.real_world_size = FloatProperty(
                name="Meters", 
                description="Size of the simulation domain in meters", 
                min=0.001,
                default=10.0,
                precision=3,
                options={'HIDDEN'},
                )
        cls.gravity_type = EnumProperty(
                name="Gravity Type",
                description="Gravity Type",
                items=types.gravity_types,
                default='GRAVITY_TYPE_SCENE',
                options={'HIDDEN'},
                )
        cls.gravity = FloatVectorProperty(
                name="Gravity",
                description="Gravity in X, Y, and Z direction",
                default=(0.0, 0.0, -9.81),
                precision=2,
                size=3,
                subtype='VELOCITY',
                )
        cls.enable_viscosity = BoolProperty(
                name="Enable Viscosity",
                description="Enable viscosity solver",
                default=False,
                )
        cls.viscosity = FloatProperty(
                name="Viscosity", 
                description="Fluid viscosity value", 
                min=0.0,
                default=5.0,
                precision=3,
                )
        cls.enable_surface_tension = BoolProperty(
                name="Enable Surface Tension",
                description="Enable surface tension forces",
                default=False,
                )
        cls.surface_tension = FloatProperty(
                name="Surface Tension", 
                description="Fluid surface tension value", 
                min=0.0,
                default=0.25,
                precision=3,
                )
        cls.surface_tension_accuracy = IntProperty(
                name="Surface Tension Accuracy", 
                description="Amount of accuracy when calculating surface tension. "
                    " Increasing accuracy will produce more accurate surface tension"
                    " results but will require more substeps and increase baking time.", 
                min=0, max=100,
                default=75,
                subtype='PERCENTAGE',
                )
        cls.surface_tension_stability = IntProperty(
                name="Surface Tension Stability", 
                description="Increasing this value may improve stability and reduce"
                    " errors and odd behaviour, but will reduce detail of fluid motion."
                    " This is a parameter for development purposes/testing and will be"
                    " removed in the future.", 
                min=0, max=100,
                default=0,
                subtype='PERCENTAGE',
                )
        cls.enable_sheet_seeding = BoolProperty(
                name="Enable Sheeting Effects",
                description="Fluid sheeting fills in gaps between fluid particles to"
                    " help preserve thin fluid sheets and splashes",
                default=False,
                )
        cls.sheet_fill_rate = FloatProperty(
                name="Sheeting Strength", 
                description="The rate at which new sheeting particles are added."
                    " A higher value will add sheeting particles more often and"
                    " fill in gaps more quickly.", 
                min=0.0, max=1.0,
                default=0.5,
                precision=2,
                )
        cls.sheet_fill_threshold = FloatProperty(
                name="Sheeting Thickness", 
                description="Controls how thick to fill in gaps.", 
                min=0.0, max=1.0,
                soft_min=0.05,
                default=0.1,
                precision=2,
                )
        cls.boundary_friction = FloatProperty(
                name="Boundary Friction", 
                description="Amount of friction on the domain boundary walls", 
                min=0.0,
                max=1.0,
                default=0.0,
                precision=2,
                subtype='FACTOR',
                )

        cls.native_surface_tension_scale = FloatProperty(default=1.0)
        cls.minimum_surface_tension_substeps = IntProperty(default=-1)
        cls.surface_tension_substeps_tooltip = BoolProperty(
                name="Estimated Substeps", 
                description="The estimated number of substeps per frame that the"
                    " simulator will run in order to keep simulation stable during surface"
                    " tension computation. This number will depend on domain resolution"
                    " and size, framerate, amount of surface tension, and surface tension" 
                    " accuracy.", 
                default=True,
                )

        cls.minimum_surface_tension_cfl = FloatProperty(default=1.0)
        cls.maximum_surface_tension_cfl = FloatProperty(default=20.0)


    @classmethod
    def unregister(cls):
        pass


    def scene_update_post(self, scene):
        self._update_surface_tension_info()


    def register_preset_properties(self, registry, path):
        add = registry.add_property
        add(path + ".enable_real_world_size",    "Enable World Scaling",      group_id=0)
        add(path + ".real_world_size",           "World Size",                group_id=0)
        add(path + ".gravity_type",              "Gravity Type",              group_id=0)
        add(path + ".gravity",                   "Gravity",                   group_id=0)
        add(path + ".enable_viscosity",          "Enable Viscosity",          group_id=0)
        add(path + ".viscosity",                 "Viscosity",                 group_id=0)
        add(path + ".enable_surface_tension",    "Enable Surface Tension",    group_id=0)
        add(path + ".surface_tension",           "Surface Tension",           group_id=0)
        add(path + ".surface_tension_accuracy",  "Surface Tension Accuracy",  group_id=0)
        add(path + ".surface_tension_stability", "Surface Tension Stability", group_id=0)
        add(path + ".enable_sheet_seeding",      "Enable Sheeting Effects",   group_id=0)
        add(path + ".sheet_fill_rate",           "Sheeting Strength",         group_id=0)
        add(path + ".sheet_fill_threshold",      "Sheeting Thickness",        group_id=0)
        add(path + ".boundary_friction",         "Boundary Friction",         group_id=0)


    def get_gravity_data_dict(self):
        domain_object = bpy.context.scene.flip_fluid.get_domain_object()
        if self.gravity_type == 'GRAVITY_TYPE_SCENE':
            scene = bpy.context.scene
            return export_utils.get_vector_property_data_dict(scene, scene, 'gravity')
        elif self.gravity_type == 'GRAVITY_TYPE_CUSTOM':
            return export_utils.get_vector_property_data_dict(domain_object, self, 'gravity')


    def _update_surface_tension_info(self):
        domain = bpy.context.scene.flip_fluid.get_domain_object()
        if domain is None:
            return
        dprops = bpy.context.scene.flip_fluid.get_domain_properties()

        bbox = AABB.from_blender_object(domain)
        max_dim = max(bbox.xdim, bbox.ydim, bbox.zdim)
        if dprops.simulation.lock_cell_size:
            unlocked_dx = max_dim / dprops.simulation.resolution
            locked_dx = dprops.simulation.locked_cell_size
            dx = locked_dx
            if abs(locked_dx - unlocked_dx) < 1e-6:
                dx = unlocked_dx
        else:
            dx = max_dim / dprops.simulation.resolution

        world_scale = 1.0
        if dprops.world.enable_real_world_size:
            world_scale = dprops.world.real_world_size / max_dim
        dx = world_scale * dx

        time_scale = dprops.simulation.time_scale
        use_fps = dprops.simulation.use_fps
        if use_fps:
            dt = (1.0 / dprops.simulation.frames_per_second) * time_scale
        else:
            num_frames = bpy.context.scene.frame_end - bpy.context.scene.frame_start + 1
            sim_time = dprops.simulation.end_time - dprops.simulation.start_time
            dt = (sim_time / num_frames) * time_scale

        mincfl, maxcfl = dprops.world.minimum_surface_tension_cfl, dprops.world.maximum_surface_tension_cfl
        accuracy_pct = dprops.world.surface_tension_accuracy / 100.0
        safety_factor = mincfl + (1.0 - accuracy_pct) * (maxcfl - mincfl)

        surface_tension = dprops.world.surface_tension
        eps = 1e-6

        restriction =  safety_factor * math.sqrt(dx * dx * dx) * math.sqrt(1.0 / (surface_tension + eps));
        num_substeps = math.ceil(dt / restriction)

        if self.minimum_surface_tension_substeps != num_substeps:
            self.minimum_surface_tension_substeps = num_substeps


def register():
    bpy.utils.register_class(DomainWorldProperties)


def unregister():
    bpy.utils.unregister_class(DomainWorldProperties)