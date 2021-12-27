# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 13:38:47 2019

@author: AsteriskAmpersand
"""
#from .dbg import dbg_init
#dbg_init()

content=bytes("","UTF-8")
bl_info = {
    "name": "MHW Mod3 Model Importer",
    "category": "Learnbgame",
    "author": "AsteriskAmpersand (Code) & CrazyT (Structure)",
    "location": "File > Import-Export > Mod3/MHW",
    "version": (1,0,0)
}
 
import bpy

from .operators.mod3import import ImportMOD3
from .operators.mod3export import ExportMOD3
from .operators.mod3import import menu_func_import as mhw_model_menu_func_import
from .operators.mod3export import menu_func_export as mhw_model_menu_func_export

def register():
    bpy.utils.register_class(ImportMOD3)
    bpy.utils.register_class(ExportMOD3)
    bpy.types.INFO_MT_file_import.append(mhw_model_menu_func_import)
    bpy.types.INFO_MT_file_export.append(mhw_model_menu_func_export)

def unregister():
    bpy.utils.unregister_class(ImportMOD3)
    bpy.utils.unregister_class(ExportMOD3)
    bpy.types.INFO_MT_file_import.remove(mhw_model_menu_func_import)
    bpy.types.INFO_MT_file_export.remove(mhw_model_menu_func_export)

if __name__ == "__main__":
    try:
        unregister()
    except:
        pass
    register()
