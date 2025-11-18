""" This script captures images from a webcam stream and saves them into specified directories based on user input."""

import cv2
import os

# Parameters
save_dir = "data_webcam"
classes = ["Red", "Green"]
img_height, img_width = 64, 64

for cls in classes:
    os.makedirs(os.path.join(save_dir, cls), exist_ok=True)

url = "http://192.168.1.13:8080/video"
cap = cv2.VideoCapture(url)

print("Press 'r' to capture Red, 'g' to capture Green, 'q' to quit.")
counters = {cls: 0 for cls in classes}

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Automatic cropping: vertical middle band
    h, w, _ = frame.shape
    crop_height = int(h * 0.7)  # crop 40% of height around vertical middle
    y1 = h//2 - crop_height//2
    y2 = h//2 + crop_height//2
    cropped = frame[y1:y2, :]   # keep full width

    # Optional: make square crop around center
    square_size = min(cropped.shape[0], w)
    x1 = w//2 - square_size//2
    x2 = w//2 + square_size//2
    cropped = cropped[:, x1:x2]
    
    # Resize to CNN input
    rotate = cv2.rotate(cropped, cv2.ROTATE_90_CLOCKWISE)
    img_to_save = cv2.resize(rotate, (img_width, img_height))

    # Show preview
    cv2.namedWindow("Capture Dataset", cv2.WINDOW_NORMAL)  # allows resizing
    cv2.resizeWindow("Capture Dataset", 320, 240)          # width x height


    cv2.imshow("Capture Dataset", rotate)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('r'):
        filename = os.path.join(save_dir, "Red", f"red_{counters['Red']:03d}.jpg")
        cv2.imwrite(filename, img_to_save)
        counters['Red'] += 1
        print(f"Saved {filename}")
    elif key == ord('g'):
        filename = os.path.join(save_dir, "Green", f"green_{counters['Green']:03d}.jpg")
        cv2.imwrite(filename, img_to_save)
        counters['Green'] += 1
        print(f"Saved {filename}")

cap.release()
cv2.destroyAllWindows()
