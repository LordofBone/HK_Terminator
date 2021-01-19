// thanks to DFRobot for the RGB LED code https://wiki.dfrobot.com/Gravity:Digital_RGB_LED_Module_SKU:DFR0605

// NeoPixel library to control the 'plasma-guns' (40 watt-range)
#include <Adafruit_NeoPixel.h>

// 'plasma-gun' LED pins
#define PIN_LED 3     // Control signal, connect to DI of the LED
#define NUM_LED 2     // Number of LEDs in a strip

// Custom colour1: Yellow
#define RED_VAL_1       255
#define GREEN_VAL_1     255
#define BLUE_VAL_1      0

// Custom colour2: Purple
#define RED_VAL_2       255
#define GREEN_VAL_2     0
#define BLUE_VAL_2      255

// Custom colour3: Cyan
#define RED_VAL_3       0
#define GREEN_VAL_3     255
#define BLUE_VAL_3      255

// Custom colour4: White
#define RED_VAL_4       255
#define GREEN_VAL_4     255
#define BLUE_VAL_4      255

// Custom colour5: Red
#define RED_VAL_5       255
#define GREEN_VAL_5     0
#define BLUE_VAL_5      0

// Number of plasma shots to fire and ms between shots
#define PLASMA_SHOTS 5
#define PLASMA_DELAY 50

// the max measurement vaule of the module is 520cm(a little bit longer than  effective max range)
#define  MAX_RANG      (520)
// ADC accuracy of Arduino UNO is 10bit
#define  ADC_SOLUTION      (1023.0)

// for incoming serial data
String incoming;

// default speeds
int default_speed = 1000;
int stop_speed = 0;

// default time (2000ms is enough to do a 180 turn)
int default_time = 1000;

// default distances to avoid objects (cm)
int default_distance = 20;
int default_back_distance = 50;
int default_under_distance = 5;

// object detect override, means the pi can send a command and the ultrasonics
// will be ignored on movement commands
bool moveoverride = false;

// override reset interval timer, after a minute the override will be disabled
// to make sure the hk doesn't run into things
unsigned long interval2 = 60000;   // the time we need to wait
unsigned long previousMillis2 = 0; // millis() returns an unsigned long.

// select the input pin for sensor 1 (right)
int sensorRightPin = A0;
// select the input pin for sensor 2 (left)
int sensorLeftPin = A1;
// select the input pin for sensor 3 (back)
int sensorBackPin = A2;
// select the input pin for sensor 4 (under)
int sensorUnderPin = A3;
// select the input pin for sensor 5 (under back)
int sensorUnderBackPin = A4;

// setup floats for right and left ultrasonic sensors
float dist_t_right, sensor_t_right, dist_t_left, sensor_t_left;

// setup floats for back and underneath ultrasonic sensors
float dist_t_back, sensor_t_back, dist_t_under, sensor_t_under, dist_t_under_back, sensor_t_under_back;

// timer setup for checking distance
unsigned long interval = 500;   // the time we need to wait
unsigned long previousMillis = 0; // millis() returns an unsigned long.

// setup control for the RGB lights
Adafruit_NeoPixel RGB_Strip = Adafruit_NeoPixel(NUM_LED, PIN_LED, NEO_GRB + NEO_KHZ800);

void setup() {
  // pin 4 controls M2 rotary direction HIGH/LOW = FORWARD/BACK
  pinMode(4, OUTPUT);
  // pin 5 controls M2 rotation speed
  pinMode(5, OUTPUT);
  // pin 6 controls M1 rotation speed
  pinMode(6, OUTPUT);
  // pin 7 controls M1 rotary direction HIGH/LOW = FORWARD/BACK
  pinMode(7, OUTPUT);

  // start up the RGB LED's
  RGB_Strip.begin();
  colorWipe(RGB_Strip.Color(0, 0, 0), 1000);  // Red
  RGB_Strip.show();
  RGB_Strip.setBrightness(128);    // Set brightness, 0-255 (darkest - brightest)

  // begin serial out to Pi
  Serial.begin(115200);

  // send first serial info to Pi
  Serial.println("setup_complete");
}

