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

    def project_plane(self, p_a, p_b, p_c):
        # 1. המרת הנקודות למערכים
        a = np.array(p_a, dtype=float)
        b = np.array(p_b, dtype=float)
        c = np.array(p_c, dtype=float)

        Dab = np.linalg.norm(b - a)
        Dbc = np.linalg.norm(c - b)
        
        int_Dab = int(np.round(Dab))
        int_Dbc = int(np.round(Dbc))

        if int_Dab == 0 or int_Dbc == 0:
            return np.zeros((1, 1), dtype=np.uint8)

        v_ab = (b - a) / Dab
        v_ac = (c - a) / Dab

        # 2. יצירת רשת קואורדינטות (Grid) - מתמטיקה וקטורית במקום לולאות
        Y = np.arange(int_Dab).reshape(-1, 1)  # ציר הגובה (Dab)
        X = np.arange(int_Dbc).reshape(1, -1)  # ציר הרוחב (Dbc)

        # 3. חישוב a1 ו-a2 לכל שורות המשולש בבת אחת
        a1 = (a + Y * v_ab)[:, np.newaxis, :]  # עיצוב מחדש למימדים (Dab, 1, 3)
        a2 = (a + Y * v_ac)[:, np.newaxis, :]

        # 4. חישוב המרחקים והכיוון (dp) לכל השורות
        d12 = np.linalg.norm(a2 - a1, axis=2, keepdims=True)
        
        # מתעלמים זמנית מאזהרות חלוקה באפס ומציבים 0 במקום
        with np.errstate(divide='ignore', invalid='ignore'):
            dp = np.where(d12 > 0, (a2 - a1) / d12, 0)

        # 5. חישוב x1 וקבלת כל הנקודות התלת-ממדיות (P) במכה אחת
        x1 = X - (int_Dbc / 2) + (d12[..., 0] / 2)
        x1_3d = x1[..., np.newaxis]
        P = a1 + x1_3d * dp

        # 6. בדיקת גבולות - יצירת מסכה (Mask) של מה שבתוך המשולש ובתוך ה-MRI
        valid_triangle = (x1 >= 0) & (x1 <= d12[..., 0])
        
        P_idx = np.round(P).astype(int)
        Px, Py, Pz = P_idx[..., 0], P_idx[..., 1], P_idx[..., 2]
        
        max_x, max_y, max_z = self.volume.shape
        valid_bounds = (0 <= Px) & (Px < max_x) & (0 <= Py) & (Py < max_y) & (0 <= Pz) & (Pz < max_z)
        
        valid_mask = valid_triangle & valid_bounds

        # 7. יצירת המטריצה הדו-ממדית (התמונה) ושליפת הנתונים מה-NRRD
        E_T = np.zeros((int_Dab, int_Dbc), dtype=self.volume.matrix.dtype)
        
        # הקסם של Numpy: שליפת כל הפיקסלים התקינים בבת אחת
        E_T[valid_mask] = self.volume.matrix[Px[valid_mask], Py[valid_mask], Pz[valid_mask]]

        # מחזירים את המטריצה משוחלפת כדי להתאים לגודל (int_Dbc, int_Dab)
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
    print(f"Loading NRRD: {nrrd_file}")
    print(f"Reading CSV points: {csv_file}")
    
    # 1. טעינת הנתונים
    volume = VolumeData(nrrd_file)
    projector = PlaneProjector(volume)
    
    # 2. קריאת נקודות המישורים מה-CSV
    planes = parse_csv_planes(csv_file)
    
    if not planes:
        print("No planes found in CSV. Exiting.")
        return

    print(f"Found {len(planes)} planes to process.")
    print(f"Video output will be saved to: {mp4_file}")
    
    # 3. הכנת אובייקט כתיבת הוידאו (OpenCV)
    # נגדיר וידאו ברוחב וגובה שרירותיים כרגע, הם יתעדכנו לפי הפריים הראשון
    video_writer = None 
    fps = 30 # קצב פריימים לשנייה

    # 4. לולאה על כל מישור - יצירת היטל והוספה לוידאו
    for i, plane_points in enumerate(planes):
        if len(plane_points) >= 3:
            # לוקחים את 3 הנקודות הראשונות כדי להגדיר משולש
            a, b, c = plane_points[0], plane_points[1], plane_points[2]
            
            print(f"Processing plane {i+1}/{len(planes)}...")
            image_matrix = projector.project_plane(a, b, c)
            
            # אם זה הפריים הראשון, נאתחל את הוידאו לפי הגודל שלו
            if video_writer is None:
                height, width = image_matrix.shape
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                video_writer = cv2.VideoWriter(mp4_file, fourcc, fps, (width, height), isColor=False)
            
            # כתיבת הפריים (המטריצה הדו-ממדית) לתוך הוידאו
            video_writer.write(image_matrix)
    
    # סגירה ושמירה של הוידאו
    if video_writer is not None:
        video_writer.release()
    print("Processing completed successfully!")
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python Ex0.py <file.nrrd> <file.csv> <file.mp4>")
        sys.exit(1)
    
    main(sys.argv[1], sys.argv[2], sys.argv[3])