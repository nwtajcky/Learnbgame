# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Copyright (C) 2017 JOSECONSCO
# Created by JOSECONSCO

import bpy
import bmesh
import math
import random
import numpy as np
from mathutils import noise, Vector, kdtree
from mathutils.bvhtree import BVHTree
from .ribbons_operations import HT_OT_CurvesUVRefresh
from bpy.props import EnumProperty, FloatProperty, BoolProperty, IntProperty, StringProperty
from .resample2d import get2dinterpol_Catmull_Rom, get2dInterpol, interpol, get_strand_proportions
from .helper_functions import calc_power
# import sys
# dir = 'C:\\Users\\JoseConseco\\AppData\\Local\\Programs\\Python\\Python35\\Lib\\site-packages'
# if not dir in sys.path:
#     sys.path.append(dir )
# import ipdb


def next_edge_ring(edge, face):  # return opposite edge
    if len(face.verts) == 4:
        target_verts = [v for v in face.verts if v not in edge.verts]
        return [e for e in face.edges if
                target_verts[0] in e.verts and
                target_verts[1] in e.verts][0]
    else:
        return


def getEdgesRing(edge):
    facesLoop = []
    edgesRing = []
    while True:
        edgesRing.append(edge)
        nextFace = [f for f in edge.link_faces if f not in facesLoop]  # edge has 2 faces
        if len(nextFace) == 0:
            break
        if nextFace[0] is None:
            break
        facesLoop.append(nextFace[0])
        edge = next_edge_ring(edge, nextFace[0])
        if not edge:
            break
    return edgesRing


def sortSelectedEdgesInLoop(selected_edges):  # for now assume we get edge
    # get BMLoop that points to the right direction

    orderedSelectedEdgesList = []  # will containt all islands loops sorted
    while True:  # for islands
        cornerEdge = None
        cornerVert = None
        for e in selected_edges:
            for v in e.verts:
                if len(v.link_edges) == 2:
                    cornerEdge = e
                    cornerVert = v
                    break
            if cornerEdge:
                break
        if not cornerEdge:
            # print('Couldnt find corner for edge loop')
            vertsStorage = set()
            for e in selected_edges:  # try detecting closed loop vert count ==  edge count
                for v in e.verts:
                    vertsStorage.add(v.index)
            if len(vertsStorage) == len(selected_edges):
                # print('Closed edge loop detected')
                cornerEdge = selected_edges[0]  # set random edge as first edge
                cornerVert = selected_edges[0].verts[0]
            else:  # no edge corner, no closed edge loop detected
                return []
        # trying detecting closed loop

        nextEdge = cornerEdge
        nextVert = cornerVert
        orderedSelectedEdges = []  # will stores edge loop in individual island
        while True:  # for getting sorted edge loops in each island
            orderedSelectedEdges.append(nextEdge)
            selected_edges.remove(nextEdge)
            nextVert = nextEdge.other_vert(nextVert)
            if len(nextVert.link_edges) == 2:
                break
            nextEdge = [edge for edge in nextVert.link_edges if edge.is_boundary and edge in selected_edges]
            if not nextEdge:
                break
            else:
                nextEdge = nextEdge[0]
        orderedSelectedEdgesList.append(orderedSelectedEdges)
        if len(selected_edges) == 0:  # no more islands to check
            break
    return orderedSelectedEdgesList


