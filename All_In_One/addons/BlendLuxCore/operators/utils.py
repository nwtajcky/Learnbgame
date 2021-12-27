import bpy
from ..nodes import TREE_TYPES, TREE_ICONS
from .. import utils
from ..ui import icons

""" Utility functions for our operators """


def make_nodetree_name(material_name):
    return "Nodes_" + material_name


def poll_node(context):
    if not hasattr(context, "node"):
        return False
    return context.node and not context.node.id_data.library


def poll_object(context):
    return context.object and not context.object.library


def poll_material(context):
        if not hasattr(context, "material"):
            return False
        return context.material and not context.material.library


def poll_world(context):
    if not hasattr(context, "world"):
        return False
    return context.world and not context.world.library


def poll_camera(context):
    if not hasattr(context, "camera"):
        return False
    return context.camera and not context.camera.library


def init_mat_node_tree(node_tree):
    # Seems like we still need this.
    # User counting does not work reliably with Python PointerProperty.
    # Sometimes, the material this tree is linked to is not counted as user.
    node_tree.use_fake_user = True

    nodes = node_tree.nodes

    output = nodes.new("LuxCoreNodeMatOutput")
    output.location = 300, 200
    output.select = False

    matte = nodes.new("LuxCoreNodeMatMatte")
    matte.location = 50, 200

    node_tree.links.new(matte.outputs[0], output.inputs[0])


def init_tex_node_tree(node_tree):
    # Seems like we still need this.
    # User counting does not work reliably with Python PointerProperty.
    # Sometimes, the material this tree is linked to is not counted as user.
    node_tree.use_fake_user = True

    nodes = node_tree.nodes

    output = nodes.new("LuxCoreNodeTexOutput")
    output.location = 300, 200
    output.select = False


def init_vol_node_tree(node_tree):
    # Seems like we still need this.
    # User counting does not work reliably with Python PointerProperty.
    # Sometimes, the material this tree is linked to is not counted as user.
    node_tree.use_fake_user = True

    nodes = node_tree.nodes

    output = nodes.new("LuxCoreNodeVolOutput")
    output.location = 300, 200
    output.select = False

    clear = nodes.new("LuxCoreNodeVolClear")
    clear.location = 50, 200

    node_tree.links.new(clear.outputs[0], output.inputs[0])


class LUXCORE_OT_set_node_tree(bpy.types.Operator):
    """
    Generic version. Do not use in UI.
    There are subclasses for materials and volumes
    """

    bl_idname = "luxcore.set_node_tree"
    bl_label = ""
    bl_description = "Assign this node tree"
    bl_options = {"UNDO"}

    def set_node_tree(self, datablock, target, prop, node_tree):
        setattr(target, prop, node_tree)

        # Flag datablock for update in viewport render
        datablock.update_tag()

        if (isinstance(datablock, bpy.types.NodeTree)
                and datablock.bl_idname == "luxcore_material_nodes"):
            # Also flag the materials for update
            for mat in bpy.data.materials:
                if mat.luxcore.node_tree is datablock:
                    mat.update_tag()


class LUXCORE_MT_node_tree(bpy.types.Menu):
    """
    Generic version. Do not use in UI.
    There are subclasses for materials and volumes
    """

    bl_idname = "LUXCORE_MT_node_tree"
    bl_label = "Select Node Tree"
    bl_description = "Select a node tree"
    bl_options = {"UNDO"}

    def draw(self, context):
        # Has to be present for class registration
        pass

    def custom_draw(self, tree_type, set_operator):
        assert tree_type in TREE_TYPES or tree_type == "ALL"

        layout = self.layout

        source = bpy.data.node_groups
        if tree_type == "ALL":
            # bpy.data.node_groups also contains node trees from other addons, so we still need to filter
            trees = [(index, tree, TREE_ICONS[tree.bl_idname])
                     for index, tree in enumerate(source)
                     if tree.bl_idname in TREE_TYPES]
        else:
            icon = TREE_ICONS[tree_type]
            trees = [(index, tree, icon)
                     for index, tree in enumerate(source)
                     if tree.bl_idname == tree_type]

        row = layout.row()
        col = row.column()

        if not trees:
            # No node trees of this type in the scene yet
            if tree_type == "ALL":
                col.label("No node trees available")
            else:
                tree_type_pretty = tree_type.split("_")[1]
                col.label("No " + tree_type_pretty + " node trees available")

            if tree_type == "luxcore_material_nodetree":
                # Volumes need a more complicated new operator (Todo)
                col.operator("luxcore.mat_nodetree_new", text="New Node Tree", icon=icons.ADD)
                col.menu("LUXCORE_MT_node_tree_preset")

        for j, (index, tree, icon) in enumerate(trees):
            if j > 0 and j % 20 == 0:
                col = row.column()

            text = utils.get_name_with_lib(tree)

            op = col.operator(set_operator, text=text, icon=icon)
            op.node_tree_index = index
