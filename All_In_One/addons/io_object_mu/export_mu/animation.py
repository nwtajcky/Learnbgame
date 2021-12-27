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

from ..mu import MuAnimation, MuClip, MuCurve, MuKey
from ..utils import strip_nnn

from .light import light_types

def shader_animations(mat, path):
    animations = {}
    if not mat.animation_data:
        return animations
    for track in mat.animation_data.nla_tracks:
        if not track.strips:
            continue
        anims = []
        strip = track.strips[0]
        for curve in strip.action.fcurves:
            dp = curve.data_path.split(".")
            if dp[0] == "mumatprop" and dp[1] in ["color", "vector", "float2", "float3"]:
                anims.append((track, path, mat))
                break
            elif dp[0] == "mumatprop" and dp[1] == "texture":
                print("don't know how to export texture anims")
        if anims:
            animations[track.name] = anims
    return animations

def object_animations(obj, path):
    animations = {}
    typ = "obj"
    if type(obj) in light_types:
        typ = "lit"
    elif type(obj.data) == bpy.types.Armature:
        typ = "arm"
    if obj.animation_data:
        for track in obj.animation_data.nla_tracks:
            if track.strips:
                animations[track.name] = [(track, path, typ)]
        # if nla_tracks exist, then action will be an nla track that has been
        # opened for tweaking, so export action only if there are no nla tracks
        if not animations and obj.animation_data.action:
            action = obj.animation_data.action
            animations[action.name] = [(action, path, typ)]
    return animations

def extend_animations(animations, anims):
    for a in anims:
        if a not in animations:
            animations[a] = []
        animations[a].extend(anims[a])

def collect_animations(obj, path=""):
    animations = {}
    if path:
        path += "/"
    path += strip_nnn(obj.name)
    extend_animations(animations, object_animations (obj, path))
    if type(obj.data) == bpy.types.Mesh:
        for mat in obj.data.materials:
            if mat: # material slot may be empty
                extend_animations(animations, shader_animations(mat, path))
    if type(obj.data) in light_types:
        extend_animations(animations, object_animations (obj.data, path))
    for o in obj.children:
        extend_animations(animations, collect_animations(o, path))
    return animations

def find_path_root(animations):
    paths = {}
    for clip in animations:
        for data in animations[clip]:
            objects = data[1].split("/")
            p = paths
            for o in objects:
                if not o in p:
                    p[o] = {}
                p = p[o]
            # flag the path as having animation data so that the first object
            # whith animation data is found when all objects form a vine
            # instead of a tree
            p[None] = {}
    path_root = ""
    p = paths
    while len(p) == 1:
        o = list(p)[0]
        if o == None:
            break
        if path_root:
            path_root += "/"
        path_root += o
        p = p[o]
    return path_root

def make_key(key, mult):
    fps = bpy.context.scene.render.fps
    mukey = MuKey()
    x, y = key.co
    mukey.time = (x - bpy.context.scene.frame_start) / fps
    mukey.value = y * mult
    dx, dy = key.handle_left
    dx = (x - dx) / fps
    dy = (y - dy) * mult
    t1 = dy / dx
    dx, dy = key.handle_right
    dx = (dx - x) / fps
    dy = (dy - y) * mult
    t2 = dy / dx
    mukey.tangent = t1, t2
    mukey.tangentMode = 0
    return mukey

property_map = {
    "location":(
        ("m_LocalPosition.x", 1, 0),
        ("m_LocalPosition.z", 1, 0),
        ("m_LocalPosition.y", 1, 0),
    ),
    "rotation_quaternion":(
        ("m_LocalRotation.w", 1, 0),
        ("m_LocalRotation.x", -1, 0),
        ("m_LocalRotation.z", -1, 0),
        ("m_LocalRotation.y", -1, 0),
    ),
    "scale":(
        ("m_LocalScale.x", 1, 0),
        ("m_LocalScale.z", 1, 0),
        ("m_LocalScale.y", 1, 0),
    ),
    "color":(
        ("m_Color.r", 1, 2),
        ("m_Color.g", 1, 2),
        ("m_Color.b", 1, 2),
        ("m_Color.a", 1, 2),#probably not used
    ),
    "energy":(
        ("m_Intensity", 1, 2),
    ),
}

vector_map={
    "color": (".r", ".g", ".b", ".a"),
    "vector": (".x", ".y", ".z", ".w"),
}

def make_curve(mu, muobj, curve, path, typ):
    mucurve = MuCurve()
    mucurve.path = path
    if typ in {"obj", "lit"}:
        property, mult, ctyp = property_map[curve.data_path][curve.array_index]
    elif typ == "arm":
        bpath, dpath = curve.data_path.rsplit(".", 1)
        bone_path = muobj.bone_paths[bpath]
        mucurve.path = path + bone_path[len(muobj.path):]
        property, mult, ctyp  = property_map[dpath][curve.array_index]
    elif type(typ) == bpy.types.Material:
        dp = curve.data_path.split(".")
        v = {}
        str = "v['property'] = typ.%s.name" % (".".join(dp[:-1]))
        exec (str, {}, locals())
        property = v["property"]
        mult = 1
        if dp[1] in ["color", "vector"]:
            property += vector_map[dp[1]][curve.array_index]
        ctyp = 1
    mucurve.property = property
    # 0 = transform, 1 = material, 2 = light, 3 = audio source
    mucurve.type = ctyp
    mucurve.wrapMode = (8, 8)
    mucurve.keys = []
    for key in curve.keyframe_points:
        mucurve.keys.append(make_key(key, mult))
    return mucurve

def make_animations(mu, animations, anim_root):
    anim = MuAnimation()
    anim.clip = ""
    anim.autoPlay = False
    for clip_name in animations:
        clip = MuClip()
        if not anim.clip:   #FIXME how to select when multiple?
            anim.clip = clip_name
        clip.name = clip_name
        clip.lbCenter = (0, 0, 0)
        clip.lbSize = (0, 0, 0)
        clip.wrapMode = 0   #FIXME
        for data in animations[clip_name]:
            track, path, typ = data
            muobj = mu.object_paths[path]
            path = path[len(anim_root) + 1:]
            if type(track) is bpy.types.Action:
                action = track
            else:
                action = track.strips[0].action
            for curve in action.fcurves:
                clip.curves.append(make_curve(mu, muobj, curve, path, typ))
        anim.clips.append(clip)
    return anim
