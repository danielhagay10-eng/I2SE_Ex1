# Testing Strategy

## 1. Unit Testing
*   **Vector Math:** Verify distance calculations and vector normalization for accuracy, ensuring floating-point errors are handled (EPS < 0.001).
*   **Boundary Handling:** Ensure the 3D volume sampling returns a default value of 0 (black) when queried coordinates fall outside the valid matrix dimensions.

## 2. Integration Testing
*   Validate the full data pipeline: loading an NRRD file, parsing the CSV points, generating 2D projections, and compiling them into a video sequence.

## 3. Demo and System Testing
*   The system will be tested via the main demo script using the command format: `python Ex0.py <file.nrrd> <file.csv> <file.mp4>`.
*   Verify that the output MP4 file correctly compiles the projected frames in the exact sequence specified by the CSV file.
    
## 4. Performance Testing
*   Benchmark the execution time to ensure the projection algorithm processes a 500^3 bytes volume at a rate of at least 100 FPS.
