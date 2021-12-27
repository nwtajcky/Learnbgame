
bl_info = {
    "name":        "USDZ Export",
    "author":      "Robert Crosby",
    "version":     (0, 0, 1),
    "blender":     (2, 80, 0),
    "location":    "File > Export",
    "description": "Export USDZ Files",
    "category": "Learnbgame",
    }


import bpy
from bpy.props import (
        BoolProperty,
        FloatProperty,
        IntProperty,
        StringProperty,
        EnumProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        path_reference_mode,
        axis_conversion,
        )

class ExportUSDZ(bpy.types.Operator, ExportHelper):
    """Save a USDZ File"""

    bl_idname       = "export.usdz"
    bl_label        = "Export USDZ File"
    bl_options      = {'PRESET'}

    filename_ext    = ".usdz"
    filter_glob: StringProperty(
            default="*.usdz;*.usda",
            options={'HIDDEN'},
            )

    materials = BoolProperty(
        name="Export Materials",
        description="Export Materials from Objects",
        default=True,
        )
    keepUSDA = BoolProperty(
        name="Keep USDA",
        description="Keep generated USDA and image files",
        default=False,
        )
    animated = BoolProperty(
        name="Export Animations",
        description="Export Ridgid Body Animations",
        default=False,
        )
    bakeTextures = BoolProperty(
        name="Bake Textures",
        description="Bake Diffuse, Roughness, Normal, etc",
        default=False,
        )
    bakeAO = BoolProperty(
        name="Bake AO",
        description="Bake Ambiant Occlusion Texture",
        default=False,
        )
    samples = IntProperty(
        name="Samples",
        description="Number of Samples for Ambiant Occlusion",
        min=1,
        max=1000,
        default= 64,
        )
    scale = FloatProperty(
        name="Scale",
        min=0.01,
        max=1000.0,
        default=1.0,
        )

    def execute(self, context):
        from . import export_usdz
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "global_scale",
                                            "check_existing",
                                            "filter_glob",
                                            ))
        return export_usdz.export_usdz(context, **keywords)


def menu_func_usdz_export(self, context):
    self.layout.operator(ExportUSDZ.bl_idname, text="USDZ (.usdz)");


classes = (
    ExportUSDZ,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_usdz_export)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_usdz_export)
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
