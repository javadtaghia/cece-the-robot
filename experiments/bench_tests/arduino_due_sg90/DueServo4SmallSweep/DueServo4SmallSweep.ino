// Arduino Due Programming Port. Servo 4 signal -> D9.
// External regulated 5 V servo supply; common ground with Due.
// Direct 3.3 V signal. Test the servo unloaded, outside the robot.
// Standard positional SG90: repeated sweep, NOT continuous shaft rotation.
#include <Servo.h>

const uint8_t SERVO4_PIN = 9;
const int LOW_US = 1400;
const int HIGH_US = 1600;
const int CENTER_US = 1500;
const unsigned long UPDATE_MS = 20;
const int STEP_US = 5;
Servo servo4;
bool running = false;
int pulseUs = CENTER_US;
int direction = 1;
unsigned long lastUpdate = 0;
char commandWord[16];
uint8_t wordLength = 0;

void stopServo() {
  running = false;
  if (servo4.attached()) servo4.detach();
  pinMode(SERVO4_PIN, OUTPUT);
  digitalWrite(SERVO4_PIN, LOW);
  digitalWrite(LED_BUILTIN, LOW);
  Serial.println("STOPPED: servo 4 pulses off. Supply is still powered.");
}

void startServo() {
  if (running) return; // Another 4 does not reset the position mid-sweep.
  pulseUs = CENTER_US;
  direction = 1;
  servo4.attach(SERVO4_PIN, 1000, 2000);
  servo4.writeMicroseconds(pulseUs);
  lastUpdate = millis();
  running = true;
  digitalWrite(LED_BUILTIN, HIGH);
  Serial.println("RUNNING servo 4 on D9. Send x or stop to stop.");
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
    } else if (c >= 'a' && c <= 'z') {
      if (wordLength < sizeof(commandWord) - 1) commandWord[wordLength++] = c;
      else wordLength = 0;
      commandWord[wordLength] = '\0';
      // Recognise "stop" even with No line ending selected.
      if (wordLength == 4 && commandWord[0] == 's' && commandWord[1] == 't' &&
          commandWord[2] == 'o' && commandWord[3] == 'p') {
        wordLength = 0;
        stopServo();
      }
    } else {
      wordLength = 0; // Ignore spaces / CR / LF.
    }
  }
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  for (uint8_t pin = 6; pin <= 9; ++pin) {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW); // Other three servo signals remain inactive.
  }
  Serial.begin(115200);
  delay(1500);
  Serial.println("Send 4 to repeat servo 4 movement until stopped.");
  Serial.println("Send x or stop to stop. Serial Monitor: 115200 baud.");
  Serial.println("Small 1400..1600 us sweep; not a walking gait or continuous rotation.");
}

void loop() {
  processSerial();
  if (!running || millis() - lastUpdate < UPDATE_MS) return;
  lastUpdate = millis();
  int next = pulseUs + direction * STEP_US;
  if (next > HIGH_US || next < LOW_US) {
    direction = -direction;
    next = pulseUs + direction * STEP_US;
  }
  pulseUs = next;
  servo4.writeMicroseconds(pulseUs);
}
