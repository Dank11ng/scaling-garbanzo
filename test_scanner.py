import itertools
import unittest
import numpy as np
from make_demo import generate
from scanner import detect_document, order_corners, rectify, enhance


class ScannerTests(unittest.TestCase):
    def test_detection_matches_ground_truth(self):
        image, expected = generate()
        actual, _ = detect_document(image)
        self.assertLess(np.linalg.norm(actual - expected, axis=1).max(), 10)
        scan = enhance(rectify(image, actual))
        self.assertGreater(scan.shape[0], scan.shape[1])
        self.assertEqual(set(np.unique(scan)), {0, 255})

    def test_corner_permutations(self):
        _, expected = generate()
        for permutation in itertools.permutations(expected):
            np.testing.assert_array_equal(order_corners(permutation), expected)

    def test_empty_scene_fails(self):
        with self.assertRaises(ValueError):
            detect_document(np.zeros((200, 300, 3), np.uint8))

    def test_degenerate_corners_fail(self):
        with self.assertRaises(ValueError):
            order_corners(np.zeros((4, 2)))


if __name__ == "__main__":
    unittest.main()
