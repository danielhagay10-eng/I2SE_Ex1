# Main Algorithm Definition: Plane Projection

## 1. Input Parameters
* **M**: A 3D raster data matrix (volumetric data).
* **p**: A plane defined by 3 spatial points (a, b, c) forming an isosceles triangle where `dist(a,b) == dist(a,c)`.

## 2. Mathematical Setup
1. Calculate distances: Let $D_{ab} = dist(a,b)$ and $D_{bc} = dist(b,c)$.
2. Calculate normalized directional vectors:
   * $v(a,b) = \frac{vector(a,b)}{D_{ab}}$
   * $v(a,c) = \frac{vector(a,c)}{D_{ab}}$
3. Initialize an empty 2D output matrix **E** of size $D_{bc} \times D_{ab}$ (width x height).

## 3. Projection Loop (Pseudo-code)
```text
a1 = a
a2 = a

For y = 0 to Dab:
    // Step forward along the triangle edges
    a1 = a1 + v(ab)
    a2 = a2 + v(ac)
    
    // Setup for scanning the horizontal line between a1 and a2
    p_current = a1
    d12 = dist(a1, a2)
    dp = vector(a1, a2) / d12  // Normalized step vector across the row
    
    For x1 = 0 to d12:
        // Sample the 3D volume (return 0 if out of bounds)
        v_val = M[p_current]
        
        // Calculate the centered x coordinate in the 2D matrix
        x = (Dbc / 2) - (d12 / 2) + x1
        
        // Assign value and advance the point
        E[x][y] = v_val
        p_current = p_current + dp

Return E
