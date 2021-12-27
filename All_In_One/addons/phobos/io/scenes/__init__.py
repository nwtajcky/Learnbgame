#!/usr/bin/python3.5
# coding=utf-8

# -------------------------------------------------------------------------------
# This file is part of Phobos, a Blender Add-On to edit robot models.
# Copyright (C) 2018 University of Bremen & DFKI GmbH Robotics Innovation Center

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# -------------------------------------------------------------------------------

"""
Parses the scene entities at import and provides them as :data:`scene_types`.
"""

import os
import importlib.util

scene_types = dict()
structure_export_folders = []

# this creates a dict entry for every python file in this subfolder
for filename in os.listdir(os.path.dirname(__file__)):
    mod_name, file_ext = os.path.splitext(os.path.split(filename)[-1])

    # only take .py files and ignore this __init__ file
    if (filename != os.path.split(__file__)[-1]) and (file_ext.lower() == '.py'):
        modpath = os.path.join(os.path.dirname(__file__), filename)

        # load the module from file and source it to access its data
        spec = importlib.util.spec_from_file_location(filename, modpath)
        py_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(py_mod)

        # try reading the entity dictionary and add it to the existing entities
        if hasattr(py_mod, 'scene_type_dict'):
            scene_types.update(py_mod.scene_type_dict.copy())
            print('Registered scene plugin:', list(py_mod.scene_type_dict.keys()))
        else:
            print(
                'ERROR in scenes/__init__: "' + filename + '" has no valid scene plugin interface.'
            )