def sortSelectedEdgesToVerts(selected_edges):  # for now assume we get edge
    # get BMLoop that points to the right direction

    orderedVertsLoops = []  # will containt all islands loops sorted
    while True:  # for islands
        cornerEdge = None
        cornerVert = None
        for e in selected_edges:
            for v in e.verts:
                if len(v.link_edges) == 2:
                    cornerEdge = e
                    cornerVert = v
                    break
            if cornerEdge:
                break
        if not cornerEdge:
            return []

        nextEdge = cornerEdge
        nextVert = cornerVert
        VertsLoops = []
        VertsLoops.append([])
        CheckedEdges = []
        while True:  # first pass for filling VertsLoops[0] with sharp edges/verts
            VertsLoops[0].append(nextVert)
            CheckedEdges.append(nextEdge)
            selected_edges.remove(nextEdge)
            nextVert = nextEdge.other_vert(nextVert)
            # if len(nextVert.link_edges) == 2: break
            proposedEdge = [edge for edge in nextVert.link_edges if edge in selected_edges]
            if not proposedEdge:
                VertsLoops[0].append(nextVert)  # add last vert  v -e- v  -e- (v)
                break
            else:
                nextEdge = proposedEdge[0]
        i = 0

        while True:  # try filling VertsLoops[0+n]
            VertsLoops.append([])  # add new row i+1
            for vert in VertsLoops[i]:
                for e in vert.link_edges:
                    if e not in CheckedEdges:
                        nextVert = e.other_vert(vert)
                        if nextVert not in VertsLoops[i + 1] and nextVert not in VertsLoops[
                                i]:  # next vert not in current loop, or previous loop
                            VertsLoops[i + 1].append(nextVert)
                        CheckedEdges.append(e)
            if len(VertsLoops[i + 1]) == 0:  # nothing added in this pass == break
                break
            i += 1
        VertsLoops.pop()  # remove last empty row
        orderedVertsLoops.append(VertsLoops)
        if len(selected_edges) == 0:  # no more islands to check
            break

    return orderedVertsLoops


def get_sorted_verts_co(obj):
    # --- get a mesh from the object ---
    apply_modifiers = True
    # settings = 'PREVIEW'
    me = obj.to_mesh(bpy.context.depsgraph, apply_modifiers, calc_undeformed=False)
    bm = bmesh.new()  # create an empty BMesh
    bm.from_mesh(me)
    selected_edges = [e for e in bm.edges if not e.smooth and e.is_boundary]  # get sharp boundary eges only
    if len(selected_edges) == 0:
        return 0
    orderedVertsLoopsIsland = sortSelectedEdgesToVerts(selected_edges)

    VertsCoLoops = []
    for i, orderedVertsLoops in enumerate(orderedVertsLoopsIsland):
        VertsCoLoops.append([])
        for j, VertsLoop in enumerate(orderedVertsLoops):
            VertsCoLoops[i].append([])
            for vert in VertsLoop:
                VertsCoLoops[i][j].append(vert.co)
    bm.free()
    bpy.data.meshes.remove(me)
    return VertsCoLoops


def get_edge_ring_centers(obj):
    # --- get a mesh from the object ---
    apply_modifiers = True
    # settings = 'PREVIEW'
    me = obj.to_mesh(bpy.context.depsgraph, apply_modifiers, calc_undeformed=False)
    bm = bmesh.new()  # create an empty BMesh
    bm.from_mesh(me)
    selected_edges = [e for e in bm.edges if not e.smooth and e.is_boundary]  # get sharp boundary eges only
    if len(selected_edges) == 0:
        return 0
    if len(selected_edges) == 1:
        return 1
    sorted_selected_edgesPerIslands = sortSelectedEdgesInLoop(selected_edges)  # list - island1Edges, island2Edges ...
    edge_ring_centers_List_per_island = []
    for islandEdgesLoop in sorted_selected_edgesPerIslands:  # for selected/sharp edge loops in island
        edge_ring_centers_List = []
        for loopEdge in islandEdgesLoop:  # create edge rings for sharp edge loops
            edgeRing = getEdgesRing(loopEdge)
            edge_ring_Centers = []
            for e in edgeRing:
                center = (e.verts[0].co + e.verts[1].co) / 2
                # edge_ring_Centers.append(center[:])
                edge_ring_Centers.append(center)
            edge_ring_centers_List.append(edge_ring_Centers.copy())
        edge_ring_centers_List_per_island.append([list(i) for i in zip(*edge_ring_centers_List)])  # does the transpose

    bm.free()
    bpy.data.meshes.remove(me)
    return edge_ring_centers_List_per_island


def get_edge_ring_vert_co(obj):
    me = obj.data
    bm = bmesh.new()  # create an empty BMesh
    bm.from_mesh(me)
    selected_edges = [e for e in bm.edges if not e.smooth]
    sorted_selected_edgesPerIslands = sortSelectedEdgesToVerts(selected_edges)  # list - island1Edges, island2Edges ...
    edge_ring_centers_List_per_island = []
    for islandEdgesLoop in sorted_selected_edgesPerIslands:  # for selected/sharp edge loops in island
        edge_ring_centers_List = []
        for loopEdge in islandEdgesLoop:  # create edge rings for sharp edge loops
            currentVert = [v for v in loopEdge.verts if len(v.link_edges) == 2]
            edgeRing = getEdgesRing(loopEdge)
            vert_ring_co = []
            for e in edgeRing:
                vertLoc = currentVert.co
                # vert_ring_co.append(vertLoc[:])
                vert_ring_co.append(vertLoc)
                currentVert = e.other_vert(currentVert)  # TODO: make it work
            edge_ring_centers_List.append(vert_ring_co.copy())
        edge_ring_centers_List_per_island.append(edge_ring_centers_List.copy())

    bm.free()
    bpy.data.meshes.remove(me)
    return edge_ring_centers_List_per_island


