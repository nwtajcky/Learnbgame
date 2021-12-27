# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 00:07:45 2019

@author: AsteriskAmpersand
"""

from collections import OrderedDict
try:
    from ..common import Cstruct as CS
    from ..mrl3.maptype import maptypeTranslation
except:
    import sys
    sys.path.insert(0, r'..\common')
    sys.path.insert(0, r'..\mrl3')
    import Cstruct as CS
    from maptype import maptypeTranslation

translation = lambda x: maptypeTranslation[x>>12]
intBytes = lambda x: int.from_bytes(x, byteorder='little', signed=False)
hex_read = lambda f,x: intBytes(f.read(x))

from ..common.crc import CrcJamcrc
#from crccheck.crc import CrcJamcrc
generalhash =  lambda x:  CrcJamcrc.calc(x.encode())

class MRL3Header(CS.PyCStruct):
    fields = OrderedDict([
            ("headId","long"),
            ("unknArr","ubyte[12]"),
            ("materialCount","ulong"),
            ("textureCount","ulong"),
            ("textureOffset","uint64"),
            ("materialOffset","uint64")            
            ])
    
class MRL3Texture(CS.PyCStruct):
    fields = OrderedDict([
            ("textureId","long"),
            ("unknArr","ubyte[12]"),
            ("path","char[256]")    
            ])

class MRL3ResourceBinding(CS.PyCStruct):
    resourceTypes = ["cbuffer", "sampler", "texture"]
    fields = OrderedDict([
            ("resourceType","ubyte"),#[cbuffer, sampler, texture]
            ("unknArr","ubyte[3]"),
            ("mapType","uint"),#Type of the Texture (Albedo Diffuse etc)
            ("texIdx","uint"),
            ("unkn","uint"),
            ])
    
    def marshall(self, data):
        super().marshall(data)
        self.mapTypeName = translation(self.mapType)
        self.resourceTypeName = self.resourceTypes[self.resourceType&0xF]
        

class MRL3MaterialHeader(CS.PyCStruct):
    fields = OrderedDict([
            ("headId","uint"),
            ("materialNameHash","uint"),
            ("shaderHash","uint"),
            ("skinid","uint"),
            ("matSize","uint"),
            ("unkn4","short"),
            ("floatArrayOffset","ubyte"),
            ("unkn5","ubyte[9]"),
            ("unkn6","ubyte"),
            ("unkn7","ubyte[15]"),            
            ("startAddress","uint"),
            ("unkn8","long")])
    
class MRL3ParameterArray(CS.PyCStruct):
    def __init__(self, blocktype):
        self.fields = {"Parameters":"float[%d]"%((blocktype.Header.matSize-blocktype.Header.floatArrayOffset*8)//4)}
        super().__init__()
    
class MRL3Material():
    def __init__(self):
        self.Header = MRL3MaterialHeader()
        self.resourceBindings = []
        self.paramArray = []
    
    def marshall(self, data):
        self.Header.marshall(data)
        pos = data.tell()
        data.seek(self.Header.startAddress)
        self.resourceBindings = [MRL3ResourceBinding() for _ in range(self.Header.floatArrayOffset*8//len(MRL3ResourceBinding()))]
        [arg.marshall(data) for arg in self.resourceBindings]
        self.paramArray = MRL3ParameterArray(self)
        self.paramArray.marshall(data)
        data.seek(pos)
        
    def serialize(self):
        return self.Header.serialize()+b''.join(map(lambda x: x.serialize(),self.textureArguments))+self.paramArray.serialize()
    
    def getAlbedoIndex(self):
        for resource in self.resourceBindings:
            if "Albedo".upper() in resource.mapTypeName.upper():
                return resource.texIdx
        return 0
    
class MRL3():
    def __init__(self):
        self.Header = MRL3Header()
        self.Textures = []
        self.Materials = []
        
    def marshall(self, file):
        self.Header.marshall(file)
        file.seek(self.Header.textureOffset)
        self.Textures = [MRL3Texture() for _ in range(self.Header.textureCount)]
        [mat.marshall(file) for mat in self.Textures]
        file.seek(self.Header.materialOffset)
        self.Materials = [MRL3Material() for _ in range(self.Header.materialCount)]
        [mat.marshall(file) for mat in self.Materials]
        
    def __getitem__(self, materialString):
        idHash = generalhash(materialString)
        for material in self.Materials:
            if material.Header.materialNameHash == idHash:
                index = material.getAlbedoIndex()-1
                if index < 0 or index > len(self.Textures):
                    raise KeyError
                return self.Textures[index].path.replace("\x00","")
        raise KeyError