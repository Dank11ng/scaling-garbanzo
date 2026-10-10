"""Small drawing pad for trying the saved digit classifier."""
import tkinter as tk

import cv2
import numpy as np

from digits import predict

SIZE = 280


class DigitApp:
    def __init__(self, root):
        root.title("Handwritten digit recognition")
        self.canvas = tk.Canvas(root, width=SIZE, height=SIZE, bg="black", cursor="cross")
        self.canvas.pack(padx=12, pady=12)
        self.image = np.zeros((SIZE, SIZE), np.uint8)
        self.last = None
        self.canvas.bind("<Button-1>", self.start)
        self.canvas.bind("<B1-Motion>", self.move)
        self.canvas.bind("<ButtonRelease-1>", lambda event: setattr(self, "last", None))
        self.result = tk.StringVar(value="Draw one digit, then click Recognize")
        tk.Label(root, textvariable=self.result, font=("Arial", 14)).pack(pady=8)
        tk.Button(root, text="Recognize", command=self.recognize).pack(fill="x", padx=12)
        tk.Button(root, text="Clear", command=self.clear).pack(fill="x", padx=12, pady=8)

    def start(self, event):
        self.last = (event.x, event.y)
        self.move(event)

    def move(self, event):
        current = (max(0, min(SIZE - 1, event.x)), max(0, min(SIZE - 1, event.y)))
        if self.last is not None:
            self.canvas.create_line(*self.last, *current, fill="white", width=22,
                                    capstyle=tk.ROUND, smooth=True)
            cv2.line(self.image, self.last, current, 255, 22, cv2.LINE_AA)
        self.last = current

    def recognize(self):
        try:
            number, _ = predict(self.image)
            self.result.set(f"Prediction: {number}")
        except (ValueError, OSError) as error:
            self.result.set(str(error))

    def clear(self):
        self.canvas.delete("all")
        self.image.fill(0)
        self.last = None
        self.result.set("Draw one digit, then click Recognize")


if __name__ == "__main__":
    DigitApp(tk.Tk())
    tk.mainloop()
