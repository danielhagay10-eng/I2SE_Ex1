import unittest
import numpy as np
import os
from Ex0 import VolumeData, PlaneProjector, parse_csv_planes

class TestEdgeCases(unittest.TestCase):
    def setUp(self):
        # טעינת הנתונים פעם אחת לפני כל הטסטים
        self.volume = VolumeData("MRHead.nrrd")
        self.projector = PlaneProjector(self.volume)

    def test_out_of_bounds_projection(self):
        # טסט 1: חריגה מגבולות המוח
        p_a, p_b, p_c = [10000, 10000, 10000], [10100, 10000, 10000], [10000, 10100, 10000]
        result = self.projector.project_plane([p_a, p_b, p_c])
        self.assertTrue(np.all(result == 0), "Out of bounds should return zeros")

    def test_zero_distance_triangle(self):
        # טסט 2: משולש במרחק 0 (נקודות זהות - מניעת קריסה)
        p_a = p_b = p_c = [50, 50, 50]
        result = self.projector.project_plane([p_a, p_b, p_c])
        self.assertEqual(result.shape, (1, 1), "Zero distance should return 1x1 matrix")
        self.assertEqual(result[0, 0], 0)
        
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

if __name__ == '__main__':
    unittest.main()