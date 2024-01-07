import math
import numpy as np

class Projection:
    """
    Handles the projection of 3D coordinates to screen space.

    This class calculates the projection matrix and the transformation matrix to convert
    world-space coordinates to screen-space coordinates.

    Attributes:
    - projection_matrix: 4x4 numpy array representing the projection matrix.
    - to_screen_matrix: 4x4 numpy array representing the transformation matrix to screen resolution.

    Methods:
    - __init__(self, render): Initializes the Projection object with the given Renderer object.

    Note:
    - The projection_matrix is used for the perspective projection of 3D coordinates.
    - The to_screen_matrix is used to transform vertices to screen resolution.
    """
    def __init__(self, render):
        NEAR = render.camera.near_plane
        FAR = render.camera.far_plane
        RIGHT = math.tan(render.camera.h_fov / 2)
        LEFT = -RIGHT
        TOP = math.tan(render.camera.v_fov / 2)
        BOTTOM = -TOP

        m00 = 2 / (RIGHT - LEFT)
        m11 = 2 / (TOP - BOTTOM)
        m22 = (FAR + NEAR) / (FAR - NEAR)
        m32 = -2 * NEAR * FAR / (FAR - NEAR)
        self.projection_matrix = np.array([
            [m00, 0, 0, 0],
            [0, m11, 0, 0],
            [0, 0, m22, 1],
            [0, 0, m32, 0]
        ])

        HW, HH = render.H_WIDTH, render.H_HEIGHT
        self.to_screen_matrix = np.array([
            [HW, 0, 0, 0],
            [0, -HH, 0, 0],
            [0, 0, 1, 0],
            [HW, HH, 0, 1]
        ])

def translate(pos):
    print(type(pos))
    """
    Generate a 4x4 translation matrix for a given position.

    Args:
    - pos (list): The translation vector (tx, ty, tz).

    Returns:
    - np.array: 4x4 translation matrix.
    """
    tx, ty, tz = pos
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [tx, ty, tz, 1]
    ])

def rotate(a, axis):
    """
    Generate a 4x4 rotation matrix for rotation around the chosen axis.
    
    Args:
    - a (float): The rotation angle in radians.
    - axis(str): The rotation axis ('x', 'y', or 'z').

    Returns:
    - np.array: 4x4 rotation matrix.
    """
    if axis == "x":
        return np.array([
            [1, 0, 0, 0],
            [0, math.cos(a), math.sin(a), 0],
            [0, -math.sin(a), math.cos(a), 0],
            [0, 0, 0, 1]
        ])
    elif axis == "y":
        return np.array([
            [math.cos(a), 0, -math.sin(a), 0],
            [0, 1, 0, 0],
            [math.sin(a), 0, math.cos(a), 0],
            [0, 0, 0, 1]
        ])
    elif axis == "z":
        return np.array([
            [math.cos(a), math.sin(a), 0, 0],
            [-math.sin(a), math.cos(a), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

def scale(n):
    """
    Generate a 4x4 scaling matrix for a uniform scaling factor.

    Args:
    - n (float): The scaling factor.

    Returns:
    - np.array: 4x4 scaling matrix.
    """
    return np.array([
        [n, 0, 0, 0],
        [0, n, 0, 0],
        [0, 0, n, 0],
        [0, 0, 0, 1]
    ])