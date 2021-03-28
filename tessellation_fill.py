from tessellation import Tessellation
from button import Button
import numpy as np
import pygame


def fill_tess(tessellation, max_fill, window, button_list, random_fill):
    # Loop until the tessellation fills to the maximum
    while tessellation.vert_filled < max_fill:
        
        # Display how many vertices are currently filled as the window title
        pygame.display.set_caption(
            'Tessellation ------ Vertices Filled: {} out of {}'.format(tessellation.vert_filled, max_fill)
        )
        
        # Redraw the buttons for each frame, in case the tessellation is drawn over the buttons
        for buts in button_list:
            buts.draw_button(window)
            
        # At start of loop, check if the current vertex is filled.
        # This is an important step since previous auto-fills may have filled the current vertex already
        tessellation.current_vertex.check_filled()
        
        # On a not-filled vertex, continue to loop until the vertex becomes filled
        while not tessellation.current_vertex.is_filled:
            add_poly = -1 # Make sure polygons do not accidentally get added multiple times
            
            for event in pygame.event.get():
                # End all loops and exit
                if event.type == pygame.QUIT:
                    return False

                # Check if one of the polygon buttons is clicked only if random fill option off
                if (not random_fill and event.type == pygame.MOUSEBUTTONDOWN):
                    mouse_pos = pygame.mouse.get_pos()
                    if (button_list[0]).mouse_on_button(mouse_pos):
                        add_poly = 0 # Triangle
                    if (button_list[1]).mouse_on_button(mouse_pos):
                        add_poly = 1 # Square
                        
            if random_fill: # Mark a polygon at random to be filled, with random fill option on
                add_poly = np.random.randint(2)
                
            # Add the polygon (whether random fill or not), and update reference vertex for next polygon
            if add_poly != -1:
                tessellation.add_poly_to_tess(add_poly, tessellation.current_vertex, tessellation.reference_vertex)
                tessellation.update_vertex_reference()
    
            # Auto-fill all adjacent points, as well as two spaces ahead, to avoid possible 135 degree angles.
            # This has the extra benefit of auto-filling the current vertex as well.
            tessellation.autofill_adjacent_recursive(tessellation.current_vertex)
        
        # Vertices should always be auto-filled for at least the last polygon.
        # Whenever the auto-fill completes the vertex, need to move to next vertex to fill and update reference.
        tessellation.update_vertex_reference()
    
    # When tessellation has reached the maximum value, update title and wait for quit
    pygame.display.set_caption('Tessellation ------ Maximum Vertices Filled: {}'.format(tessellation.vert_filled))
    pygame.display.update()
    return True
    

    
if __name__ == "__main__":
    pygame.init()

    center = np.array([200,200])
    win = pygame.display.set_mode((400,400))
    win.fill((255,255,255))
    
    tess = Tessellation(win,center,10)
    fill_tess(tess, 100, win, [], True)