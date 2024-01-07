import pygame as pg
from matrix_functionality import *

class Camera:
    def __init__(self, render, position):
        """
        Initialize the Camera object.

        Parameters:
        - render: Renderer object.
        - position: Initial position of the camera as a 3D vector (list or tuple).
        """
        self.render = render
        self.position = np.array([*position, 1.0])
        self.forward = np.array([0, 0, 1, 1])
        self.up = np.array([0, 1, 0, 1])
        self.right = np.array([1, 0, 0, 1])
        self.h_fov = math.pi / 3
        self.v_fov = self.h_fov * (render.HEIGHT / render.WIDTH)
        self.near_plane = 0.1
        self.far_plane = 100
        self.moving_speed = 0.3
        self.rotation_speed = 0.015

        self.anglePitch = 0
        self.angleYaw = 0
        self.angleRoll = 0

    def control(self):
        """
        Control the camera movement and orientation based on keyboard input.

        Key Controls:
        - 'W': Move forward
        - 'A': Move left
        - 'S': Move backward
        - 'D': Move right
        - 'Q': Move up
        - 'E': Move down
        - 'R': Reset camera position and orientation
        - Arrow keys: Rotate the camera

        The movement and rotation speed are controlled by the 'moving_speed' and 'rotation_speed' attributes.
        """
        key = pg.key.get_pressed()
        if key[pg.K_r]:
            self.position = np.array([*[-1, 6, -30], 1.0])
            self.anglePitch = 0
            self.angleYaw = 0
            self.angleRoll = 0
        if key[pg.K_a]:
            self.position -= self.right * self.moving_speed
        if key[pg.K_d]:
            self.position += self.right * self.moving_speed
        if key[pg.K_w]:
            self.position += self.forward * self.moving_speed
        if key[pg.K_s]:
            self.position -= self.forward * self.moving_speed
        if key[pg.K_q]:
            self.position += self.up * self.moving_speed
        if key[pg.K_e]:
            self.position -= self.up * self.moving_speed
        if key[pg.K_LEFT]:
            self.angleYaw -= self.rotation_speed
        if key[pg.K_RIGHT]:
            self.angleYaw += self.rotation_speed
        if key[pg.K_UP]:
            self.anglePitch -= self.rotation_speed
        if key[pg.K_DOWN]:
            self.anglePitch += self.rotation_speed

    def axiiIdentity(self):
        """
        Initialize camera axes to the identity orientation.

        Creates three 4D homogeneous vectors representing the forward, up, and right axes.
        """
        self.forward = np.array([0, 0, 1, 1])
        self.up = np.array([0, 1, 0, 1])
        self.right = np.array([1, 0, 0, 1])

    def camera_update_axii(self): 
        """
        Update camera axes based on pitch and yaw angles.

        Rotates the forward, up, and right vectors based on the current pitch and yaw angles.
        """
        rotating = rotate(self.anglePitch, "x") @ rotate(self.angleYaw, "y") 
        self.axiiIdentity()
        self.forward = self.forward @ rotating
        self.right = self.right @ rotating
        self.up = self.up @ rotating

    def camera_matrix(self):
        """
        Compute the combined camera transformation matrix.

        Returns:
        - numpy.ndarray: The combined camera transformation matrix.
        """
        self.camera_update_axii()
        return self.translate_matrix() @ self.rotate_matrix()

    def translate_matrix(self):
        """
        Create a translation matrix based on the camera position.

        Returns:
        - numpy.ndarray: Translation matrix based on the camera position.
        """
        x, y, z, w = self.position
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [-x, -y, -z, 1]
        ])
    
    def rotate_matrix(self):
        """
        Create a rotation matrix based on the camera orientation.

        Returns:
        - numpy.ndarray: Rotation matrix based on the camera orientation.
        """
        rx, ry, rz, w = self.right
        fx, fy, fz, w = self.forward
        ux, uy, uz, w = self.up
        return np.array([
            [rx, ux, fx, 0],
            [ry, uy, fy, 0],
            [rz, uz, fz, 0],
            [0, 0, 0, 1]
        ])