# Software Requirements Specification (SRS)

## 1. Functional Requirements
- **Data Ingestion:** The system shall load and parse 3D volumetric data from NRRD files.
- **Input Parsing:** The system shall read spatial coordinates from a CSV file, extracting sets of 3 or 4 points that define 3D planes.
- **Projection Computation:** The system shall calculate the 2D projection of each plane out of the 3D volume using normalized vectors and step-distance mapping.
- **Video Export:** The system shall generate an MP4 video file where each frame corresponds to the 2D projection of a plane listed in the CSV.

## 2. Non-Functional Requirements
- **Performance:** The projection algorithm must execute efficiently, achieving at least 30 Frames Per Second (FPS) for a 500^3 byte matrix.
- **Robustness:** Coordinates mapped outside the bounds of the 3D matrix must be handled safely, defaulting to a value of 0 without causing system crashes.
- **Extensibility:** The system must be designed using Object-Oriented Programming (OOP) principles, allowing future expansion.