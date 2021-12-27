bl_info = {
    "name": "Import Terrain (.hgt)",
    "author": "Vladimir Elistratov <prokitektura+support@gmail.com>",
    "version": (1, 1, 0),
    "blender": (2, 7, 9),
    "location": "File > Import > Terrain (.hgt)",
    "description" : "Import real world terrain data from files in the SRTM format (.hgt)",
    "warning": "",
    "wiki_url": "https://github.com/vvoovv/blender-terrain/wiki/Documentation",
    "tracker_url": "https://github.com/vvoovv/blender-terrain/issues",
    "support": "COMMUNITY",
    "category": "Learnbgame",
}

import os,sys

def _checkPath():
    path = os.path.dirname(__file__)
    if path in sys.path:
        sys.path.remove(path)
    # make <path> the first one to search for a module
    sys.path.insert(0, path)
_checkPath()

import bpy, mathutils
# ImportHelper is a helper class, defines filename and invoke() function which calls the file selector
from bpy_extras.io_utils import ImportHelper

import struct, math, gzip
from urllib import request

from transverse_mercator import TransverseMercator
from donate import Donate

def getSrtmIntervals(x1, x2):
    """
    Split (x1, x2) into SRTM intervals. Examples:
    (31.2, 32.7) => [ (31.2, 32), (32, 32.7) ]
    (31.2, 32) => [ (31.2, 32) ]
    """
    _x1 = x1
    intervals = []
    while True:
        _x2 = math.floor(_x1 + 1)
        if (_x2>=x2):
            intervals.append((_x1, x2))
            break
        else:
            intervals.append((_x1, _x2))
            _x1 = _x2
    return intervals

def getSelectionBoundingBox(context):
    # perform context.scene.update(), otherwise o.matrix_world or o.bound_box are incorrect
    context.scene.update()
    if len(context.selected_objects)==0:
        return None
    xmin = float("inf")
    ymin = float("inf")
    xmax = float("-inf")
    ymax = float("-inf")
    for o in context.selected_objects:
        for v in o.bound_box:
            (x,y,z) = o.matrix_world * mathutils.Vector(v)
            if x<xmin: xmin = x
            elif x>xmax: xmax = x
            if y<ymin: ymin = y
            elif y>ymax: ymax = y
    return {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}


