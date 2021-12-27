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

# <pep8 compliant>


bl_info = {
    'name': 'Screencast Keys Mod',
    'author': 'Paulo Gomes, Bart Crouch, John E. Herrenyo, '
              'Gaia Clary, Pablo Vazquez, chromoly, Nutti',
    'version': (2, 0, 1),
    'blender': (2, 77, 0),
    'location': '3D View > Properties Panel > Screencast Keys',
    'warning': '',
    'description': 'Display keys pressed in the 3D View, '
                   'useful for screencasts.',
    'wiki_url': 'http://wiki.blender.org/index.php/Extensions:2.6/'
                'Py/Scripts/3D_interaction/Screencast_Key_Status_Tool',
    'wiki_url2': 'https://github.com/chromoly/blender-ScreencastKeysMod',
    'tracker_url': 'http://projects.blender.org/tracker/index.php?'
                   'func=detail&aid=21612',
    "category": "Learnbgame",
}


"""
既知の問題点:
    レンダリング中は全てのイベントを取得出来ない。
    scene_callback_pre で wmWindow.modalhandlersを並び替えるので
    落ちる可能性がある。
"""


import collections
import enum
import importlib
import re
import string
import time

import bpy
import bgl
import blf
import bpy.props

try:
    importlib.reload(structures)
    importlib.reload(utils)
    importlib.reload(modalmanager)
except NameError:
    pass
from .utils import AddonPreferences, AddonKeyMapUtility
from .modalmanager import ModalHandlerManager


###############################################################################
# Addon Preferences
###############################################################################
class ScreenCastKeysPreferences(
    AddonKeyMapUtility,
    AddonPreferences,
    bpy.types.PropertyGroup if '.' in __name__ else
    bpy.types.AddonPreferences):
    bl_idname = __name__

    color = bpy.props.FloatVectorProperty(
        name='Color',
        default=(1.0, 1.0, 1.0),
        min=0.0,
        max=1.0,
        subtype='COLOR_GAMMA',
        size=3
    )
    color_shadow = bpy.props.FloatVectorProperty(
        name='Shadow Color',
        default=(0.0, 0.0, 0.0, 1.0),
        min=0.0,
        max=1.0,
        subtype='COLOR_GAMMA',
        size=4
    )
    font_size = bpy.props.IntProperty(
        name='Font Size',
        default=bpy.context.user_preferences.ui_styles[0].widget.points,
        min=6,
        max=48
    )
    origin = bpy.props.EnumProperty(
        name='Origin',
        items=[('REGION', 'Region', "Region.type is 'WINDOW'"),
               ('AREA', 'Area', ''),
               ('WINDOW', 'Window', '')],
        default='REGION',
    )
    offset = bpy.props.IntVectorProperty(
        name='Offset',
        default=(20, 80),
        size=2,
    )
    display_time = bpy.props.FloatProperty(
        name='Display Time',
        default=3.0,
        min=0.5,
        max=10.0,
        step=10,
        subtype='TIME'
    )
    # fade_time = bpy.props.FloatProperty(
    #     name='Fade Out Time',
    #     description='Time in seconds for keys to last on screen',
    #     default=1.0,
    #     min=0.0,
    #     max=10.0,
    #     step=10,
    #     subtype='TIME'
    # )
    show_last_operator = bpy.props.BoolProperty(
        name='Show Last Operator',
        default=False,
    )

    # TODO: continuous grab が有効な場合に正確なカーソル座標を取得できない
    # use_avoid = bpy.props.BoolProperty(
    #     name='Avoid',
    #     description='Avoid mouse cursor',
    #     default=False,
    # )

    def draw(self, context):
        layout = self.layout
        """:type: bpy.types.UILayout"""

        column = layout.column()
        split = column.split()
        col = split.column()
        col.prop(self, 'color')
        col.prop(self, 'color_shadow')
        col.prop(self, 'font_size')

        col = split.column()
        col.prop(self, 'display_time')
        # col.prop(self, 'fade_time')

        col = split.column()
        col.prop(self, 'origin')
        col.prop(self, 'offset')
        col.prop(self, 'show_last_operator')

        super().draw(context)


