# Experiment Results

## Setup
*   **Data Volume:** `MRHead.nrrd` (Shape: 256x256x130).
*   **Planes Data:** A stress-test set of 100 spatial planes configured inside a CSV file, plus tests for 3-point (triangle) and 4-point (trapezoid) inputs.
*   **Execution:** Tested using `test_performance.py` leveraging Numpy vectorization, Scipy Trilinear Interpolation, and 8-bit OpenCV normalization.

## Results
*   **Performance Metrics:** The algorithm processed 100 planes in ~0.594 seconds.
*   **Throughput (FPS):** The system achieved an average of **168.3 FPS**, comfortably exceeding the assignment requirement of 100+ FPS while maintaining high visual accuracy.
*   **Visual Quality:** Trilinear interpolation smoothed out pixels on diagonals, and 8-bit normalization eliminated vertical rendering artifacts.
*   **Robustness:** Out-of-bounds coordinates and zero-distance edge cases were safely handled without crashing, verified by automated unit tests.
*   **Output:** The 2D projection frames were successfully generated and compiled into the attached MP4 video format.