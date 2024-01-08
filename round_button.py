import pygame as pg

class RoundButton:
    """
    A class representing a round button in a Pygame screen.

    Attributes:
    - screen: Pygame display surface to draw the button on.
    - rect: Pygame Rect object defining the position and size of the button.
    - text: Text to be displayed on the button.
    - radius: Radius of the rounded corners of the button.
    - hover_factor: Factor to darken the button color when hovered.
    - is_hovered: A boolean indicating whether the button is currently being hovered over.

    Methods:
    - draw: Draw the button on the screen.
    """
    def __init__(self, screen, rect, color, text='', radius=10, hover_factor=0.7):
        self.screen = screen
        self.rect = pg.Rect(rect)
        self.color = color
        self.text = text
        self.text_color = (255, 255, 255)
        self.radius = radius
        self.hover_factor = hover_factor
        self.is_hovered = False
    def draw(self):
        # Darken the color if hovered
        if self.is_hovered:
            hover_color = tuple(int(component * self.hover_factor) for component in self.color)
            pg.draw.rect(self.screen, hover_color, self.rect, border_radius=self.radius)
        else:
            pg.draw.rect(self.screen, self.color, self.rect, border_radius=self.radius)
        if self.text != '':
            # Draw text
            font = pg.font.Font(None, 36)
            text_surface = font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            self.screen.blit(text_surface, text_rect)