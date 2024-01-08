import pygame as pg
from tkinter import Tk, filedialog
import sys
from object3d import *
from camera import *
from matrix_functionality import *
from round_button import *
import os
import aspose.threed as a3d

class Renderer:
    """
    3D Object Viewer Application using Pygame and Tkinter.

    This class initializes the application, manages the rendering loop, and handles user interactions.

    Attributes:
    - RES: Screen resolution tuple (WIDTH, HEIGHT).
    - H_WIDTH, H_HEIGHT: Half of the screen resolution. 
    - screen: Pygame screen surface.
    - clock: Pygame clock for controlling frame rate.
    - show_help: Boolean flag to control the display of help text.
    - rotateX_checkbox_rect, rotateY_checkbox_rect, rotateZ_checkbox_rect: Pygame Rectangles for checkboxes.
    - rotateX_checked, rotateY_checked, rotateZ_checked: Boolean flags for checkbox states.
    - openFile_button, resetObj_button, showHelp_button: Instances of RoundButton class.
    - font: Pygame font for text rendering.
    - script_dir: Script directory for locating resources
    - skybox_image: Background image.
    - camera: Instance of the Camera class for managing the viewpoint.
    - projection: Instance of the Projection class for handling projection.
    - object: Instance of the Object3D class representing the 3D object to be displayed.
    """
    def __init__(self):
        """
        Initialize the Renderer application.

        - Initializes Pygame and sets up screen properties.
        - Creates UI elements such as checkboxes, buttons, and initializes fonts.
        - Calls create_objects to set up the 3D objects in the scene.
        """
        pg.init()
        self.RES = self.WIDTH, self.HEIGHT = 900, 600
        self.H_WIDTH, self.H_HEIGHT = self.WIDTH // 2, self.HEIGHT // 2
        self.FPS = 60
        self.screen = pg.display.set_mode(self.RES)
        self.clock = pg.time.Clock()
        self.show_help, self.rotateX_checked, self.rotateY_checked, self.rotateZ_checked  = False, False, False, False
        
        #Buttons
        self.openFile_button = RoundButton(self.screen, (25, 10, 150, 35),(0, 128, 255),"Select File")
        self.resetObj_button = RoundButton(self.screen, (25, 140, 150, 35),(0, 128, 255),"Reset object")
        self.showHelp_button = RoundButton(self.screen, (25, 180, 150, 35),(0, 128, 255),"Help")
        self.rotateX_checkbox = RoundButton(self.screen, (130, 50, 25, 25), (220, 220, 220), '', 0)
        self.rotateY_checkbox = RoundButton(self.screen, (130, 80, 25, 25), (220, 220, 220), '', 0)
        self.rotateZ_checkbox = RoundButton(self.screen, (130, 110, 25, 25), (220, 220, 220), '', 0)

        # Buttons dictionary for dynamic handling
        self.buttons = [self.rotateX_checkbox, self.rotateY_checkbox, self.rotateZ_checkbox,
                        self.resetObj_button, self.openFile_button, self.showHelp_button
        ]

        self.font = pg.font.Font(None, 30)
        self.script_dir = os.path.dirname(__file__)
        skybox_path = os.path.join(self.script_dir, "skybox.jpg")
        self.skybox_image = pg.image.load(skybox_path)
        self.skybox_image = pg.transform.scale(self.skybox_image, (900, 600))
        self.create_objects()

    def handle_button_click(self, button):
        """
        Handle button clicks.

        Parameters:
        - button: The button object clicked.

        Actions:
        - Reset the object if the reset button is clicked.
        - Open a new file if the open file button is clicked.
        - Toggle the help display if the show help button is clicked.
        - Toggle the corresponding boolean attribute for checkboxes (rotateX, rotateY, rotateZ).
        """
        if button == self.resetObj_button:
            self.object.reset()
        elif button == self.openFile_button:
            self.open_new_file()
        elif button == self.showHelp_button:
            self.show_help = not self.show_help
        elif button == self.rotateX_checkbox:
            self.rotateX_checked = not self.rotateX_checked
        elif button == self.rotateY_checkbox:
            self.rotateY_checked = not self.rotateY_checked
        elif button == self.rotateZ_checkbox:
            self.rotateZ_checked = not self.rotateZ_checked

    def create_objects(self):
        """
        Initialize the 3D objects in the scene.

        - Creates instances of Camera, Projection, and loads a 3D object from the file.
        - Applies initial transformations to the loaded object.
        """
        self.camera = Camera(self, [-1, 6, -30])
        self.projection = Projection(self)
        obj_path = os.path.join(self.script_dir, 'res/Tree.obj')
        self.object = self.get_object_from_file(obj_path)
        self.object.translate([0, 0, 0])
 
    def get_object_from_file(self, filename):
        """
        Load a 3D object from a file. Reads the .obj (and .mtl, if exists) file.

        Args:
        - filename (str): Path to the .obj file.

        Returns:
        - Object3D: Instance of the Object3D class representing the loaded 3D object.
        """
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
    
    def open_new_file(self):
        """
        Open a file dialog to load a new 3D object.

        - Supports .obj, .fbx, and .3ds file formats.
        - Converts .fbx and .3ds files to .obj format using Aspose if needed.
        """
        file_types = [
            ("OBJ Files", "*.obj"),
            ("FBX Files", "*.fbx"),
            ("3DS Files", "*.3ds"),
            ("All Files", "*.*")
        ]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        if file_path and file_path.endswith(".obj"):
            self.object = self.get_object_from_file(file_path)
        #If it's a .fbx or .3ds file, it should first be converted to .obj
        elif file_path and (file_path.endswith(".fbx") or file_path.endswith(".3ds")):
            scene = a3d.Scene.from_file(file_path)
            root, _ = os.path.splitext(file_path)
            obj_filename = root + ".obj"
            scene.save(obj_filename)
            self.object = self.get_object_from_file(obj_filename)
            if(file_path.endswith(".fbx")):
                #.fbx objects get scaled up a lot after conversion, so we need to account for that and scale them down
                self.object.scale(0.02)
                self.object.vertices_untouched = self.object.vertices
            else:
                self.camera.reset_cam_position()

    def draw_text(self, text, color, position):
        """
        Draw text on the screen.

        Args:
        - text (str): Text to be rendered.
        - color (tuple): RGB color tuple.
        - position (tuple): (x, y) position of the text on the screen.
        """
        surface = self.font.render(text, True, color)
        self.screen.blit(surface, position)

    def draw(self):
        """
        Draw the 3D scene and the loaded object on the screen.
        """
        self.screen.blit(self.skybox_image, (0, 0))
        self.object.draw(self.rotateX_checked, self.rotateY_checked, self.rotateZ_checked)

    def draw_checkboxes(self):
        """
        Draw the checkboxes and a checkmark if a checkbox is checked
        """
        self.rotateX_checkbox.draw()
        self.rotateY_checkbox.draw()
        self.rotateZ_checkbox.draw()

        for checkbox, checked in zip([self.rotateX_checkbox, self.rotateY_checkbox, self.rotateZ_checkbox], 
                                     [self.rotateX_checked, self.rotateY_checked, self.rotateZ_checked]):
            pg.draw.rect(self.screen, 'black', checkbox.rect, 2)
            if checked:
                pg.draw.line(self.screen, 'black', (checkbox.rect.left + 5, checkbox.rect.centery),
                             (checkbox.rect.centerx - 5, checkbox.rect.bottom - 5), 2)
                pg.draw.line(self.screen, 'black', (checkbox.rect.centerx - 5, checkbox.rect.bottom - 5),
                             (checkbox.rect.right - 5, checkbox.rect.top + 5), 2)

    def run(self):
        """
        Main rendering loop for the application.

        - Continuously renders the scene and handles user input.
        - Manages the display of checkboxes, buttons, and help text.
        """
        while True:
            self.draw()
            self.camera.control() #enabling camera controls
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    for i, button in enumerate(self.buttons):
                        if button.rect.collidepoint(event.pos):
                            self.handle_button_click(button)
                elif event.type == pg.MOUSEMOTION:
                    for i, button in enumerate(self.buttons):
                        button.is_hovered = button.rect.collidepoint(event.pos)

            # Drawing the checkboxes
            self.rotateX_checkbox.draw()
            self.rotateY_checkbox.draw()
            self.rotateZ_checkbox.draw() 
            pg.draw.rect(self.screen, 'black', self.rotateX_checkbox.rect, 2)
            pg.draw.rect(self.screen, 'black', self.rotateY_checkbox.rect, 2)
            pg.draw.rect(self.screen, 'black', self.rotateZ_checkbox.rect, 2)

            self.draw_text("Rotate (x) ", (255, 255, 255), (self.openFile_button.rect.x + 5, self.openFile_button.rect.y + 40))
            self.draw_text("Rotate (y) ", (255, 255, 255), (self.openFile_button.rect.x + 5, self.openFile_button.rect.y + 70))
            self.draw_text("Rotate (z)", (255, 255, 255), (self.openFile_button.rect.x + 5, self.openFile_button.rect.y + 100))
            
            self.draw_checkboxes()
            #Drawing the help text if Help button is pressed
            if self.show_help:
                lines = ["Controls:", "W - move forward", "A - move left", "S - move backward", 
                         "D - move right", "Q - move up", "E - move down", "R - reset camera",
                         "Arrow keys rotate the camera accordingly", "Hide this text by pressing the Help button",
                         "If .fbx object is too small, open the created .obj"]
                sk = 20
                for line in lines:
                    sk+=20
                    self.draw_text(line, (255, 255, 255), (self.showHelp_button.rect.x, self.showHelp_button.rect.y+sk))

            self.openFile_button.draw()
            self.resetObj_button.draw()
            self.showHelp_button.draw()

            #Drawing informational text
            self.draw_text("Discovered material count: " + str(self.object.materials_count), 
                           (255, 255, 255), 
                           (self.openFile_button.rect.x + 560, self.openFile_button.rect.y + 5))
            self.draw_text("Polygon count: " + str(self.object.polygon_count), 
                           (255, 255, 255), 
                           (self.openFile_button.rect.x + 630, self.openFile_button.rect.y + 35))
            self.draw_text("FPS: " + str(round(self.clock.get_fps())), 
                           (255, 255, 255), 
                           (self.openFile_button.rect.x + 780, self.openFile_button.rect.y + 560))
            
            pg.display.set_caption("3d Object Viewer")
            pg.display.flip()
            self.clock.tick(self.FPS)

if __name__ == '__main__':
    app = Renderer()
    app.run()
