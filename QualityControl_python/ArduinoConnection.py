""" This script establishes serial communication with an Arduino, listens for detection signals,
captures frames from a webcam, predicts block colors using a pre-trained CNN model"""

import serial
import time
from helper import predict_block_from_webcam

arduino = serial.Serial(port="COM3", baudrate=9600, timeout=1)

print("Listening for Arduino messages...")

while True:
    line = arduino.readline().decode("utf-8").strip()
    if line:
        print(f"Received: {line}")
        if line == "DETECTED":
            print("Object detected by Arduino!")
            try:
                time.sleep(1)  # brief pause to ensure stable frame capture
                label = predict_block_from_webcam()
                print(f"Predicted block color: {label}")
                arduino.write(f'{label}\n'.encode('utf-8'))
            except Exception as e:
                print(f"Error during prediction: {e}")
            time.sleep(3)  # optional delay
            arduino.write(f"{label}\n".encode('utf-8'))
