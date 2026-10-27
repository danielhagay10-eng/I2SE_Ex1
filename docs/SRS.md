# Software Requirements Specification (SRS)

## 1. Functional Requirements
- **Data Input:** The system must read and load 3D medical imaging files in NRRD format.
- **Plane Parsing:** The system must parse CSV files, filter out empty rows, and identify lists of 3 points (defining a triangle) or 4 points (defining an isosceles trapezoid) that represent planes in 3D space.
- **Processing & Projection:** The system must compute and sample the appropriate pixels from the 3D volume onto the requested 2D plane. It must utilize trilinear interpolation to ensure image quality and sharpness.
- **Output:** The system must aggregate the generated 2D slices and export them as a continuous sequence of frames into an MP4 video file.

## 2. Non-Functional Requirements & Performance
- **Robustness:** The system must handle invalid data gracefully without crashing. In cases of: 4 points not sharing the same plane, 3 collinear points, out-of-bounds coordinates, or extreme dimensions causing memory overflow—the system must block the operation, log a clear error, and safely skip to the next plane.
- **Performance:** The system must process and render slices from a volume size of up to 500x500x500 pixels efficiently, strictly maintaining a minimum processing rate of at least 30 Frames Per Second (FPS).