"""
    Paradox asset files, read/write binary data.

    This is designed to be compatible with both Python 2 and Python 3 (so code can be shared across Maya and Blender)
    Critically, the way strings and binary data are handled must now be done with care, see...
        http://python-future.org/compatible_idioms.html#byte-string-literals

    author : ross-g
"""

from __future__ import print_function

import os
import sys
import struct
from collections import OrderedDict

try:
    import xml.etree.cElementTree as Xml
except ImportError:
    import xml.etree.ElementTree as Xml

# Py2, Py3 compatibility
try:
    basestring
except NameError:
    basestring = str


""" ====================================================================================================================
    PDX data classes.
========================================================================================================================
"""


class PDXData(object):
    """
        Simple class that turns an XML element hierarchy with attributes into a object for more convenient
        access to attributes.
    """

    def __init__(self, element, depth=None):
        # use element tag as object name
        setattr(self, 'name', element.tag)

        # object depth in hierarchy
        self.depth = 0
        if depth is not None:
            self.depth = depth

        # object attribute collection
        self.attrdict = OrderedDict()

        # set element attributes as object attributes
        for attr in element.attrib:
            setattr(self, attr, element.attrib[attr])
            self.attrdict[attr] = element.attrib[attr]

        # iterate over element children, set these as attributes which nest further PDXData objects
        for child in list(element):
            child_data = type(self)(child, self.depth + 1)
            setattr(self, child.tag, child_data)
            self.attrdict[child.tag] = child_data

    def __str__(self):
        string = list()
        for _key, _val in self.attrdict.iteritems():
            if type(_val) == type(self):
                string.append('{}{}:'.format(self.depth * '    ', _key))
                string.append('{}'.format(_val))
            else:
                string.append('{}{}:  {}'.format(self.depth * '    ', _key, len(_val)))
        return '\n'.join(string)


""" ====================================================================================================================
    Functions for reading and parsing binary data.
========================================================================================================================
"""


def parseProperty(bdata, pos):
    # starting at '!'
    pos += 1

    # get length of property name
    prop_name_length = struct.unpack_from('b', bdata, offset=pos)[0]
    pos += 1

    # get property name as string
    prop_name = parseString(bdata, pos, prop_name_length)
    pos += prop_name_length

    # get property data
    prop_values, pos = parseData(bdata, pos)

    return prop_name, prop_values, pos


def parseObject(bdata, pos):
    # skip and record any repeated '[' characters
    objdepth = 0
    while struct.unpack_from('c', bdata, offset=pos)[0].decode() == '[':
        objdepth += 1
        pos += 1

    # get object name as string
    obj_name = ''
    # we don't know the string length, so look for an ending byte of zero
    while struct.unpack_from('b', bdata, offset=pos)[0] != 0:
        obj_name += struct.unpack_from('c', bdata, offset=pos)[0].decode()
        pos += 1

    # skip the ending zero byte
    pos += 1

    return obj_name, objdepth, pos


def parseString(bdata, pos, length):
    val_tuple = struct.unpack_from('c' * length, bdata, offset=pos)

    # turn the resulting tuple into a string of bytes
    string = b''.join(val_tuple).decode()

    # check if the ending byte is zero and remove if so
    if string[-1] == chr(0):
        string = string[:-1]

    return string


def parseData(bdata, pos):
    # determine the  data type
    datatype = struct.unpack_from('c', bdata, offset=pos)[0].decode()
    # TODO: use an array here instead of list for memory efficiency?
    datavalues = []

    if datatype == 'i':
        # handle integer data
        pos += 1

        # count
        size = struct.unpack_from('i', bdata, offset=pos)[0]
        pos += 4

        # values
        for i in range(0, size):
            val = struct.unpack_from('i', bdata, offset=pos)[0]
            datavalues.append(val)
            pos += 4

    elif datatype == 'f':
        # handle float data
        pos += 1

        # count
        size = struct.unpack_from('i', bdata, offset=pos)[0]
        pos += 4

        # values
        for i in range(0, size):
            val = struct.unpack_from('f', bdata, offset=pos)[0]
            datavalues.append(val)
            pos += 4

    elif datatype == 's':
        # handle string data
        pos += 1

        # count
        size = struct.unpack_from('i', bdata, offset=pos)[0]
        # TODO: we are assuming that we always have a count of 1 string, not an array of multiple strings
        pos += 4

        # string length
        str_data_length = struct.unpack_from('i', bdata, offset=pos)[0]
        pos += 4

        # value
        val = parseString(bdata, pos, str_data_length)
        datavalues.append(val)
        pos += str_data_length

    else:
        raise NotImplementedError("Unknown data type encountered. {}".format(datatype))

    return datavalues, pos


