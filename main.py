from tessellation import Tessellation
from tessellation_fill import *
from button import Button
import numpy as np
import pygame



def main():
    
    # Simple settings to establish
    polygon_side_length = 12 # How large is the polygon
    maximum_vertices_filled = 2500 # How large is the entire tessellation
    randomly_fill_vertices = True # Should each choice of polygon be made by a person (False) or filled randomly (True)
    
    
        
    # Set up the Pygame window
    pygame.init()

    # Size of display window
    xmax = 1000
    ymax = 800

    center = np.array([xmax//2,ymax//2]) # Tessellation will be centered in the middle of the display screen
    win = pygame.display.set_mode((xmax,ymax))
    win.fill((255,255,255)) # White Background

    # Setup button properties for adding triangles and squares
    # Buttons located at at bottom middle of screen with slight offset. (Pixel location of top left corner)
    # If the vertices will be randomly filled, we do not need to initialize or redraw these buttons
    button_list = []
    if not randomly_fill_vertices:
        button_size = np.array([100,50])

        tri_but_loc = np.array([xmax//2,ymax]) - button_size - np.array([2,0])
        tri_but = Button(tri_but_loc, button_size, (200,200,200), 'Triangle')

        sq_but_loc = np.array([xmax//2,ymax]) - np.array([0,1])*button_size + np.array([2,0])
        sq_but = Button(sq_but_loc, button_size, (200,200,200), 'Square')
        
        button_list = [tri_but, sq_but]

    # Initialize the tessellation
    tess = Tessellation(win, center, polygon_side_length)
    
    # Continue to fill and display until quiting
    run = True
    while run and fill_tess(tess, maximum_vertices_filled, win, button_list, randomly_fill_vertices):
        for event in pygame.event.get():       
            if event.type == pygame.QUIT:
                run = False
    
    pygame.quit()
    

    

if __name__ == "__main__":
    main()