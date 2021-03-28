# Some notes about vertex properties when polygons are added.
# 
# We begin with a configuration v0, v1 vertices.  These two vertices establish the cww_max_index for each other.  Furthermore, the line connecting v0 and v1 set up the reference edge/angle for the first created polygon.
# 
# When creating a polygon around v0, all previously established vertices v1, v2, ... vk do not have their cww_max_index changed.
# 
# The only exception is when v0 becomes filled, then v1.cww_max_index must be updated to maintain border.  v0.cww_max_index should not be referenced beyond this point, so it can be set to null or simply not updated.
# 
# However, all new vertices va, vb, vc, ... will NOT have v0 as cww_max_index.  If the polygon is created around v0 with reference v1, then the only viable options for new vertex cww_max_index is {v1, va, vb, ...}.
# 
# 
# 
# Keep in mind:
#     > Linked list of ccw_max_index creates linked list denoting the BORDER of the tessellation, as well as THREADs from the interior web of filled vertices.
#     > THREADs should allow you to choose any random vertex, whether on interior or border, and follow the linked list back to the border.  There should be no cycles within the interior.



import numpy as np

class Vertex:
    def __init__(self,coords):
        self.coords = coords # np.array
        self.n = 12 # Maximum number of neighbors
        self.neighbors = {} # Dictionary of directions:Vertex, 1:, 2:, ... , n:
        
        self.tol = 10**(-8) # Tolerance in corrdinates close to zero
        self.correct_ang_error(self.tol) # Correct any issues where repeated rotations will move points away from zero
        
        self.ccw_max_index = None # Store the vertex index corresponding to the most counter-clockwise filled direction.
        self.is_filled = False # In combination w/ ccw_max_index, have a linked list of the border.
        
        # Array of [Triangles, Squares] around the vertex. Order of placement not maintained.
        # 30 x poly_value = interior angle of polygon.
        # poly_value correspond to the number of neighbor indices n taken up by the polygon.
        self.polys = np.array([0,0])
        self.polys_value = np.array([2,3])
        
        self.polys_excl = [[4,1],[1,3]] # Special set of polygon configurations that will lead to unfillable vertices.
        
        
    def correct_ang_error(self, tol):
        for i in range(2):
            if abs(self.coords[i]) < tol:
                self.coords[i] = 0.
        
    
    def info(self):
        print('Coords: ', self.coords)
        print('Counter Clockwise Index Set: ', self.ccw_max_index)
        print('Completely Filled: ', self.is_filled)
        print('Polygons: {} Tri, {} Square'.format(self.polys[0],self.polys[1]))
        print('Neighbors: ', self.neighbors)
        
    
    
    # Take (adjacent) vertex and find the angle with respect to current vertex.
    # Angle must lie on 1 or 12 directions. Each index corresponds to 360/n degrees.
    # Return index number corresponding to this direction.
    def neighbor_num(self, vtx):
        vec = vtx.coords - self.coords
        ang = round(np.arccos(vec[0]/np.linalg.norm(vec))/np.pi*self.n/2)
        if np.linalg.norm(vec) > 1.0001:
            print('Careful, vector length > 1', np.linalg.norm(vec))
            print(self.coords)
        #print('Neighbor_num', vec, ang, np.linalg.norm(vec))
        if vec[1] < 0:
            ang = (-ang)%self.n # Fix angle [0,360) from the restriction from principle branch of arccosine/arcsine
        return int(ang)
    
    
    
    # Check whether a vertex has already been established in a particular direction.
    # Return Bool, True = Vertex location is open, False = Vertex is already present
    def check_avail(self, vtx):
        return (self.neighbor_num(vtx) not in self.neighbors)
    
    
    
    # Attempt to set an (adjacent) vertex to a direction in neighbor list.
    # If available, the vertex is assigned that location.
    # If unavailable, do not set any new neighbors.
    def set_neighbor(self, vtx):
        if self.check_avail(vtx):
            self.neighbors[self.neighbor_num(vtx)] = vtx
        else:
            if vtx != self.neighbors[self.neighbor_num(vtx)]:
                print('Trying to append a different vertex... uh oh')
                

    
    # Update the most counter-clockwise filled direction of the vertex.
    def store_ccw_index(self, vtx):
        self.ccw_max_index = self.neighbor_num(vtx)
        
        
        
    # Check whether the current set of polygons around the vertex is a valid configuration.
    # If configuration does not overfill vertex or a disallowed configuration, return True
    # If invalid, return False.
    def check_valid_polys(self, extra_polys=np.array([0,0])):
        temp_polys = self.polys + extra_polys
        if (np.dot(temp_polys, self.polys_value) > self.n) or (temp_polys==self.polys_excl).all(axis=1).any():
            #print('Invalid Configuration of Polygons')
            return False
        return True
    
    
    
    # Check whether the entire vertex is filled, and update is_filled if so.
    def check_filled(self):
        if np.dot(self.polys, self.polys_value) == self.n:
            self.is_filled = True
            
            

    # Add some number of polygons to the vertex if the resulting configuration is valid.
    # If the configuration is not valid, do no add the polygons.
    def add_polys(self, new_polys):
        if self.check_valid_polys(new_polys):
            #print(f'Adding {new_polys} to vertex config: {self.polys}')
            self.polys += new_polys
            
            
    
    # Find the unique solution to fill the vertex, if one exists.
    # Above a certain plane in the (tri, sq) space, the vertex can be filled with either all triangles or squares.
    # Graphically, it does not matter the order we add only squares or only triangles, since they will be indistinguishable.
    # Thus, one of the values in the array will always be zero.
    # To find this configuration, we leave either # of Triangles or # of Squares the same and check if the number of
    # squares or triangles, respectively, is an integer value.
    # Returns np.array with same format as self.polys.
    def finish_fill(self):
        if np.dot(self.polys, self.polys_value) > 6: # Special plane that determines if unique solution of possible
            # Solve how many triangles/squares are needed if the opposite number is held constant
            temp_sol = ((self.n - self.polys*self.polys_value)/self.polys_value[::-1])[::-1]
            
            # Require the solution to have integer number of polygons and be adding polygons (no deleting triangles/squares)
            valid = (temp_sol%1 == 0) & (temp_sol - self.polys > 0)
            
            # Unique solution of the form [x, 0] or [0, x]
            return ((temp_sol - self.polys)*valid).astype(int)
        
        # No unique solution, so do not add any more polygons.
        # This return matches a failed-to-find solution from before corresponding to polys = [2,1] configuration.
        return np.array([0,0])