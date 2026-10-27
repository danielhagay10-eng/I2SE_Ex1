# Datasets

The project utilizes two primary file types to execute the projection:

## 1. Volumetric Scan Data (.nrrd)
The NRRD (Nearly Raw Raster Data) file contains 3D imaging data (e.g., MRI or CT scans). 
It consists of a header containing metadata, followed by the data block which is a massive 3D matrix in grayscale. The system reads this matrix and extracts the voxel intensity at any given `[x, y, z]` coordinate.

## 2. Plane Coordinates File (.csv)
A comma-separated values text file defining the list of planes (slices) to be extracted.
**The file structure must strictly follow this format:**
- The first row is a Header (ignored during runtime).
- Every subsequent row must begin with an integer representing the number of points for that plane (3 for a triangle, 4 for a trapezoid).
- This is followed by the `[x, y, z]` coordinates of each point. Therefore, a row will contain 9 consecutive coordinate values for 3 points, or 12 values for 4 points.