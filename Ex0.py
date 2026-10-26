import sys
import os
import glob
import csv
import numpy as np
import cv2
import nrrd
import scipy.ndimage

class VolumeData:
    def __init__(self, filepath):
        self.filepath = filepath
        # טעינת המטריצה התלת-ממדית (MRI) מקובץ ה-NRRD
        self.matrix, self.header = nrrd.read(self.filepath)
        self.shape = self.matrix.shape
        print(f"Loaded volume with shape: {self.shape}")

class PlaneProjector:
    def __init__(self, volume_data):
        self.volume = volume_data

    def project_plane(self, points):
        points = np.array(points, dtype=float)
        
        # זיהוי אם התקבלו 3 נקודות (משולש) או 4 נקודות (טרפז)
        if len(points) == 3:
            a1_start, a2_start, b, c = points[0], points[0], points[1], points[2]
        elif len(points) == 4:
            a1_start, a2_start, b, c = points[0], points[1], points[2], points[3]
        else:
            return np.zeros((1, 1), dtype=np.uint8)

        # חישוב המרחקים על בסיס הנקודות שהתקבלו
        Dab = np.linalg.norm(b - a1_start)
        Dbc = np.linalg.norm(c - b)
        
        # עיגול המרחקים למספרים שלמים כדי שישמשו כממדי התמונה הדו-ממדית
        int_Dab = int(np.round(Dab))
        int_Dbc = int(np.round(Dbc))

        # מניעת קריסה אם המרחק הוא 0
        if int_Dab == 0 or int_Dbc == 0:
            return np.zeros((1, 1), dtype=np.uint8)

        # יצירת וקטורים מנורמלים שקובעים את כיוון ההתקדמות במרחב
        v_ab = (b - a1_start) / Dab
        v_ac = (c - a2_start) / Dab

        # יצירת רשת הקואורדינטות הדו-ממדית (Grid) כדי לחשב הכל במכה אחת בלי לולאות
        Y = np.arange(int_Dab).reshape(-1, 1)
        X = np.arange(int_Dbc).reshape(1, -1)

        # חישוב וקטורי ההתחלה והסיום (a1, a2) לכל שורה בחיתוך
        a1 = (a1_start + Y * v_ab)[:, np.newaxis, :]
        a2 = (a2_start + Y * v_ac)[:, np.newaxis, :]

        # חישוב המרחק האופקי בכל שורה
        d12 = np.linalg.norm(a2 - a1, axis=2, keepdims=True)
        
        # חישוב וקטור ההתקדמות האופקי (dp), תוך התעלמות מאזהרות חלוקה באפס
        with np.errstate(divide='ignore', invalid='ignore'):
            dp = np.where(d12 > 0, (a2 - a1) / d12, 0)

        # מציאת הקואורדינטות התלת-ממדיות (P) המדויקות עבור כל פיקסל בתמונה המבוקשת
        x1 = X - (int_Dbc / 2) + (d12[..., 0] / 2)
        x1_3d = x1[..., np.newaxis]
        P = a1 + x1_3d * dp

        # שינוי סדר הצירים כדי להתאים לפונקציית ההחלקה של Scipy
        coords = P.transpose(2, 0, 1)
        
        # דגימה חלקה (אינטרפולציה תלת-ליניארית) של הצבע מתוך ה-MRI. 
        sampled_values = scipy.ndimage.map_coordinates(
            self.volume.matrix, coords, order=1, mode='constant', cval=0.0
        )

        # יצירת מסכה שמאפסת (צובעת בשחור) אזורים שנמצאים מחוץ לצורת המשולש/טרפז
        valid_triangle = (x1 >= 0) & (x1 <= d12[..., 0])
        sampled_values[~valid_triangle] = 0
        
        # המרת הנתונים לפורמט המתאים לתמונה ושחלוף (Transpose) לכיוון הנכון
        E_T = sampled_values.astype(self.volume.matrix.dtype)
        return E_T.T
   
