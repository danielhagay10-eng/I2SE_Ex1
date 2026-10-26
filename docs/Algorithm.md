# Main Algorithm Definition: Plane Projection

## 1. Input Parameters
- **M**: A 3D raster data matrix (volumetric data).
- **p**: A plane defined by 3 spatial points (a, b, c) forming an isosceles triangle where `dist(a,b) == dist(a,c)`.

## 2. Mathematical Setup
1. Calculate distances: Let $D_{ab} = dist(a,b)$ and $D_{bc} = dist(b,c)$.
2. Calculate normalized directional vectors:
   * $v_{ab} = \frac{vector(a,b)}{D_{ab}}$
   * $v_{ac} = \frac{vector(a,c)}{D_{ab}}$
3. Initialize an empty 2D output matrix **E** of size $D_{bc} \times D_{ab}$ (width x height).

## 3. Projection Loop (Pseudo-code)
```text
For y = 0 to int(Dab) - 1:
    // Calculate current row endpoints directly based on y
    a1 = a + y * v_ab
    a2 = a + y * v_ac
    
    // Calculate distance between the endpoints of the current row
    d12 = dist(a1, a2)
    
    // Prevent division by zero at the triangle's apex (when d12 == 0)
    If d12 == 0:
        dp = vector(0, 0, 0)
    Else:
        dp = vector(a1, a2) / d12
    
    p_current = a1
    
    For x1 = 0 to int(d12):
        // Sample the 3D volume (returns 0 if coordinates are out of bounds)
        v_val = M[p_current]
        
        // Calculate and round the centered X coordinate for the 2D matrix
        x = round( (Dbc / 2) - (d12 / 2) + x1 )
        
        // Assign value if within horizontal bounds
        If 0 <= x < Dbc:
            E[x][y] = v_val
            
        p_current = p_current + dp

Return E