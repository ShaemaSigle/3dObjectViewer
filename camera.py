import pygame as pg
from matrix_functionality import *

class Camera:
    def __init__(self, render, position):
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

    #Moving the camera around using keyboard
    def control(self):
        key = pg.key.get_pressed()
        #Resetting the camera in case user gets lost
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

    # Initialize camera axes to the identity orientation
    def axiiIdentity(self):
        # Creates 3 vectors in 4D homogeneous coordinates
        self.forward = np.array([0, 0, 1, 1])
        self.up = np.array([0, 1, 0, 1])
        self.right = np.array([1, 0, 0, 1])

    def camera_update_axii(self): 
        # Update camera axes based on pitch and yaw angles
        rotate = rotate_x(self.anglePitch) @ rotate_y(self.angleYaw)  # this gives right visual
        # Rotate the forward, up, and right vectors
        self.axiiIdentity()
        self.forward = self.forward @ rotate
        self.right = self.right @ rotate
        self.up = self.up @ rotate

    # Compute the combined camera transformation matrix
    def camera_matrix(self):
        self.camera_update_axii()
        return self.translate_matrix() @ self.rotate_matrix()

    # Create a translation matrix based on the camera position
    def translate_matrix(self):
        x, y, z, w = self.position
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [-x, -y, -z, 1]
        ])
    
    # Create a rotation matrix based on the camera orientation
    def rotate_matrix(self):
        rx, ry, rz, w = self.right
        fx, fy, fz, w = self.forward
        ux, uy, uz, w = self.up
        return np.array([
            [rx, ux, fx, 0],
            [ry, uy, fy, 0],
            [rz, uz, fz, 0],
            [0, 0, 0, 1]
        ])