def parse_csv_planes(csv_filepath):
    """
    קוראת את קובץ ה-CSV על פי הפורמט הנדרש (כולל עמודת מספר הנקודות).
    """
    planes = []
    try:
        with open(csv_filepath, 'r') as f:
            reader = csv.reader(f)
            
            # דילוג על שורת הכותרת (Header)
            next(reader, None)
            
            for row in reader:
                if not row or not row[0].strip():
                    continue
                    
                num_points = int(row[0].strip())
                points = []
                
                # קריאת 3 הנקודות הראשונות
                points.append([float(row[1]), float(row[2]), float(row[3])])
                points.append([float(row[4]), float(row[5]), float(row[6])])
                points.append([float(row[7]), float(row[8]), float(row[9])])
                
                # קריאת הנקודה הרביעית במידה והוגדרה
                if num_points == 4:
                    points.append([float(row[10]), float(row[11]), float(row[12])])
                
                planes.append(points)
                
    except Exception as e:
        print(f"Error reading CSV: {e}")
        
    return planes
        
def main(nrrd_file, csv_file, mp4_file):
    print(f"Loading NRRD: {nrrd_file}")
    print(f"Reading CSV points: {csv_file}")
    
    # טעינת קובץ התלת-ממד ואתחול מחלקת החישוב
    volume = VolumeData(nrrd_file)
    projector = PlaneProjector(volume)
    
    # קריאת קואורדינטות המישורים מתוך ה-CSV
    planes = parse_csv_planes(csv_file)
    
    if not planes:
        print("No planes found in CSV. Exiting.")
        return

    print(f"Found {len(planes)} planes to process.")
    print(f"Video output will be saved to: {mp4_file}")
    
    video_writer = None 
    fps = 30 
    
    # לולאה שעוברת על כל מישור
    for i, plane_points in enumerate(planes):
        if len(plane_points) >= 3:
            print(f"Processing plane {i+1}/{len(planes)} (Points: {len(plane_points)})...")
            
            image_matrix = projector.project_plane(plane_points)
            
            # נרמול התמונה מ-16-ביט לטווח של 0-255 והמרה ל-uint8
            normalized_img = cv2.normalize(image_matrix, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
            image_matrix_8u = normalized_img.astype(np.uint8)
            
            if video_writer is None:
                height, width = image_matrix_8u.shape
                fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
                video_writer = cv2.VideoWriter(mp4_file, fourcc, fps, (width, height), isColor=False)
            
            video_writer.write(image_matrix_8u)
    
    if video_writer is not None:
        video_writer.release()
    print("Processing completed successfully!")

if __name__ == "__main__":
    if len(sys.argv) == 4:
        # הרצה אוטומטית דרך הטרמינל (עבור הטסטים והמרצה)
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        # תפריט אינטראקטיבי לפי מבנה התיקיות החדש
        nrrd_dir = os.path.join("datasets", "rnnd")
        csv_dir = os.path.join("datasets", "cvs")
        
        if not os.path.exists(nrrd_dir) or not os.path.exists(csv_dir):
            print(f"Error: Make sure '{nrrd_dir}' and '{csv_dir}' folders exist.")
            sys.exit(1)

        # שלב 1: בחירת קובץ דימות
        nrrd_files = glob.glob(os.path.join(nrrd_dir, "*.nrrd"))
        if not nrrd_files:
            print(f"No .nrrd files found in {nrrd_dir}.")
            sys.exit(1)
            
        print("\n--- Choose an MRI file ---")
        for i, f in enumerate(nrrd_files):
            print(f"{i+1}. {os.path.basename(f)}")
        try:
            nrrd_choice = int(input("Enter number: ")) - 1
            nrrd_file = nrrd_files[nrrd_choice]
        except (ValueError, IndexError):
            print("Invalid selection.")
            sys.exit(1)
        
        # שלב 2: בחירת קובץ נקודות
        csv_files = glob.glob(os.path.join(csv_dir, "*.csv"))
        if not csv_files:
            print(f"No .csv files found in {csv_dir}.")
            sys.exit(1)
            
        print("\n--- Choose a CSV file ---")
        for i, f in enumerate(csv_files):
            print(f"{i+1}. {os.path.basename(f)}")
        try:
            csv_choice = int(input("Enter number: ")) - 1
            csv_file = csv_files[csv_choice]
        except (ValueError, IndexError):
            print("Invalid selection.")
            sys.exit(1)
        
        # שלב 3: הגדרת שם קובץ פלט
        nrrd_name = os.path.splitext(os.path.basename(nrrd_file))[0]
        csv_name = os.path.splitext(os.path.basename(csv_file))[0]
        output_file = f"output_{nrrd_name}_{csv_name}.mp4"
        
        print(f"\nRunning with:\nMRI: {nrrd_file}\nCSV: {csv_file}\nOutput: {output_file}\n")
        
        # קריאה לפונקציה הראשית
        main(nrrd_file, csv_file, output_file)