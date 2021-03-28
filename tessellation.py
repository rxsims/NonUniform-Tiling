from vertex import Vertex
from polygon import *
import numpy as np

class Tessellation:
    def __init__(self, win, center, length):
        # Setup first two vertices
        self.v0 = Vertex(np.array([0,0])) # First vertex to be filled
        self.v1 = Vertex(np.array([1,0])) # First reference vertex
        self.v0.set_neighbor(self.v1)
        self.v1.set_neighbor(self.v0)
        self.v0.store_ccw_index(self.v1)
        self.v1.store_ccw_index(self.v0)
        
        self.current_vertex = self.v0 # Current vertex that is being filled
        self.reference_vertex = self.v1 # Reference vertex to define polygons
        
        self.tri_color = (235,235,0)#(91, 132, 177) # RGB color for triangles
        self.sq_color =  (255,0,0)#(252, 118, 106) # RGB color for squares
        
        self.win = win # Window where the Tessellation will be drawn
        self.center_loc = center # Location on window of the center of the tessellation on
        self.scale = length # Length of each side of polygons
        
        self.vert_filled = 0 # Total number of vertices filled
        
        self.autofill_list = []
    
    
    
    # Update the current reference vertex
    def update_vertex_reference(self):
        
        # If the current vertex is filled, need to update both current and reference vertices
        # The current vertex is simply moved to the next element in the `border' linked list
        if self.current_vertex.is_filled:
            self.current_vertex = self.current_vertex.neighbors[self.current_vertex.ccw_max_index]
        
        # Reference vertex must still be updated to the current vertex's most Counter Clockwise point
        self.reference_vertex = self.current_vertex.neighbors[self.current_vertex.ccw_max_index]
            
    
        
    # Add a polygon
    def add_poly_to_tess(self, poly_id, central_vertex, reference_vertex):
        # Properties setup if adding Triangle
        if poly_id == 0:
            new_poly = Triangle(central_vertex, reference_vertex)
            color = self.tri_color
        # Properties setup if adding Square
        else:
            new_poly = Square(central_vertex, reference_vertex)
            color = self.sq_color
            
        # If the polygon can be inserted successfully, draw the polygon to the window
        if new_poly.inserted:
            new_poly.draw_poly(self.win, self.center_loc, self.scale, color)
    
    
    
    # Fill the vertex (and all associated vertices) with the list of polygons (triangles, squares).
    def fill_with_poly(self, polys_to_add, temp_check_vert):
        # Add Triangles
        for i in range(polys_to_add[0]):
            self.add_poly_to_tess(0, temp_check_vert, temp_check_vert.neighbors[temp_check_vert.ccw_max_index])
        # Add Squares
        for i in range(polys_to_add[1]):
            self.add_poly_to_tess(1, temp_check_vert, temp_check_vert.neighbors[temp_check_vert.ccw_max_index])
    
            
    
    # Fill any vertex adjacent to the current one that has a single valid solution/orientation
    # Iterative DFS search algorithm for auto-filling vertices
    def autofill_adjacent(self, current_check_neighbors):
        
        # Expection for the current vertex. Check for auto-filling neighboring vertices, even if we cannot auto-fill the current one.
        append_if_fill = False
        self.autofill_list.append(current_check_neighbors)
        
        while len(self.autofill_list) > 0: # Check until no more vertices left to check
            temp_check_vert = self.autofill_list.pop() # Look at the farthest vertex
            polys_to_add = temp_check_vert.finish_fill()
            if not append_if_fill or (polys_to_add != [0,0]).any(): # If the vertex can be filled (or is the first one)...
                append_if_fill = True
                
                # If the vertex can be filled, add all its neighbors to check for filling
                for vert_index in temp_check_vert.neighbors:
                    self.autofill_list.append(temp_check_vert.neighbors[vert_index])
                    
                # Fill the vertex. Newly created vertices cannot be auto-filled, so we do not need to check them with the previous append.
                self.fill_with_poly(polys_to_add, temp_check_vert)
                self.vert_filled += 1
                
                
                
    # Fill any vertex adjacent to the current one that has a single valid solution/orientation
    # Recursive DFS search algorithm for auto-filling vertices
    # Unlike the iterative version, no special exception is made for the first vertex.
    def autofill_adjacent_recursive(self, current_check_neighbors):
        polys_to_add = current_check_neighbors.finish_fill()
        
        # If the vertex can be filled, fill with those polygons.
        # Make a copy of neighbor dictionary before inserting vertices so we do not check these extra vertices for filling
        if (polys_to_add != [0,0]).any():
            current_neighbor_dict = current_check_neighbors.neighbors.copy()
            self.fill_with_poly(polys_to_add, current_check_neighbors)
            self.vert_filled += 1
            
            # Check each neighbor, excluding newly created ones, for autofilling.
            for vert_index in current_neighbor_dict:
                self.autofill_adjacent_recursive(current_check_neighbors.neighbors[vert_index])