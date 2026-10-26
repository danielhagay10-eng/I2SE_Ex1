import csv

def generate_400_csv(filename="planes_400.csv"):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        # שורת הכותרת הנדרשת
        writer.writerow(["Number of Points", "x1", "y1", "z1", "x2", "y2", "z2", "x3", "y3", "z3", "x4", "y4", "z4"])
        
        for i in range(400):
            # חצי מהשורות עם 4 נקודות וחצי עם 3
            num_points = 4 if i % 2 == 0 else 3
            
            # יצירת גיוון בגבהים ובשיפועים
            z_start = i % 100
            z_offset = (i % 20)  
            
            row = [num_points]
            
            # נקודה 1: פינה שמאלית עליונה
            row.extend([0, 0, z_start])
            # נקודה 2: פינה ימנית עליונה
            row.extend([255, 0, z_start])
            # נקודה 3: פינה שמאלית תחתונה (עם שיפוע אפשרי)
            row.extend([0, 255, z_start + z_offset])
            
            if num_points == 4:
                # נקודה 4: פינה ימנית תחתונה
                row.extend([255, 255, z_start + z_offset])
                
            writer.writerow(row)
            
    print(f"Successfully generated {filename} with 400 planes.")

if __name__ == "__main__":
    generate_400_csv()