def get_islands_proportions(splinesInIslands):
    widthPerIsland = []
    lengthPerIsland = []
    for splines in splinesInIslands:  # for islands
        splinesTotalLen = 0
        splineTotalWidth = 0
        prevSpline = splines[0]
        for splineIndex, spline in enumerate(splines):
            prevPoint = spline[0]
            for pointIndex, point in enumerate(spline):
                splinesSpacing = Vector(spline[pointIndex]) - Vector(prevSpline[pointIndex])
                splineTotalWidth += splinesSpacing.length
                splinesLen = Vector(point) - Vector(prevPoint)
                splinesTotalLen += splinesLen.length
                prevPoint = point
            prevSpline = spline
        lengthPerIsland.append(splinesTotalLen / len(splines))  # len*numb of spliness / number of splines
        widthPerIsland.append(splineTotalWidth / len(splines[0]))  # width*pointsNumb / numb of points
    maxWidthX = max(widthPerIsland)
    maxLengthY = max(lengthPerIsland)
    NormalizedWidthXPerIsland = [xWidth / maxWidthX for xWidth in widthPerIsland]
    NormalizedLengthYPerIsland = [yWidth / maxLengthY for yWidth in lengthPerIsland]
    return NormalizedWidthXPerIsland, NormalizedLengthYPerIsland


