import sys
import numpy as np
import csv
import nrrd

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
        # 1.  numpy המרת הנקודות למערכים מתמטיים של 
        a = np.array(p_a, dtype=float)
        b = np.array(p_b, dtype=float)
        c = np.array(p_c, dtype=float)

        # 2. חישוב הווקטורים והמרחקים
        Dab = np.linalg.norm(b - a)
        Dbc = np.linalg.norm(c - b)

        # הפיכת המרחקים למספרים שלמים (כדי שנוכל להשתמש בהם בלולאות ובגודל המטריצה)
        int_Dab = int(np.round(Dab))
        int_Dbc = int(np.round(Dbc))

        # 3. יצירת וקטורים מנורמלים (וקטור התקדמות של פיקסל 1)
        v_ab = (b - a) / Dab
        v_ac = (c - a) / Dab

        # 4. דו מימדית  ריקה שתהיה התמונה שלנו E יצירת מטריצה  
        E = np.zeros((int_Dbc, int_Dab), dtype=np.uint8)

        # 5.a לולאות הסריקה - מתחילים מנקודה 
        a1 = np.copy(a)
        a2 = np.copy(a)

        for y in range(int_Dab):
            # צועדים צעד אחד על השוקיים של המשולש
            a1 = a1 + v_ab
            a2 = a2 + v_ac
            
            p = np.copy(a1)
            d12 = np.linalg.norm(a2 - a1)
            int_d12 = int(np.round(d12))
            
            #  חישוב וקטור ההתקדמות האופקי על השורה 
            # from a1 to a2
            if int_d12 > 0:
                dp = (a2 - a1) / d12
            else:
                dp = np.zeros(3)

            for x1 in range(int_d12 + 1):
                # שליפת הצבע/ערך מהמטריצה התלת-ממדית
                v_val = self.get_voxel_value(p) 
                
                # במטריצה הדו ממדית כדי שהתמונה תהיה ממורכזת  Xחישוב מיקום ה 
                x = int((int_Dbc / 2) - (int_d12 / 2) + x1)
                
                # הצבת הערך בתוך התמונה (מוודאים שאנחנו לא חורגים מהגבולות)
                if 0 <= x < int_Dbc:
                    E[x, y] = v_val
                
                # מתקדמים לנקודה הבאה על השורה
                p = p + dp

        return E

    def get_voxel_value(self, p):
        # הפיכת הקואורדינטות למספרים שלמים כדי לגשת למטריצה
        x, y, z = int(np.round(p[0])), int(np.round(p[1])), int(np.round(p[2]))
        
        # וידוא שאנחנו לא חורגים מגבולות המוח/תמונה
        max_x, max_y, max_z = self.volume.shape
        if 0 <= x < max_x and 0 <= y < max_y and 0 <= z < max_z:
            return self.volume.matrix[x, y, z]
        else:
            return 0  # אם חרגנו מהגבולות נחזיר שחור (0)5

   
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