def read_meshfile(filepath, to_stdout=False):
    """
        Reads through a .mesh file and gathers all the data into hierarchical element structure.
        The resulting XML is not natively writable to string as it contains Python data types.
    """
    # read the data
    with open(filepath, 'rb') as fp:
        fdata = fp.read()

    # create an XML structure to store the object hierarchy
    file_element = Xml.Element('File')
    file_element.attrib = dict(name=os.path.split(filepath)[1], path=os.path.split(filepath)[0])

    # determine the file length and set initial file read position
    eof = len(fdata)
    pos = 0

    # read the file header '@@b@'
    header = struct.unpack_from('c' * 4, fdata, pos)
    if bytes(b''.join(header)) == b'@@b@':
        pos = 4
    else:
        raise NotImplementedError("Unknown file header. {}".format(header))

    parent_element = file_element
    depth_list = [file_element]
    current_depth = 0

    # parse through until EOF
    while pos < eof:
        # we have a property
        if struct.unpack_from('c', fdata, offset=pos)[0].decode() == '!':
            # check the property type and values
            prop_name, prop_values, pos = parseProperty(fdata, pos)
            if to_stdout:
                print("  " * current_depth + "  ", prop_name, " (count", len(prop_values), ")")

            # assign property values to the parent object
            parent_element.set(prop_name, prop_values)

        # we have an object
        elif struct.unpack_from('c', fdata, offset=pos)[0].decode() == '[':
            # check the object type and hierarchy depth
            obj_name, depth, pos = parseObject(fdata, pos)
            if to_stdout:
                print("  " * depth, obj_name, depth)

            # deeper branch of the tree => current parent valid
            # same or shallower branch of the tree => parent gets redefined back a level
            if not depth > current_depth:
                # remove elements from depth list, change parent
                depth_list = depth_list[:depth]
                parent_element = depth_list[-1]

            # create a new object as a child of the current parent
            new_element = Xml.SubElement(parent_element, obj_name)
            # update parent
            parent_element = new_element
            # update depth
            depth_list.append(parent_element)
            current_depth = depth

        # we have something that we can't parse
        else:
            raise NotImplementedError("Unknown object encountered.")

    return file_element


""" ====================================================================================================================
    Functions for writing XML tree to binary data.
========================================================================================================================
"""


def writeProperty(prop_name, prop_data):
    datastring = b''

    # write starting '!'
    datastring += struct.pack('c', '!'.encode())

    # write length of property name
    prop_name_length = len(prop_name)
    datastring += struct.pack('b', prop_name_length)

    # write property name as string
    datastring += writeString(prop_name)

    # write property data
    datastring += writeData(prop_data)

    return datastring


def writeObject(obj_xml, obj_depth):
    datastring = b''

    # write object hierarchy depth
    for x in range(obj_depth):
        datastring += struct.pack('c', '['.encode())

    # write object name as string
    obj_name = obj_xml.tag
    datastring += writeString(obj_name)
    # write zero-byte ending
    datastring += struct.pack('x')

    return datastring


def writeString(string):
    datastring = b''

    string = str(string)  # struct.pack cannot handle unicode strings in Python 2

    for x in string:
        datastring += struct.pack('c', x.encode())

    return datastring


def writeData(data_array):
    datastring = b''

    # determine the data type in the array
    types = set([type(d) for d in data_array])
    if len(types) == 1:
        datatype = types.pop()
    elif len(types) < 1:
        return datastring
    else:
        raise NotImplementedError("Mixed data type encountered. {} - {}".format(types, data_array))

    if all(isinstance(d, int) for d in data_array):
        # write integer data
        datastring += struct.pack('c', 'i'.encode())

        # write the data count
        size = len(data_array)
        datastring += struct.pack('i', size)

        # write the data values
        datastring += struct.pack('i' * size, *data_array)

    elif all(isinstance(d, float) for d in data_array):
        # write float data
        datastring += struct.pack('c', 'f'.encode())

        # count
        size = len(data_array)
        datastring += struct.pack('i', size)

        # values
        datastring += struct.pack('f' * size, *data_array)

    elif all(isinstance(d, basestring) for d in data_array):
        # write string data
        datastring += struct.pack('c', 's'.encode())

        # count
        size = 1
        # TODO: we are assuming that we always have a count of 1 string, not an array of multiple strings
        datastring += struct.pack('i', size)

        # string length
        str_data_length = len(data_array[0])
        datastring += struct.pack('i', (str_data_length + 1))  # string length + 1 to account for zero-byte ending

        # values
        datastring += writeString(data_array[0])  # Py2 struct.pack cannot handle unicode strings
        # write zero-byte ending
        datastring += struct.pack('x')

    else:
        raise NotImplementedError("Unknown data type encountered. {}".format(datatype))

    return datastring


