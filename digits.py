"""Train and use an SVM on scikit-learn's 8x8 handwritten digits."""
import argparse
import json
from pathlib import Path

import cv2
import joblib
import numpy as np
from sklearn.datasets import load_digits
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

MODEL_PATH = Path(__file__).with_name("model.joblib")
METRICS_PATH = Path(__file__).with_name("metrics.json")


def train(model_path=MODEL_PATH, metrics_path=METRICS_PATH):
    data = load_digits()
    x_train, x_test, y_train, y_test = train_test_split(
        data.data, data.target, test_size=0.2, random_state=42,
        stratify=data.target
    )
    # Add a version passed through the same image preparation used by the UI.
    prepared_train = np.array([prepare_image(cv2.resize(
        np.uint8(row.reshape(8, 8) / 16 * 255), (64, 64),
        interpolation=cv2.INTER_NEAREST)).ravel() for row in x_train])
    prepared_test = np.array([prepare_image(cv2.resize(
        np.uint8(row.reshape(8, 8) / 16 * 255), (64, 64),
        interpolation=cv2.INTER_NEAREST)).ravel() for row in x_test])
    model = make_pipeline(StandardScaler(), SVC(kernel="rbf", C=10, gamma="scale"))
    model.fit(np.vstack((x_train, prepared_train)), np.concatenate((y_train, y_train)))
    predictions = model.predict(x_test)
    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "prepared_image_accuracy": float(accuracy_score(y_test, model.predict(prepared_test))),
        "train_samples": int(len(x_train)),
        "test_samples": int(len(x_test)),
        "random_state": 42,
        "classification_report": classification_report(y_test, predictions, output_dict=True),
        "confusion_matrix": confusion_matrix(y_test, predictions).tolist(),
    }
    joblib.dump(model, model_path, compress=3)
    Path(metrics_path).write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return model, metrics


def prepare_image(image):
    """Convert a single white digit on a dark background to the 8x8 data format."""
    if image is None or image.size == 0:
        raise ValueError("Cannot read image")
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif image.ndim == 2:
        gray = image
    else:
        raise ValueError("Expected a grayscale or BGR image")
    if gray.dtype != np.uint8:
        raise ValueError("Expected an 8-bit image")
    # The training set has light strokes on a dark background.
    if np.median(gray) > 127:
        gray = 255 - gray
    _, mask = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)
    points = cv2.findNonZero(mask)
    if points is None:
        raise ValueError("No digit found in image")
    x, y, width, height = cv2.boundingRect(points)
    digit = gray[y:y + height, x:x + width]
    side = max(width, height)
    # Leave a small margin, as in the training images.
    margin = max(1, round(side * 0.12))
    canvas = np.zeros((side + 2 * margin, side + 2 * margin), np.uint8)
    x0, y0 = (canvas.shape[1] - width) // 2, (canvas.shape[0] - height) // 2
    canvas[y0:y0 + height, x0:x0 + width] = digit
    output = cv2.resize(canvas, (8, 8), interpolation=cv2.INTER_AREA)
    return output.astype(np.float64) / 255 * 16


def predict(image, model_path=MODEL_PATH):
    model = joblib.load(model_path)
    pixels = prepare_image(image)
    return int(model.predict(pixels.reshape(1, -1))[0]), pixels


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("train", help="Train and save model.joblib")
    predict_command = commands.add_parser("predict", help="Predict one digit image")
    predict_command.add_argument("image", type=Path)
    args = parser.parse_args()
    if args.command == "train":
        _, metrics = train()
        print(f"Test accuracy: {metrics['accuracy']:.4f} ({metrics['test_samples']} images)")
        print(f"Saved {MODEL_PATH.name} and {METRICS_PATH.name}")
    else:
        image = cv2.imdecode(np.fromfile(args.image, dtype=np.uint8), cv2.IMREAD_COLOR)
        number, _ = predict(image)
        print(number)


if __name__ == "__main__":
    main()
