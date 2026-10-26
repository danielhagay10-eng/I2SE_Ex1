import numpy as np
import cv2
from Ex0 import VolumeData, PlaneProjector

def test_perfect_oblique_circle():
    print("Loading MRI data...")
    volume = VolumeData("MRHead.nrrd")
    shape = volume.matrix.shape
    
    # מציאת המרכז המדויק
    cx, cy, cz = shape[0] // 2, shape[1] // 2, shape[2] // 2
    radius = 30
    
    print("Injecting 3D sphere into the center...")
    # התיקון: סדר הצירים x, y, z הותאם לגדלי המטריצה
    x, y, z = np.ogrid[0:shape[0], 0:shape[1], 0:shape[2]]
    distance = np.sqrt((x - cx)**2 + (y - cy)**2 + (z - cz)**2)
    volume.matrix[distance <= radius] = 3000  
    
    print("Projecting a 4-point full diagonal plane...")
    p_a1 = [0, 0, 0]
    p_a2 = [shape[0]-1, 0, shape[2]-1]
    p_b  = [0, shape[1]-1, 0]
    p_c  = [shape[0]-1, shape[1]-1, shape[2]-1]
    
    projector = PlaneProjector(volume)
    img_matrix = projector.project_plane([p_a1, p_a2, p_b, p_c])
    
    normalized_img = cv2.normalize(img_matrix, None, 0, 255, cv2.NORM_MINMAX)
    output_file = "circle_test_oblique.png"
    cv2.imwrite(output_file, normalized_img.astype(np.uint8))
    
    print(f"Test finished! Open '{output_file}' to view the correct result.")

if __name__ == "__main__":
    test_perfect_oblique_circle()