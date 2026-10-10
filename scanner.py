"""Classical computer vision document scanner; no trained model required."""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np


def order_corners(points):
    """Return convex quadrilateral corners in TL, TR, BR, BL order."""
    points = np.asarray(points, dtype=np.float32).reshape(4, 2)
    if not np.isfinite(points).all():
        raise ValueError("Corners must be finite")
    hull = cv2.convexHull(points).reshape(-1, 2)
    if len(hull) != 4 or cv2.contourArea(hull) < 1:
        raise ValueError("Four distinct convex corners are required")
    # Angle ordering avoids duplicate assignments on diamond-shaped documents.
    angles = np.arctan2(points[:, 1] - points[:, 1].mean(),
                        points[:, 0] - points[:, 0].mean())
    ordered = points[np.argsort(angles)]
    return np.roll(ordered, -np.argmin(ordered.sum(axis=1)), axis=0)


def detect_document(image, min_area_ratio=0.15):
    if image is None or image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("Expected a BGR color image")
    scale = min(1.0, 1000 / max(image.shape[:2]))
    small = cv2.resize(image, None, fx=scale, fy=scale)
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    area = small.shape[0] * small.shape[1]
    for contour in sorted(contours, key=cv2.contourArea, reverse=True):
        if cv2.contourArea(contour) < min_area_ratio * area:
            break
        polygon = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
        if len(polygon) == 4 and cv2.isContourConvex(polygon):
            return order_corners(polygon / scale), edges
    raise ValueError("No document found. Use a contrasting background or --corners.")


def rectify(image, corners):
    tl, tr, br, bl = order_corners(corners)
    width = round(max(np.linalg.norm(tr - tl), np.linalg.norm(br - bl)))
    height = round(max(np.linalg.norm(bl - tl), np.linalg.norm(br - tr)))
    if min(width, height) < 16:
        raise ValueError("Document is too small")
    if max(width, height) > 10000:
        raise ValueError("Document exceeds 10000 pixel limit")
    target = np.float32([[0, 0], [width - 1, 0],
                         [width - 1, height - 1], [0, height - 1]])
    matrix = cv2.getPerspectiveTransform(np.float32([tl, tr, br, bl]), target)
    return cv2.warpPerspective(image, matrix, (width, height))


def enhance(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 21, 10)


def read_image(path):
    # imdecode supports Chinese paths on Windows.
    image = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Cannot decode image: {path}")
    return image


def write_image(path, image):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ok, encoded = cv2.imencode(path.suffix, image)
    if not ok:
        raise ValueError(f"Cannot encode image: {path}")
    encoded.tofile(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    parser.add_argument("--corners", type=float, nargs=8, metavar="XY",
                        help="Four corner coordinates x1 y1 ... x4 y4")
    args = parser.parse_args()
    try:
        image = read_image(args.image)
        if args.corners:
            corners = order_corners(args.corners)
            edges = None
        else:
            corners, edges = detect_document(image)
        h, w = image.shape[:2]
        if (corners < 0).any() or (corners[:, 0] >= w).any() or (corners[:, 1] >= h).any():
            raise ValueError("Corners must lie inside the image")
        warped = rectify(image, corners)
        overlay = image.copy()
        cv2.polylines(overlay, [corners.astype(np.int32)], True, (0, 200, 0), 3)
        for name, result in [("detected.jpg", overlay), ("rectified.jpg", warped),
                             ("scan.png", enhance(warped)), ("edges.png", edges)]:
            if result is not None:
                write_image(args.output / name, result)
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "metadata.json").write_text(json.dumps({
            "corners": corners.tolist(), "width": warped.shape[1],
            "height": warped.shape[0], "mode": "manual" if args.corners else "automatic"
        }, indent=2), encoding="utf-8")
        print(f"Saved scan to {args.output.resolve()}")
    except (ValueError, OSError, cv2.error) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
