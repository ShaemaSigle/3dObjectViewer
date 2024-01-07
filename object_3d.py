import pygame as pg
from numba import njit
from matrix_functionality import *

@njit(fastmath=True)
#A Numba-optimized function to check if any element in the array equals 'a' or 'b'.
def any_func(arr, a, b):
    return np.any((arr == a) | (arr == b))

class Object3D:
    def __init__(self, render, vertices='', faces='', materials=None):
        """
        Initialize a 3D object.

        Args:
        - render: The Renderer instance.
        - vertices (list): List of vertices defining the object.
        - faces (list): List of faces defining the object.
        - materials (dict): Dictionary of materials associated with the object's faces.
        """
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
        """
        Draw the 3D object on the screen.

        Args:
        - rotateX (bool): Flag indicating whether to rotate around the X-axis.
        - rortateY (bool): Flag indicating whether to rotate around the Y-axis.
        - rotateZ (bool): Flag indicating whether to rotate around the Z-axis.
        """
        if(rotateX or rortateY or rotateZ): 
            self.movement_flag = True
            self.movement(rotateX, rortateY, rotateZ)
        else: self.movement_flag = False
        self.screen_projection()

    def movement(self, x, y, z):
        """
        Apply movement (currently only rotation) to the 3D object.

        Args:
        - x (bool): Flag indicating whether to rotate around the X-axis.
        - y (bool): Flag indicating whether to rotate around the Y-axis.
        - z (bool): Flag indicating whether to rotate around the Z-axis.
        """
        if self.movement_flag:
            if x: self.rotate(-(pg.time.get_ticks() % 0.005), "x")
            if y: self.rotate(-(pg.time.get_ticks() % 0.005), "y")
            if z: self.rotate(-(pg.time.get_ticks() % 0.005), "z")

    def reset(self):
        #Reset the object to its original state
        self.vertices = self.vertices_untouched
    
    def screen_projection(self):
        ##Project the object onto the screen and draw it.
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
    
    def translate(self, pos):
        """
        Translate the object to a specified position.

        Args:
        - pos (list): The translation vector (tx, ty, tz).
        """
        self.vertices = self.vertices @ translate(pos)

    def scale(self, scale_to):
        """
        Scale the object by a specified factor.

        Args:
        - scale_to (float): The scaling factor.
        """
        self.vertices = self.vertices @ scale(scale_to)

    def rotate(self, angle, axis):
        """
        Rotate the object around a specified axis.

        Args:
        - angle (float): The rotation angle in radians.
        - axis (str): The rotation axis ('x', 'y', or 'z').
        """
        if axis == "x":
            self.vertices = self.vertices @ rotate(angle, "x")
        elif axis == "y":
            self.vertices = self.vertices @ rotate(angle, "y")
        elif axis == "z":
            self.vertices = self.vertices @ rotate(angle, "z")

class Face:
    """
    Initialize a Face instance.

    Args:
    - vertices (list): List of vertex indices defining the face.
    - material_name (str): The name of the material associated with the face.
    """
    def __init__(self, vertices, material_name=None):
        self.vertices = vertices
        self.material_name = material_name

class Axes(Object3D):
    """
    Initialize an Axes instance. 
    Can be used to display both world and local object axes.

    Args:
    - render: The Renderer instance.
    """
    def __init__(self, render):
        super().__init__(render)
        self.vertices = np.array([(0, 0, 0, 1), (1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1)])
        self.faces = [Face([0, 1]), Face([0, 2]), Face([0, 3])]
        self.colors = [pg.Color('red'), pg.Color('green'), pg.Color('blue')]
        self.color_faces = [(color, face) for color, face in zip(self.colors, self.faces)]
        self.draw_vertices = False
        self.label = 'XYZ'