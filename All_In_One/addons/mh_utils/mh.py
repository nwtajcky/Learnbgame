# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Project Name:        MakeHuman
# Product Home Page:   http://www.makehuman.org/
# Code Home Page:      http://code.google.com/p/makehuman/
# Authors:             Thomas Larsson
# Script copyright (C) MakeHuman Team 2001-2013
# Coding Standards:    See http://www.makehuman.org/node/165


#----------------------------------------------------------
#  Setting
#----------------------------------------------------------

class CSettings:
    
    def __init__(self, version):
        self.version = version

        if version == "alpha7":                    
            self.vertices = {
                "Body"      : (0, 15340),
                "Skirt"     : (15340, 16096),
                "Tights"    : (16096, 18528),
            }

            self.clothesVerts   = (self.vertices["Skirt"][0], self.vertices["Tights"][1])
            self.nTotalVerts    = self.vertices["Tights"][1]
            self.nBodyVerts     = self.vertices["Body"][1]
            self.nBodyFaces     = 14812           

        elif version == "alpha8a":
            self.vertices = {
                "Body"      : (0, 13380),
                "Tongue"    : (13380, 13606),
                "Joints"    : (13606, 14614),
                "Eyes"      : (14614, 14758),
                "EyeLashes" : (14758, 15008),
                "LoTeeth"   : (15008, 15076),
                "UpTeeth"   : (15076, 15144),
                "Penis"     : (15144, 15344),
                "Tights"    : (15344, 18018),
                "Skirt"     : (18018, 18738),
                "Hair"      : (18738, 19166),
            }

            self.clothesVerts   = (self.vertices["Tights"][0], self.vertices["Skirt"][1])
            self.nTotalVerts    = 19174
            self.nBodyVerts     = self.vertices["Body"][1]
            self.nBodyFaces     = 13606

        elif version == "alpha8b":
            self.vertices = {
                "Body"      : (0, 13380),
                "Tongue"    : (13380, 13606),
                "Joints"    : (13606, 14598),
                "Eyes"      : (14598, 14742),
                "EyeLashes" : (14742, 14992),
                "LoTeeth"   : (14992, 15060),
                "UpTeeth"   : (15060, 15128),
                "Penis"     : (15128, 15328),
                "Tights"    : (15328, 18002),
                "Skirt"     : (18002, 18722),
                "Hair"      : (18722, 19150),
            }
            self.clothesVerts   = (self.vertices["Tights"][0], self.vertices["Skirt"][1])
            self.nTotalVerts    = 19158
            self.nBodyVerts     = self.vertices["Body"][1]
            self.nBodyFaces     = 13606


#----------------------------------------------------------
#   Global variables
#----------------------------------------------------------

proxy = None
confirm = None
confirmString = "" 
confirmString2 = ""
