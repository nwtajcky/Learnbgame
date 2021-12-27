# -*- coding: utf-8 -*-
import bpy
from g_tools.nbf import *
from g_tools.WORLD_CONSTANTS import *

#########################################################decorators
def get_active_obj():
    return bpy.context.scene.objects.active
    
def get_sel_objs(exclude_active = False):
    """
    選択中なオブジェクトを検索する
    """
    obj = get_active_obj()
    res = (o for o in bpy.context.scene.objects if (o.select))
    if exclude_active:
        res = tuple(o for o in res if (o != obj))
    return res

def get_sel_obj():
    """
    アクティブオブジェクトではないかつ選択中なオブジェクトを検索して、一番目に見つかるものを戻り値とする
    """
    return get_sel_objs(exclude_active = True)[0]

def defac(f):
    """
    アクティブオブジェクトをデフォルトのオブジェクトにしてくれる関数
    Set a function to use the active object by default
    """
    def default_activand(*args,obj = None,**kwargs):
        if obj == None:
            obj = bpy.context.scene.objects.active
        return f(*args,obj = obj,**kwargs,)
    return default_activand

def defac2(f):
    """
    アクティブオブジェクトと（アクティブ以外の）選択されてるオブジェクト一個をデフォルトのオブジェクトにしてくれる関数
    Set a function to use the active object by default
    """
    def default_activand(*args,obj = None,sobj = None,**kwargs):
        if obj == None:
            obj = bpy.context.scene.objects.active
        if sobj == None:        
            sobj = get_sel_obj_any()
        return f(*args,obj = obj,sobj = sobj,**kwargs,)
    return default_activand

def moderate(mode):
    mode = mode.upper()
    def moderator(f):
        def moderated(*args,**kwargs):
            original_mode = set_mode(mode)
            res = f(*args,**kwargs)
            set_mode(original_mode)
            return res
        return moderated
    return moderator
    
#########################################################layers
def get_visible_layers(obj = None,scn = None):
    vislayers = tuple(filter(lambda x: obj.layers[x]*scn.layers[x],range((20))))
    return (vislayers)
    
def sync_layers(obj,sobj):
    for i in rlen(obj.layers):
        sobj.layers[i] = obj.layers[i]

#########################################################vertex groups
def make_group(groupname = "Bone"):
    ct = bpy.context
    scn = ct.scene
    data = bpy.data
    objs = scn.objects
    obj = objs.active
    vgroups = obj.vertex_groups

    newgroup = vgroups.new(name=groupname)
    return newgroup


#########################################################object groups
def make_group(name = "Group"):
    dgrps = bpy.data.groups
    ng = dgrps.new(name = name)
    return ng

@tuplize
def add_objs_group(objs,target_group = None,make_new = False,new_name = "Group"):
    dgrps = bpy.data.groups
    if make_new or (target_group == None):
        g = make_group(name = new_name)
    else:
        g = dgrps[target_group]
    return map(acc(g,"g.objects.link"),objs)


#########################################################bpy object manipulation
def get_ac():
    return bpy.context.scene.objects.active

def set_ac(obj):
    ac = bpy.context.scene.objects.active
    bpy.context.scene.objects.active = obj
    return ac
    
def set_mode(new_mode):
    mode = bpy.context.scene.objects.active.mode
    bpy.ops.object.mode_set(mode=new_mode)
    return mode
    
def set_context(newctx):
    """
    参照までに、可能なcontextの種類:
    'VIEW_3D', 'TIMELINE', 'GRAPH_EDITOR', 'DOPESHEET_EDITOR', 'NLA_EDITOR', 'IMAGE_EDITOR', 'CLIP_EDITOR', 'SEQUENCE_EDITOR', 'NODE_EDITOR', 'TEXT_EDITOR', 'LOGIC_EDITOR', 'PROPERTIES', 'OUTLINER', 'USER'（？）
    注意:最後だけ何故か不正の様。
    """
    ctx = bpy.context
    scn = ctx.scene
    area = ctx.area
    old_type = area.type
    area.type = newctx
    return old_type
    
