# Some notes about polygon implementation and how polygons will work to tessellate the plane.
# 
# 

from vertex import Vertex
import numpy as np
import pygame

class Polygon:
    def __init__(self, center_vertex, ref_vertex, sides):
        self.inserted = False # Determine whether the polygon can be inserted at all associated vertices 
        self.v0 = center_vertex # Vertex around which we fill with polygons
        self.v1 = ref_vertex # Reference vertex. v0 -> v1 establishes one side of the polygon to build all the rest
        
        self.sides = sides # Number of sides of the polygon
        self.ang = (self.sides-2)/self.sides * np.pi # Interior angle of the polygon
        self.R = np.array([[np.cos(self.ang), np.sin(self.ang)],[-np.sin(self.ang), np.cos(self.ang)]]) # CW Rotation matrix
        
        self.vertex_list = [self.v0, self.v1] # Keep ordered list of vertices associated with the polygon
        
        # Populating the remaining self.sides - 2 vertices must be handled carefully.
        # Each shape (sides = 3,4,6,12) have some complications that can be addressed individually.
        
    
    
    # Find the coordinates for the new vertex from the vertex we will rotate around and a reference vertex.
    # By default, the polygon rotation matrix is clockwise.  If cw = False, we must rotate counter-clockwise.
#     def find_new_coords(self, vert_rot, vert_ref, cw):
#         rot = cw*self.R + (1-cw)*np.linalg.inv(self.R)
#         return np.dot(rot, vert_ref.coords - vert_rot.coords) + vert_rot.coords

    # A second option to find the coordinates for new vertices.
    # Using the method with rotation matrices compounds errors, but will take several hundred rotations to do so
    # This method will gaurantee each new segment has length 1, and only deals with misalignment, which is typically small
    def find_new_coords(self, vert_rot, vert_ref, cw):
        rot = int(6*self.ang/np.pi *(1-2*cw))
        final_ang = (vert_rot.neighbor_num(vert_ref) + rot)*np.pi/6
        return np.array([np.cos(final_ang), np.sin(final_ang)]) + vert_rot.coords
        
        
    
    # Check if every vertex associated with the polygon can accommodate a polygon of this size.
    def check_add_poly(self, poly_array):
        return all(vert.check_valid_polys(poly_array) for vert in self.vertex_list)
    
    
    
    # If every element of the vertex list can accommodate an the extra polygon, add the polygon to the tesselation
    # This requires:
    #     > Insert polygon to each vertex's poly list
    #     > Update neighbors for each vertex
    def insert_poly(self, poly_array):
        if not self.check_add_poly(self.poly_assign):
            print('Cannot add this polygon')
            return False
        
        for i in range(len(self.vertex_list)):

            # Since the vertices are added to vertex_list in order, set consecutive vertices to be neighbors
            # In the case of a triangle:
            #    > If v0 and v1 have (somehow) have different neighbors, an error message will appear.
            self.vertex_list[i].set_neighbor(self.vertex_list[i-1])
            self.vertex_list[i].set_neighbor(self.vertex_list[(i+1)%len(self.vertex_list)])
            self.vertex_list[i].add_polys(poly_array)

            # If a vertex is new, the previous vertex will be the most counter-clockwise vertex filled
            #    > If it already existed, there exists a set of vertices [..., a,vi,v(i-1),...] where a is more CCW.
            if self.vertex_list[i].ccw_max_index == None or i==0:
                self.vertex_list[i].store_ccw_index(self.vertex_list[i-1])

        # If the center vertex becomes filled by the addition of the new polygon, special consideration is needed.
        # In particular, the final vertex is already present, and should be pointing back to the center vertex.
        # In this case, v(-1) will have a more counter-clockwise vertex, which updates the border of the tessellation.
        self.v0.check_filled()
        if self.v0.is_filled:
            self.vertex_list[-1].store_ccw_index(self.vertex_list[-2])
        return True
        
        
        
    def draw_poly(self, win, center, scale_factor, color, width=0):
        vertex_coords = []
        for vert in self.vertex_list:
            vertex_coords.append(tuple(center + scale_factor*vert.coords))
        pygame.draw.polygon(win,color,tuple(vertex_coords),width)
        pygame.draw.polygon(win,(0,0,0),tuple(vertex_coords),1) # Add a black border to the polygon
        pygame.display.update()
            
            
        

class Triangle(Polygon):
    def __init__(self, center_vertex, ref_vertex):
        super().__init__(center_vertex, ref_vertex, 3)
        self.poly_assign = np.array([1,0]) # ID (array) corresponding to Vertex.polys
        self.populate() # Create and add all vertices associated with the Triangle
        self.inserted = self.insert_poly(self.poly_assign)
        
    def populate(self):
        # Populating the final vertex of a triangle.
        # Find coordinates by rotating the segment from v0 to v1 around the v1 vertex
        temp_new_vertex = Vertex(self.find_new_coords(self.v1, self.v0, True))
        
        # Since there is only 1 new vertex, we must check whether the new vertex already exists as a neighbor of v0 or v1.
        if not self.v1.check_avail(temp_new_vertex):
            temp_new_vertex = self.v1.neighbors[self.v1.neighbor_num(temp_new_vertex)]
        
        # If both v0 + v1 have a vertex at the new position, we are not currently checking if it is the same vertex.
        if not self.v0.check_avail(temp_new_vertex):
            temp_new_vertex = self.v0.neighbors[self.v0.neighbor_num(temp_new_vertex)]
        
        self.vertex_list.append(temp_new_vertex) # Add the new vertex to list
        
        # If every element of the list can accommodate an extra triangle, insert the triangle.
            

            
            
            
class Square(Polygon):
    def __init__(self, center_vertex, ref_vertex):
        super().__init__(center_vertex, ref_vertex, 4)
        self.poly_assign = np.array([0,1]) # ID (array) corresponding to Vertex.polys
        self.populate() # Create and add all vertices associated with the Square
        self.inserted = self.insert_poly(self.poly_assign)
        
    def populate(self):
        # Begin with vertex v(-1).  To do so, use v0 -> v1 line and rotate around v0 by R^-1 (Rotate CCW)
        temp_last_vertex = Vertex(self.find_new_coords(self.v0, self.v1, False))
        
        # Need to check whether v0 already has a neighbor associated with these coords
        if not self.v0.check_avail(temp_last_vertex):
            temp_last_vertex = self.v0.neighbors[self.v0.neighbor_num(temp_last_vertex)]
            
        self.vertex_list.append(temp_last_vertex) # Add the final vertex to the list
        
        # Create v2 using the line v1 -> v0 and rotating around v1 by R (CW rotation)
        temp_new_vertex = Vertex(self.find_new_coords(self.v1, self.v0, True))
        
        if not self.v1.check_avail(temp_new_vertex):
            temp_new_vertex = self.v1.neighbors[self.v1.neighbor_num(temp_new_vertex)]
            
        # Since the last vertex v(-1) is already in the list, we insert new vertices second from last to maintain order
        self.vertex_list.insert(-1, temp_new_vertex)