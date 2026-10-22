import sys
import numpy as np

class VolumeData:
    def __init__(self, filepath):
        self.filepath = filepath
        # בהמשך נטען כאן את הנתונים

class PlaneProjector:
    def __init__(self, volume_data):
        self.volume = volume_data

    def project_plane(self, p1, p2, p3):
        # כאן נממש את המתמטיקה של המישור
        pass

def main(nrrd_file, csv_file, mp4_file):
    print(f"Loading NRRD: {nrrd_file}")
    print(f"Reading CSV points: {csv_file}")
    print(f"Video output will be saved to: {mp4_file}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python Ex0.py <file.nrrd> <file.csv> <file.mp4>")
        sys.exit(1)
    
    main(sys.argv[1], sys.argv[2], sys.argv[3])