from .shape import *
from ..utils.fc_view_3d_utils import get_view_direction_by_rot_matrix, get_3d_vertex_for_2d

class Rectangle_Shape(Shape):
    
    def __init__(self):
        super().__init__() 
        self._vertex1 = None
        self._vertex3 = None
        self._vertices_2d = [None, None, None, None]
        self._center_2d = None

    def handle_mouse_press(self, mouse_pos_2d, mouse_pos_3d, event, context):

        if mouse_pos_3d is None:
            return False

        if self.is_none() and event.ctrl:
            self._vertices_2d[0] = mouse_pos_2d

            self._vertex1 = mouse_pos_3d

            self.state = ShapeState.PROCESSING
            return False

        elif self.is_processing():
            self.state = ShapeState.CREATED
            return False

        elif self.is_created() and event.ctrl:
            return True

        return False

    def handle_mouse_move(self, mouse_pos_2d, mouse_pos_3d, event, context):

        if self.is_processing():

            self._vertex3 = mouse_pos_3d
            self._vertices_2d[2] = mouse_pos_2d

            self._vertices_2d[1] = (self._vertices_2d[0][0], self._vertices_2d[2][1])
            self._vertices_2d[3] = (self._vertices_2d[2][0], self._vertices_2d[0][1])

            self.calc_center_2d()
 
            self.create_rect(context)
            return True

        result = super().handle_mouse_move(mouse_pos_2d, mouse_pos_3d, event, context)

        return result

    def calc_center_2d(self):
        self._center_2d = (self._vertices_2d[0][0] +  (self._vertices_2d[3][0] - self._vertices_2d[0][0]) / 2, 
                            self._vertices_2d[0][1] +  (self._vertices_2d[1][1] - self._vertices_2d[0][1]) / 2)


    def stop_move(self, context):
        super().stop_move(context)

        self.calc_center_2d()


    def create_rect(self, context):
        rv3d      = context.space_data.region_3d
        view_rot  = rv3d.view_rotation

        self._vertices.clear()

        # get missing 3d vertices
        if not self._snap_to_target:
            vertex2 = get_3d_vertex(context, self._vertices_2d[1])
            vertex4 = get_3d_vertex(context, self._vertices_2d[3])
        else:
            vertex2 = self.get_3d_for_2d(self._vertices_2d[1], context)
            vertex4 = self.get_3d_for_2d(self._vertices_2d[3], context)  
        
        self._vertices.extend([self._vertex1, vertex2, self._vertex3, vertex4])
        
    def start_rotate(self, mouse_pos, context):
        if self.is_created():
           
            tmp_vertices_2d = []
            ox = self._center_2d[0]
            oy = self._center_2d[1]

            for i, vertex2d in enumerate(self._vertices_2d):
                px = vertex2d[0]
                py = vertex2d[1]

                # 15 degree steps (TODO: parametrize?)
                angle = radians(15)
               
                x = ox + cos(angle) * (px - ox) - sin(angle) * (py - oy)
                y = oy + sin(angle) * (px - ox) + cos(angle) * (py - oy)

                tmp_vertices_2d.append((x,y))
                
                if not self._snap_to_target:
                    direction = get_view_direction_by_rot_matrix(self._view_context.view_rotation) * context.scene.draw_distance
                    self._vertices[i] = get_3d_vertex_for_2d(self._view_context, (x,y), -direction)
                else:
                    self._vertices[i] = self.get_3d_for_2d((x,y), context) 
            
            self._vertices_2d = tmp_vertices_2d

            return True
        
        return False

    def draw_points(self):
        return True

    def get_text(self, context):
        text = "{0} | Mode (M): {1} | Primitive (P): {2} | {3}"

        keyboard = "Esc: Exit"
        mouse_action = "Set point 1: Ctrl + Left click"
        p_type = "Rectangle"

        if self.is_created():
            keyboard = "Esc: Undo | G: Move | R: Rotate | E: Extrude"
            mouse_action = "Apply: Ctrl + Left Click"
   
        if self.is_processing():
            mouse_action = "Set point 2: Left click"
            keyboard = "Esc: Undo"

        return text.format(mouse_action, context.scene.bool_mode, p_type, keyboard)