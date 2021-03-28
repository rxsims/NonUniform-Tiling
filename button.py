import pygame
import numpy as np

class Button:
    def __init__(self, coords, size, color, text=None):
        self.x = coords[0]
        self.y = coords[1]
        self.width = size[0]
        self.height = size[1]
        self.color = color
        self.text = text
    
    
    
    # Draw button and update display window
    # If the button has some text associated with it, center the text on the button
    def draw_button(self, win):
        button_rect = pygame.draw.rect(win, self.color,(self.x, self.y, self.width, self.height))
        
        if self.text != None:
            button_font = pygame.font.SysFont('arial',np.int(0.5*self.height))
            button_render = button_font.render(self.text, True, (0,0,0))
            cent_x, cent_y = button_rect.center
            button_text_location = (cent_x - button_render.get_width()/2, cent_y - button_render.get_height()/2)
            win.blit(button_render, button_text_location)
        
        pygame.display.update()
    
    
    
    
    # Check whether the mouse if over the button
    def mouse_on_button(self,mouse_pos):
        mouse_x = mouse_pos[0]
        mouse_y = mouse_pos[1]
        if mouse_x > self.x and mouse_x < self.x + self.width:
            if mouse_y > self.y and mouse_y < self.y + self.height:
                return True
        return False