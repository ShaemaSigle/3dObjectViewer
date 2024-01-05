import pygame as pg
from matrix_functions import *
from numba import njit
from projection import *


@njit(fastmath=True)
def any_func(arr, a, b):
    return np.any((arr == a) | (arr == b))

class Object3D:
    def __init__(self, render, vertices='', faces='', materials=None):
        self.render = render
        self.vertices = np.array(vertices)
        self.faces = faces
        self.translate([0.0001, 0.0001, 0.0001])

        self.font = pg.font.SysFont('Arial', 30, bold=True)
        # self.color_faces = [(pg.Color('red'), face) for face in self.faces]
        self.color_faces = [(pg.Color(materials[face.material_name]), face) for face in self.faces]
        self.movement_flag, self.draw_vertices = False, False
        self.label = ''
    
    def draw(self, fill_faces):
        self.screen_projection(fill_faces)
        self.movement()

    def movement(self):
        if self.movement_flag:
            self.rotate_y(-(pg.time.get_ticks() % 0.005))

    def screen_projection(self, filling_faces):
        vertices = self.vertices @ self.render.camera.camera_matrix()
        vertices = vertices @ self.render.projection.projection_matrix
        # Normalizing vertices
        vertices /= vertices[:, -1].reshape(-1, 1)
        vertices[(vertices > 2) | (vertices < -2)] = 0
        vertices = vertices @ self.render.projection.to_screen_matrix
        vertices = vertices[:, :2]

        for index, color_face in enumerate(self.color_faces):
            color, face = color_face
            polygon = vertices[face.vertices]
            # if not np.any((polygon == self.render.H_WIDTH) | (polygon == self.render.H_HEIGHT)):
            if not any_func(polygon, self.render.H_WIDTH, self.render.H_HEIGHT):
                if not filling_faces: pg.draw.polygon(self.render.screen, color, polygon, 2)
                else: pg.draw.polygon(self.render.screen, color, polygon)
                if self.label:
                    text = self.font.render(self.label[index], True, pg.Color('white'))
                    self.render.screen.blit(text, polygon[-1])
            # break

        if self.draw_vertices:
            for vertex in vertices:
                # if not np.any((vertex == self.render.H_WIDTH) | (vertex == self.render.H_HEIGHT)):
                if not any_func(vertex, self.render.H_WIDTH, self.render.H_HEIGHT):
                    pg.draw.circle(self.render.screen, pg.Color('white'), vertex, 2)

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

class Face:
    def __init__(self, vertices, material_name):
        self.vertices = vertices
        self.material_name = material_name

# Used to display axes
class Axes(Object3D):
    def __init__(self, render):
        super().__init__(render)
        self.vertices = np.array([(0, 0, 0, 1), (1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1)])
        self.faces = np.array([(0, 1), (0, 2), (0, 3)])
        self.colors = [pg.Color('red'), pg.Color('green'), pg.Color('blue')]
        self.color_faces = [(color, face) for color, face in zip(self.colors, self.faces)]
        self.draw_vertices = False
        self.label = 'XYZ'