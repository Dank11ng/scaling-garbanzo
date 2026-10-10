import tempfile
import unittest
from pathlib import Path

import numpy as np
from sklearn.datasets import load_digits

from digits import prepare_image, train


class DigitTests(unittest.TestCase):
    def test_training_and_reload(self):
        with tempfile.TemporaryDirectory() as directory:
            model_path = Path(directory) / "model.joblib"
            model, metrics = train(model_path, Path(directory) / "metrics.json")
            self.assertTrue(model_path.exists())
            self.assertGreater(metrics["accuracy"], 0.95)
            self.assertGreater(metrics["prepared_image_accuracy"], 0.95)
            self.assertEqual(metrics["test_samples"], 360)
            sample = load_digits()
            self.assertEqual(model.predict(sample.data[:1])[0], sample.target[0])

    def test_empty_image_rejected(self):
        with self.assertRaises(ValueError):
            prepare_image(np.zeros((28, 28), np.uint8))


if __name__ == "__main__":
    unittest.main()
