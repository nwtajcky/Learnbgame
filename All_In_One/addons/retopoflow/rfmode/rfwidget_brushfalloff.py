'''
Copyright (C) 2017 CG Cookie
http://cgcookie.com
hello@cgcookie.com

Created by Jonathan Denning, Jonathan Williamson

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import math
import random

import bgl
from mathutils import Matrix, Vector

from ..common.maths import Vec, Point, Point2D, Direction

from .rfwidget_registry import RFWidget_Registry


class RFWidget_BrushFalloff:
    rfwidget_name = 'brush falloff'

    ###################
    # radius

    def radius_to_dist(self):
        return self.radius

    def dist_to_radius(self, d):
        self.radius = max(1, int(d))

    def radius_gettersetter(self):
        def getter():
            return int(self.radius)
        def setter(v):
            self.radius = max(1, int(v))
        return (getter, setter)

    ##################
    # strength

    def strength_to_dist(self):
        return self.radius * (1.0 - self.strength)

    def dist_to_strength(self, d):
        self.strength = 1.0 - max(0.01, min(1.0, d / self.radius))

    def strength_gettersetter(self):
        def getter():
            return int(self.strength * 100)
        def setter(v):
            self.strength = max(1, min(100, v)) / 100
        return (getter, setter)

    ##################
    # falloff

    def falloff_to_dist(self):
        return self.radius * math.pow(0.5, 1.0 / self.falloff)

    def dist_to_falloff(self, d):
        self.falloff = math.log(0.5) / math.log(max(0.01, min(0.99, d / self.radius)))

    def falloff_gettersetter(self):
        def getter():
            return int(100 * math.pow(0.5, 1.0 / self.falloff))
        def setter(v):
            self.falloff = math.log(0.5) / math.log(max(0.01, min(0.99, v / 100)))
            pass
        return (getter, setter)

    ##################
    # modal functions

    @RFWidget_Registry.Register_FSM_State('brush falloff', 'main')
    def brushfalloff_modal_main(self):
        if self.rfcontext.actions.pressed('brush radius'):
            self.setup_change(self.radius_to_dist, self.dist_to_radius)
            return 'change'
        if self.rfcontext.actions.pressed('brush strength'):
            self.setup_change(self.strength_to_dist, self.dist_to_strength)
            return 'change'
        if self.rfcontext.actions.pressed('brush falloff'):
            self.setup_change(self.falloff_to_dist, self.dist_to_falloff)
            return 'change'

    @RFWidget_Registry.Register_Callback('brush falloff', 'mouse cursor')
    def brushfalloff_mouse_cursor(self):
        if self.mode == 'main':
            return 'NONE' if self.hit else 'CROSSHAIR'
        return 'MOVE_X'

    @RFWidget_Registry.Register_Callback('brush falloff', 'draw post3d')
    def brushfalloff_postview(self):
        if self.mode != 'main': return
        if not self.hit: return
        cx,cy,cp = self.hit_x,self.hit_y,self.hit_p
        cs_outer = self.scale * self.radius
        cs_inner = self.scale * self.radius * math.pow(0.5, 1.0 / self.falloff)
        cr,cg,cb = self.color

        bgl.glDepthRange(0, 0.999)      # squeeze depth just a bit
        bgl.glEnable(bgl.GL_BLEND)
        self.drawing.line_width(2.0)
        self.drawing.point_size(3.0)

        ######################################
        # draw in front of geometry

        bgl.glDepthFunc(bgl.GL_LEQUAL)
        bgl.glDepthMask(bgl.GL_FALSE)   # do not overwrite depth

        bgl.glColor4f(cr, cg, cb, 0.75 * self.strength)
        bgl.glBegin(bgl.GL_TRIANGLES)
        for p0,p1 in zip(self.points[:-1], self.points[1:]):
            x0,y0 = p0
            x1,y1 = p1
            outer0 = (cs_outer * ((cx * x0) + (cy * y0))) + cp
            outer1 = (cs_outer * ((cx * x1) + (cy * y1))) + cp
            inner0 = (cs_inner * ((cx * x0) + (cy * y0))) + cp
            inner1 = (cs_inner * ((cx * x1) + (cy * y1))) + cp
            bgl.glVertex3f(*outer0)
            bgl.glVertex3f(*outer1)
            bgl.glVertex3f(*inner0)
            bgl.glVertex3f(*outer1)
            bgl.glVertex3f(*inner1)
            bgl.glVertex3f(*inner0)
        bgl.glEnd()

        bgl.glColor4f(1, 1, 1, 1)       # outer ring
        bgl.glBegin(bgl.GL_LINE_STRIP)
        for x,y in self.points:
            p = (cs_outer * ((cx * x) + (cy * y))) + cp
            bgl.glVertex3f(*p)
        bgl.glEnd()

        bgl.glColor4f(1, 1, 1, 0.5)     # inner ring
        bgl.glBegin(bgl.GL_LINE_STRIP)
        for x,y in self.points:
            p = (cs_inner * ((cx * x) + (cy * y))) + cp
            bgl.glVertex3f(*p)
        bgl.glEnd()

        bgl.glColor4f(1, 1, 1, 0.25)    # center point
        bgl.glBegin(bgl.GL_POINTS)
        bgl.glVertex3f(*cp)
        bgl.glEnd()

        ######################################
        # draw behind geometry (hidden below)

        bgl.glDepthFunc(bgl.GL_GREATER)
        bgl.glDepthMask(bgl.GL_FALSE)   # do not overwrite depth

        bgl.glColor4f(cr, cg, cb, 0.10 * self.strength)
        bgl.glBegin(bgl.GL_TRIANGLES)
        for p0,p1 in zip(self.points[:-1], self.points[1:]):
            x0,y0 = p0
            x1,y1 = p1
            outer0 = (cs_outer * ((cx * x0) + (cy * y0))) + cp
            outer1 = (cs_outer * ((cx * x1) + (cy * y1))) + cp
            inner0 = (cs_inner * ((cx * x0) + (cy * y0))) + cp
            inner1 = (cs_inner * ((cx * x1) + (cy * y1))) + cp
            bgl.glVertex3f(*outer0)
            bgl.glVertex3f(*outer1)
            bgl.glVertex3f(*inner0)
            bgl.glVertex3f(*outer1)
            bgl.glVertex3f(*inner1)
            bgl.glVertex3f(*inner0)
        bgl.glEnd()

        bgl.glColor4f(1, 1, 1, 0.05)    # outer ring
        bgl.glBegin(bgl.GL_LINE_STRIP)
        for x,y in self.points:
            p = (cs_outer * ((cx * x) + (cy * y))) + cp
            bgl.glVertex3f(*p)
        bgl.glEnd()

        bgl.glColor4f(1, 1, 1, 0.025)   # inner ring
        bgl.glBegin(bgl.GL_LINE_STRIP)
        for x,y in self.points:
            p = (cs_inner * ((cx * x) + (cy * y))) + cp
            bgl.glVertex3f(*p)
        bgl.glEnd()

        ######################################
        # reset to defaults

        bgl.glDepthFunc(bgl.GL_LEQUAL)
        bgl.glDepthMask(bgl.GL_TRUE)

        bgl.glDepthRange(0, 1)

    @RFWidget_Registry.Register_Callback('brush falloff', 'draw post2d')
    def brushfalloff_postpixel(self):
        if self.mode == 'main': return

        w,h = self.rfcontext.actions.size

        cx,cy,cp = Vector((1,0)),Vector((0,1)),self.change_center #Vector((w/2,h/2))
        cs_outer = self.radius
        cs_inner = self.radius * math.pow(0.5, 1.0 / self.falloff)
        cr,cg,cb = self.color

        bgl.glEnable(bgl.GL_BLEND)
        self.drawing.line_width(2.0)

        bgl.glColor4f(cr, cg, cb, 0.75 * self.strength)
        bgl.glBegin(bgl.GL_TRIANGLES)
        for p0,p1 in zip(self.points[:-1], self.points[1:]):
            x0,y0 = p0
            x1,y1 = p1
            outer0 = (cs_outer * ((cx * x0) + (cy * y0))) + cp
            outer1 = (cs_outer * ((cx * x1) + (cy * y1))) + cp
            inner0 = (cs_inner * ((cx * x0) + (cy * y0))) + cp
            inner1 = (cs_inner * ((cx * x1) + (cy * y1))) + cp
            bgl.glVertex2f(*outer0)
            bgl.glVertex2f(*outer1)
            bgl.glVertex2f(*inner0)
            bgl.glVertex2f(*outer1)
            bgl.glVertex2f(*inner1)
            bgl.glVertex2f(*inner0)
        bgl.glEnd()

        bgl.glColor4f(1, 1, 1, 1)                       # outer ring
        bgl.glBegin(bgl.GL_LINE_STRIP)
        for x,y in self.points:
            p = (cs_outer * ((cx * x) + (cy * y))) + cp
            bgl.glVertex2f(*p)
        bgl.glEnd()

        bgl.glColor4f(1, 1, 1, 0.5)                     # inner ring
        bgl.glBegin(bgl.GL_LINE_STRIP)
        for x,y in self.points:
            p = (cs_inner * ((cx * x) + (cy * y))) + cp
            bgl.glVertex2f(*p)
        bgl.glEnd()

