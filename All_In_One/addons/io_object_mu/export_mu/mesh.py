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
from mathutils import Vector

from ..mu import MuMesh, MuRenderer
from ..utils import collect_modifiers

from .material import make_material

from . import export

from pprint import pprint

def split_face(mesh, index, vertex_map):
    face = mesh.polygons[index]
    s, e = face.loop_start, face.loop_start + face.loop_total
    fv = list(vertex_map[s:e])
    tris = []
    for i in range(1, len(fv) - 1):
        tri = (fv[0], fv[i], fv[i+1])
        tris.append(tri)
    return tris

def build_submeshes(mesh):
    submeshes = []
    submesh = []
    for i in range(len(mesh.polygons)):
        submesh.append(i)
    submeshes.append(submesh)
    return submeshes

def make_tris(mesh, submeshes, vertex_map):
    for sm in submeshes:
        i = 0
        while i < len(sm):
            tris = split_face(mesh, sm[i], vertex_map)
            sm[i:i+1] = tris
            i += len(tris)
    return submeshes

def get_mesh(obj):
    #FIXME mesh = obj.to_mesh(bpy.context.scene, True, 'RENDER')
    modifiers = collect_modifiers(obj)
    for mod in modifiers:
        mod.show_viewport = False
    mesh = obj.to_mesh(bpy.context.depsgraph, True)
    for mod in modifiers:
        mod.show_viewport = True
    return mesh

def get_vertex_data(mu, mesh, obj):
    vertdata = [None] * len(mesh.loops)
    if not vertdata:
        return vertdata
    if mesh.loops[0].normal == Vector():
        mesh.calc_normals()
    tangentsOk = True
    if mesh.uv_layers:
        #FIXME active UV layer?
        uvs = list(map(lambda a: Vector(a.uv).freeze(), mesh.uv_layers[0].data))
        try:
            mesh.calc_tangents(uvmap = mesh.uv_layers[0].name)
        except RuntimeError:
            tangentsOk = False
            mu.messages.append(({'WARNING'}, "tangents not exported due to N-gons in the mesh: " + obj.name))
    else:
        uvs = [None] * len(mesh.loops)
    if mesh.vertex_colors:
        #FIXME active colors?
        colors = list(map(lambda a: Vector(a.color).freeze(), mesh.vertex_colors[0].data))
    else:
        colors = [None] * len(mesh.loops)
    for i in range(len(mesh.loops)):
        v = mesh.loops[i].vertex_index
        n = Vector(mesh.loops[i].normal).freeze()
        uv = uvs[i]
        col = colors[i]
        if uv != None and tangentsOk:
            t = Vector(mesh.loops[i].tangent).freeze()
            bts = mesh.loops[i].bitangent_sign
        else:
            t = None
            bts = None
        vertdata[i] = (v, n, uv, t, bts, col)
    return vertdata

def make_vertex_map(vertex_data):
    vdict = {}
    vmap = []
    for i, v in enumerate(vertex_data):
        #print(i, v in vdict)
        if v not in vdict:
            vdict[v] = len(vdict)
        vmap.append(vdict[v])
    return vmap, len(vdict)

def make_mumesh(mesh, submeshes, vertex_data, vertex_map, num_verts):
    verts = [None] * num_verts
    uvs = [None] * num_verts
    normals = [None] * num_verts
    tangents = [None] * num_verts
    bitangents = [None] * num_verts
    colors = [None] * num_verts
    for i, vind in enumerate(vertex_map):
        v, n, uv, t, bts, col = vertex_data[i]
        verts[vind] = v
        normals[vind] = n
        uvs[vind] = uv
        tangents[vind] = t
        bitangents[vind] = bts
        colors[vind] = col
    for i, v in enumerate(verts):
        verts[i] = mesh.vertices[v].co
    if tangents[0] != None:
        for i, t in enumerate(tangents):
            tangents[i] = tuple(t) + (bitangents[i],)
    mumesh = MuMesh()
    mumesh.submeshes = submeshes
    mumesh.verts = verts
    if normals[0] != None:
        mumesh.normals = normals
    if uvs[0] != None:
        mumesh.uvs = uvs
    if tangents[0] != None:
        mumesh.tangents = tangents
    if colors[0] != None:
        mumesh.colors = colors
    return mumesh

def make_mesh(mu, obj):
    mesh = get_mesh(obj)
    vertex_data = get_vertex_data(mu, mesh, obj)
    vertex_map, num_verts = make_vertex_map(vertex_data)
    submeshes = build_submeshes(mesh)
    submeshes = make_tris(mesh, submeshes, vertex_map)
    #pprint(submeshes)
    mumesh = make_mumesh(mesh, submeshes, vertex_data, vertex_map, num_verts)
    return mumesh

def mesh_materials(mu, mesh):
    materials = []
    for mat in mesh.materials:
        if mat.mumatprop.shaderName:
            if mat.name not in mu.materials:
                mu.materials[mat.name] = make_material(mu, mat)
            materials.append(mu.materials[mat.name].index)
    return materials

def make_renderer(mu, mesh):
    rend = MuRenderer()
    #FIXME shadows
    rend.materials = mesh_materials(mu, mesh)
    if not rend.materials:
        return None
    return rend

def mesh_bones(obj, mumesh, armature):
    boneset = set()
    for bone in armature:
        boneset.add(bone.name)
    bones = []
    boneindices = {}
    for grp in obj.vertex_groups:
        if grp.name in boneset:
            boneindices[grp.name] = len(bones)
            bones.append(grp.name)
    for vgrp in mumesh.groups:
        weights = []
        for i in len(vgrp):
            gname = obj.vertex_groups[vgrp[i].group].name
            if gname in boneindices:
                weights.append((boneindices[gname], vgrp[i].weight))
        weights.sort(key=lambda w: w[1])
        weights.reverse()
        if len(weights) < 4:
            weights += [(0,0)]*4 - len(weights)
        print(weights)
    return bones

def handle_mesh(obj, muobj, mu):
    muobj.shared_mesh = make_mesh(mu, obj)
    muobj.renderer = make_renderer(mu, obj.data)
    return muobj

def handle_skinned_mesh(obj, muobj, mu, armature):
    smr = MuSkinnedMeshRenderer()
    smr.mesh = make_mesh(mu, obj)
    smr.bones = mesh_bones(obj, smr.mesh, armature)
    smr.materials = mesh_materials(mu, obj.data)
    #FIXME center, size, quality, updateWhenOffscreen
    muobj.skinned_mesh_renderer = smr
    if hasattr(muobj, "renderer"):
        delattr(muobj, "renderer")
    if hasattr(muobj, "shared_mesh"):
        delattr(muobj, "shared_mesh")
    return muobj

type_handlers = {
    bpy.types.Mesh: handle_mesh,
}
