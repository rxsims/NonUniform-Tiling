# NonUniform-Tiling

Using regular polygons to tile a Euclidean plane is been a well known and well studied [topic](https://en.wikipedia.org/wiki/Euclidean_tilings_by_convex_regular_polygons).  The restriction of uniformity inherently removes any user input to the problem.  While the beautiful mathematical symmetry is lost, removing the uniform requirement allows infinitely many tilings using Triangles and Squares (with the option to add Hexagons and Dodecagons).  This can be easily seen using the tiling

<p align="center">
 <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/2-uniform_n4.svg/659px-2-uniform_n4.svg.png" width="250" height="250">
</p>

where removing the uniform requirement allows for an arbitrary number of square layers to be inserted between triangular layers.  Each vertex is still required to be entirely filled (no gaps allowed), which still greatly restricts the number of choices one can make in a simple tiling.

In this program, the basic rules of complete vertices are used to build non-uniform tilings.  The default settings allow the construction of 1000 filled vertices, where decisions for which polygon (triangle or square) are chosen at random.  The following settings can be easily changed within the main.py file:
1) Decisions made by user: randomly_fill_vertices = False
2) Number of vertices (N) to be filled can be changed using maximum_vertices_filled
3) Side length (L) of the polygon can be changed using polygon_side_length

Keep in mind, for the entire tessellation to appear on the window, the quantity L<sup>2</sup>N should be roughly constant.

####Sample Output:
<p align="center">
 <img src="https://i.imgur.com/E9oKFbM.jpg" width="300" height="294">
</p>
