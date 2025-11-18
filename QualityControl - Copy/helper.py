""" This module captures frames from a webcam/IP camera, preprocesses them, and predicts labels using a pre-trained CNN model."""

import cv2
import numpy as np
from tensorflow.keras.models import load_model # type: ignore

# Load model once
model = load_model('block_AI.h5')
img_height, img_width = 64, 64
class_names = ["Green", "Red"]

def predict_block_from_webcam(url="http://192.168.1.13:8080/video"):
    """
    Captures one frame from the webcam/IP camera, crops, preprocesses,
    and returns the predicted label and confidence.
    """
    cap = cv2.VideoCapture(url)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise RuntimeError("Failed to capture frame from camera.")

    # --- Crop frame: vertical middle band + square around center ---
    h, w, _ = frame.shape
    crop_height = int(h * 0.7)  # 70% of vertical height
    y1 = h//2 - crop_height//2
    y2 = h//2 + crop_height//2
    cropped = frame[y1:y2, :]   # keep full width

    square_size = min(cropped.shape[0], w)
    x1 = w//2 - square_size//2
    x2 = w//2 + square_size//2
    cropped = cropped[:, x1:x2]

    # --- Convert BGR to RGB and preprocess ---
    img_for_model = cv2.rotate(cropped, cv2.ROTATE_90_CLOCKWISE)
    img_for_model = cv2.cvtColor(img_for_model, cv2.COLOR_BGR2RGB)
    img_for_model = cv2.resize(img_for_model, (img_width, img_height))
    img_for_model = img_for_model.astype("float32") / 255.0
    img_for_model = np.expand_dims(img_for_model, axis=0)

    # --- Prediction ---
    preds = model.predict(img_for_model, verbose=0)
    class_idx = np.argmax(preds)
    label = class_names[class_idx]

    return label
