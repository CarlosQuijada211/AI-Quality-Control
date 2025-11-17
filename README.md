# AI Quality Control
## Project Overview
This project is a simulation of a quality-control system that uses AI to distinguish between two different objects (a red cube and a green cube) and sort them accordingly. It was built with an Arduino Mega and an AI model trained using the TensorFlow library.
The setup works as follows: a dispenser releases a cube onto a conveyor belt, which carries it forward until it reaches an ultrasonic sensor. When the cube is in position, a camera captures an image, and the trained AI model classifies the object. The classification result is then sent back to the Arduino, which moves a divided container at the end of the conveyor belt so the cube is sorted into the correct section.
The aim of the project was to apply newly learned AI concepts to a practical system that mirrors real-world industrial processes. Although the build is small and made of cardboard, it serves as a proof of concept for how similar systems can tackle real-world challenges. Through this project, I strengthened my skills in AI( such as image classification, dataset creation, and model visualization) as well as in robotics and mechanical design.
### Demo
TODO
### Features
- Real-time object classification using a TensorFlow-trained model.
- Automated dispensing mechanism that reliably releases a single cube at a time
- Conveyor-belt transport system driven by stepper motors and synchronized with the classifier
- Ultrasonic sensor-based positioning, ensuring the cube is photographed at the correct moment
- Integrated camera capture pipeline, converting live images into inputs for the AI model.
- Serial communication between Arduino and AI model, enabling two-way decision flow. 
- Low-cost build using cardboard
- Custom dataset creation for training the red vs green classifier. 

## Technical Details
### Mechanical Design

**Cube Dispensing Mechanism** \
The dispenser is inspired by the mechanism commonly used in gumball machines. It consists of a rotating circular disk with a single circular cavity on one side. An inclined vertical tower holds the cubes above the disk, allowing gravity to feed one cube into the cavity when it aligns with the opening at the base of the tower.
When the disk rotates, the cavity carries the cube forward until it reaches an opening positions above the conveyor belt. At that point, the cube drops onto the belt. The disk then rotates back to its original position, where a new cube falls into the cavity ready for the next cycle. The disk’s rotation is controlled by a SG90 Servo Motor. 
This design ensures consistent single-cube dispensing and prevents multiple cubes from being released at once. 

**Conveyor Belt** \
The conveyor belt is constructed from cardboard and designed with small protruding “teeth” along its surface. These teeth allow the belt to engage with the rollers and move reliably without slipping. The system uses two rollers; one positioned at each end of the belt. The first roller rotates freely and provides tension, while the second roller is driven by a NEMA 17 stepper motor. 
Both rollers are also made from cardboard and include matching teeth that interlock with the belt, functioning like a simple gear system. As the stepper motor turns the driven roller, the interlocking teeth pull the belt forward, transporting the cube smoothly toward the sensing and classification area. 

**Sorting Container** \
The sorting container consists of a circular tray divided into two equal compartments. A stepper motor is attached to the base of the tray, allowing it to rotate precisely between the two positions. As each cube reaches the end of the conveyor belt, the system checks the classification result provided by the AI model. Based on this result, the program tracks which compartment should receive the cube and rotates the tray accordingly. Once aligned, the cube falls into the correct section of the container. After each sorting action, the tray remains in its new position until the next rotation is required.

## Electronic System
### Electrical System Overview
The electronic system can be divided into the same three sections as the mechanical system: the cube dispenser, the conveyor belt, and the sorting container.
The cube dispenser is controlled by an SG90 servo motor powered separately through a dedicated 5V supply connected via a barrel jack. This motor rotates the dispensing disk to release a cube.
The conveyor belt is driven by a NEMA 17 stepper motor controlled by a DRV8825 driver set to ¼ microstepping. It is powered by a 12V external supply connected through a barrel jack. An ultrasonic sensor is positioned along the belt to detect when a cube reaches the classification point.
Finally, a second NEMA 17 stepper motor—powered and driven in the same way—controls the rotation of the sorting container, ensuring it aligns with the appropriate compartment based on the AI classification.

