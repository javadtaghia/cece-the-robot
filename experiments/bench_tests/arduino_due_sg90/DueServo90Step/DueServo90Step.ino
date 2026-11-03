// Arduino Due Programming Port; Serial Monitor 115200 baud.
// Same wiring as DueFourServoTest: direct signals D6,D7,D8,D9;
// external regulated 5 V servo power and common ground.
// SG90 is a positional servo, not continuous rotation.
#include <Servo.h>

const uint8_t PINS[4] = {6, 7, 8, 9};
// Conservative starting pulse mapping. Physical angles are not calibrated:
// actual 90-degree travel must be measured for these particular SG90 units.
const int PULSE_AT_0_US = 1000;
const int PULSE_AT_180_US = 2000;
Servo motors[4];
int angle[4] = {90, 90, 90, 90};
int direction[4] = {1, 1, 1, 1};
bool centred[4] = {false, false, false, false};

void stopAll() {
  for (uint8_t i = 0; i < 4; ++i) {
    if (motors[i].attached()) motors[i].detach();
    pinMode(PINS[i], OUTPUT);
    digitalWrite(PINS[i], LOW);
    centred[i] = false;
  }
  digitalWrite(LED_BUILTIN, LOW);
}

bool waitWithStop(unsigned long durationMs) {
  unsigned long start = millis();
  while (millis() - start < durationMs) {
    while (Serial.available()) {
      char c = Serial.read();
      if (c == 'x' || c == 'X') {
        stopAll();
        Serial.println("Stopped. Send c before resuming. Servo supply remains powered.");
        return false;
      }
      // No command queue: send the next number when the movement finishes.
    }
    delay(2);
  }
  return true;
}

void centreAll() {
  stopAll();
  Serial.println("Centring all four at nominal 90 degrees. Keep horns unloaded.");
  for (uint8_t i = 0; i < 4; ++i) {
    motors[i].attach(PINS[i], PULSE_AT_0_US, PULSE_AT_180_US);
    motors[i].write(90);
    angle[i] = 90;
    direction[i] = 1;
    if (!waitWithStop(800)) return;
    centred[i] = true;
  }
  Serial.println("Ready. Send 1, 2, 3 or 4. Each command requests a 90-degree step.");
}

void step90(uint8_t i) {
  if (!centred[i]) {
    Serial.println("Send c first to establish the starting position.");
    return;
  }
  int target = angle[i] + direction[i] * 90;
  if (target > 180 || target < 0) {
    direction[i] = -direction[i];
    target = angle[i] + direction[i] * 90;
  }
  Serial.print("Servo "); Serial.print(i + 1);
  Serial.print(": "); Serial.print(angle[i]);
  Serial.print(" -> "); Serial.println(target);
  digitalWrite(LED_BUILTIN, HIGH);
  while (angle[i] != target) {
    angle[i] += constrain(target - angle[i], -2, 2);
    motors[i].write(angle[i]);
    if (!waitWithStop(20)) return;
  }
  digitalWrite(LED_BUILTIN, LOW);
  Serial.println("Ready for the next command.");
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  stopAll();
  Serial.begin(115200);
  delay(1500);
  Serial.println("SG90 90-degree STEP test. Send c to centre, then 1/2/3/4 to step.");
  Serial.println("At the travel limit the direction reverses: 90,180,90,0,90,...");
  Serial.println("x stops pulses. No servo moves until a command is sent.");
}

void loop() {
  if (!Serial.available()) return;
  char c = Serial.read();
  if (c == 'c' || c == 'C') centreAll();
  else if (c >= '1' && c <= '4') step90(c - '1');
  else if (c == 'x' || c == 'X') {
    stopAll();
    Serial.println("Signals off. Send c before resuming.");
  }
}