###############################################################################
# enum.IntEnum: EventType
###############################################################################
# タイポを防ぐために使う
def has_release_event(self):
    # 自分用にパッチでRIGHTBRACKETKEY直後にCOLONKEY,ATKEY,ASCIICIRCUMKEYを
    # 追加している
    if 'ASCIICIRCUM' in EventType.__members__:
        key = 'ASCIICIRCUM'
    else:
        key = 'RIGHT_BRACKET'

    if self in {EventType.LEFTMOUSE, EventType.MIDDLEMOUSE,
                EventType.RIGHTMOUSE}:
        return True
    elif re.match('BUTTON\d+MOUSE', self.name):
        return True
    elif self in {EventType.PEN, EventType.ERASER}:
        return True
    elif (EventType['ZERO'].value <= self.value <=
          EventType[key]):
        return True
    elif EventType['F1'].value <= self.value <= EventType['F19']:
        return True
    return False

event_type_enum_items = bpy.types.Event.bl_rna.properties['type'].enum_items

EventType = enum.IntEnum(
    'EventType',
    [(e.identifier, e.value) for e in event_type_enum_items])

EventType.has_release_event = has_release_event
EventType.names = {e.identifier: e.name for e in event_type_enum_items}


###############################################################################
# Operator
###############################################################################
def intersect_aabb(min1, max1, min2, max2):
    """from isect_aabb_aabb_v3()
    """
    for i in range(len(min1)):
        if max1[i] < min2[i] or max2[i] < min1[i]:
            return False
    return True


def region_window_rectangle(area):
    rect = [99999, 99999, 0, 0]
    for region in area.regions:
        if region.type == 'WINDOW':
            rect[0] = min(rect[0], region.x)
            rect[1] = min(rect[1], region.y)
            rect[2] = max(region.x + region.width - 1, rect[2])
            rect[3] = max(region.y + region.height - 1, rect[3])
    return rect


def region_rectangle_v3d(context, area=None, region=None):
    """
    for Region Overlap
    return window coordinates (xmin, ymin, xmax, ymax)
    """
    if not area:
        area = context.area
    if not region:
        region = context.region

    if region.type != 'WINDOW':
        return (region.x, region.y,
                region.x + region.width, region.y + region.height)

    window = tools = tool_props = ui = None
    for ar in area.regions:
        if ar.width > 1:
            if ar.type == 'WINDOW':
                if ar == region:
                    region = ar
            elif ar.type == 'TOOLS':
                tools = ar
            elif ar.type == 'TOOL_PROPS':
                tool_props = ar
            elif ar.type == 'UI':
                ui = ar

    # xmin = region.x
    # xmax = xmin + region.width - 1
    xmin, _, xmax, _ = region_window_rectangle(area)
    sys_pref = context.user_preferences.system
    if sys_pref.use_region_overlap:
        left_widht = right_widht = 0
        if tools and ui:
            r1, r2 = sorted([tools, ui], key=lambda ar: ar.x)
            if r1.x == area.x:
                # 両方左
                if r2.x == r1.x + r1.width:
                    left_widht = r1.width + r2.width
                # 片方ずつ
                else:
                    left_widht = r1.width
                    right_widht = r2.width
            # 両方右
            else:
                right_widht = r1.width + r2.width

        elif tools:
            if tools.x == area.x:
                left_widht = tools.width
            else:
                right_widht = tools.width

        elif ui:
            if ui.x == area.x:
                left_widht = ui.width
            else:
                right_widht = ui.width

        xmin = max(xmin, area.x + left_widht)
        xmax = min(xmax, area.x + area.width - right_widht - 1)

    # xmin = max(0, xmin - region.x)
    # xmax = min(xmax - region.x, region.width - 1)
    ymin = region.y  #0
    ymax = region.y + region.height - 1  #window.height - 1
    return xmin, ymin, xmax, ymax


def invoke_callback(context, event, dst, src):
    win = context.window
    dst.event_timer_add(context)
    # if src:
    #     dst.hold_keys.update(src.hold_keys)
mhm = ModalHandlerManager('wm.screencast_keys', callback=invoke_callback)
# mhm = ModalHandlerManager('wm.screencast_keys')