class ImportTerrain(bpy.types.Operator, ImportHelper):
    """Import digital elevation model data from files in the SRTM format (.hgt)"""
    bl_idname = "import_scene.terrain"  # important since its how bpy.ops.import_scene.terrain is constructed
    bl_label = "Import Terrain"
    bl_options = {"UNDO","PRESET"}

    # ImportHelper mixin class uses this
    filename_ext = ".hgt.gz"

    filter_glob = bpy.props.StringProperty(
        default="*.hgt.gz",
        options={"HIDDEN"}
    )
    
    # SRTM3 data are sampled at either 3 arc-second and contain 1201 lines and 1201 samples
    # or 1 arc-second and contain 3601 lines and 3601 samples
    resolution = bpy.props.EnumProperty(
        name="Resolution",
        items=(("1", "1 arc-second", "1 arc-second"), ("3", "3 arc-second", "3 arc-second")),
        description="Spation resolution",
        default="1"
    )

    ignoreGeoreferencing = bpy.props.BoolProperty(
        name="Ignore existing georeferencing",
        description="Ignore existing georeferencing and make a new one",
        default=False
    )
    
    useSelectionAsExtent = bpy.props.BoolProperty(
        name="Use selected objects as extent",
        description="Use selected objects as extent",
        default=False
    )
    
    primitiveType = bpy.props.EnumProperty(
        name="Mesh primitive type: quad or triangle",
        items=(("quad","quad","quad"),("triangle","triangle","triangle")),
        description="Primitive type used for the terrain mesh: quad or triangle",
        default="quad"
    )
    
    useSpecificExtent = bpy.props.BoolProperty(
        name="Use manually set extent",
        description="Use specific extent by setting min lat, max lat, min lon, max lon",
        default=True
    )
    
    minLat = bpy.props.FloatProperty(
        name="min lat",
        description="Minimum latitude of the imported extent",
        default=0
    )

    maxLat = bpy.props.FloatProperty(
        name="max lat",
        description="Maximum latitude of the imported extent",
        default=0
    )

    minLon = bpy.props.FloatProperty(
        name="min lon",
        description="Minimum longitude of the imported extent",
        default=0
    )

    maxLon = bpy.props.FloatProperty(
        name="max lon",
        description="Maximum longitude of the imported extent",
        default=0
    )

    def execute(self, context):
        scene = context.scene
        projection = None
        if "lat" in scene and "lon" in scene and not self.ignoreGeoreferencing:
            projection = TransverseMercator(lat=scene["lat"], lon=scene["lon"])
        if self.useSelectionAsExtent:
            bbox = getSelectionBoundingBox(context)
            if not bbox or bbox["xmin"]>=bbox["xmax"] or bbox["ymin"]>=bbox["ymax"]:
                self.report({"ERROR"}, "No objects are selected or extent of the selected objects is incorrect")
                return {"FINISHED"}
            # convert bbox to geographical coordinates
            (minLat, minLon) = projection.toGeographic(bbox["xmin"], bbox["ymin"])
            (maxLat, maxLon) = projection.toGeographic(bbox["xmax"], bbox["ymax"])
        elif self.useSpecificExtent:
            minLat = self.minLat
            maxLat = self.maxLat
            minLon = self.minLon
            maxLon = self.maxLon
        else:
            # use extent of the self.filepath (a single .hgt file)
            srtmFileName = os.path.basename(self.filepath)
            if not srtmFileName:
                self.report({"ERROR"}, "A .hgt file with terrain data wasn't specified")
                return {"FINISHED"}
            minLat = int(srtmFileName[1:3])
            if srtmFileName[0]=="S":
                minLat = -minLat
            maxLat = minLat + 1
            minLon = int(srtmFileName[4:7])
            if srtmFileName[3]=="W":
                minLon = -minLon
            maxLon = minLon + 1
        
        # remember if we have georeferencing
        _projection = projection
        if not projection:
            projection = TransverseMercator(lat=(minLat+maxLat)/2, lon=(minLon+maxLon)/2)
        srtm = Srtm(
            minLat=minLat,
            maxLat=maxLat,
            minLon=minLon,
            maxLon=maxLon,
            projection=projection,
            srtmDir=os.path.dirname(self.filepath), # directory for the .hgt files
            primitiveType = self.primitiveType,
            size = 3600//int(self.resolution)
        )
        missingSrtmFiles = srtm.getMissingSrtmFiles()
        # download missing SRTM files
        for missingPath in missingSrtmFiles:
            missingFile = os.path.basename(missingPath)
            url = "http://s3.amazonaws.com/elevation-tiles-prod/skadi/%s/%s" % (missingFile[:3], missingFile)
            print("Downloading the file from %s..." % url)
            try:
                request.urlretrieve(url, missingPath)
            except Exception as e:
                self.report({'ERROR'}, str(e))
                return {'FINISHED'}
            print("Saving the file to %s... Done." % missingPath)
        verts = []
        indices = []
        srtm.build(verts, indices)
        
        # create a mesh object in Blender
        mesh = bpy.data.meshes.new("Terrain")
        mesh.from_pydata(verts, [], indices)
        mesh.update()
        obj = bpy.data.objects.new("Terrain", mesh)
        # set custom parameter "lat" and "lon" to the active scene
        if not _projection:
            scene["lat"] = projection.lat
            scene["lon"] = projection.lon
        bpy.context.scene.objects.link(obj)
        
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        
        Donate.gui(
            layout,
            self.bl_label
        )
        
        #row = layout.row()
        #row.prop(self, "resolution")
        
        row = layout.row()
        if self.useSelectionAsExtent: row.enabled = False
        row.prop(self, "useSpecificExtent")
        
        if self.useSpecificExtent:
            box = layout.box()
            
            split = box.split(percentage=0.25)
            split.label()
            split.split(percentage=0.67).prop(self, "maxLat")
            
            row = box.row()
            row.prop(self, "minLon")
            row.prop(self, "maxLon")
            
            split = box.split(percentage=0.25)
            split.label()
            split.split(percentage=0.67).prop(self, "minLat")
        
        layout.separator()
        
        row = layout.row()
        if self.useSpecificExtent or self.ignoreGeoreferencing or not ("lat" in context.scene and "lon" in context.scene):
            row.enabled = False
        row.prop(self, "useSelectionAsExtent")
        
        #layout.label("Mesh primitive type:")
        #row = layout.row()
        #row.prop(self, "primitiveType", expand=True)
        
        layout.separator()
        
        row = layout.row()
        if self.useSelectionAsExtent: row.enabled = False
        row.prop(self, "ignoreGeoreferencing")