def write_meshfile(filepath, root_xml):
    """
        Iterates over an XML element and writes the hierarchical element structure back into a binary file.
    """
    datastring = b''

    # write the file header '@@b@'
    header = '@@b@'
    for x in header:
        datastring += struct.pack('c', x.encode())

    # write the file properties
    if root_xml.tag == 'File':
        datastring += writeProperty('pdxasset', root_xml.get('pdxasset'))
    else:
        raise NotImplementedError("Unknown XML root encountered. {}".format(root_xml.tag))

    # TODO: writing properties would be easier if order was irrelevant, you should test this
    # write objects root
    object_xml = root_xml.find('object')
    if object_xml:
        current_depth = 1
        datastring += writeObject(object_xml, current_depth)

        # write each shape node
        for shape_xml in object_xml:
            current_depth = 2
            datastring += writeObject(shape_xml, current_depth)

            # write each mesh
            for child_xml in shape_xml:
                current_depth = 3
                datastring += writeObject(child_xml, current_depth)

                if child_xml.tag == 'mesh':
                    mesh_xml = child_xml
                    # write mesh properties
                    for prop in ['p', 'n', 'ta', 'u0', 'u1', 'tri']:
                        if mesh_xml.get(prop) is not None:
                            datastring += writeProperty(prop, mesh_xml.get(prop))

                    # write mesh sub-objects
                    aabb_xml = mesh_xml.find('aabb')
                    if aabb_xml is not None:
                        current_depth = 4
                        datastring += writeObject(aabb_xml, current_depth)
                        for prop in ['min', 'max']:
                            if aabb_xml.get(prop) is not None:
                                datastring += writeProperty(prop, aabb_xml.get(prop))

                    material_xml = mesh_xml.find('material')
                    if material_xml is not None:
                        current_depth = 4
                        datastring += writeObject(material_xml, current_depth)
                        for prop in ['shader', 'diff', 'n', 'spec']:
                            if material_xml.get(prop) is not None:
                                datastring += writeProperty(prop, material_xml.get(prop))

                    skin_xml = mesh_xml.find('skin')
                    if skin_xml is not None:
                        current_depth = 4
                        datastring += writeObject(skin_xml, current_depth)
                        for prop in ['bones', 'ix', 'w']:
                            if skin_xml.get(prop) is not None:
                                datastring += writeProperty(prop, skin_xml.get(prop))

                elif child_xml.tag == 'skeleton':
                    # write bone sub objects and properties
                    for bone_xml in child_xml:
                        current_depth = 4
                        datastring += writeObject(bone_xml, current_depth)
                        for prop in ['ix', 'pa', 'tx']:
                            if bone_xml.get(prop) is not None:
                                datastring += writeProperty(prop, bone_xml.get(prop))

    # write locators root
    locator_xml = root_xml.find('locator')
    if locator_xml:
        current_depth = 1
        datastring += writeObject(locator_xml, current_depth)

        # write each locator
        for locnode_xml in locator_xml:
            current_depth = 2
            datastring += writeObject(locnode_xml, current_depth)

            # write locator properties
            for prop in ['p', 'q', 'pa']:
                if locnode_xml.get(prop) is not None:
                    datastring += writeProperty(prop, locnode_xml.get(prop))

    # write the data
    with open(filepath, 'wb') as fp:
        fp.write(datastring)


""" ====================================================================================================================
    Main.
========================================================================================================================
"""


if __name__ == '__main__':
    """
       When called from the command line we just print the structure and contents of the .mesh or .anim file to stdout
    """
    clear = lambda: os.system('cls')
    clear()

    if len(sys.argv) > 1:
        a_file = sys.argv[1]
        a_data = read_meshfile(a_file)

        for elem in a_data.iter():
            print('object', elem.tag)
            for k, v in elem.items():
                print('    property', k, '({})'.format(len(v)))
                print(v)
            print()


"""
General binary format is:
    data description
    data type
    depth of data
    data content


.mesh file format
========================================================================================================================
    header    (@@b@ for binary, @@t@ for text)
    pdxasset    (int)  number of assets?
        object    (object)  parent item for all 3D objects
            shape    (object)
                ...  multiple shapes, used for meshes under different node transforms
            shape    (object)
                mesh    (object)
                    ...  multiple meshes per shape, used for different material IDs
                mesh    (object)
                    ...
                mesh    (object)
                    p    (float)  verts
                    n    (float)  normals
                    ta    (float)  tangents
                    u0    (float)  UVs
                    tri    (int)  triangles
                    aabb    (object)
                        min    (float)  min bounding box
                        max    (float)  max bounding box
                    material    (object)
                        shader    (string)  shader name
                        diff    (string)  diffuse texture
                        n    (string)  normal texture
                        spec    (string)  specular texture
                    skin    (object)
                        bones    (int)  num skin influences
                        ix    (int)  skin bone ids
                        w    (float)  skin weights
                skeleton    (object)
                    bone    (object)
                        ix    (int)  index
                        pa    (int)  parent index, omitted for root
                        tx    (float)  transform, 3*4 matrix
        locator    (object)  parent item for all locators
            node    (object)
                p    (float)  position
                q    (float)  quarternion
                pa    (string)  parent


.anim file format
========================================================================================================================
    header    (@@b@ for binary, @@t@ for text)
    pdxasset    (int)  number of assets?
        info    (object)
            sa    (int)  num keyframes
            j    (int)  num bones 
            fps    (float)  anim speed
            bone    (object)
                ...  multiple bones, not all may be animated based on 'sa' attribute
            bone    (object)
                ...
            bone    (object)
                q    (float)  initial rotation as quaternion
                s    (float)  initial scale as single float
                sa    (string)  animation curve types, combination of 's', 't', 'q'
                t    (float)  initial translation as vector
        samples    (object)
            s    
            q    
            t    


"""
