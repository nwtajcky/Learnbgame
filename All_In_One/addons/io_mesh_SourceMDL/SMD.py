import time
try:
    import MDL_DATA
    import VTX_DATA
    import progressBar
    from MDL import *
    from VTX import *
    from VVD import *
    from VTX_DATA import *
    from MDL_DATA import *
    from VVD_DATA import *
except:
    from . import MDL_DATA
    from . import VTX_DATA
    from . import progressBar
    from .MDL import *
    from .VTX import *
    from .VVD import *
    from .VTX_DATA import *
    from .MDL_DATA import *
    from .VVD_DATA import *
import os.path


class SMD:
    def __init__(self, mdl, vvd, vtx):
        self.mdl = mdl  # type: SourceMdlFile49
        self.vvd = vvd  # type: SourceVvdFile49
        self.vtx = vtx  # type: SourceVtxFile49
        self.filemap = {}
        self.vertex_offset = 0

    def get_polygon(self, strip_group: VTX_DATA.SourceVtxStripGroup, vtx_index_index: int, _, mesh_vertex_offset):
        vertex_indices = []
        vn_s = []
        for i in [0, 2, 1]:
            vtx_vertex_index = strip_group.vtx_indexes[vtx_index_index + i]  # type: int
            vtx_vertex = strip_group.vtx_vertexes[vtx_vertex_index]  # type: VTX_DATA.SourceVtxVertex
            vertex_index = vtx_vertex.original_mesh_vertex_index + self.vertex_offset + mesh_vertex_offset
            if vertex_index > self.vvd.file_data.lod_vertex_count[0]:
                print('vertex index out of bounds, skipping this mesh_data')
                return False, False
            try:
                vn = self.vvd.file_data.vertexes[vertex_index].normal.as_list
            except IndexError:
                vn = [0, 1, 0]
            vertex_indices.append(vertex_index)
            vn_s.append(vn)

        return vertex_indices, vn_s

    def convert_mesh(self, vtx_model: VTX_DATA.SourceVtxModel, lod_index, model: MDL_DATA.SourceMdlModel,
                     material_indexes):
        vtx_meshes = vtx_model.vtx_model_lods[lod_index].vtx_meshes  # type: List[VTX_DATA.SourceVtxMesh]
        indexes = []
        vertex_normals = []
        # small speedup
        i_ex = indexes.extend
        m_ex = material_indexes.extend
        vn_ex = vertex_normals.extend

        for mesh_index, vtx_mesh in enumerate(vtx_meshes):  # type: int,VTX_DATA.SourceVtxMesh
            material_index = model.meshes[mesh_index].material_index
            mesh_vertex_start = model.meshes[mesh_index].vertex_index_start
            if vtx_mesh.vtx_strip_groups:
                for group_index, strip_group in enumerate(
                        vtx_mesh.vtx_strip_groups):  # type: VTX_DATA.SourceVtxStripGroup
                    strip_indexes = []
                    strip_material = []
                    strip_vertex_normals = []
                    # small speedup
                    sm_app = strip_material.append
                    si_app = strip_indexes.append
                    svn_app = strip_vertex_normals.extend
                    if strip_group.vtx_strips and strip_group.vtx_indexes and strip_group.vtx_vertexes:
                        field = progressBar.Progress_bar('Converting mesh_data', len(strip_group.vtx_indexes), 20)
                        for vtx_index in range(0, len(strip_group.vtx_indexes), 3):
                            if not vtx_index % 3 * 10:
                                field.increment(3)
                            f, vn = self.get_polygon(strip_group, vtx_index, lod_index, mesh_vertex_start)
                            if not f and not vn:
                                break
                            si_app(f)
                            svn_app(vn)
                            sm_app(material_index)
                        field.is_done = True
                        field.draw()
                    else:
                        pass

                    i_ex(strip_indexes)
                    m_ex(strip_material)
                    vn_ex(strip_vertex_normals)
            else:
                pass
        return indexes, material_indexes, vertex_normals

    def write_meshes(self, output_dir=os.path.dirname(__file__)):

        for bodypart_index, body_part in enumerate(self.vtx.vtx.vtx_body_parts):  # type: SourceVtxBodyPart
            if body_part.model_count > 0:
                for model_index, vtx_model in enumerate(body_part.vtx_models):  # type: SourceVtxModel
                    if vtx_model.lodCount > 0:
                        if self.mdl.file_data.body_parts[bodypart_index].model_count < 1:
                            print('Body part number {} don\'t have any models'.format(bodypart_index))
                            continue
                        print(
                            "Trying to load model_path number {} from body part number {}, total body part count {}".format(
                                model_index, bodypart_index, len(self.mdl.file_data.body_parts)))
                        model = self.mdl.file_data.body_parts[bodypart_index].models[model_index]  # type: SourceMdlModel
                        name = model.name if model.name else "mesh_{}-{}".format(bodypart_index, model_index)
                        if os.path.split(name)[0]!='':
                            os.makedirs(os.path.join(output_dir,'decompiled',os.path.dirname(name)),exist_ok=True)
                        fileh = open(os.path.join(output_dir, 'decompiled', name) + '.smd', 'w')
                        self.filemap[name] = name+'.smd'
                        self.write_header(fileh)
                        self.write_nodes(fileh)
                        self.write_skeleton(fileh)
                        material_indexes = []
                        vtx_model_lod = vtx_model.vtx_model_lods[0]  # type: SourceVtxModelLod
                        print('Converting {} mesh_data'.format(name))
                        print('Converting {} mesh_data'.format(name))
                        if vtx_model_lod.meshCount > 0:
                            t = time.time()
                            polygons, polygon_material_indexes, normals = self.convert_mesh(vtx_model, 0, model,
                                                                                            material_indexes)
                            print('Mesh convertation took {} sec'.format(round(time.time() - t), 3))
                        else:
                            return
                        for polygon,material_index in zip(polygons,polygon_material_indexes):
                            fileh.write(self.mdl.file_data.textures[material_index].path_file_name)
                            fileh.write('\n')
                            for vertex_id in polygon:
                                v = self.vvd.file_data.vertexes[vertex_id]

                                weight = ' '.join(["{} {}".format(bone, round(weight,4)) for weight, bone in zip(v.boneWeight.weight, v.boneWeight.bone)])
                                fileh.write(
                                    "{} {} {} {:.6f} {:.6f} {} {}\n".format(v.boneWeight.bone[0], v.position.as_string_smd,
                                                                            v.normal.as_string_smd, v.texCoordX, v.texCoordY,
                                                                            v.boneWeight.boneCount, weight))

                        self.vertex_offset += model.vertex_count



    def write_header(self, fileh):
        fileh.write('// Created by SourceIO\n')
        fileh.write('version 1\n')

    def write_nodes(self, fileh):
        bones = self.mdl.file_data.bones  # type: List[SourceMdlBone]
        fileh.write('nodes\n')
        for num, bone in enumerate(bones):
            fileh.write('{} "{}" {}\n'.format(num, bone.name, bone.parentBoneIndex))
        fileh.write('end\n')

    def write_skeleton(self, fileh):
        bones = self.mdl.file_data.bones  # type: List[SourceMdlBone]
        fileh.write('skeleton\n')
        fileh.write('time 0\n')
        for num, bone in enumerate(bones):
            fileh.write("{} {} {}\n".format(num, bone.position.as_string_smd, bone.rotation.as_string_smd))
        fileh.write('end\n')

    def write_end(self, fileh):
        fileh.close()


if __name__ == '__main__':
    mdl = SourceMdlFile49(r'.\test_data\nick_hwm')
    vvd = SourceVvdFile49(r'.\test_data\nick_hwm')
    vtx = SourceVtxFile49(r'.\test_data\nick_hwm')
    A = SMD(mdl, vvd, vtx)
    A.write_meshes()
