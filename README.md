# 3D Volume Plane Projection (I2SE_Ex1)

## Problem Statement
Given a 3D raster data matrix (M) and a plane (p), the goal is to compute the 2D matrix (image) of the projection of p within M. The system calculates the exact intersection points using vector normalization and mapping algorithms to generate an accurate 2D slice from volumetric data.

## Scope of the Project
The project requires reading 3D volumetric data files in NRRD format and processing sets of 3D spatial coordinates provided via CSV files. For each plane defined by these coordinates, the software computes the 2D projection and outputs a compiled MP4 video showcasing the sequential plane projections as individual frames. The implementation is written in Python, focusing on Object-Oriented Design (OOD) principles, algorithmic accuracy, and high runtime efficiency (targeting 100+ FPS).
