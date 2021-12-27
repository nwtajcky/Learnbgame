from .. import LuxCoreNodeMaterial
from ...utils import node as utils_node


class LuxCoreNodeMatMix(LuxCoreNodeMaterial):
    bl_label = "Mix Material"
    bl_width_default = 160

    def init(self, context):
        self.add_input("LuxCoreSocketMaterial", "Material 1")
        self.add_input("LuxCoreSocketMaterial", "Material 2")
        self.add_input("LuxCoreSocketFloat0to1", "Mix Factor", 0.5)
        self.add_common_inputs()

        self.outputs.new("LuxCoreSocketMaterial", "Material")

    def sub_export(self, exporter, props, luxcore_name=None, output_socket=None):
        # luxcore_name, cached = self.is_cached(exporter, luxcore_name)
        # if cached:
        #     return luxcore_name
        
        # Material inputs need special export because their sockets can't
        # construct a black fallback material in their export method
        material1 = utils_node.export_material_input(self.inputs["Material 1"], exporter, props)
        material2 = utils_node.export_material_input(self.inputs["Material 2"], exporter, props)

        definitions = {
            "type": "mix",
            "material1": material1,
            "material2": material2,
            "amount": self.inputs["Mix Factor"].export(exporter, props),
        }
        self.export_common_inputs(exporter, props, definitions)
        return self.create_props(props, definitions, luxcore_name)
