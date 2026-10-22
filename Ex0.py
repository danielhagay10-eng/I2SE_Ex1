import sys
import numpy as np
import csv
import nrrd
import cv2

class VolumeData:
    def __init__(self, filepath):
        self.filepath = filepath
        # טעינת המטריצה התלת-ממדית מהקובץ!
        self.matrix, self.header = nrrd.read(self.filepath)
        self.shape = self.matrix.shape
        print(f"Loaded volume with shape: {self.shape}")
class PlaneProjector:
    def __init__(self, volume_data):
        self.volume = volume_data

    def project_plane(self, points):
        points = np.array(points, dtype=float)
        
        # זיהוי 3 נקודות (משולש) או 4 נקודות (טרפז)
        if len(points) == 3:
            a1_start, a2_start, b, c = points[0], points[0], points[1], points[2]
        elif len(points) == 4:
            a1_start, a2_start, b, c = points[0], points[1], points[2], points[3]
        else:
            return np.zeros((1, 1), dtype=np.uint8)

        Dab = np.linalg.norm(b - a1_start)
        Dbc = np.linalg.norm(c - b)
        
        int_Dab = int(np.round(Dab))
        int_Dbc = int(np.round(Dbc))

        if int_Dab == 0 or int_Dbc == 0:
            return np.zeros((1, 1), dtype=np.uint8)

        v_ab = (b - a1_start) / Dab
        v_ac = (c - a2_start) / Dab

        Y = np.arange(int_Dab).reshape(-1, 1)
        X = np.arange(int_Dbc).reshape(1, -1)

        a1 = (a1_start + Y * v_ab)[:, np.newaxis, :]
        a2 = (a2_start + Y * v_ac)[:, np.newaxis, :]

        d12 = np.linalg.norm(a2 - a1, axis=2, keepdims=True)
        
        with np.errstate(divide='ignore', invalid='ignore'):
            dp = np.where(d12 > 0, (a2 - a1) / d12, 0)

        x1 = X - (int_Dbc / 2) + (d12[..., 0] / 2)
        x1_3d = x1[..., np.newaxis]
        P = a1 + x1_3d * dp

        valid_triangle = (x1 >= 0) & (x1 <= d12[..., 0])
        
        P_idx = np.round(P).astype(int)
        Px, Py, Pz = P_idx[..., 0], P_idx[..., 1], P_idx[..., 2]
        
        max_x, max_y, max_z = self.volume.shape
        valid_bounds = (0 <= Px) & (Px < max_x) & (0 <= Py) & (Py < max_y) & (0 <= Pz) & (Pz < max_z)
        
        valid_mask = valid_triangle & valid_bounds

        E_T = np.zeros((int_Dab, int_Dbc), dtype=self.volume.matrix.dtype)
        E_T[valid_mask] = self.volume.matrix[Px[valid_mask], Py[valid_mask], Pz[valid_mask]]

        return E_T.T
   
def parse_csv_planes(csv_filepath):
    planes = []
    try:
        with open(csv_filepath, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                coords = [float(val) for val in row if val.strip()]
                points = [coords[i:i+3] for i in range(0, len(coords), 3)]
                if len(points) >= 3:
                    planes.append(points)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        
    return planes
        
def main(nrrd_file, csv_file, mp4_file):
    # הדפסת שמות הקבצים שהתקבלו מהטרמינל
    print(f"Loading NRRD: {nrrd_file}")
    print(f"Reading CSV points: {csv_file}")
    
    # 1. טעינת קובץ התלת-ממד (ה-MRI) ואתחול מחלקת החישוב
    volume = VolumeData(nrrd_file)
    projector = PlaneProjector(volume)
    
    # 2. קריאת קואורדינטות המישורים מתוך קובץ ה-CSV
    planes = parse_csv_planes(csv_file)
    
    # בדיקה האם נמצאו מישורים, אם לא - התוכנית עוצרת בבטחה
    if not planes:
        print("No planes found in CSV. Exiting.")
        return

    print(f"Found {len(planes)} planes to process.")
    print(f"Video output will be saved to: {mp4_file}")
    
    # 3. הכנת משתנים ליצירת הווידאו
    video_writer = None 
    fps = 30 # קצב פריימים לשנייה (30 תמונות בשנייה)

    # 4. לולאה שעוברת על כל מישור (שורה) שנקרא מקובץ ה-CSV
    for i, plane_points in enumerate(planes):
        # מוודאים שיש לפחות 3 נקודות תקינות (משולש או טרפז)
        if len(plane_points) >= 3:
            print(f"Processing plane {i+1}/{len(planes)} (Points: {len(plane_points)})...")
            
            # הפעלת האלגוריתם שמחשב ומייצר את התמונה הדו-ממדית
            image_matrix = projector.project_plane(plane_points)
            
            # אם זו התמונה הראשונה, אנחנו פותחים ומגדירים את גודל הווידאו לפיה
            if video_writer is None:
                height, width = image_matrix.shape
                fourcc = cv2.VideoWriter_fourcc(*'mp4v') # קידוד לפורמט MP4
                video_writer = cv2.VideoWriter(mp4_file, fourcc, fps, (width, height), isColor=False)
            
            # כתיבת התמונה הנוכחית (הפריים) לתוך קובץ הווידאו
            video_writer.write(image_matrix)
    
    # 5. סגירה ושמירה סופית של קובץ הווידאו לאחר סיום הלולאה
    if video_writer is not None:
        video_writer.release()
    print("Processing completed successfully!")

# נקודת הכניסה של התוכנית - קריאת הארגומנטים מהטרמינל
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python Ex0.py <file.nrrd> <file.csv> <file.mp4>")
        sys.exit(1)
    
    main(sys.argv[1], sys.argv[2], sys.argv[3])