// Cece USB-only hello world. Board: Seeed XIAO ESP32-S3 / Sense.
// Enable USB CDC On Boot. Open Serial Monitor at 115200 baud.
#include <Arduino.h>

void setup() {
  Serial.begin(115200);
  const uint32_t start = millis();
  while (!Serial && millis() - start < 3000) delay(10);
}

void loop() {
  Serial.println("Hello world! Cece ESP32-S3 is running.");
  delay(1000);
}