class ScreencastKeysStatus(bpy.types.Operator):
    bl_idname = 'wm.screencast_keys'
    bl_label = 'Screencast Keys'
    bl_description = 'Display keys pressed'
    bl_options = {'REGISTER'}

    # modifier確認要。不要か？
    # window_event = {}  # {Window.as_pointer(): Event, ...}

    hold_keys = []
    event_log = []  # [[time, event_type, mod, repeat], ...]
    operator_log = []  # [[time, bl_label, idname_py, addr], ...]

    modifier_event_types = [
        EventType.LEFT_SHIFT,
        EventType.RIGHT_SHIFT,
        EventType.LEFT_CTRL,
        EventType.RIGHT_CTRL,
        EventType.LEFT_ALT,
        EventType.RIGHT_ALT,
        EventType.OSKEY
    ]

    space_types = {
        'VIEW_3D': bpy.types.SpaceView3D,
        'TIMELINE': bpy.types.SpaceTimeline,
        'GRAPH_EDITOR': bpy.types.SpaceGraphEditor,
        'DOPESHEET_EDITOR': bpy.types.SpaceDopeSheetEditor,
        'NLA_EDITOR': bpy.types.SpaceNLA,
        'IMAGE_EDITOR': bpy.types.SpaceImageEditor,
        'SEQUENCE_EDITOR': bpy.types.SpaceSequenceEditor,
        'CLIP_EDITOR': bpy.types.SpaceClipEditor,
        'TEXT_EDITOR': bpy.types.SpaceTextEditor,
        'NODE_EDITOR': bpy.types.SpaceNodeEditor,
        'LOGIC_EDITOR': bpy.types.SpaceLogicEditor,
        'PROPERTIES': bpy.types.SpaceProperties,
        'OUTLINER': bpy.types.SpaceOutliner,
        'USER_PREFERENCES': bpy.types.SpaceUserPreferences,
        'INFO': bpy.types.SpaceInfo,
        'FILE_BROWSER': bpy.types.SpaceFileBrowser,
        'CONSOLE': bpy.types.SpaceConsole,
    }

    SEPARATOR_HEIGHT = 0.6  # フォント高の倍率

    TIMER_STEP = 0.1
    prev_time = 0.0
    timers = {}  # {Window.as_pointer(): Timer, ...}

    handlers = {}  # {(Space, region_type): handle, ...}

    draw_regions_prev = set()  # {region.as_pointer(), ...}
    origin = {'window': '', 'area': '', 'space': '', 'region_type': ''}
    # {area_addr: [space_addr, ...], ...}
    area_spaces = collections.defaultdict(set)

    @classmethod
    def sorted_modifiers(cls, modifiers):
        """modifierを並び替えて重複を除去した名前を返す"""

        def sort_func(et):
            if et in cls.modifier_event_types:
                return cls.modifier_event_types.index(et)
            else:
                return 100

        modifiers = sorted(modifiers, key=sort_func)
        names = []
        for mod in modifiers:
            name = mod.names[mod.name]
            if mod in cls.modifier_event_types:
                name = re.sub('(Left | Right )', '', name)
            if name not in names:
                names.append(name)
        return names

    @classmethod
    def removed_old_event_log(cls):
        prefs = ScreenCastKeysPreferences.get_instance()
        """:type: ScreenCastKeysPreferences"""
        current_time = time.time()
        event_log = []
        for item in cls.event_log:
            event_time = item[0]
            t = current_time - event_time
            if t <= prefs.display_time:
                event_log.append(item)
        return event_log

    @classmethod
    def removed_old_operator_log(cls):
        prefs = ScreenCastKeysPreferences.get_instance()
        """:type: ScreenCastKeysPreferences"""
        # 時間経過ではなく数で制限する
        if 0:
            current_time = time.time()
            operator_log = []
            for item in cls.operator_log:
                event_time = item[0]
                t = current_time - event_time
                if t <= prefs.display_time:
                    operator_log.append(item)
            return operator_log
        else:
            return cls.operator_log[-32:]

    @classmethod
    def get_origin(cls, context):
        prefs = ScreenCastKeysPreferences.get_instance()
        """:type: ScreenCastKeysPreferences"""

        def match(area):
            # for area in context.screen.areas:
            if area.as_pointer() == cls.origin['area']:
                return True
            elif area.spaces.active.as_pointer() == cls.origin['space']:
                return True
            else:
                addr = area.as_pointer()
                if addr in cls.area_spaces:
                    addrs = {sp.as_pointer() for sp in area.spaces}
                    if cls.origin['space'] in addrs:
                        return True
            return False

        x, y = prefs.offset
        for win in context.window_manager.windows:
            if win.as_pointer() == cls.origin['window']:
                break
        else:
            return None, None, None, 0, 0
        if prefs.origin == 'WINDOW':
            return win, None, None, x, y
        elif prefs.origin == 'AREA':
            for area in win.screen.areas:
                if match(area):
                    return win, area, None, x + area.x, y + area.y

        elif prefs.origin == 'REGION':
            for area in win.screen.areas:
                if match(area):
                    for region in area.regions:
                        if region.type == cls.origin['region_type']:
                            if area.type == 'VIEW_3D':
                                rect = region_rectangle_v3d(context, area,
                                                            region)
                                x += rect[0]
                                y += rect[1]
                            else:
                                x += region.x
                                y += region.y
                            return win, area, region, x, y
        return None, None, None, 0, 0

    @classmethod
    def calc_draw_rectangle(cls, context):
        """(xmin, ymin, xmax, ymax)というwindow座標を返す。
        該当する描画範囲がないならNoneを返す。
        """

        prefs = ScreenCastKeysPreferences.get_instance()
        """:type: ScreenCastKeysPreferences"""

        font_size = prefs.font_size
        font_id = 0
        dpi = context.user_preferences.system.dpi
        blf.size(font_id, font_size, dpi)

        th = blf.dimensions(0, string.printable)[1]

        win, area, region, x, y = cls.get_origin(context)
        if not win:
            return None

        w = h = 0

        if prefs.show_last_operator:
            operator_log = cls.removed_old_operator_log()
            if operator_log:
                t, name, idname_py, addr = operator_log[-1]
                text = bpy.app.translations.pgettext(name, 'Operator')
                text += " ('{}')".format(idname_py)
                tw = blf.dimensions(font_id, text)[0]
                w = max(w, tw)
            h += th + th * cls.SEPARATOR_HEIGHT

        if cls.hold_keys:
            mod_names = cls.sorted_modifiers(cls.hold_keys)
            text = ' + '.join(mod_names)
            tw = blf.dimensions(font_id, text)[0]
            w = max(w, tw)
            h += th

        event_log = cls.removed_old_event_log()

        if cls.hold_keys or event_log:
            tw = blf.dimensions(font_id, 'Left Mouse')[0]
            w = max(w, tw)
            h += th * cls.SEPARATOR_HEIGHT

        for event_time, event_type, modifiers, count in event_log[::-1]:
            # t = current_time - event_time
            # if t > prefs.display_time:
            #     continue

            text = event_type.names[event_type.name]
            if modifiers:
                mod_names = cls.sorted_modifiers(modifiers)
                text = ' + '.join(mod_names) + ' + ' + text
            if count > 1:
                text += ' x' + str(count)

            w = max(w, blf.dimensions(font_id, text)[0])
            h += th

        h += th

        if 0:
            return x, y, x + w, y + h
        else:
            if prefs.origin == 'WINDOW':
                return x, y, x + w, y + h
            else:
                if prefs.origin == 'AREA':
                    xmin = area.x
                    ymin = area.y
                    xmax = area.x + area.width - 1
                    ymax = area.y + area.height - 1
                else:
                    xmin = region.x
                    ymin = region.y
                    xmax = region.x + region.width - 1
                    ymax = region.y + region.height - 1
                return (max(x, xmin), max(y, ymin),
                        min(x + w, xmax), min(y + h, ymax))

    @classmethod
    def find_redraw_regions(cls, context):
        """[(area, region), ...]"""
        rect = cls.calc_draw_rectangle(context)
        if not rect:
            return []
        x, y, xmax, ymax = rect
        w = xmax - x
        h = ymax - y
        if w == h == 0:
            return []

        regions = []
        for area in context.screen.areas:
            for region in area.regions:
                if region.id != 0:
                    min1 = (region.x, region.y)
                    max1 = (region.x + region.width - 1,
                            region.y + region.height - 1)
                    if intersect_aabb(min1, max1, (x, y),
                                      (x + w - 1, y + h - 1)):
                        regions.append((area, region))
        return regions

    @classmethod
    def draw_callback(cls, context):
        prefs = ScreenCastKeysPreferences.get_instance()
        """:type: ScreenCastKeysPreferences"""

        if context.window.as_pointer() != cls.origin['window']:
            return
        rect = cls.calc_draw_rectangle(context)
        if not rect:
            return
        xmin, ymin, xmax, ymax = rect
        win, _area, _region, x, y = cls.get_origin(context)
        w = xmax - x
        h = ymax - y
        if w == h == 0:
            return
        region = context.region
        area = context.area
        if region.type == 'WINDOW':
            r_xmin, r_ymin, r_xmax, r_ymax = region_window_rectangle(area)
        else:
            r_xmin, r_ymin, r_xmax, r_ymax = (
                region.x,
                region.y,
                region.x + region.width - 1,
                region.y + region.height - 1)
        if not intersect_aabb(
                (r_xmin, r_ymin), (r_xmax, r_ymax),
                (xmin + 1, ymin + 1), (xmax - 1, ymax - 1)):
            return

        current_time = time.time()
        draw_any = False

        font_size = prefs.font_size
        font_id = 0
        dpi = context.user_preferences.system.dpi
        blf.size(font_id, font_size, dpi)

        def draw_text(text):
            col = prefs.color_shadow
            bgl.glColor4f(*col[:3], col[3] * 20)
            blf.blur(font_id, 5)
            blf.draw(font_id, text)
            blf.blur(font_id, 0)

            bgl.glColor3f(*prefs.color)
            blf.draw(font_id, text)

        def draw_line(p1, p2):
            bgl.glEnable(bgl.GL_BLEND)
            bgl.glEnable(bgl.GL_LINE_SMOOTH)

            bgl.glLineWidth(3.0)
            bgl.glColor4f(*prefs.color_shadow)
            bgl.glBegin(bgl.GL_LINES)
            bgl.glVertex2f(*p1)
            bgl.glVertex2f(*p2)
            bgl.glEnd()

            bgl.glLineWidth(1.0 if prefs.color_shadow[-1] == 0.0 else 1.5)
            bgl.glColor3f(*prefs.color)
            bgl.glBegin(bgl.GL_LINES)
            bgl.glVertex2f(*p1)
            bgl.glVertex2f(*p2)
            bgl.glEnd()

            bgl.glLineWidth(1.0)
            bgl.glDisable(bgl.GL_LINE_SMOOTH)

        # user_preferences.system.use_region_overlapが真の場合に、
        # 二重に描画されるのを防ぐ
        glscissorbox = bgl.Buffer(bgl.GL_INT, 4)
        bgl.glGetIntegerv(bgl.GL_SCISSOR_BOX, glscissorbox)
        if context.area.type == 'VIEW_3D' and region.type == 'WINDOW':
            xmin, ymin, xmax, ymax = region_rectangle_v3d(context)
            bgl.glScissor(xmin, ymin, xmax - xmin + 1, ymax - ymin + 1)

        th = blf.dimensions(0, string.printable)[1]
        px = x - region.x
        py = y - region.y

        operator_log = cls.removed_old_operator_log()
        if prefs.show_last_operator and operator_log:
            t, name, idname_py, addr = operator_log[-1]
            if current_time - t <= prefs.display_time:
                color = prefs.color
                bgl.glColor3f(*color)

                text = bpy.app.translations.pgettext_iface(name, 'Operator')
                text += " ('{}')".format(idname_py)

                blf.position(font_id, px, py, 0)
                draw_text(text)
                py += th + th * cls.SEPARATOR_HEIGHT * 0.2
                tw = blf.dimensions(font_id, 'Left Mouse')[0]  # 適当
                draw_line((px, py), (px + tw, py))
                py += th * cls.SEPARATOR_HEIGHT * 0.8

                draw_any = True

            else:
                py += th + th * cls.SEPARATOR_HEIGHT

        bgl.glColor3f(*prefs.color)
        if cls.hold_keys or mhm.is_rendering():
            col = prefs.color_shadow[:3] + (prefs.color_shadow[3] * 2,)
            mod_names = cls.sorted_modifiers(cls.hold_keys)
            if mhm.is_rendering():
                if 0:
                    text = '- - -'
                else:
                    text = ''
            else:
                text = ' + '.join(mod_names)
            blf.position(font_id, px, py, 0)
            # blf.draw(font_id, text)
            draw_text(text)
            py += th
            draw_any = True
        else:
            py += th

        event_log = cls.removed_old_event_log()

        if cls.hold_keys or event_log:
            py += th * cls.SEPARATOR_HEIGHT * 0.2
            tw = blf.dimensions(font_id, 'Left Mouse')[0]  # 適当
            draw_line((px, py), (px + tw, py))
            py += th * cls.SEPARATOR_HEIGHT * 0.8
            draw_any = True
        else:
            py += th * cls.SEPARATOR_HEIGHT

        for event_time, event_type, modifiers, count in event_log[::-1]:
            color = prefs.color
            bgl.glColor3f(*color)

            text = event_type.names[event_type.name]
            if modifiers:
                mod_names = cls.sorted_modifiers(modifiers)
                text = ' + '.join(mod_names) + ' + ' + text
            if count > 1:
                text += ' x' + str(count)
            blf.position(font_id, px, py, 0)
            # blf.draw(font_id, text)
            draw_text(text)

            py += th
            draw_any = True

        bgl.glDisable(bgl.GL_BLEND)
        bgl.glScissor(*glscissorbox)
        bgl.glLineWidth(1.0)
        # blf.disable(font_id, blf.SHADOW)

        if draw_any:
            cls.draw_regions_prev.add(region.as_pointer())

    def update_holed_keys(self, event):
        """self.hold_keysを更新"""
        if mhm.is_rendering():
            self.hold_keys.clear()

        event_type = EventType[event.type]
        if event_type == EventType.WINDOW_DEACTIVATE:
            self.hold_keys.clear()
        elif event_type in self.modifier_event_types:
            if event.value == 'PRESS':
                if event_type not in self.hold_keys:
                    self.hold_keys.append(event_type)
            elif event.value == 'RELEASE':
                if event_type in self.hold_keys:
                    self.hold_keys.remove(event_type)
        elif event_type.has_release_event():
            if event.value == 'PRESS':
                if event_type not in self.hold_keys:
                    self.hold_keys.append(event_type)
            elif event.value == 'RELEASE':
                if event_type in self.hold_keys:
                    self.hold_keys.remove(event_type)
        # TODO: evenetを取得出来ずにmodifierが更新されていた場合
        # モディファイアキーを押しっぱなしでwindowを非アクティブから
        # アクティブにしてもPRESSイベントが無いとそのモディファイアは有効に
        # ならない

    def is_ignore_event(self, event):
        """表示しないeventなら真を返す"""
        event_type = EventType[event.type]
        if event_type in {EventType.NONE, EventType.MOUSEMOVE,
                          EventType.INBETWEEN_MOUSEMOVE,
                          EventType.WINDOW_DEACTIVATE, EventType.TEXTINPUT}:
            return True
        elif event_type.name.startswith('EVT_TWEAK'):
            return True
        elif event_type.name.startswith('TIMER'):
            return True

    def is_modifier_event(self, event):
        event_type = EventType[event.type]
        return event_type in self.modifier_event_types

    @mhm.modal
    def modal(self, context, event):
        prefs = ScreenCastKeysPreferences.get_instance()
        """:type: ScreenCastKeysPreferences"""
        # print(context.screen, context.window.as_pointer())

        event_type = EventType[event.type]
        current_time = time.time()

        # update cls.area_spaces
        for area in context.screen.areas:
            for space in area.spaces:
                self.area_spaces[area.as_pointer()].add(space.as_pointer())

        # modifiers
        self.update_holed_keys(event)
        current_mod = self.hold_keys.copy()
        if event_type in current_mod:
            current_mod.remove(event_type)

        # event_log
        if (not self.is_ignore_event(event) and
                not self.is_modifier_event(event) and event.value == 'PRESS'):
            last = self.event_log[-1] if self.event_log else None
            current = [current_time, event_type, current_mod, 1]
            if (last and last[1:-1] == current[1:-1] and
                    current_time - last[0] < prefs.display_time):
                last[0] = current_time
                last[-1] += 1
            else:
                self.event_log.append(current)
        self.event_log[:] = self.removed_old_event_log()

        # operator_log
        operators = list(context.window_manager.operators)

        if operators:
            if self.operator_log:
                addr = self.operator_log[-1][-1]
            else:
                addr = None
            j = 0
            for i, op in enumerate(operators[::-1]):
                if op.as_pointer() == addr:
                    j = len(operators) - i
                    break

            for op in operators[j:]:
                m, f = op.bl_idname.split('_OT_')
                idname_py = m.lower() + '.' + f
                self.operator_log.append(
                    [current_time, op.bl_label, idname_py, op.as_pointer()])
        self.operator_log[:] = self.removed_old_operator_log()

        # redraw
        prev_time = self.prev_time
        if (not self.is_ignore_event(event) or
                prev_time and current_time - prev_time >= self.TIMER_STEP):
            # print(self.draw_regions_prev, current_time)
            regions = self.find_redraw_regions(context)

            # 前回描画した箇所でregionsに含まれないものは再描画
            for area in context.screen.areas:
                for region in area.regions:
                    if region.as_pointer() in self.draw_regions_prev:
                        if region.id != 0:
                            region.tag_redraw()
                        self.draw_regions_prev.remove(region.as_pointer())
            # self.draw_regions_prev.clear()

            # 再描画
            for area, region in regions:
                space_type = self.space_types[area.type]
                h_key = (space_type, region.type)
                if h_key not in self.handlers:
                    self.handlers[h_key] = space_type.draw_handler_add(
                        self.draw_callback, (context,), region.type,
                        'POST_PIXEL')
                region.tag_redraw()
                self.draw_regions_prev.add(region.as_pointer())

            self.__class__.prev_time = current_time

        return {'PASS_THROUGH'}

    @classmethod
    def draw_handler_remove(cls):
        for (space_type, region_type), handle in cls.handlers.items():
            space_type.draw_handler_remove(handle, region_type)
        cls.handlers.clear()

    @classmethod
    def event_timer_add(cls, context):
        wm = context.window_manager
        for win in wm.windows:
            key = win.as_pointer()
            if key not in cls.timers:
                cls.timers[key] = wm.event_timer_add(cls.TIMER_STEP, win)

    @classmethod
    def event_timer_remove(cls, context):
        wm = context.window_manager
        for win in wm.windows:
            key = win.as_pointer()
            if key in cls.timers:
                wm.event_timer_remove(cls.timers[key])
        cls.timers.clear()

    @mhm.invoke
    def invoke(self, context, event):
        # cls = self.__class__
        if mhm.is_running(context):
            self.event_timer_remove(context)
            self.draw_handler_remove()
            self.hold_keys.clear()
            self.event_log.clear()
            self.operator_log.clear()
            self.draw_regions_prev.clear()
            context.area.tag_redraw()
            return {'CANCELLED'}
        else:
            self.update_holed_keys(event)
            # self.draw_handler_add(context)
            self.event_timer_add(context)
            context.window_manager.modal_handler_add(self)
            self.origin['window'] = context.window.as_pointer()
            self.origin['area'] = context.area.as_pointer()
            self.origin['space'] = context.space_data.as_pointer()
            self.origin['region_type'] = context.region.type
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}


