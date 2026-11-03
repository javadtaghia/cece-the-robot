// Standalone UNLOADED SG90 bench test. Not Cece walking firmware.
// Board: Arduino Due (Programming Port). Serial Monitor: 115200 baud.
// Servo signals: D6,D7,D8,D9. External regulated 5 V servo supply;
// common ground. The Due's 3.3 V signals connect directly to servo inputs.
// This test checks whether these particular SG90s accept that signal level.
#include <Servo.h>

const uint8_t SERVO_PINS[4] = {6, 7, 8, 9};
const int CENTER_US = 1500;
const int LOW_US = 1400;
const int HIGH_US = 1600;
Servo motors[4];
int positionUs = CENTER_US;

void releaseAll() {
  for (uint8_t i = 0; i < 4; ++i) {
    if (motors[i].attached()) motors[i].detach();
    pinMode(SERVO_PINS[i], OUTPUT);
    digitalWrite(SERVO_PINS[i], LOW);
  }
  digitalWrite(LED_BUILTIN, LOW);
}

// Keep checking for STOP even while a test is moving or holding a position.
bool waitWithStop(unsigned long durationMs) {
  unsigned long started = millis();
  while (millis() - started < durationMs) {
    while (Serial.available()) {
      char c = Serial.read();
      if (c == 'x' || c == 'X') {
        releaseAll();
        Serial.println("STOP: signals off. Disconnect the 5 V supply to remove servo power.");
        return false;
      }
      // Other characters during a test are discarded, not queued as movement.
    }
    delay(2);
  }
  return true;
}

void writeMask(uint8_t mask, int pulseUs) {
  for (uint8_t i = 0; i < 4; ++i)
    if (mask & (1 << i)) motors[i].writeMicroseconds(pulseUs);
}

bool moveMask(uint8_t mask, int targetUs) {
  while (positionUs != targetUs) {
    int delta = targetUs - positionUs;
    positionUs += constrain(delta, -5, 5);
    writeMask(mask, positionUs);
    if (!waitWithStop(20)) return false;
  }
  return waitWithStop(500);
}

bool testMask(uint8_t mask) {
  releaseAll();
  positionUs = CENTER_US;
  for (uint8_t i = 0; i < 4; ++i) {
    if (mask & (1 << i)) {
      // This starts at approximately centre; the first movement can be sudden
      // if the shaft was previously elsewhere. Keep horns unloaded and clear.
      motors[i].attach(SERVO_PINS[i], 1000, 2000);
      motors[i].writeMicroseconds(CENTER_US);
    }
  }
  digitalWrite(LED_BUILTIN, HIGH);
  if (!waitWithStop(1000)) return false;
  if (!moveMask(mask, LOW_US)) return false;
  if (!moveMask(mask, HIGH_US)) return false;
  if (!moveMask(mask, CENTER_US)) return false;
  releaseAll();
  Serial.println("Test finished; signals off.");
  return true;
}

void printMenu() {
  Serial.println("\nFour-SG90 Arduino Due bench test");
  Serial.println("1 / 2 / 3 / 4 : test only that servo");
  Serial.println("a             : test all four, one at a time");
  Serial.println("t             : test all four together (after individual tests)");
  Serial.println("x             : stop / detach all signals");
  Serial.println("?             : show this menu");
  Serial.println("Range: 1400..1600 us around 1500 us; no full-travel sweep.");
  Serial.println("Servo power must come from the separate regulated 5 V supply.");
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  releaseAll();
  Serial.begin(115200);
  delay(1500);
  printMenu();
}

void loop() {
  if (!Serial.available()) return;
  char command = Serial.read();
  if (command >= '1' && command <= '4') {
    Serial.print("Testing servo "); Serial.println(command);
    testMask(1 << (command - '1'));
  } else if (command == 'a' || command == 'A') {
    for (uint8_t i = 0; i < 4; ++i) {
      Serial.print("Testing servo "); Serial.println(i + 1);
      if (!testMask(1 << i)) break;
    }
  } else if (command == 't' || command == 'T') {
    Serial.println("Testing all four together.");
    testMask(0x0F);
  } else if (command == 'x' || command == 'X') {
    releaseAll();
    Serial.println("Signals off; servo supply is still powered.");
  } else if (command == '?') {
    printMenu();
  }
}