def get_obj_type_args(obj_name,obj_type,sub_type):
    """これは酷い。見なかったことにしてください。"""
    default_lst = ('meshes','new',)
    tlst = (
    "EMPTY",
    "MESH",
    "ARMATURE",
    "CURVE",
    "METABALL",
    "LATTICE",
    "LAMP",)
    if obj_type not in tlst:
        raise ValueError("Specified object type is invalid")
    def pluralize(s):
        return s + "s" if s[-1] in 'aeioulpt' else s + "es" 
    
    fdict = {t:[pluralize(t.lower()),'new',[obj_name]] for t in tlst}
    
    subtype_dict = {
    "CURVE":["CURVE","SURFACE","FONT"],
    "LAMP":["POINT","SUN","SPOT","HEMI","AREA"]
    }
    

    fdict["LAMP"][2].append("AREA")
    fdict["CURVE"][2].append("CURVE")
    
    if sub_type != "":
        sub_type_idx = subtype_dict[obj_type].index(sub_type)
        sub_type = subtype_dict[obj_type][sub_type_idx]
        fdict[obj_type][2][-1] = sub_type
        
    return fdict[obj_type]

def make_obj(name = "new_obj",type = "MESH",subtype = "",do_link = True,layer_sync = True):
    """
    オブジェクトの作成を補助してくれる関数
    """
    ctx = bpy.context
    scn = ctx.scene
    dat = bpy.data
    dobjs = bpy.data.objects
    objs = bpy.context.scene.objects
    
    coll_name,create_func_name,create_func_args = get_obj_type_args(name,type,subtype)
    if type == "EMPTY":
        ndata = None
    else:
        ndata = getattr(getattr(dat,coll_name),create_func_name)(*create_func_args)
    nobj = dobjs.new(name = name,object_data = ndata)
    
    if do_link:
        objs.link(nobj)
        
    if layer_sync:
        for i in rlen(scn.layers):
            nobj.layers[i] = scn.layers[i]
    
    return nobj
	
def make_arm(name = "New_Armature",do_link = True):
    new_arm = make_obj(name = name,type = "ARMATURE",do_link = do_link)
    return new_arm

def make_cam(name = "New_Camera"):
    scn = bpy.context.scene
    objs = scn.objects
    cam = bpy.data.cameras.new(name = name)
    camo = bpy.data.objects.new(name = name,object_data = cam)
    objs.link(camo)
    return camo
    
def dupli_obj(link = True, obj = None,link_data = False,obj_name = "duplicated"):
    newobj = obj.copy()
    if link_data:
        newobj.data = obj.data
    else:
        newobj.data = obj.data.copy()
    if link == True:
        bpy.context.scene.objects.link(newobj)
    elif link == False:
        pass
    newobj.name = obj.name + "_" + obj_name
    return newobj

def make_objs(coords,scale = 1,name = "",count = -1,type = "EMPTY"):
    """Creates things at coordinates.
    Pass a count > 0 with the coords to only create some of the coordinates.
    Pass None and a count to create without coordinate setting."""
    if name == "":
        name = "new_" + type
    if count > 0:
        if coords == None:
            return tmap(lambda x: make_obj(name = name,obj_type = type),range(count))
        else:
            return tmap(lambda x: make_obj(coords = coords[x],obj_type = type,obj_name = name),range(count))
    return from_coords(coords,name=name,obj_type = type,**{"scale":scale})
    
def from_coords(coords,name = "new_obj",obj_type = "EMPTY",prop_name = "location",*args,**kwargs):
    '''
    Make a series of objects from given coordinates.
    **Kwargs treated as property arguments.
    '''
    res = list(map(lambda x: make_obj(obj_type = obj_type,obj_name = name),coords))
    any(map(lambda r: setattr(res[r],prop_name,coords[r]),rlen(res)))
    any(map(lambda r: dict2attr(kwargs,r),res))
    return res
    

defac_funcs = (
dupli_obj,get_visible_layers,
)
for f in defac_funcs:
    globals()[f.__name__] = defac(f)