import unittest
import numpy as np
import os
import cv2
from Ex0 import VolumeData, PlaneProjector, parse_csv_planes, validate_plane_points, check_memory_limits

class TestEdgeCases(unittest.TestCase):
    def setUp(self):
        # טעינת הנתונים מהנתיב החדש בתוך תיקיית datasets/rnnd
        nrrd_path = os.path.join("datasets", "rnnd", "MRHead.nrrd")
        self.volume = VolumeData(nrrd_path)
        self.projector = PlaneProjector(self.volume)

    def test_out_of_bounds_projection(self):
        # טסט 1: חריגה מגבולות המוח
        p_a, p_b, p_c = [10000, 10000, 10000], [10100, 10000, 10000], [10000, 10100, 10000]
        result = self.projector.project_plane([p_a, p_b, p_c])
        self.assertTrue(np.all(result == 0), "Out of bounds should return zeros")

    def test_zero_distance_triangle(self):
        # טסט 2: משולש במרחק 0 (נקודות זהות)
        # המערכת אמורה לזרוק שגיאה מתמטית כי אי אפשר לבנות מישור
        p_a = p_b = p_c = [50, 50, 50]
        with self.assertRaises(ValueError):
            self.projector.project_plane([p_a, p_b, p_c])
        
    def test_four_points_trapezoid(self):
        # טסט 3: תמיכה ב-4 נקודות (טרפז)
        p_a1, p_a2 = [50, 50, 50], [70, 50, 50]
        p_b, p_c = [30, 100, 50], [90, 100, 50]
        result = self.projector.project_plane([p_a1, p_a2, p_b, p_c])
        self.assertGreater(result.size, 0, "4-point trapezoid failed")

    def test_invalid_csv_data(self):
        # טסט 4: קובץ זבל (Garbage CSV)
        bad_csv = "garbage_test.csv"
        with open(bad_csv, "w") as f:
            f.write("hello, world\n1, 2, 3\n")
        planes = parse_csv_planes(bad_csv)
        self.assertEqual(len(planes), 0, "Garbage CSV should return empty list")
        
        # ניקוי קובץ הזבל
        if os.path.exists(bad_csv):
            os.remove(bad_csv)

    def test_direct_match(self):
        # טסט 5: בדיקת התאמה מושלמת בין חיתוך האלגוריתם לחיתוך ישיר מהמטריצה
        z_val = 65
        p_a1 = [0, 0, z_val]
        p_a2 = [255, 0, z_val]
        p_b  = [0, 255, z_val]
        p_c  = [255, 255, z_val]
        
        # חיתוך דרך האלגוריתם הגיאומטרי
        projected_img = self.projector.project_plane([p_a1, p_a2, p_b, p_c])
        
        # התאמת גודל השליפה הישירה לממדי התמונה המחושבת (255x255) כדי לאפשר השוואה
        h, w = projected_img.shape
        direct_slice = self.volume.matrix[:h, :w, z_val]
        
        # חישוב השגיאה המקסימלית
        diff = np.abs(projected_img.astype(float) - direct_slice.astype(float))
        max_error = np.max(diff)
        
        # מוודא שהשגיאה קטנה מ-5 ערכי פיקסל (מתחשב בהחלקת אינטרפולציה)
        self.assertLess(max_error, 5.0, f"Direct Match failed: max deviation is {max_error}")

    def test_axes_phantom(self):
        # טסט 6: פנטום צירים גיאומטרי לבדיקת חיתוך אלכסוני
        shape = self.volume.shape
        cx, cy, cz = shape[0] // 2, shape[1] // 2, shape[2] // 2
        
        # גיבוי המטריצה המקורית כדי לא להרוס טסטים אחרים
        original_matrix = self.volume.matrix.copy()
        
        try:
            # איפוס המרחב לשחור וציור צלב צירים תלת-ממדי
            self.volume.matrix.fill(0)
            self.volume.matrix[:, cy, cz] = 3000  # ציר X
            self.volume.matrix[cx, :, cz] = 3000  # ציר Y
            self.volume.matrix[cx, cy, :] = 3000  # ציר Z
            
            # חיתוך אלכסוני במרכז
            p_a1 = [0, 0, cz - 40]
            p_a2 = [shape[0]-1, 0, cz]
            p_b  = [0, shape[1]-1, cz + 40]
            
            # נעביר רק 3 נקודות כדי להבטיח מתמטית מישור מושלם שלא ייזרק על ידי הוולידציה
            img_matrix = self.projector.project_plane([p_a1, p_a2, p_b])
            
            # וידוא שהתמונה נוצרה בהצלחה ואינה ריקה
            self.assertIsNotNone(img_matrix)
            self.assertGreater(img_matrix.size, 0)
            
            # שמירת התמונה לבדיקה ויזואלית
            normalized_img = cv2.normalize(img_matrix, None, 0, 255, cv2.NORM_MINMAX)
            output_file = "phantom_axes_oblique.png"
            cv2.imwrite(output_file, normalized_img.astype(np.uint8))
            self.assertTrue(os.path.exists(output_file), "Phantom image was not saved")
            
        finally:
            # שחזור המטריצה המקורית
            self.volume.matrix = original_matrix

    def test_collinear_points(self):
        # טסט 7: 3 נקודות על קו ישר אחד
        points = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]])
        with self.assertRaises(ValueError):
            validate_plane_points(points)

    def test_non_planar_points(self):
        # טסט 8: 4 נקודות כאשר הרביעית קופצת החוצה מהמישור
        points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 5]])
        with self.assertRaises(ValueError):
            validate_plane_points(points)

    def test_missing_points(self):
        # טסט 9: רק 2 נקודות (חסר מידע להרכבת מישור)
        points = np.array([[0, 0, 0], [1, 1, 1]])
        with self.assertRaises(ValueError):
            validate_plane_points(points)

    def test_memory_overflow(self):
        # טסט 10: ניסיון לייצר רשת ענקית של 100,000 על 100,000 פיקסלים
        with self.assertRaises(MemoryError):
            check_memory_limits(100000, 100000)

if __name__ == '__main__':
    unittest.main()