// all movement functions run the avoidance routine first; to ensure that the HK won't run into anything
// unless the override mode is on which will move the HK regardless
void moveStop(int movetime = default_time, int movespeed = stop_speed) {
  avoidanceRoutine();

  Serial.println("stopping_movement");

  digitalWrite(4, HIGH);
  analogWrite(5, movespeed);
  digitalWrite(7, HIGH);
  analogWrite(6, movespeed);

  delay(movetime);
}

void moveForward(int movetime = default_time, int movespeed = default_speed) {
  avoidanceRoutine();

  Serial.println("moving_forward");

  digitalWrite(4, HIGH);
  analogWrite(5, movespeed);
  digitalWrite(7, HIGH);
  analogWrite(6, movespeed - 35);

  delay(movetime);

  moveStop();
}

void moveBackward(int movetime = default_time, int movespeed = default_speed) {
  avoidanceRoutine();

  Serial.println("moving_backward");

  digitalWrite(4, LOW);
  analogWrite(5, movespeed - 65);
  digitalWrite(7, LOW);
  analogWrite(6, movespeed);

  delay(movetime);

  moveStop();
}

void turnLeft(int movetime = default_time, int movespeed = default_speed) {
  avoidanceRoutine();

  Serial.println("turning_left");

  digitalWrite(4, HIGH);
  analogWrite(5, movespeed - 15);
  digitalWrite(7, LOW);
  analogWrite(6, movespeed);

  delay(movetime);

  moveStop();
}

void turnRight(int movetime = default_time, int movespeed = default_speed) {
  avoidanceRoutine();

  Serial.println("turning_right");

  digitalWrite(4, LOW);
  analogWrite(5, movespeed);
  digitalWrite(7, HIGH);
  analogWrite(6, movespeed - 85);

  delay(movetime);

  moveStop();
}

// distance functions get the distance from 5 different sensors - 2 forward facing for right/left
// one facing back, one facing under at the front and one facing under at the back; to prevent the HK running off of surfaces
float getDistanceRight() {
  // read the value from the sensor:
  sensor_t_right = analogRead(sensorRightPin);

  dist_t_right = sensor_t_right * MAX_RANG  / ADC_SOLUTION;//

  return dist_t_right;
}

float getDistanceLeft() {
  // read the value from the sensor:
  sensor_t_left = analogRead(sensorLeftPin);

  dist_t_left = sensor_t_left * MAX_RANG  / ADC_SOLUTION;//

  return dist_t_left;
}

float getDistanceBack() {
  // read the value from the sensor:
  sensor_t_back = analogRead(sensorBackPin);

  dist_t_back = sensor_t_back * MAX_RANG  / ADC_SOLUTION;//

  return dist_t_back;
}

float getDistanceUnder() {
  // read the value from the sensor:
  sensor_t_under = analogRead(sensorUnderPin);

  dist_t_under = sensor_t_under * MAX_RANG  / ADC_SOLUTION;//

  return dist_t_under;
}

float getDistanceUnderBack() {
  // read the value from the sensor:
  sensor_t_under_back = analogRead(sensorUnderBackPin);

  dist_t_under_back = sensor_t_under_back * MAX_RANG  / ADC_SOLUTION;//

  return dist_t_under_back;
}

// get distance function returns results from all of the sensors and prints them out on the serial interface
void getDistance() {
  Serial.print("Right Sensor: ");
  Serial.print(getDistanceRight(), 0);
  Serial.println("cm");

  Serial.print("Left Sensor: ");
  Serial.print(getDistanceLeft(), 0);
  Serial.println("cm");

  Serial.print("Back Sensor: ");
  Serial.print(getDistanceBack(), 0);
  Serial.println("cm");

  Serial.print("Under Sensor: ");
  Serial.print(getDistanceUnder(), 0);
  Serial.println("cm");

  Serial.print("Under Back Sensor: ");
  Serial.print(getDistanceUnderBack(), 0);
  Serial.println("cm");
}

