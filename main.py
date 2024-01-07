import pygame as pg
import tkinter as tk
from tkinter import Tk, filedialog, Button
import sys
from object_3d import *
from camera import *
from projection import *
import os
from threading import Thread

class SoftwareRender:
    def __init__(self):
        pg.init()
        self.RES = self.WIDTH, self.HEIGHT = 900, 600
        self.H_WIDTH, self.H_HEIGHT = self.WIDTH // 2, self.HEIGHT // 2
        self.FPS = 120
        self.screen = pg.display.set_mode(self.RES)
        self.clock = pg.time.Clock()
        self.show_help = False

        #Checkboxes
        self.rotateX_checkbox_rect = pg.Rect(130, 50, 25, 25)
        self.rotateX_checked = False
        self.rotateY_checkbox_rect = pg.Rect(130, 80, 25, 25)
        self.rotateY_checked = False
        self.rotateZ_checkbox_rect = pg.Rect(130, 110, 25, 25)
        self.rotateZ_checked = False
        
        #Buttons
        self.openFile_buttonRect = pg.Rect(25, 10, 150, 35)
        self.resetObj_buttonRect = pg.Rect(25, 140, 150, 35)
        self.showHelp_buttonRect = pg.Rect(25, 200, 150, 35)

        self.font = pg.font.Font(None, 30)
        self.skybox_image = pg.image.load("skybox.jpg")  # Replace with your skybox image path
        self.skybox_image = pg.transform.scale(self.skybox_image, (900, 600))
        self.create_objects()
        
    def create_objects(self):
        self.camera = Camera(self, [-1, 6, -30])
        self.projection = Projection(self)
        self.object = self.get_object_from_file('res/Tree.obj')
        self.object.rotate_y(-math.pi / 4)
        self.object.translate([0, 0, 0])

    # Reading the .obj (and .mtl, if exists) file
    # Code only takes rgb values from the .mtl file, if there is no Kd line in the material, it will default to black
    def get_object_from_file(self, filename):
        vertices, faces_inst, materials = [], [], {}
        root, _ = os.path.splitext(filename)
        mtl_filename = root + ".mtl"
        current_material = None
        if os.path.exists(mtl_filename):
            with open(mtl_filename) as mtl_file:
                for line in mtl_file:
                    if line.startswith('newmtl'):
                        current_material = line.split()[1]
                        materials[current_material] = pg.Color('black')  # Default color, used if the material has no Kd line
                    elif line.startswith('Kd'):
                        rgb_values = [float(value) * 255 for value in line.split()[1:]]
                        print(current_material, rgb_values)
                        materials[current_material] = rgb_values
        else: 
            #In case there is no .mtl file, a default material is used since it is needed to create a Face instance
            current_material_name = "default"
            materials["default"] = [0,0,0]
        with open(filename) as f:
            for line in f:
                if line.startswith('v '):
                    vertices.append([float(i) for i in line.split()[1:]] + [1])
                elif line.startswith('usemtl') and os.path.exists(mtl_filename):
                    current_material_name = line.split()[1]
                elif line.startswith('f'):
                    faces_ = line.split()[1:]
                    faces_inst.append(Face([int(face_.split('/')[0]) - 1 for face_ in faces_], current_material_name))
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

    def draw(self):
        self.screen.blit(self.skybox_image, (0, 0))
        self.object.draw(self.rotateX_checked, self.rotateY_checked, self.rotateZ_checked)

    def run(self):
        while True:
            self.draw()
            self.camera.control()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                #All clickable things are handled here
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if self.rotateX_checkbox_rect.collidepoint(event.pos):
                        self.rotateX_checked = not self.rotateX_checked
                    elif self.rotateY_checkbox_rect.collidepoint(event.pos):
                        self.rotateY_checked = not self.rotateY_checked
                    elif self.rotateZ_checkbox_rect.collidepoint(event.pos):
                        self.rotateZ_checked = not self.rotateZ_checked
                    elif self.resetObj_buttonRect.collidepoint(event.pos):
                        self.object.reset()
                    elif self.openFile_buttonRect.collidepoint(event.pos):
                        self.show_file_dialog()
                    elif self.showHelp_buttonRect.collidepoint(event.pos):
                        if self.show_help:
                            self.show_help = False
                        else: 
                            self.show_help = True

            # Draw the checkboxes
            pg.draw.rect(self.screen, 'gray', self.rotateX_checkbox_rect, 0)
            pg.draw.rect(self.screen, 'black', self.rotateX_checkbox_rect, 2)
            pg.draw.rect(self.screen, 'gray', self.rotateY_checkbox_rect, 0)
            pg.draw.rect(self.screen, 'black', self.rotateY_checkbox_rect, 2)
            pg.draw.rect(self.screen, 'gray', self.rotateZ_checkbox_rect, 0)
            pg.draw.rect(self.screen, 'black', self.rotateZ_checkbox_rect, 2)
            self.draw_text("Rotate (x) ", (255, 255, 255), (self.openFile_buttonRect.x + 5, self.openFile_buttonRect.y + 40))
            self.draw_text("Rotate (y) ", (255, 255, 255), (self.openFile_buttonRect.x + 5, self.openFile_buttonRect.y + 70))
            self.draw_text("Rotate (z)", (255, 255, 255), (self.openFile_buttonRect.x + 5, self.openFile_buttonRect.y + 100))
            
            # Draw the checkmark if the checkbox is checked
            if self.rotateX_checked:
                pg.draw.line(self.screen, 'black', (self.rotateX_checkbox_rect.left + 5, self.rotateX_checkbox_rect.centery),
                                (self.rotateX_checkbox_rect.centerx - 5, self.rotateX_checkbox_rect.bottom - 5), 2)
                pg.draw.line(self.screen, 'black', (self.rotateX_checkbox_rect.centerx - 5, self.rotateX_checkbox_rect.bottom - 5),
                                (self.rotateX_checkbox_rect.right - 5, self.rotateX_checkbox_rect.top + 5), 2)
            if self.rotateY_checked:
                pg.draw.line(self.screen, 'black', (self.rotateY_checkbox_rect.left + 5, self.rotateY_checkbox_rect.centery),
                                (self.rotateY_checkbox_rect.centerx - 5, self.rotateY_checkbox_rect.bottom - 5), 2)
                pg.draw.line(self.screen, 'black', (self.rotateY_checkbox_rect.centerx - 5, self.rotateY_checkbox_rect.bottom - 5),
                                (self.rotateY_checkbox_rect.right - 5, self.rotateY_checkbox_rect.top + 5), 2)
            if self.rotateZ_checked:
                pg.draw.line(self.screen, 'black', (self.rotateZ_checkbox_rect.left + 5, self.rotateZ_checkbox_rect.centery),
                                (self.rotateZ_checkbox_rect.centerx - 5, self.rotateZ_checkbox_rect.bottom - 5), 2)
                pg.draw.line(self.screen, 'black', (self.rotateZ_checkbox_rect.centerx - 5, self.rotateZ_checkbox_rect.bottom - 5),
                                (self.rotateZ_checkbox_rect.right - 5, self.rotateZ_checkbox_rect.top + 5), 2)
                
            #Draw the help text if Help button is pressed
            if self.show_help:
                lines = ["Controls:", "W - move forward", "A - move left", "S - move backward", 
                         "D - move right", "Q - move up", "E - move down", "R - reset camera",
                         "Arrow keys rotate the camera accordingly", "Hide this text by pressing the Help button"]
                sk = 20
                for line in lines:
                    sk+=20
                    self.draw_text(line, (255, 255, 255), (self.showHelp_buttonRect.x, self.showHelp_buttonRect.y+sk))

            # Draw buttons
            pg.draw.rect(self.screen, (0, 128, 255), self.openFile_buttonRect)
            self.draw_text("Select File", (255, 255, 255), (self.openFile_buttonRect.x + 8, self.openFile_buttonRect.y + 8))

            pg.draw.rect(self.screen, (0, 128, 255), self.resetObj_buttonRect)
            self.draw_text("Reset object", (255, 255, 255), (self.resetObj_buttonRect.x + 8, self.resetObj_buttonRect.y + 8))
            
            #Button to show the help popup
            pg.draw.rect(self.screen, (0, 128, 255), self.showHelp_buttonRect)
            self.draw_text("Help", (255, 255, 255), (self.showHelp_buttonRect.x + 5, self.showHelp_buttonRect.y + 5))

            #Draw labels
            self.draw_text("Discovered material count: " + str(self.object.materials_count), (255, 255, 255), (self.openFile_buttonRect.x + 560, self.openFile_buttonRect.y + 5))
            self.draw_text("Polygon count: " + str(self.object.polygon_count), (255, 255, 255), (self.openFile_buttonRect.x + 630, self.openFile_buttonRect.y + 35))
            self.draw_text("FPS: " + str(round(self.clock.get_fps())), (255, 255, 255), (self.openFile_buttonRect.x + 780, self.openFile_buttonRect.y + 560))
            
            pg.display.set_caption("3d Object Viewer")
            pg.display.flip()
            self.clock.tick(self.FPS)

if __name__ == '__main__':
    app = SoftwareRender()
    app.run()