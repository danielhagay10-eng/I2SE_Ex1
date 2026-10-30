import sys
import os
import glob
import csv
import numpy as np
import cv2
import nrrd
import scipy.ndimage

def validate_plane_points(points):
    """Validates that the points can form a proper plane."""
    if len(points) < 3:
        raise ValueError("Not enough points: At least 3 points are required to define a plane.")

    # Check for collinear points
    v1 = points[1] - points[0]
    v2 = points[2] - points[0]
    normal = np.cross(v1, v2)
    
    if np.linalg.norm(normal) < 1e-6:
        raise ValueError("Points are collinear - cannot define a single plane.")

    # Check if 4 points are non-planar
    if len(points) >= 4:
        v3 = points[3] - points[0]
        if abs(np.dot(normal, v3)) > 1e-3:
            raise ValueError("The four points are non-planar.")

def check_memory_limits(width, height):
    """Prevents out-of-memory crashes for excessively large planes."""
    MAX_PIXELS = 5000 * 5000
    if width * height > MAX_PIXELS:
        raise MemoryError(f"Memory Error: The requested plane is too large ({width}x{height}) and will cause a crash.")


class VolumeData:
    def __init__(self, filepath):
        self.filepath = filepath
        # Load 3D matrix (MRI) from NRRD file
        self.matrix, self.header = nrrd.read(self.filepath)
        self.shape = self.matrix.shape
        print(f"Loaded volume with shape: {self.shape}")

class PlaneProjector:
    def __init__(self, volume_data):
        self.volume = volume_data

    def project_plane(self, points):
        points = np.array(points, dtype=float)
        
        # Protection phase 1: validate geometric coordinates
        validate_plane_points(points)
        
        # Identify if 3 points (triangle) or 4 points (trapezoid/rectangle)
        if len(points) == 3:
            a1_start, a2_start, b, c = points[0], points[0], points[1], points[2]
        elif len(points) == 4:
            a1_start, a2_start, b, c = points[0], points[1], points[2], points[3]
        else:
            return np.zeros((1, 1), dtype=np.uint8)

        # Calculate distances based on points
        Dab = np.linalg.norm(b - a1_start)
        Dbc = np.linalg.norm(c - b)
        
        # Round distances to integers for 2D image dimensions
        int_Dab = int(np.round(Dab))
        int_Dbc = int(np.round(Dbc))

        # Protection phase 2: prevent Out of Memory
        check_memory_limits(int_Dbc, int_Dab)

        # Prevent crash if distance is 0
        if int_Dab == 0 or int_Dbc == 0:
            return np.zeros((1, 1), dtype=np.uint8)

        # Create normalized vectors for movement direction
        v_ab = (b - a1_start) / Dab
        v_ac = (c - a2_start) / Dab

        # Create 2D coordinate grid for vectorized calculation
        Y = np.arange(int_Dab).reshape(-1, 1)
        X = np.arange(int_Dbc).reshape(1, -1)

        # Calculate start and end vectors (a1, a2) for each row
        a1 = (a1_start + Y * v_ab)[:, np.newaxis, :]
        a2 = (a2_start + Y * v_ac)[:, np.newaxis, :]

        # Calculate horizontal distance for each row
        d12 = np.linalg.norm(a2 - a1, axis=2, keepdims=True)
        
        # Calculate horizontal progression vector (dp), ignoring division by zero warnings
        with np.errstate(divide='ignore', invalid='ignore'):
            dp = np.where(d12 > 0, (a2 - a1) / d12, 0)

        # Find precise 3D coordinates (P) for each pixel
        x1 = X - (int_Dbc / 2) + (d12[..., 0] / 2)
        x1_3d = x1[..., np.newaxis]
        P = a1 + x1_3d * dp

        # Transpose coordinates for Scipy interpolation
        coords = P.transpose(2, 0, 1)
        
        # Smooth sampling (trilinear interpolation) from MRI volume
        sampled_values = scipy.ndimage.map_coordinates(
            self.volume.matrix, coords, order=1, mode='constant', cval=0.0
        )

        # Create mask to black out areas outside the triangle/trapezoid shape
        valid_triangle = (x1 >= 0) & (x1 <= d12[..., 0])
        sampled_values[~valid_triangle] = 0
        
        # Convert data to proper format and transpose to correct orientation
        E_T = sampled_values.astype(self.volume.matrix.dtype)
        return E_T.T


