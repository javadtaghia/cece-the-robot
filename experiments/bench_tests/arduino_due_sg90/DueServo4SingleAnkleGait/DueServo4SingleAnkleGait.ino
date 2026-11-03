// Arduino Due Programming Port. Servo 4 = right ankle reference, signal D9.
// Separate regulated 5 V servo power; common ground; direct 3.3 V signal.
// This is one joint of the Cece 2 forward gait, not a full walking controller.
#include <Servo.h>
#include <math.h>
// BEGIN GENERATED CECE2 SERVO4 GAIT
// GENERATED from experiments/cece2/gait.py, joint index 3 (right ankle).
// Signed hundredths of a nominal degree relative to neutral.
#include <stdint.h>
const uint16_t GAIT_SAMPLE_MS = 20;
const uint16_t GAIT_SAMPLE_COUNT = 56;
const int16_t SERVO4_GAIT_CDEG[GAIT_SAMPLE_COUNT] = {
  0, 177, 635, 1275, 1996, 2687, 3217, 3425,
  2848, 1777, 1200, 1200, 1200, 1200, 1200, 1200,
  1200, 1200, 1200, 1200, 1200, 1777, 2848, 3425,
  3035, 2139, 1137, 333, 0, -66, -238, -472,
  -728, -962, -1134, -1200, -1200, -1200, -1200, -1200,
  -1200, -1200, -1200, -1200, -1200, -1200, -1200, -1200,
  -1200, -1200, -1200, -1200, -1075, -778, -422, -125,
};
// END GENERATED CECE2 SERVO4 GAIT

const uint8_t SERVO4_PIN = 9;
const int NEUTRAL_US = 1500;       // Calibrate to the actual assembled joint.
const float US_PER_DEGREE = 10.0f; // Same assumption as CeceBench, not measured.
const int SERVO_DIRECTION = 1;     // Change to -1 if the mounted joint is reversed.
const int MIN_PULSE_US = 1100;
const int MAX_PULSE_US = 1900;
const unsigned long SETTLE_MS = 1000;
Servo servo4;
bool running = false;
unsigned long startedAt = 0;
unsigned long lastSample = 0;
bool haveSample = false;
char commandWord[16];
uint8_t wordLength = 0;

void stopServo() {
  running = false;
  if (servo4.attached()) servo4.detach();
  pinMode(SERVO4_PIN, OUTPUT);
  digitalWrite(SERVO4_PIN, LOW);
  digitalWrite(LED_BUILTIN, LOW);
  Serial.println("STOPPED: pulses off. Servo supply remains powered.");
}

void attachAtCentre() {
  servo4.attach(SERVO4_PIN, MIN_PULSE_US, MAX_PULSE_US);
  servo4.writeMicroseconds(NEUTRAL_US);
}

void startServo() {
  if (running) return;
  attachAtCentre();
  startedAt = millis();
  haveSample = false;
  running = true;
  digitalWrite(LED_BUILTIN, HIGH);
  Serial.println("CECE2_ANKLE_V3: settle 1 s, then repeat right-ankle gait at 50 Hz.");
  Serial.println("Offsets -12 to +34.25 nominal degrees. Send stop or x to release.");
}

void processSerial() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c >= 'A' && c <= 'Z') c += 'a' - 'A';
    if (c == '4') {
      wordLength = 0;
      startServo();
    } else if (c == 'x') {
      wordLength = 0;
      stopServo();
    } else if (c == 'c' && wordLength == 0) {
      running = false;
      attachAtCentre();
      digitalWrite(LED_BUILTIN, LOW);
      Serial.println("Holding servo 4 neutral at 1500 us. Send 4 to run, x to release.");
    } else if (c >= 'a' && c <= 'z') {
      if (wordLength < sizeof(commandWord) - 1) commandWord[wordLength++] = c;
      else wordLength = 0;
      commandWord[wordLength] = '\0';
      if (wordLength == 4 && commandWord[0]=='s' && commandWord[1]=='t' &&
          commandWord[2]=='o' && commandWord[3]=='p') {
        wordLength = 0;
        stopServo();
      }
    } else wordLength = 0;
  }
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  for (uint8_t pin = 6; pin <= 9; ++pin) {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
  }
  Serial.begin(115200);
  delay(1500);
  Serial.println("CECE2_ANKLE_V3 - servo 4 only, D9, simulation reference targets");
  Serial.println("4: run | stop / x: release | c: hold neutral");
  Serial.println("Check real neutral, direction and joint clearance with the foot lifted.");
}

void loop() {
  processSerial();
  if (!running) return;
  unsigned long elapsed = millis() - startedAt;
  if (elapsed < SETTLE_MS) return;
  unsigned long sample = (elapsed - SETTLE_MS) / GAIT_SAMPLE_MS;
  if (haveSample && sample == lastSample) return;
  lastSample = sample;
  haveSample = true;
  float offsetDeg = SERVO4_GAIT_CDEG[sample % GAIT_SAMPLE_COUNT] / 100.0f;
  int pulseUs = NEUTRAL_US + (int)lroundf(SERVO_DIRECTION * US_PER_DEGREE * offsetDeg);
  servo4.writeMicroseconds(constrain(pulseUs, MIN_PULSE_US, MAX_PULSE_US));
}