class HT_OT_CurvesFromsurface(bpy.types.Operator):
    bl_label = "Curves from grid surface"
    bl_idname = "object.curves_from_mesh"
    bl_description = "Generate hair curves from grid type mesh object \n" \
                     "For operator to work one border loop must be marked as sharp"
    bl_options = {"REGISTER", "UNDO", "PRESET", 'USE_EVAL_DATA'}

    hairMethod: bpy.props.EnumProperty(name="Hair Method", default="edge",
                                       items=(("edge", "Edge Centers", ""),
                                              ("vert", "Vertex position", "")))
    hairType: bpy.props.EnumProperty(name="Hair Type", default="NURBS",
                                     items=(("BEZIER", "Bezier", ""),
                                            ("NURBS", "Nurbs", ""),
                                            ("POLY", "Poly", "")))
    bezierRes: IntProperty(name="Bezier resolution", default=3, min=1, max=12)
    t_in_x: IntProperty(name="Strands amount", default=10, min=1, soft_max=400)
    x_uniform: BoolProperty(name="Uniform Distribution", description="Uniform Distribution", default=True)
    noiseStrandSeparation: FloatProperty(name="Randomize Spacing", description="Randomize spacing between strands", default=0.3, min=0,
                                         max=1, subtype='PERCENTAGE')
    t_in_y: IntProperty(name="Strand Segments", default=7, min=3, soft_max=20)
    y_uniform: BoolProperty(name="Uniform Distribution", description="Uniform Distribution", default=True)
    shortenStrandLen: FloatProperty(name="Shorten Segment", description="Shorten strand length",
                                    default=0.1, min=0, max=1, subtype='PERCENTAGE')
    Seed: IntProperty(name="Noise Seed", default=1, min=1, max=1000)
    noiseMixFactor: FloatProperty(name="Noise Mix", description="Uniform vs non uniform noise", default=0.3, min=0,
                                  max=1, subtype='PERCENTAGE')
    noiseMixVsAdditive: BoolProperty(name="Mix additive", description="additive vs mix strand noise", default=False)
    noiseFalloff: FloatProperty(name="Noise falloff", description="Noise influence over strand lenght", default=0,
                                min=-1, max=1, subtype='PERCENTAGE')
    snapAmount: FloatProperty(name="Snap Amount", default=0.5, min=0.0, max=1.0, subtype='PERCENTAGE')
    freq: FloatProperty(name="Noise freq", default=0.5, min=0.0, soft_max=5.0)
    strandFreq: FloatProperty(name="Strand freq", default=0.5, min=0.0, soft_max=5.0)
    noiseAmplitude: FloatProperty(name="Noise Amplitude", default=1.0, min=0.0, soft_max=10.0)
    offsetAbove: FloatProperty(name="Offset Strands", description="Offset strands above surface", default=0.1,
                               min=0.01, max=1.0)
    Radius: FloatProperty(name="Radius", description="Radius for bezier curve", default=1, min=0, soft_max=100)

    generateRibbons: BoolProperty(name="Generate Ribbons", description="Generate Ribbons on curve", default=False)
    strandResU: IntProperty(name="Segments U", default=3, min=1, max=5, description="Additional subdivision along strand length")
    strandResV: IntProperty(name="Segments V", default=2, min=1, max=5, description="Subdivisions perpendicular to strand length ")
    strandWidth: FloatProperty(name="Strand Width", default=0.5, min=0.0, soft_max=10)
    strandPeak: FloatProperty(name="Strand peak", default=0.4, min=0.0, max=1,
                              description="Describes how much middle point of ribbon will be elevated")
    strandUplift: FloatProperty(name="Strand uplift", default=0.0, min=-1, max=1, description="Moves whole ribbon up or down")

    alignToSurface: BoolProperty(name="Align tilt", description="Align tilt to Surface", default=False)
    # new_int_method: BoolProperty(name="New interpol Method", description="New", default=True)
    clump_amount: FloatProperty(name="clump  Amount", default=0, min=0, max=1, description="clump Amount", subtype='PERCENTAGE')
    clump_Seed: IntProperty(name="Clump Seed", default=1, min=1, max=1000)
    clump_strength: FloatProperty(name="clump_strength", description="clump_strength", default=1, min=0,
                                  max=1, subtype='PERCENTAGE')
    clump_falloff: FloatProperty(name="clump_fallof", description="clump_fallof", default=0, min=-1.0,
                                 max=1, subtype='PERCENTAGE')

    yLengthPerIsland = []
    xWidthPerIsland = []
    diagonal = 0
    source_curve = None
    source_grid_mesh = None
    # @classmethod #breaks undo
    # def poll(cls, context):
    #     return context.active_object.type == 'MESH'  # bpy.context.scene.render.engine == "CYCLES"
    # def invoke(self, context, event): #just shows prop pop-up but wont execute operator
    #     wm = context.window_manager
    #     return wm.invoke_props_dialog(self)

    def check(self, context):  # DONE: can prop panel be fixed/refreshed when using f6 prop popup
        return True

    @staticmethod
    def is_inside(p, bvht_tree, searchDistance):
        hitpoint, norm, face_index, distance = bvht_tree.find_nearest(p, searchDistance)  # max_dist = 10
        # hit, hitpoint, norm, face_index = obj.closest_point_on_mesh(p, 10)  # max_dist = 10
        vecP = hitpoint - p
        v = vecP.dot(norm)
        return v < 0.0

    def callInterpolation(self, verts2dListIsland, xFactor, yFactor, shortenStrandLen):
        xNormalized = max(round(self.t_in_x * xFactor), 2)
        yNormalized = max(round(self.t_in_y * yFactor), 2)
        if self.t_in_x == 1:
            xNormalized = -1
        # return get2dInterpol(verts2dListIsland, xNormalized, yNormalized, shortenStrandLen, self.Seed, self.x_uniform, self.y_uniform, self.noiseStrandSeparation)
        # if self.new_int_method:
        return get2dinterpol_Catmull_Rom(verts2dListIsland, xNormalized, yNormalized, shortenStrandLen, self.Seed, self.x_uniform, self.y_uniform, self.noiseStrandSeparation)
        # else:
        #     return get2dInterpol(verts2dListIsland, xNormalized, yNormalized, shortenStrandLen, self.Seed, self.x_uniform, self.y_uniform, self.noiseStrandSeparation)

    def draw(self, context):
        #replacing self with hair_grid_settings, wont update hair_grid_settings props. That is why use self
        layout = self.layout
        box = layout.box()
        box.label(text="Hair Settings:")
        col = box.column(align=True)
        # col.prop(self, 'new_int_method')
        col.prop(self, 'hairMethod')
        # if self.hairMethod =='BEZIER' or self.hairMethod =='NURBS':
        col = box.column(align=True)
        col.prop(self, 'bezierRes')
        col.prop(self, 'Radius')
        col = box.column(align=True)
        col.prop(self, 'hairType')
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(self, 't_in_x')
        row.prop(self, 'x_uniform', icon_only=True, emboss=True, icon='ARROW_LEFTRIGHT')
        row = col.row(align=True)
        row.prop(self, 't_in_y')
        row.prop(self, 'y_uniform', icon_only=True, emboss=True, icon='ARROW_LEFTRIGHT')
        row = col.row(align=True)
        row.prop(self, 'shortenStrandLen')

        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(self, 'clump_strength')
        row = col.row(align=True)
        row.prop(self, 'clump_Seed')
        row = col.row(align=True)
        row.prop(self, 'clump_amount')
        row.prop(self, 'clump_falloff')

        box.label(text="Noise Settings:")
        col = box.column(align=True)
        col.prop(self, 'Seed')
        col.prop(self, 'noiseStrandSeparation')
        col.prop(self, 'noiseAmplitude')
        col.prop(self, 'noiseFalloff')
        col.prop(self, 'freq')
        col.prop(self, 'snapAmount')
        col.prop(self, 'offsetAbove')
        col = box.column(align=True)
        row = col.row()
        row.prop(self, 'noiseMixVsAdditive', icon_only=True, emboss=True, icon='PLUS')
        row.prop(self, 'noiseMixFactor')
        col.prop(self, 'strandFreq')

        box.prop(self, 'generateRibbons')
        if self.generateRibbons:
            col = box.column(align=True)
            col.prop(self, 'strandResU')
            col.prop(self, 'strandResV')
            col.prop(self, 'strandWidth')
            col.prop(self, 'strandPeak')
            col.prop(self, 'strandUplift')
            col.prop(self, 'alignToSurface')

  

    def save_settings(self, target_obj):  # Tto object hair_grid_settings
        for d in self.properties.bl_rna.properties.keys():
            if d == 'rna_type':
                continue
            setattr(target_obj.hair_grid_settings, d, getattr(self.properties, d))

    def load_settings(self, source_obj):  # from hair_grid_settings
        # what exception could occur here??
        for d in source_obj.hair_grid_settings.bl_rna.properties.keys():
            if d in {'name', 'rna_type', 'was_created_from_grid'}:
                continue
            setattr(self.properties, d, getattr(source_obj.hair_grid_settings, d))


    def invoke(self, context, event):
        active_obj = context.active_object
        sourceSurface = None
        self.source_grid_mesh = None
        if active_obj.type == 'CURVE':
            if active_obj.hair_grid_settings.was_created_from_grid and active_obj.targetObjPointer in bpy.data.objects.keys():  # obtain source grid surface, that hair was generated from
                self.source_curve = active_obj.name  # somewho if I refrence sourceSurface, then in execute it is lost. So use name instead
                sourceSurface = bpy.data.objects[active_obj.targetObjPointer]
            else:
                self.report({'INFO'}, 'Selected is not recognized as generated from grid surface. Cancelling')
                return {"CANCELLED"}
        elif active_obj.type == 'MESH':
            for face in active_obj.data.polygons:
                if len(face.edge_keys) != 4:
                    self.report({'INFO'}, 'Non quad polygon detected. This operation works on quad only meshes')
                    return {"CANCELLED"}
            sourceSurface = active_obj

        if sourceSurface is None:
            self.report({'INFO'}, 'Select grid mesh type or generated curve hairs first. Cancelling')
            return {"CANCELLED"}
        if self.source_curve: #if operator wa executed on curve use its settigns
            self.load_settings(bpy.data.objects[self.source_curve]) #load settings from cure hairs
        else:
            self.load_settings(sourceSurface)  #else from target mesh

        # Get a BMesh representation
        me = sourceSurface.data
        bm = bmesh.new()  # create an empty BMesh
        bm.from_mesh(me)
        bm.edges.ensure_lookup_table()
        sharp_edges = [e for e in bm.edges if not e.smooth]
        if len(sharp_edges) == 0:
            self.report({'INFO'}, 'No edges marked as sharp! Mark one border edge loop as sharp')
            bm.free()
            return {"CANCELLED"}
        sharp_boundary_edges = [e for e in sharp_edges if e.is_boundary]
        if len(sharp_boundary_edges) == 0:
            self.report({'INFO'}, 'None of sharp edges are boundary edges! Mark one border edge loop as sharp')
            bm.free()
            return {"CANCELLED"}
        if len(sharp_boundary_edges) == 1:
            self.hairMethod = 'vert'
        bm.free()

        self.sourceSurface_BVHT = BVHTree.FromObject(sourceSurface, context.depsgraph)  # TODO: broken in 2.8
        # to normalize some values
        self.diagonal = math.sqrt(pow(sourceSurface.dimensions[0], 2) + pow(sourceSurface.dimensions[1], 2) + pow(sourceSurface.dimensions[2], 2))
        self.source_grid_mesh = sourceSurface.name  # somewho if I refrence sourceSurface, then in execute it is lost. So use name instead
        return self.execute(context)

    def execute(self, context):
        sourceSurface = bpy.data.objects[self.source_grid_mesh]
        if self.hairMethod == 'edge':
            coLoopsPerIslandsList = get_edge_ring_centers(sourceSurface)
            #detect if any island was made on one ring only, and if so switch to another algorithm
            islands_center_count = [len(loop_centers[0]) == 1 for loop_centers in coLoopsPerIslandsList]
            if any(islands_center_count):
                self.hairMethod = 'vert'
                coLoopsPerIslandsList.clear()
                coLoopsPerIslandsList = get_sorted_verts_co(sourceSurface)
        else:
            coLoopsPerIslandsList = get_sorted_verts_co(sourceSurface)

        self.yLengthPerIsland, self.xWidthPerIsland = get_islands_proportions(coLoopsPerIslandsList)

        # hide source surface
        sourceSurface.display_type = 'WIRE'
        sourceSurface.show_all_edges = True
        sourceSurface.hide_render = True
        sourceSurface.cycles_visibility.camera = False
        sourceSurface.cycles_visibility.diffuse = False
        sourceSurface.cycles_visibility.glossy = False
        sourceSurface.cycles_visibility.transmission = False
        sourceSurface.cycles_visibility.scatter = False
        sourceSurface.cycles_visibility.shadow = False

        # create the Curve Datablock
        if self.source_curve:
            curveOB = bpy.data.objects[self.source_curve]
            for spl in reversed(curveOB.data.splines):
                curveOB.data.splines.remove(spl)
            curveData = curveOB.data
        else:
            curveData = bpy.data.curves.new(sourceSurface.name+'_curve', type='CURVE')
            curveData.dimensions = '3D'
            curveData.fill_mode = 'FULL'
            curveOB = bpy.data.objects.new(sourceSurface.name+'_curve', curveData)
            context.scene.collection.objects.link(curveOB)
        # unitsScale = 1 # context.scene.unit_settings.scale_length
        if self.diagonal == 0:
            diagonal = math.sqrt(pow(sourceSurface.dimensions[0], 2) + pow(sourceSurface.dimensions[1],
                                                                           2) + pow(sourceSurface.dimensions[2], 2))  # to normalize some values
        else:
            diagonal = self.diagonal
        # print("diagonal is: "+str(diagonal))
        curveData.bevel_depth = 0.004 * diagonal * self.Radius
        curveData.bevel_resolution = 2

        sourceSurface_BVHT = self.sourceSurface_BVHT
        searchDistance = 1000 * diagonal
        cpow = calc_power(self.noiseFalloff)
        np.random.seed(self.clump_Seed)
        if self.clump_amount > 0:
            clump_amount = max(int(self.t_in_x * self.clump_amount), 1)
            # without repeating  len(avg_clupm_size) < len(tab)
            parent_strands = np.random.choice(range(self.t_in_x), clump_amount, replace=False) # without repeating 
            clump_ids_int = np.sort(np.random.choice(parent_strands, self.t_in_x, replace=True)
                                    ).tolist()  # with repeating - get parents strands  t_in_x times

        for xFactor, yFactor, edgeCentersRingsList in zip(self.xWidthPerIsland, self.yLengthPerIsland, coLoopsPerIslandsList):  # for islands
            Centers_of_EdgeRingsInterpolated = self.callInterpolation(edgeCentersRingsList, xFactor, yFactor, self.shortenStrandLen)
            # map coords to spline
            for l, edgeRingCenters in enumerate(Centers_of_EdgeRingsInterpolated):  # for each strand/ring
                curveLenght = len(edgeRingCenters)
                polyline = curveData.splines.new(self.hairType)
                if self.hairType == 'BEZIER':
                    polyline.bezier_points.add(curveLenght - 1)
                elif self.hairType == 'POLY' or self.hairType == 'NURBS':
                    polyline.points.add(curveLenght - 1)
                if self.hairType == 'NURBS':
                    polyline.order_u = 3  # like bezier thing
                    polyline.use_endpoint_u = True
                for i, edgeCenter in enumerate(edgeRingCenters):  # for strand point
                    edgeCenter = Vector(edgeCenter)
                    noise.seed_set(self.Seed)
                    noiseVectorPerAllHair = noise.noise_vector(edgeCenter * self.freq / diagonal, noise_basis='PERLIN_ORIGINAL')
                    noise.seed_set(self.Seed + l)  # seed per strand/ring
                    noiseVectorPerStrand = noise.noise_vector(edgeCenter * self.strandFreq / diagonal, noise_basis='PERLIN_ORIGINAL')
                    if self.noiseMixVsAdditive:
                        noiseMix = noiseVectorPerAllHair + noiseVectorPerStrand * self.noiseMixFactor
                    else:
                        noiseMix = noiseVectorPerAllHair * (1 - self.noiseMixFactor) + noiseVectorPerStrand * self.noiseMixFactor
                    noiseFalloff = math.pow(i / curveLenght, cpow)  # 0.1 to give 1% of influence on root
                    noisedEdgeCenter = edgeCenter + noiseMix * noiseFalloff * self.noiseAmplitude * diagonal  # linear fallof

                    snappedPoint, normalSourceSurf, index, distance = sourceSurface_BVHT.find_nearest(noisedEdgeCenter, searchDistance)
                    if not snappedPoint:  # search radius is too small ...
                        snappedPoint = noisedEdgeCenter  # snap to itself...
                        normalSourceSurf = Vector((0, 0, 1))
                    snapMix = snappedPoint * self.snapAmount + noisedEdgeCenter * (1 - self.snapAmount)
                    offsetAbove = snapMix + (self.offsetAbove * 0.2) * diagonal * normalSourceSurf * noiseFalloff
                    x, y, z = offsetAbove
                    if self.hairType == 'BEZIER':
                        polyline.bezier_points[i].co = (x, y, z)
                        polyline.bezier_points[i].handle_left_type = 'AUTO'
                        polyline.bezier_points[i].handle_right_type = 'AUTO'
                    else:
                        polyline.points[i].co = (x, y, z, 1)
        if self.clump_amount > 0:
            cpowTip = calc_power(self.clump_falloff)
            for clump_id, spline in zip(clump_ids_int, curveData.splines):
                points = [p for p in spline.bezier_points] if self.hairType == 'BEZIER' else [p for p in spline.points]
                target_points = [p.co for p in curveData.splines[clump_id]] if self.hairType == 'BEZIER' else [
                    p.co for p in curveData.splines[clump_id].points]
                for i, (source_point, target_point) in enumerate(zip(points, target_points)):
                    Fallof_tip = math.pow((self.t_in_y-i) / self.t_in_y, cpowTip)
                    source_point.co = target_point * (1-Fallof_tip) * self.clump_strength + \
                        source_point.co * (self.clump_strength * (Fallof_tip - 1) + 1)
        curveData.resolution_u = self.bezierRes
        # create Object
        
        curveOB.targetObjPointer = sourceSurface.name  # store source surface for snapping oper
        curveOB.matrix_world = sourceSurface.matrix_world
        context.view_layer.objects.active = curveOB
        curveOB.select_set(True)
        sourceSurface.select_set(False)
        # curveOB.data.show_normal_face = False
        curveOB.data.use_uv_as_generated = True
        if self.generateRibbons:
            bpy.ops.object.generate_ribbons(strandResU=self.strandResU, strandResV=self.strandResV,
                                            strandWidth=self.strandWidth, strandPeak=self.strandPeak,
                                            strandUplift=self.strandUplift, alignToSurface=self.alignToSurface)
            HT_OT_CurvesUVRefresh.uvCurveRefresh(curveOB)
        self.save_settings(curveOB)
        curveOB.hair_grid_settings.was_created_from_grid = True
        self.save_settings(sourceSurface)
        return {"FINISHED"}