class ScreencastKeysStatusSetOrigin(bpy.types.Operator):
    bl_idname = 'wm.screencast_keys_set_origin'
    bl_label = 'Screencast Keys Set Origin'
    bl_description = ''
    bl_options = {'REGISTER'}

    color = (1.0, 0.0, 0.0, 0.3)
    handles = {}  # {(space_type, region_type): handle, ...}

    def draw_callback(self, context):
        region = context.region
        if region and region == self.region:
            bgl.glEnable(bgl.GL_BLEND)
            bgl.glColor4f(*self.color)
            bgl.glRecti(0, 0, region.width, region.height)
            bgl.glDisable(bgl.GL_BLEND)
            bgl.glColor4f(1.0, 1.0, 1.0, 1.0)  # 初期値ってこれだっけ？

    def draw_handler_add(self, context):
        for area in context.screen.areas:
            space_type = ScreencastKeysStatus.space_types[area.type]
            for region in area.regions:
                if region.id != 0:
                    key = (space_type, region.type)
                    if key not in self.handles:
                        handle = space_type.draw_handler_add(
                            self.draw_callback, (context,), region.type,
                            'POST_PIXEL')
                        self.handles[key] = handle

    def draw_handler_remove(self):
        for (space_type, region_type), handle in self.handles.items():
            space_type.draw_handler_remove(handle, region_type)
        self.handles.clear()

    def current_region(self, context, event):
        x, y = event.mouse_x, event.mouse_y
        for area in context.screen.areas:
            for region in area.regions:
                if region.id != 0:
                    if region.x <= x < region.x + region.width:
                        if region.y <= y < region.y + region.height:
                            return area, region
        return None, None

    def modal(self, context, event):
        area, region = self.current_region(context, event)
        if self.area_prev:
            self.area_prev.tag_redraw()
        if area:
            area.tag_redraw()
        self.region = region
        if event.type in {'LEFTMOUSE', 'SPACE', 'RET', 'NUMPAD_ENTER'}:
            if event.value == 'PRESS':
                origin = ScreencastKeysStatus.origin
                origin['window'] = context.window.as_pointer()
                origin['area'] = area.as_pointer()
                origin['space'] = area.spaces.active.as_pointer()
                origin['region_type'] = region.type
                self.draw_handler_remove()
                return {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.draw_handler_remove()
            return {'CANCELLED'}
        self.area_prev = area
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.area_prev = None
        self.region = None
        self.draw_handler_add(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class ScreencastKeysPanel(bpy.types.Panel):
    bl_idname = 'WM_PT_screencast_keys'
    bl_label = 'Screencast Keys'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw_header(self, context):
        layout = self.layout
        """:type: bpy.types.UILayout"""
        layout.prop(context.window_manager, 'enable_screencast_keys',
                    text='')

    def draw(self, context):
        layout = self.layout
        """:type: bpy.types.UILayout"""

        prefs = ScreenCastKeysPreferences.get_instance()
        """:type: ScreenCastKeysPreferences"""

        column = layout.column()

        column.prop(prefs, 'color')
        column.prop(prefs, 'color_shadow')
        column.prop(prefs, 'font_size')
        column.prop(prefs, 'display_time')
        # column.prop(prefs, 'fade_time')

        column.separator()

        column.prop(prefs, 'origin')
        row = column.row()
        row.prop(prefs, 'offset')
        column.operator('wm.screencast_keys_set_origin',
                        text='Set Origin')
        column.prop(prefs, 'show_last_operator', text='Last Operator')

    @classmethod
    def register(cls):
        def get_func(self):
            return mhm.is_running(bpy.context)

        def set_func(self, value):
            pass

        def update_func(self, context):
            bpy.ops.wm.screencast_keys('INVOKE_REGION_WIN')

        bpy.types.WindowManager.enable_screencast_keys = \
            bpy.props.BoolProperty(
                name='Screencast Keys',
                get=get_func,
                set=set_func,
                update=update_func,
            )

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.enable_screencast_keys


###############################################################################
# Register
###############################################################################
classes = (
    ScreenCastKeysPreferences,
    ScreencastKeysStatus,
    ScreencastKeysStatusSetOrigin,
    ScreencastKeysPanel,
)

addon_keymaps = []


def register():
    for c in classes:
        bpy.utils.register_class(c)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('wm.screencast_keys', 'C', 'PRESS',
                                  shift=True, alt=True)
        addon_keymaps.append((km, kmi))

        addon_prefs = ScreenCastKeysPreferences.get_instance()
        """:type: ScreenCastKeysPreferences"""
        addon_prefs.register_keymap_items(addon_keymaps)


def unregister():
    addon_prefs = ScreenCastKeysPreferences.get_instance()
    """:type: ScreenCastKeysPreferences"""
    addon_prefs.unregister_keymap_items()

    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == '__main__':
    register()
