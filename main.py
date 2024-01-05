import pygame as pg
from tkinter import Tk, filedialog
import sys
from object_3d import *
from camera import *
from projection import *
import os

class SoftwareRender:
    def __init__(self):
        pg.init()
        self.RES = self.WIDTH, self.HEIGHT = 800, 500
        self.H_WIDTH, self.H_HEIGHT = self.WIDTH // 2, self.HEIGHT // 2
        self.FPS = 60
        self.screen = pg.display.set_mode(self.RES)
        self.clock = pg.time.Clock()
        self.fill_checkbox_rect = pg.Rect(50, 50, 30, 30)
        self.fill_checked = False
        self.font = pg.font.Font(None, 36)
        self.skybox_image = pg.image.load("skybox.jpg")  # Replace with your skybox image path
        self.skybox_image = pg.transform.scale(self.skybox_image, (800, 500))
        self.create_objects()
        
    def create_objects(self):
        self.camera = Camera(self, [-5, 6, -30])
        self.projection = Projection(self)
        self.object = self.get_object_from_file('C:/Users/User/Desktop/python-3sem/res/Tree.obj')
        self.object.rotate_y(-math.pi / 4)
        self.object.translate([-5, 6, -30])

# Reading the .obj file
    def get_object_from_file(self, filename):
        vertices, faces_inst, materials = [], [], {}
        root, _ = os.path.splitext(filename)
        mtl_filename = root + ".mtl"
        current_material = None

        with open(mtl_filename) as mtl_file:
            for line in mtl_file:
                if line.startswith('newmtl'):
                    current_material = line.split()[1]
                    materials[current_material] = pg.Color('red')  # Default color, change if needed
                elif line.startswith('Kd'):
                    rgb_values = [float(value) * 255 for value in line.split()[1:]]
                    print(rgb_values)
                    materials[current_material] = rgb_values

        with open(filename) as f:
            for line in f:
                if line.startswith('v '):
                    vertices.append([float(i) for i in line.split()[1:]] + [1])
                elif line.startswith('usemtl'):
                    current_material_name = line.split()[1]
                elif line.startswith('f'):
                    faces_ = line.split()[1:]
                    faces_inst.append(Face([int(face_.split('/')[0]) - 1 for face_ in faces_], current_material_name))
                    # faces.append([int(face_.split('/')[0]) - 1 for face_ in faces_])
        return Object3D(self, vertices, faces_inst, materials)

    def show_file_dialog(self):
        root = Tk()
        root.withdraw()  # Hide the main window
        file_path = filedialog.askopenfilename()
        root.destroy()  # Close the hidden window
        if file_path and file_path.endswith(".obj"):
            self.object = self.get_object_from_file(file_path)

    def draw_text(self, text, color, position):
        surface = self.font.render(text, True, color)
        self.screen.blit(surface, position)

    @property
    def button_rect(self):
        return pg.Rect(25, 10, 150, 35)

    def draw(self):
        self.screen.blit(self.skybox_image, (0, 0))
        self.object.draw(self.fill_checked)

    def run(self):
        while True:
            self.draw()
            self.camera.control()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if self.fill_checkbox_rect.collidepoint(event.pos):
                        self.fill_checked = not self.fill_checked
                    elif self.button_rect.collidepoint(event.pos):
                        self.show_file_dialog()
            # Draw the checkbox
            pg.draw.rect(self.screen, 'gray', self.fill_checkbox_rect, 0)
            pg.draw.rect(self.screen, 'black', self.fill_checkbox_rect, 2)

            # Draw button
            pg.draw.rect(self.screen, (0, 128, 255), self.button_rect)
            self.draw_text("Select File", (255, 255, 255), (self.button_rect.x + 8, self.button_rect.y + 8))

            # Draw the checkmark if the checkbox is checked
            if self.fill_checked:
                pg.draw.line(self.screen, 'black', (self.fill_checkbox_rect.left + 5, self.fill_checkbox_rect.centery),
                                (self.fill_checkbox_rect.centerx - 5, self.fill_checkbox_rect.bottom - 5), 2)
                pg.draw.line(self.screen, 'black', (self.fill_checkbox_rect.centerx - 5, self.fill_checkbox_rect.bottom - 5),
                                (self.fill_checkbox_rect.right - 5, self.fill_checkbox_rect.top + 5), 2)
            pg.display.set_caption(str(self.clock.get_fps()))
            pg.display.flip()
            self.clock.tick(self.FPS)
        
if __name__ == '__main__':
    app = SoftwareRender()
    app.run()
