import time
from Ex0 import VolumeData, PlaneProjector, parse_csv_planes

def run_experiment():
    print("--- Starting Performance Test (Section 8) ---")
    volume = VolumeData("datasets/rnnd/MRHead.nrrd")
    projector = PlaneProjector(volume)
    planes = parse_csv_planes("datasets/cvs/big_planes.csv")
    
    start_time = time.time()
    for plane_points in planes:
        if len(plane_points) >= 3:
            # מעבירים את כל הנקודות יחד לפונקציה המעודכנת
            projector.project_plane(plane_points)
    
    total_time = time.time() - start_time
    fps = len(planes) / total_time
    
    print(f"Total time: {total_time:.3f} seconds")
    print(f"Average FPS: {fps:.1f}")

if __name__ == "__main__":
    run_experiment()