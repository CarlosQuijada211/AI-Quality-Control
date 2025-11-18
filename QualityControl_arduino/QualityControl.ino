#include <Servo.h>

// Conveyor Belt Pin
#define STEP_PIN 5
#define DIR_PIN 6

// Sorter Pin
#define STEP_PIN_2 7
#define DIR_PIN_2 8

// Ultrasonic Sensor Pin
#define TRIG_PIN 9
#define ECHO_PIN 10

// Servo
Servo myServo;
int servoPin = 4;    // Servo signal pin

// Sensor cm Range
const int distanceThreshold = 9; // cm

// Conveyor Belt Motor
const int stepDelay = 500;      
const int stepsPerMove = 4;      

// Sorter Motor
const int stepsPerRevolution = 200; // 1.8° per step
const int stepsFor180 = stepsPerRevolution / 2; // 100 steps
const int stepDelay_2 = 2000; // microseconds between steps (adjust speed)

// Cooldown Variables
bool motorRunning = true; 
unsigned long motorStartTime = 0;
unsigned long sensorCooldownTime = 0;
const unsigned long cooldownDuration = 5000; // 3s after RESUME

// Sorter variables
bool color = false; // Green = false, Red = true

// Dropper variables
bool av = true;

// --- New dropper timing ---
unsigned long dropReadyTime = 0; // when it's allowed to drop next block
const unsigned long dropDelay = 4000; // 4s after motor resumes before drop


void setup() {
  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);
  digitalWrite(DIR_PIN, HIGH);  

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  pinMode(STEP_PIN_2, OUTPUT);
  pinMode(DIR_PIN_2, OUTPUT);

  myServo.attach(servoPin);
  myServo.write(0); 

  Serial.begin(9600);
}

// Read ultrasound sensor
int readDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  if (duration == 0) return 999; 
  int distance = duration * 0.034 / 2;
  return distance; // Return distance from object
}

// Rotate Sorter 180 degrees
void rotate180(bool clockwise) {
  digitalWrite(DIR_PIN_2, clockwise ? HIGH : LOW);

  for (int i = 0; i < stepsFor180; i++) {
    digitalWrite(STEP_PIN_2, HIGH);
    delayMicroseconds(stepDelay_2);
    digitalWrite(STEP_PIN_2, LOW);
    delayMicroseconds(stepDelay_2);
  }
}


void loop() {
  unsigned long now = millis();

  // --- Check if cooldown is active ---
  bool cooldownActive = (now < sensorCooldownTime);

  int distance = readDistance();

  // --- Only detect if motor is running and cooldown not active ---
  // If it is not in cooldown, the motor is running, and an object is detected within 6cm of the sensor
  if (!cooldownActive && motorRunning && distance <= distanceThreshold && distance > 0) {
    motorRunning = false; // stop conveyor
    Serial.println("DETECTED");
  }

  // Drop block
  if (av && now >= dropReadyTime) {
    myServo.write(140);
    delay(500);
    myServo.write(0);
    av = false;
  }


  // --- Check for Python response ---
  if (Serial.available() > 0) {
    String msg = Serial.readStringUntil('\n');
    msg.trim();

    // Python detected green object 
    if (msg == "Green") {
      if (color) { // If current sorter position is red: rotate 
        color = false;
        rotate180(true);
        delay(1500);
      }

      // Resume motor movement and initiate a cooldown to avoid repeated detection
      Serial.println("AVAILABLE");
      motorRunning = true;
      sensorCooldownTime = now + cooldownDuration; // sensor cooldown
      dropReadyTime = now + dropDelay;             // drop delay
      av = true;

    }

    // Python detected red object 
    else if (msg == "Red") {
      if (!color) { // If current position is green: rotate
        color = true;
        rotate180(true);
        delay(1500);
      }
      Serial.println("AVAILABLE");
      motorRunning = true;
      sensorCooldownTime = now + cooldownDuration; // sensor cooldown
      dropReadyTime = now + dropDelay;             // drop delay
      av = true;

    }
  }

  // --- Stepper motion if motor is running ---
  if (motorRunning) {
    for (int i = 0; i < stepsPerMove; i++) {
      digitalWrite(STEP_PIN, HIGH);
      delayMicroseconds(stepDelay);
      digitalWrite(STEP_PIN, LOW);
      delayMicroseconds(stepDelay);
    }
  }

  delay(10);
}
