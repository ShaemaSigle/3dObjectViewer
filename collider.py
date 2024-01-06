import numpy as np
import pygame as pg

class Collider:
    def __init__(self, object_vertices):
        # Calculate the approximate size of the object
        min_coords = np.min(object_vertices, axis=0)
        max_coords = np.max(object_vertices, axis=0)
        size = np.abs(max_coords - min_coords)

        # Use the size to create a bounding cylinder
        self.radius = np.max(size) / 2.0
        self.height = np.max(size)
        print("coll created: ", size)

    def is_point_inside_cylinder(self, point):
        # Check if the point is inside the bounding cylinder
        distance_to_axis = np.linalg.norm(point[:2])  # Consider only x and y coordinates
        return distance_to_axis <= self.radius and 0 <= point[2] <= self.height