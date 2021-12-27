# vim:ts=4:et
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

# <pep8 compliant>

import bpy
import bmesh

def create_uvs(mu, uvs, bm, name):
    layer = bm.loops.layers.uv.new(name)
    for face in bm.faces:
        for loop in face.loops:
            loop[layer].uv = uvs[loop.vert.index]

def create_mesh(mu, mumesh, name):
    mesh = bpy.data.meshes.new(name)
    faces = []
    for sm in mumesh.submeshes:
        faces.extend(sm)
    bm = bmesh.new()
    bv = [None] * len(mumesh.verts)
    for i, v in enumerate(mumesh.verts):
        bv[i] = bm.verts.new(v)
    if mumesh.normals:
        for i, n in enumerate(mumesh.normals):
            bv[i].normal = n
    #FIXME how to set tangents?
    #if mumesh.tangents:
    #    for i, t in enumerate(mumesh.tangents):
    #        bv[i].tangent = t
    bm.verts.index_update()
    bm.verts.ensure_lookup_table()
    for f in faces:
        try:
            bm.faces.new([bv[i] for i in f])
        except ValueError:
            print(name + ": duplicate face?", f)
    bm.faces.index_update()
    bm.faces.ensure_lookup_table()
    if mumesh.uvs:
        create_uvs(mu, mumesh.uvs, bm, "UV")
    if mumesh.uv2s:
        create_uvs(mu, mumesh.uv2s, bm, "UV2")
    bm.to_mesh(mesh)
    return mesh
