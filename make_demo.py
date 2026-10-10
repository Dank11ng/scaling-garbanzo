"""Generate an original synthetic document photo with known ground truth."""
import json
from pathlib import Path
import cv2
import numpy as np
from scanner import write_image


def generate():
    paper = np.full((700, 500, 3), 245, np.uint8)
    cv2.putText(paper, "COMPUTER VISION", (35, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (25, 25, 25), 2)
    cv2.putText(paper, "Document Scanner Demo", (35, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (40, 40, 40), 1)
    for y in range(160, 430, 35):
        cv2.line(paper, (35, y), (450 - (y % 3) * 20, y), (70, 70, 70), 2)
    cv2.rectangle(paper, (35, 480), (220, 620), (60, 60, 60), 2)
    cv2.circle(paper, (340, 550), 65, (80, 80, 80), 2)
    source = np.float32([[0, 0], [499, 0], [499, 699], [0, 699]])
    corners = np.float32([[210, 110], [680, 180], [760, 850], [120, 790]])
    transform = cv2.getPerspectiveTransform(source, corners)
    background = np.full((960, 900, 3), (75, 65, 55), np.uint8)
    warped = cv2.warpPerspective(paper, transform, (900, 960))
    mask = cv2.warpPerspective(np.full((700, 500), 255, np.uint8), transform, (900, 960))
    background[mask > 0] = warped[mask > 0]
    return background, corners


if __name__ == "__main__":
    image, corners = generate()
    write_image("examples/document.jpg", image)
    Path("examples/corners.json").write_text(json.dumps(corners.tolist()), encoding="utf-8")
    print("Created examples/document.jpg")
