# Experiment Results

## Setup
*   **Data Volume:** `MRHead.nrrd` (Shape: 256x256x130).
*   **Planes Data:** A stress-test set of 100 spatial planes configured inside a CSV file, plus tests for 3-point (triangle) and 4-point (trapezoid) inputs.
*   **Execution:** Tested using `test_performance.py` leveraging Numpy vectorization and Scipy Trilinear Interpolation.

## Results
*   **Performance Metrics:** The vectorized and smoothed projection algorithm processed 100 planes in ~0.419 seconds.
*   **Throughput (FPS):** The system achieved an average of **238.4 FPS**, vastly exceeding the assignment requirement of 100+ FPS despite the added computational weight of 3D interpolation.
*   **Visual Quality:** Trilinear interpolation successfully smoothed out the pixels on diagonal plane projections.
*   **Robustness:** Out-of-bounds coordinates and zero-distance edge cases were safely handled without crashing, verified by automated unit tests.
*   **Output:** The 2D projection frames were successfully generated and compiled into the attached MP4 video format.