class Srtm:

    voidValue = -32768

    def __init__(self, **kwargs):
        self.srtmDir = "."
        self.voidSubstitution = 0
        
        for key in kwargs:
            setattr(self, key, kwargs[key])
        
        # we are going from top to down, that's why we call reversed()
        self.latIntervals = list(reversed(getSrtmIntervals(self.minLat, self.maxLat)))
        self.lonIntervals = getSrtmIntervals(self.minLon, self.maxLon)

    def build(self, verts, indices):
        """
        The method fills verts and indices lists with values
        verts is a list of vertices
        indices is a list of tuples; each tuple is composed of 3 indices of verts that define a triangle
        """
        latIntervals = self.latIntervals
        lonIntervals = self.lonIntervals
        
        minHeight = 32767
        maxHeight = -32767
        maxLon = 0
        maxLat = 0
        
        vertsCounter = 0
        
        # we have an extra row for the first latitude interval
        firstLatInterval = 1
        
        # initialize the array of vertCounter values
        lonIntervalVertsCounterValues = []
        for lonInterval in lonIntervals:
            lonIntervalVertsCounterValues.append(None)
        
        for latInterval in latIntervals:
            # latitude of the lower-left corner of the SRTM tile
            _lat = math.floor(latInterval[0])
            # vertical indices that limit the active SRTM tile area
            y1 = math.floor( self.size * (latInterval[0] - _lat) )
            y2 = math.ceil( self.size * (latInterval[1] - _lat) ) + firstLatInterval - 1
            
            # we have an extra column for the first longitude interval
            firstLonInterval = 1
            
            for lonIntervalIndex,lonInterval in enumerate(lonIntervals):
                # longitude of the lower-left corner of the SRTM tile
                _lon = math.floor(lonInterval[0])
                # horizontal indices that limit the active SRTM tile area
                x1 = math.floor( self.size * (lonInterval[0] - _lon) ) + 1 - firstLonInterval 
                x2 = math.ceil( self.size * (lonInterval[1] - _lon) )
                xSize = x2-x1
                
                srtmFileName = self.getSrtmFileName(_lat, _lon)
                
                with gzip.open(srtmFileName, "rb") as f:
                    for y in range(y2, y1-1, -1):
                        # set the file object position at y, x1
                        f.seek( 2*((self.size-y)*(self.size+1) + x1) )
                        for x in range(x1, x2+1):
                            lat = _lat + y/self.size
                            lon = _lon + x/self.size
                            xy = self.projection.fromGeographic(lat, lon)
                            # read two bytes and convert them
                            buf = f.read(2)
                            # ">h" is a signed two byte integer
                            z = struct.unpack('>h', buf)[0]
                            if z==self.voidValue:
                                z = self.voidSubstitution
                            if z<minHeight:
                                minHeight = z
                            elif z>maxHeight:
                                maxHeight = z
                                maxLon = lat
                                maxLat = lon
                            # add a new vertex to the verts array
                            verts.append((xy[0], xy[1], z))
                            if not firstLatInterval and y==y2:
                                topNeighborIndex = lonIntervalVertsCounterValues[lonIntervalIndex] + x - x1
                                if x!=x1:
                                    if self.primitiveType == "quad":
                                        indices.append((vertsCounter, topNeighborIndex, topNeighborIndex-1, vertsCounter-1))
                                    else: # self.primitiveType == "triangle"
                                        indices.append((vertsCounter-1, topNeighborIndex, topNeighborIndex-1))
                                        indices.append((vertsCounter, topNeighborIndex, vertsCounter-1))
                                elif not firstLonInterval:
                                    leftNeighborIndex = prevLonIntervalVertsCounter - (y2-y1)*(prevXsize+1)
                                    leftTopNeighborIndex = topNeighborIndex-prevYsize*(x2-x1+1)-1
                                    if self.primitiveType == "quad":
                                        indices.append((vertsCounter, topNeighborIndex, leftTopNeighborIndex, leftNeighborIndex))
                                    else: # self.primitiveType == "triangle"
                                        indices.append((leftNeighborIndex, topNeighborIndex, leftTopNeighborIndex))
                                        indices.append((vertsCounter, topNeighborIndex, leftNeighborIndex))
                            elif not firstLonInterval and x==x1:
                                if y!=y2:
                                    leftNeighborIndex = prevLonIntervalVertsCounter - (y-y1)*(prevXsize+1)
                                    topNeighborIndex = vertsCounter-xSize-1
                                    leftTopNeighborIndex = leftNeighborIndex-prevXsize-1
                                    if self.primitiveType == "quad":
                                        indices.append((vertsCounter, topNeighborIndex, leftTopNeighborIndex, leftNeighborIndex))
                                    else: # self.primitiveType == "triangle"
                                        indices.append((leftNeighborIndex, topNeighborIndex, leftTopNeighborIndex))
                                        indices.append((vertsCounter, topNeighborIndex, leftNeighborIndex))
                            elif x>x1 and y<y2:
                                topNeighborIndex = vertsCounter-xSize-1
                                leftTopNeighborIndex = vertsCounter-xSize-2
                                if self.primitiveType == "quad":
                                    indices.append((vertsCounter, topNeighborIndex, leftTopNeighborIndex, vertsCounter-1))
                                else: # self.primitiveType == "triangle"
                                    indices.append((vertsCounter-1, topNeighborIndex, leftTopNeighborIndex))
                                    indices.append((vertsCounter, topNeighborIndex, vertsCounter-1))
                            vertsCounter += 1
                
                if firstLonInterval:
                    # we don't have an extra column anymore
                    firstLonInterval = 0
                # remembering vertsCounter value
                prevLonIntervalVertsCounter = vertsCounter - 1
                lonIntervalVertsCounterValues[lonIntervalIndex] = prevLonIntervalVertsCounter - xSize
                # remembering xSize
                prevXsize = xSize
            if firstLatInterval:
                firstLatInterval = 0
            # remembering ySize
            prevYsize = y2-y1

    def getSrtmFileName(self, lat, lon):
        prefixLat = "N" if lat>= 0 else "S"
        prefixLon = "E" if lon>= 0 else "W"
        fileName = "{}{:02d}{}{:03d}.hgt.gz".format(prefixLat, abs(lat), prefixLon, abs(lon))
        return os.path.join(self.srtmDir, fileName)

    def getMissingSrtmFiles(self):
        """
        Returns the list of missing SRTM files
        """
        latIntervals = self.latIntervals
        lonIntervals = self.lonIntervals
        missingFiles = []
        for latInterval in latIntervals:
            # latitude of the lower-left corner of the SRTM tile
            _lat = math.floor(latInterval[0])
            for lonInterval in lonIntervals:
                # longitude of the lower-left corner of the SRTM tile
                _lon = math.floor(lonInterval[0])
                srtmFileName = self.getSrtmFileName(_lat, _lon)
                # check if the SRTM file exists
                if not os.path.exists(srtmFileName):
                    missingFiles.append(srtmFileName)
        return missingFiles


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportTerrain.bl_idname, text="Terrain (.hgt)")

def register():
    bpy.utils.register_class(ImportTerrain)
    bpy.utils.register_class(Donate)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(ImportTerrain)
    bpy.utils.unregister_class(Donate)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
