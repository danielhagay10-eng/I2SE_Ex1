# I2SE_Ex1: Plane Projection of 3D Volume

## Project Description
This project implements an algorithm to project a 2D plane out of 3D raster data (such as an MRI scan in NRRD format). The plane is defined by either 3 or 4 coordinates. The output is a generated MP4 video file displaying the continuous sequence of the projected slices.

## Project Structure
- `Ex0.py`: The core script containing the data processing classes and the main projection algorithm.
- `tests/`: The test suite directory containing edge cases and performance tests.
- `docs/`: The documentation directory containing the SRS, Algorithm definition, Datasets info, and Experiment report.
- `datasets/`: The data directory containing the `.nrrd` volumetric files and the `.csv` coordinate files.

## System Requirements
- Python 3.x
- Third-party libraries: `numpy`, `opencv-python` (cv2), `pynrrd`, `scipy`

## Usage
You can run the system via the command line with pre-defined arguments:
```bash
python Ex0.py <file.nrrd> <file.csv> <file.mp4>
```

Alternatively, run it without arguments to launch the interactive menu:
```bash
python Ex0.py
```

The project includes a comprehensive test suite to ensure stability and performance.
You can run the tests using the interactive test runner:
```bash
 python run_tests.py
```
Alternatively, you can run all tests directly via the command line using Python's built-in unittest framework: 
```bash
python -m unittest discover tests
```