def parse_csv_planes(csv_filepath):
    """
    Reads the CSV file based on the required format.
    """
    planes = []
    try:
        with open(csv_filepath, 'r') as f:
            reader = csv.reader(f)
            
            # Skip header
            next(reader, None)
            
            for row in reader:
                if not row or not row[0].strip():
                    continue
                    
                num_points = int(row[0].strip())
                points = []
                
                # Read first 3 points
                points.append([float(row[1]), float(row[2]), float(row[3])])
                points.append([float(row[4]), float(row[5]), float(row[6])])
                points.append([float(row[7]), float(row[8]), float(row[9])])
                
                # Read 4th point if defined
                if num_points == 4:
                    points.append([float(row[10]), float(row[11]), float(row[12])])
                
                planes.append(points)
                
    except Exception as e:
        print(f"Error reading CSV: {e}")
        
    return planes


def main(nrrd_file, csv_file, mp4_file):
    print(f"Loading NRRD: {nrrd_file}")
    print(f"Reading CSV points: {csv_file}")
    
    # Load 3D file and initialize projector
    volume = VolumeData(nrrd_file)
    projector = PlaneProjector(volume)
    
    # Read plane coordinates from CSV
    planes = parse_csv_planes(csv_file)
    
    if not planes:
        print("No planes found in CSV. Exiting.")
        return

    print(f"Found {len(planes)} planes to process.")
    print(f"Video output will be saved to: {mp4_file}")
    
    video_writer = None 
    fps = 30 
    
    # Iterate over each plane
    for i, plane_points in enumerate(planes):
        if len(plane_points) >= 3:
            print(f"Processing plane {i+1}/{len(planes)} (Points: {len(plane_points)})...")
            
            try:
                # Project the plane and catch mathematical/memory errors to skip safely
                image_matrix = projector.project_plane(plane_points)
                
                # Normalize image from 16-bit to 0-255 uint8 range
                normalized_img = cv2.normalize(image_matrix, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
                image_matrix_8u = normalized_img.astype(np.uint8)
                
                if video_writer is None:
                    height, width = image_matrix_8u.shape
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
                    video_writer = cv2.VideoWriter(mp4_file, fourcc, fps, (width, height), isColor=False)
                
                video_writer.write(image_matrix_8u)
                
            except (ValueError, MemoryError) as e:
                print(f"  -> Skipped plane {i+1} due to error: {e}")
                continue
    
    if video_writer is not None:
        video_writer.release()
    print("Processing completed successfully!")


if __name__ == "__main__":
    if len(sys.argv) == 4:
        # Automatic execution via terminal arguments
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        # Smart interactive menu that scans directories automatically
        print("\n--- Interactive Mode (Auto-Scan) ---")
        
        # Find NRRD files in 'datasets' folder (and subdirectories)
        nrrd_files = glob.glob("datasets/**/*.nrrd", recursive=True)
        if not nrrd_files:
            nrrd_files = glob.glob("*.nrrd") # Fallback: search in current directory
            
        # Find CSV files
        csv_files = glob.glob("datasets/**/*.csv", recursive=True)
        if not csv_files:
            csv_files = glob.glob("*.csv")

        if not nrrd_files:
            print("Error: No NRRD files found in 'datasets' or current directory.")
            sys.exit(1)
        if not csv_files:
            print("Error: No CSV files found in 'datasets' or current directory.")
            sys.exit(1)

        # Display available NRRD files
        print("\nAvailable NRRD files:")
        for i, f in enumerate(nrrd_files, 1):
            print(f"[{i}] {f}")
        try:
            nrrd_choice = int(input("Select NRRD file number: ")) - 1
            if nrrd_choice < 0 or nrrd_choice >= len(nrrd_files):
                raise ValueError
            selected_nrrd = nrrd_files[nrrd_choice]
        except (ValueError, IndexError):
            print("Invalid choice. Exiting.")
            sys.exit(1)

        # Display available CSV files
        print("\nAvailable CSV files:")
        for i, f in enumerate(csv_files, 1):
            print(f"[{i}] {f}")
        try:
            csv_choice = int(input("Select CSV file number: ")) - 1
            if csv_choice < 0 or csv_choice >= len(csv_files):
                raise ValueError
            selected_csv = csv_files[csv_choice]
        except (ValueError, IndexError):
            print("Invalid choice. Exiting.")
            sys.exit(1)

        # Get output filename
        mp4_file = input("\nEnter output video filename (e.g., output.mp4) [Press Enter for default 'output.mp4']: ").strip()
        if not mp4_file:
            mp4_file = "output.mp4" # Default if empty
        elif not mp4_file.endswith(".mp4"):
            mp4_file += ".mp4"

        print(f"\nStarting processing... (Video will be saved as {mp4_file})")
        main(selected_nrrd, selected_csv, mp4_file)