# Algorithm Definition

The Plane Projection algorithm calculates an optimal and fast 2D slice from a 3D matrix. It operates through the following mathematical and computational steps:

1. **Direction Vectors Construction:** Given 3 spatial points (a, b, c), the system calculates the Euclidean distances between them and generates normalized unit vectors 
representing the direction of progression from point 'a' to 'b', and from 'a' to 'c'.

2. **Vectorized Grid Generation:** Instead of using nested `for` loops—which are highly inefficient in Python—the algorithm leverages Numpy's vectorization capabilities to generate the full coordinate matrix (grid) of the target image simultaneously.

3. **Exact Coordinate Mapping:** For every pixel in the target 2D image, the algorithm calculates its exact relative 3D coordinate within the original MRI volume.

4. **Trilinear Interpolation:** Since the calculated coordinates are floating-point numbers, the algorithm uses the `map_coordinates` function from `scipy.ndimage`. This performs a smooth trilinear interpolation, calculating the precise grayscale value by weighting the neighboring pixels.

5. **Masking:** Areas in the grid that fall outside the defined triangle or trapezoid boundaries are mathematically cropped and masked with black color (value 0).