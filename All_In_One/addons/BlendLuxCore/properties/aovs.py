import bpy
from bpy.props import PointerProperty, BoolProperty
from bpy.types import PropertyGroup


# Attached to render layer
class LuxCoreAOVSettings(PropertyGroup):
    # Basic Information
    rgb = BoolProperty(name="RGB", default=False,
                       description="Raw RGB values (HDR)")
    rgba = BoolProperty(name="RGBA", default=False,
                       description="Raw RGBA values (HDR)")
    alpha = BoolProperty(name="Alpha", default=False,
                       description="Alpha value [0..1]")
    depth = BoolProperty(name="Depth", default=False,
                       description="Distance from camera (Z-Pass)")
    albedo = BoolProperty(name="Albedo", default=False,
                       description="Unlit material/texture colors")

    # Material/Object Information
    material_id = BoolProperty(name="Material ID", default=False,
                       description="Material ID (1 value per material, use the ID Mask Node "
                                   "in compositing nodes to extract a mask)")
    material_id_color = BoolProperty(name="Material ID Color", default=False,
                       description="Material ID (1 color per material, anti-aliased)")
    object_id = BoolProperty(name="Object ID", default=False,
                       description="Object ID (1 value per object, use the ID Mask Node "
                                   "in compositing nodes to extract a mask)")
    emission = BoolProperty(name="Emission", default=False,
                       description="Emission R, G, B")

    # Direct Light Information
    direct_diffuse = BoolProperty(name="Direct Diffuse", default=False,
                       description="Diffuse R, G, B")
    direct_glossy = BoolProperty(name="Direct Glossy", default=False,
                       description="Glossy R, G, B")

    # Indirect Light Information
    indirect_diffuse = BoolProperty(name="Indirect Diffuse", default=False,
                       description="Indirect diffuse R, G, B")
    indirect_glossy = BoolProperty(name="Indirect Glossy", default=False,
                       description="Indirect glossy R, G, B (e.g. glossy, metal")
    indirect_specular = BoolProperty(name="Indirect Specular", default=False,
                       description="Indirect specular R, G, B (e.g. glass, mirror)")

    # Geometry Information
    position = BoolProperty(name="Position", default=False,
                       description="World X, Y, Z")
    shading_normal = BoolProperty(name="Shading Normal", default=False,
                       description="Normal vector X, Y, Z with mesh smoothing")
    avg_shading_normal = BoolProperty(name="Avg. Shading Normal", default=False,
                       description="Same as shading normal, but with anti-aliasing")
    geometry_normal = BoolProperty(name="Geometry Normal", default=False,
                       description="Normal vector X, Y, Z without mesh smoothing")
    uv = BoolProperty(name="UV", default=False,
                       description="Texture coordinates U, V")

    # Shadow Information
    direct_shadow_mask = BoolProperty(name="Direct Shadow Mask", default=False,
                       description="Mask containing shadows by direct light")
    indirect_shadow_mask = BoolProperty(name="Indirect Shadow Mask", default=False,
                       description="Mask containing shadows by indirect light")

    # Render Information
    raycount = BoolProperty(name="Raycount", default=False,
                       description="Ray count per pixel (normalized so the values range from 0 to 1)")
    samplecount = BoolProperty(name="Samplecount", default=False,
                       description="Samples per pixel (normalized so the values range from 0 to 1)")
    convergence = BoolProperty(name="Convergence", default=False,
                       description="The convergence per pixel. The lower the value, the more converged "
                                   "(noise-free) the pixel is. If the convergence halt condition is "
                                   "enabled, the render is stopped once all pixels fall below the "
                                   "convergence threshold")
    noise = BoolProperty(name="Noise", default=False,
                       description="The noise amount per pixel. High values mean more noise, low values less noise")
    irradiance = BoolProperty(name="Irradiance", default=False,
                       description="Surface irradiance")
