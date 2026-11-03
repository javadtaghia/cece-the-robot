// Arduino Due, Programming Port. No external components required.
void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
  delay(1500);
  Serial.println("Hello world! Arduino Due is running.");
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);
  Serial.println("Hello from the Due - LED ON");
  delay(500);
  digitalWrite(LED_BUILTIN, LOW);
  delay(500);
}