// test run function test the basic move and avoidance functions
void testRun() {
  Serial.println("running_test");
  moveForward(1250);
  turnRight(2500);
  moveBackward(1250);
  turnLeft(2500);
}

// avoidance routine function goes over all of the sensor results to ensure that nothing is in the way of the HK
// if something is detected it will do its best to turn away and or move away from obstructing objects
// todo: probably need to find a better way to do this - all movements should ideally have checks on the surrounding sensors
// however when running the avoidance routine again within movement calls here it can cause odd looping and the robot can freeze
// at the moment all movements within here override obstacle avoidance - essentially only 1 object around the HK at any one time
// can be recognised and dealt with
void avoidanceRoutine() {
  if (moveoverride == false) {
    if (getDistanceUnder() > default_under_distance) {
      Serial.println("no_surface_ahead");
      // temporarily override movement to prevent looping back into the avoidance routine
      moveoverride = true;
      moveBackward(2000);
      if (random(100) < 49) {
        turnRight(500);
      }
      else {
        turnLeft(500);
      }
      // set movement override back to off state
      moveoverride = false;
    }
    if (getDistanceRight() < default_distance and getDistanceLeft() > default_distance) {
      Serial.println("object_detect_right");
      // temporarily override movement to prevent looping back into the avoidance routine
      moveoverride = true;
      turnLeft(500);
      // set movement override back to off state
      moveoverride = false;
    }
    if (getDistanceRight() > default_distance and getDistanceLeft() < default_distance) {
      Serial.println("object_detect_left");
      // temporarily override movement to prevent looping back into the avoidance routine
      moveoverride = true;
      turnRight(500);
      // set movement override back to off state
      moveoverride = false;
    }
    if (getDistanceRight() < default_distance and getDistanceLeft() < default_distance) {
      Serial.println("object_detect_front");
      // temporarily override movement to prevent looping back into the avoidance routine
      moveoverride = true;
      moveBackward(2000);
      if (random(100) < 49) {
        turnRight(500);
      }
      else {
        turnLeft(500);
      }
      // set movement override back to off state
      moveoverride = false;
    }
    if (getDistanceUnderBack() > default_under_distance) {
      Serial.println("no_surface_behind");
      // temporarily override movement to prevent looping back into the avoidance routine
      moveoverride = true;
      moveForward(2000);
      if (random(100) < 49) {
        turnRight(500);
      }
      else {
        turnLeft(500);
      }
      // set movement override back to off state
      moveoverride = false;
    }
    if (getDistanceBack() < default_back_distance) {
      Serial.println("object_detect_behind");
      // temporarily override movement to prevent looping back into the avoidance routine
      moveoverride = true;
      moveForward(2000);
      if (random(100) < 49) {
        turnRight(500);
      }
      else {
        turnLeft(500);
      }
    }
    // set movement override back to off state
    moveoverride = false;

  }
}

// patrol mode function will make the HK move in a patrol patter for a set number of times
void patrolMode(int patrolCycles) {
  Serial.println("patrol_mode_started");
  for (int i = 0; i <= patrolCycles; i++) {
    moveForward(1500);
    turnRight();
    turnLeft(2000);
    turnRight();
    delay(1000);
    turnRight(2000);
  }
  Serial.println("patrol_mode_ended");
}

// move override functions will allow the higher level functions to override the avoidance routines and allow the HK
// to move regardless of the ultrasonics sensor detections
void moveOverrideSwitchOn() {
  moveoverride = true;
  Serial.println("move_ovrrde_on");
}

void moveOverrideSwitchOff() {
  moveoverride = false;
  Serial.println("move_ovrrde_off");
}

