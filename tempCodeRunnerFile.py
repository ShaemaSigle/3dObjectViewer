def is_camera_inside_object(self):
        is_inside = self.object.hull.equations[:, :-1] @ self.camera.position + self.object.hull.equations[:, -1] <= 0
        return np.all(is_inside)

    def run(self):
        while True:
            self.draw()
            self.camera.control()
            # Check if the camera position is inside the convex hull
            print(is_camera_inside_object(self.camera.position))  # Should return True