### Wiring Diagram
<p align="center">
  <img width="814" height="582" alt="image" src="https://github.com/user-attachments/assets/3addc6d7-b389-4e9a-b622-b554ee0b6159" />
</p>

## Software and Logic
**QualityControl.ino** \
This program coordinates three subsystems of the sorting machine: a conveyor belt driven by a stepper motor, a rotating sorter driven by a second stepper motor, and a cube-dispensing dropper driven by a servo. An ultrasonic sensor detects incoming cubes. The system also exchanges color-classification messages with a Python program to decide which bin to sort into.

The conveyor motor runs continuously until the ultrasonic sensor detects an object within the set distance threshold. When a block is detected, the conveyor stops and waits for a Python message reporting the block’s color (“Green” or “Red”). Based on this message, the sorter rotates 180° to the correct chute if needed. Once sorted, the conveyor resumes and enters a cooldown period to avoid repeated triggering. A second timer delays the next block drop, ensuring the servo releases cubes only when the conveyor is moving again.

The servo operates as a simple two-position dropper: 0° at rest and 140° to release a block. Each subsystem operates on its own timing to keep movements smooth and prevent overlapping.

**ArduinoConnection.py** \
This script acts as the communication link between the Arduino sorting system and the computer’s vision model. It listens to the Arduino over a serial connection and waits for the “DETECTED” message, which signals that the ultrasonic sensor has found a block on the conveyor.

When detection occurs, the script briefly pauses to let the camera settle, then calls predict_block_from_webcam() from the helper module. That function analyzes the current webcam frame and returns a label such as “Green” or “Red”. The script sends this label back to the Arduino through the serial port so the hardware can rotate the sorter and resume conveyor motion. A small delay is included to keep communication stable and avoid rapid repeated messages.

This file effectively serves as the machine’s “eyes”, handing off a color classification whenever the Arduino requests it.

**Model_Training.py** \
This script trains a small convolutional neural network to distinguish between red and green blocks using images stored in the data_webcam directory. The dataset is loaded with a built-in utility that automatically labels images by folder name and splits them into training and validation sets. Images are resized to 64×64 pixels and normalized before entering the model.

The network is a simple three-layer CNN followed by a dense classifier that outputs two categories. It’s optimized with Adam and trained for up to 20 epochs, with early stopping enabled to prevent overfitting. After training, the model is saved to disk as block_AI.h5, ready to be used by the webcam prediction script. This file produces the vision system that powers the real-time sorter.

**Helper.py** \
This module provides a single function that captures a frame from an IP camera, preprocesses the image, and uses the trained CNN to classify the block’s color. The model is loaded once at import time so predictions stay fast.

The function isolates the central region of the frame by cropping a vertical band and then extracting a centered square. The cropped image is rotated, converted to RGB, resized to 64×64, and normalized to match the training format. After preprocessing, the model predicts one of two labels—“Green” or “Red”—based on the highest probability output. This helper acts as the vision front end for the serial communication script.

**Data_Recolection.py** \
This script creates and expands the training dataset used by the color-classifier model. It connects to an IP camera feed, displays a live preview, and lets the user save labeled images by pressing keys. Pressing r stores the current frame as a red block image; pressing g stores it as green; q exits.

Each captured frame is cropped around the vertical center of the camera view, then reduced to a centered square and rotated to match the model’s orientation. The final image is resized to the model’s required 64×64 format before being saved into data_webcam/Red or data_webcam/Green. This gives a clean, consistent dataset for training and retraining the block classifier.

## Limitations and Future Improvements
- The cardboard structure is unstable and tends to shift due to motor vibration, which makes frequent realignment necessary after each test. Replacing the cardboard with a more rigid material, such as wood, would greatly improve stability.
- When cubes are dispensed, they occasionally bounce and fall off the conveyor belt. Reducing the incline, adding side barriers, or increasing the belt’s width would help ensure smoother transitions and prevent cubes from leaving the system. 



