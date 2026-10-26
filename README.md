# 3D Volume Plane Projection (I2SE_Ex1)

## Problem Statement
Given a 3D raster data matrix (M) and a plane (p), the goal is to compute the 2D matrix (image) of the projection of p within M. The system calculates the exact intersection points using vector normalization and mapping algorithms to generate an accurate 2D slice from volumetric data.

## Scope of the Project
The project requires reading 3D volumetric data files in NRRD format and processing sets of 3D spatial coordinates provided via CSV files. For each plane defined by these coordinates, the software computes the 2D projection and outputs a compiled MP4 video showcasing the sequential plane projections as individual frames. The implementation is written in Python, focusing on Object-Oriented Design (OOD) principles, algorithmic accuracy, and high runtime efficiency (targeting 100+ FPS).

## Usage and Execution
The project features a dynamic Command-Line Interface (CLI) that automatically scans for datasets and provides an interactive selection menu.

**Interactive Mode:**
Simply run the main script. The system will detect `.nrrd` and `.csv` files in the `datasets` directory and prompt you to choose:
```bash
python Ex0.py
```

**Direct CLI Mode:**
For automated execution (or checking specific files directly), pass the file paths as arguments:
```bash
python Ex0.py datasets/rnnd/<filename.nrrd> datasets/cvs/<filename.csv> output.mp4
```

## Running Tests
The project includes a robust suite of unit tests and performance benchmarks located in the `tests/` directory.

**Interactive Test Menu:**
To easily select and run specific tests or all tests at once, use the built-in test runner:
```bash
python run_tests.py
```

**Standard Python Unittest Execution:**
Alternatively, you can run the test suite directly using Python's native unittest module from the root directory:
```bash
python -m unittest discover -s tests
```