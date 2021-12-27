import bpy
import os
import tempfile
import subprocess
import platform

def BooleanaOsteoDef(self, context):

    context = bpy.context
#    obj = context.active_object
    scn = context.scene

    tmpdir = tempfile.mkdtemp()

    objetos_selecionados = [ o for o in bpy.context.scene.objects if o.select ]

    A = objetos_selecionados[1]
    B = objetos_selecionados[0]

    # Cria objeto A
    bpy.ops.object.select_all(action='DESELECT')
    A.select = True
    bpy.context.scene.objects.active = A

    bpy.ops.object.modifier_add(type='TRIANGULATE')
    bpy.ops.export_mesh.off(filepath=tmpdir+"/A.off")
    bpy.ops.object.modifier_remove(modifier="Triangulate")
    bpy.ops.object.move_to_layer(layers=(False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False, False, False))

    # Cria objeto B
    bpy.ops.object.select_all(action='DESELECT')
    B.select = True
    bpy.context.scene.objects.active = B

    bpy.ops.object.modifier_add(type='TRIANGULATE')
    bpy.ops.export_mesh.off(filepath=tmpdir+"/B.off")
    bpy.ops.object.modifier_remove(modifier="Triangulate")
    bpy.ops.object.move_to_layer(layers=(False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False, False, False))

    bpy.ops.object.select_all(action='DESELECT')

    # Booleana
    if platform.system() == "Linux":
        subprocess.call('~/Programs/OrtogOnBlender/Cork/./cork -diff '+tmpdir+'/A.off '+tmpdir+'/B.off '+tmpdir+'/Result.off', shell=True)
        bpy.ops.import_mesh.off(filepath=tmpdir+"/Result.off")
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

    if platform.system() == "Windows":
        subprocess.call('C:\OrtogOnBlender\Cork\wincork.exe -diff '+tmpdir+'/A.off '+tmpdir+'/B.off '+tmpdir+'/Result.off', shell=True)
        bpy.ops.import_mesh.off(filepath=tmpdir+"/Result.off")
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

    if platform.system() == "Darwin":
        subprocess.call('/OrtogOnBlender/Cork/./cork -diff '+tmpdir+'/A.off '+tmpdir+'/B.off '+tmpdir+'/Result.off', shell=True)
        bpy.ops.import_mesh.off(filepath=tmpdir+"/Result.off")
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')


    bpy.ops.mesh.separate(type='LOOSE')

    objetos_selecionados = [ o for o in bpy.context.scene.objects if o.select ]

    for i in objetos_selecionados:
        bpy.ops.object.select_all(action='DESELECT')
        i.select = True
        bpy.context.scene.objects.active = i
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')


class BooleanaOsteo(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.booleana_osteo"
    bl_label = "Importa fatias de tomografia DICOM"
    
    def execute(self, context):
       BooleanaOsteoDef(self, context)
       return {'FINISHED'}

# Separa mandibula

def BooleanaMandDef(self, context):

    context = bpy.context
    scn = context.scene

    tmpdir = tempfile.mkdtemp()

    #objetos_selecionados = [ o for o in bpy.context.scene.objects if o.select ]

    A = bpy.data.objects['Bones']
    B = context.active_object #objetos_selecionados[0]

# Infla o objeto    
    bpy.ops.object.mode_set(mode = 'EDIT') 
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action = 'SELECT')
    
    bpy.ops.transform.shrink_fatten(value=-1.61748, use_even_offset=False, mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

    bpy.ops.object.mode_set(mode = 'OBJECT')
    
    bpy.ops.object.modifier_add(type='REMESH')
    bpy.context.object.modifiers["Remesh"].mode = 'SMOOTH'
    bpy.context.object.modifiers["Remesh"].octree_depth = 7

    # Seleciona objeto A
    A.hide = False
    bpy.ops.object.select_all(action='DESELECT')
    A.select = True
    bpy.context.scene.objects.active = A

    bpy.ops.object.modifier_add(type='TRIANGULATE')
    bpy.ops.export_mesh.off(filepath=tmpdir+"/A.off")
    bpy.ops.object.modifier_remove(modifier="Triangulate")
    bpy.ops.object.move_to_layer(layers=(False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False, False, False))

    # Cria objeto B
    bpy.ops.object.select_all(action='DESELECT')
    B.select = True
    bpy.context.scene.objects.active = B

    bpy.ops.object.modifier_add(type='TRIANGULATE')
    bpy.ops.export_mesh.off(filepath=tmpdir+"/B.off")
    bpy.ops.object.modifier_remove(modifier="Triangulate")
    bpy.ops.object.move_to_layer(layers=(False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False, False, False))

    bpy.ops.object.select_all(action='DESELECT')

    # Booleana
    if platform.system() == "Linux":
        subprocess.call('~/Programs/OrtogOnBlender/Cork/./cork -diff '+tmpdir+'/A.off '+tmpdir+'/B.off '+tmpdir+'/Skull.off', shell=True)
        bpy.ops.import_mesh.off(filepath=tmpdir+"/Skull.off")
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        
        subprocess.call('~/Programs/OrtogOnBlender/Cork/./cork -isct '+tmpdir+'/A.off '+tmpdir+'/B.off '+tmpdir+'/Mandible.off', shell=True)
        bpy.ops.import_mesh.off(filepath=tmpdir+"/Mandible.off")
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

    if platform.system() == "Windows":
        subprocess.call('C:\OrtogOnBlender\Cork\wincork.exe -diff '+tmpdir+'/A.off '+tmpdir+'/B.off '+tmpdir+'/Skull.off', shell=True)
        bpy.ops.import_mesh.off(filepath=tmpdir+"/Skull.off")
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        
        subprocess.call('C:\OrtogOnBlender\Cork\wincork.exe -isct '+tmpdir+'/A.off '+tmpdir+'/B.off '+tmpdir+'/Mandible.off', shell=True)
        bpy.ops.import_mesh.off(filepath=tmpdir+"/Mandible.off")
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

    if platform.system() == "Darwin":
        subprocess.call('/OrtogOnBlender/Cork/./cork -diff '+tmpdir+'/A.off '+tmpdir+'/B.off '+tmpdir+'/Skull.off', shell=True)
        bpy.ops.import_mesh.off(filepath=tmpdir+"/Skull.off")
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        
        subprocess.call('/OrtogOnBlender/Cork/./cork -isct '+tmpdir+'/A.off '+tmpdir+'/B.off '+tmpdir+'/Mandible.off', shell=True)
        bpy.ops.import_mesh.off(filepath=tmpdir+"/Mandible.off")
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

    
    Mandible = bpy.data.objects['Mandible']
    bpy.ops.object.select_all(action='DESELECT')
    Mandible.select = True
    bpy.context.scene.objects.active = Mandible
        
class BooleanaMand(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.booleana_mandib"
    bl_label = "Booleanas da mandíbula"
    
    def execute(self, context):
       BooleanaMandDef(self, context)
       return {'FINISHED'}
