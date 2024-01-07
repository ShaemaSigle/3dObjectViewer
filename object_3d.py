import pygame as pg
from matrix_functions import *
from numba import njit
from projection import *

#Used to speed up calculations
@njit(fastmath=True)
def any_func(arr, a, b):
    return np.any((arr == a) | (arr == b))

class Object3D:
    def __init__(self, render, vertices='', faces='', materials=None):
        self.render = render
        self.vertices_untouched = np.array(vertices) #Needed to reset the object after any transformations
        self.vertices = np.array(vertices)
        self.faces = faces
        self.translate([0.0001, 0.0001, 0.0001])
        self.polygon_count = len(faces)
        self.materials_count = len(materials)
        self.font = pg.font.SysFont('Arial', 30, bold=True)
        self.color_faces = [(pg.Color(materials[face.material_name]), face) for face in self.faces]
        self.movement_flag, self.draw_vertices = False, False
        self.label = ''
    
    def draw(self, rotateX, rortateY, rotateZ):
        if(rotate_x or rortateY or rotateZ): 
            self.movement_flag = True
            self.movement(rotateX, rortateY, rotateZ)
        else: self.movement_flag = False
        self.screen_projection()

    def movement(self, x, y, z):
        #Currently the only movement used is rotation, but it can be changed here
        if self.movement_flag:
            if x: self.rotate_x(-(pg.time.get_ticks() % 0.005))
            if y: self.rotate_y(-(pg.time.get_ticks() % 0.005))
            if z: self.rotate_z(-(pg.time.get_ticks() % 0.005))

    def reset(self):
        self.vertices = self.vertices_untouched
    
    #All vertices need to be projected onto the screen to be displayed correctly
    def screen_projection(self):
        vertices = self.vertices @ self.render.camera.camera_matrix()
        vertices = vertices @ self.render.projection.projection_matrix
        
        # Normalize homogeneous coordinates
        vertices /= vertices[:, -1].reshape(-1, 1)
        vertices[(vertices > 1) | (vertices < -1)] = 0

        # Transform to screen coordinates
        vertices = vertices @ self.render.projection.to_screen_matrix
        vertices = vertices[:, :2]

        for index, color_face in enumerate(self.color_faces):
            color, face = color_face
            polygon = vertices[face.vertices]
            if not any_func(polygon, self.render.H_WIDTH, self.render.H_HEIGHT):
                pg.draw.polygon(self.render.screen, color, polygon, 2)
                #Currently only used when displaying axes
                if self.label:
                    text = self.font.render(self.label[index], True, pg.Color('white'))
                    self.render.screen.blit(text, polygon[-1])

        if self.draw_vertices:
            for vertex in vertices:
                if all(0 <= vertex < [self.render.WIDTH, self.render.HEIGHT]):
                    pg.draw.circle(self.render.screen, pg.Color('white'), vertex.astype(int), 2)
    
    #Move object to coordinates
    def translate(self, pos):
        self.vertices = self.vertices @ translate(pos)

    def scale(self, scale_to):
        self.vertices = self.vertices @ scale(scale_to)

    def rotate_x(self, angle):
        self.vertices = self.vertices @ rotate_x(angle)

    def rotate_y(self, angle):
        self.vertices = self.vertices @ rotate_y(angle)

    def rotate_z(self, angle):
        self.vertices = self.vertices @ rotate_z(angle)

#Used to associate each face with a corresponding material
class Face:
    def __init__(self, vertices, material_name=None):
        self.vertices = vertices
        self.material_name = material_name

# Used to display axes
# class Axes(Object3D):
#     def __init__(self, render):
#         super().__init__(render)
#         self.vertices = np.array([(0, 0, 0, 1), (1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1)])
#         self.faces = [Face([0, 1]), Face([0, 2]), Face([0, 3])]
#         self.colors = [pg.Color('red'), pg.Color('green'), pg.Color('blue')]
#         self.color_faces = [(color, face) for color, face in zip(self.colors, self.faces)]
#         self.draw_vertices = False
#         self.label = 'XYZ'