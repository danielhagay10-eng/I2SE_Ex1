# Dataset Definition

## Overview
This project utilizes 3D volumetric data files in the NRRD (Nearly Raw Raster Data) format for image processing and projection, alongside corresponding CSV files that define the spatial coordinates for the planar slices.

## Primary Data Sources
- **Volumetric Data (.nrrd):** The core 3D models used for projection. The primary medical dataset (e.g., `MRHead.nrrd`) is sourced from the open-source **3D Slicer** project. Additional test volumes (such as `onion`, `croissant`, and `swiss_roll`) are provided by the course staff to validate the algorithm across different shapes and densities.

- **Coordinate Data (.csv):** Each volumetric model is accompanied by a CSV file containing sets of 3D spatial points. These points define the vertices of the specific planes (triangles or trapezoids) to be extracted and projected from the 3D volume.