// 'plasma-gun' functions will activate the RGB LEDs on the main pylon to 'fire'; either purple or red
void firePlasmaRed() {
  Serial.println("firing_red_plasma");
  for (int i = 0; i <= PLASMA_SHOTS; i++) {
    colorWipe(RGB_Strip.Color(RED_VAL_5, GREEN_VAL_5, BLUE_VAL_5), 0);  // Custom colour5: Red
    delay(PLASMA_DELAY);
    fireNoPlasma();
    delay(PLASMA_DELAY);
  }
}

void firePlasmaPurple() {
  Serial.println("firing_purple_plasma");
  for (int i = 0; i <= PLASMA_SHOTS; i++) {
    colorWipe(RGB_Strip.Color(RED_VAL_2, GREEN_VAL_2, BLUE_VAL_2), 0);   // Custom colour2: Purple
    delay(PLASMA_DELAY);
    fireNoPlasma();
    delay(PLASMA_DELAY);
  }
}

void fireNoPlasma() {
  Serial.println("plasma_off");
  colorWipe(RGB_Strip.Color(0, 0, 0), 0);   // Custom colour2: Purple
}

// this is the command processor that will take in serial inputs and select the correct functions based on the input
void runCommand(String command) {
  Serial.println("Running command: ");
  Serial.println(command);

  if (command == "run_test") {
    testRun();
  }
  else if (command == "measure_dist") {
    getDistance();
  }
  else if (command == "move_forward") {
    moveForward();
  }
  else if (command == "move_backward") {
    moveBackward();
  }
  else if (command == "turn_right") {
    turnRight();
  }
  else if (command == "turn_left") {
    turnLeft();
  }
  else if (command == "patrol_mode") {
    patrolMode(5);
  }
  else if (command == "move_override_on") {
    moveOverrideSwitchOn();
  }
  else if (command == "move_override_off") {
    moveOverrideSwitchOff();
  }
  else if (command == "plasma_purple") {
    firePlasmaPurple();
  }
  else if (command == "plasma_red") {
    firePlasmaRed();
  }
  else if (command == "plasma_off") {
    fireNoPlasma();
  }
  else if (command == "test_serial") {
    Serial.println("SUCCESS!");
  }
  else {
    Serial.println("unknown_command");
  }
}

// Fill the dots one after the other with a color
void colorWipe(uint32_t c, uint16_t wait) {
  for (uint16_t i = 0; i < RGB_Strip.numPixels(); i++) {
    RGB_Strip.setPixelColor(i, c);
    RGB_Strip.show();
    delay(wait);
  }
}

void rainbow(uint8_t wait) {
  uint16_t i, j;

  for (j = 0; j < 256; j++) {
    for (i = 0; i < RGB_Strip.numPixels(); i++) {
      RGB_Strip.setPixelColor(i, Wheel((i + j) & 255));
    }
    RGB_Strip.show();
    delay(wait);
  }
}

// Input a value 0 to 255 to get a color value.
// The colours are a transition r - g - b - back to r.
uint32_t Wheel(byte WheelPos) {
  if (WheelPos < 85) {
    return RGB_Strip.Color(WheelPos * 3, 255 - WheelPos * 3, 0);
  } else if (WheelPos < 170) {
    WheelPos -= 85;
    return RGB_Strip.Color(255 - WheelPos * 3, 0, WheelPos * 3);
  } else {
    WheelPos -= 170;
    return RGB_Strip.Color(0, WheelPos * 3, 255 - WheelPos * 3);
  }
}

void loop() {
  // while serial available take in incoming commands
  while (Serial.available()) {
    // grab incoming serial from usb until carriage return
    incoming = Serial.readStringUntil('\n');
    // send comand to command processor
    runCommand(incoming);
  }

  // grab current time
  unsigned long currentMillis = millis();

  // run avoidance routine every few seconds
  if ((unsigned long)(currentMillis - previousMillis) >= interval) {
    avoidanceRoutine();
    previousMillis = millis();
  }

  // if movement override has been set, unset it after a few seconds
  if ((unsigned long)(currentMillis - previousMillis2) >= interval2) {
    moveoverride = false;
    previousMillis2 = millis();
  }
}
