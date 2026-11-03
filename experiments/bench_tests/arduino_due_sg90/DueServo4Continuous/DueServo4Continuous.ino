// Arduino Due Programming Port: paired FOOT/ANKLE BENCH TEST, not full walking.
// Servo 3=D8 assumed LEFT foot; servo 4=D9 assumed RIGHT foot.
// Direct 3.3 V signals, external regulated 5 V servo power, common ground.
// Confirm physical joint mapping, neutral and mounting directions before loading.
#include <Servo.h>
#include <math.h>
#include <stdint.h>
// BEGIN GENERATED PAIR34 GAIT
const uint16_t GAIT_SAMPLE_COUNT = 56;
const int16_t LEFT_ANKLE_CDEG[GAIT_SAMPLE_COUNT] = {
  0, 66, 238, 472, 728, 962, 1134, 1200,
  1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200,
  1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200,
  1075, 778, 422, 125, 0, -177, -635, -1275,
  -1996, -2687, -3217, -3425, -2848, -1777, -1200, -1200,
  -1200, -1200, -1200, -1200, -1200, -1200, -1200, -1200,
  -1200, -1777, -2848, -3425, -3035, -2139, -1137, -333,
};
const int16_t RIGHT_ANKLE_CDEG[GAIT_SAMPLE_COUNT] = {
  0, 177, 635, 1275, 1996, 2687, 3217, 3425,
  2848, 1777, 1200, 1200, 1200, 1200, 1200, 1200,
  1200, 1200, 1200, 1200, 1200, 1777, 2848, 3425,
  3035, 2139, 1137, 333, 0, -66, -238, -472,
  -728, -962, -1134, -1200, -1200, -1200, -1200, -1200,
  -1200, -1200, -1200, -1200, -1200, -1200, -1200, -1200,
  -1200, -1200, -1200, -1200, -1075, -778, -422, -125,
};
// END GENERATED PAIR34 GAIT

const uint8_t FOOT_PINS[2] = {8, 9};
const int NEUTRAL_US[2] = {1500, 1500}; // Must match each real foot's neutral.
const int MOUNT_DIRECTION[2] = {1, 1};  // Reverse a sign only after checking the joint.
const float US_PER_DEGREE = 10.0f;      // Initial assumption; physical angles uncalibrated.
const float GAIT_GAIN = 0.35f;          // Reduced amplitude, NOT the full simulation gait.
const float MAX_OFFSET_DEG = 12.0f;
const unsigned long SAMPLE_MS = 40;    // 2x slower than the 20 ms source samples.
const unsigned long UPDATE_MS = 20;    // 50 Hz servo target updates.
Servo feet[2];
bool centred = false;
bool running = false;
unsigned long startedAt = 0;
unsigned long lastUpdate = 0;
unsigned long lastCycle = 0;
int lastPulseUs[2] = {1500,1500};
char commandText[16];
uint8_t commandLength = 0;

void stopFeet() {
  running = false;
  centred = false;
  for (uint8_t k=0;k<2;++k) {
    if (feet[k].attached()) feet[k].detach();
    pinMode(FOOT_PINS[k],OUTPUT);
    digitalWrite(FOOT_PINS[k],LOW);
  }
  digitalWrite(LED_BUILTIN,LOW);
  Serial.println("STOP: pulses off. Servo supply remains powered. Send c before restarting.");
}

void centreFeet() {
  running = false;
  for (uint8_t k=0;k<2;++k) {
    feet[k].attach(FOOT_PINS[k],1000,2000);
    feet[k].writeMicroseconds(NEUTRAL_US[k]);
    lastPulseUs[k]=NEUTRAL_US[k];
  }
  centred=true;
  digitalWrite(LED_BUILTIN,LOW);
  Serial.println("Holding both feet at configured neutral (1500 us by default).");
  Serial.println("Check feet are neutral, not at a mechanical stop. Send 4 to run both.");
}

void startFeet() {
  if (running) return;
  if (!centred) {
    Serial.println("Send c first. Check both neutral positions before sending 4.");
    return;
  }
  startedAt=millis();
  lastUpdate=startedAt;
  lastCycle=0;
  running=true;
  digitalWrite(LED_BUILTIN,HIGH);
  Serial.println("RUN PAIR34_SMALL_GAIT_V4: both feet, repeat until stop / x.");
  Serial.println("Reduced ankle pattern; max nominal offset 12 deg, cycle 2.24 s.");
}

void readCommands() {
  while (Serial.available()) {
    char c=Serial.read();
    if (c>='A' && c<='Z') c+='a'-'A';
    if (c=='4') { commandLength=0; startFeet(); }
    else if (c=='x') { commandLength=0; stopFeet(); }
    else if (c=='c' && commandLength==0) { centreFeet(); }
    else if (c>='a' && c<='z') {
      if (commandLength<sizeof(commandText)-1) commandText[commandLength++]=c;
      else commandLength=0;
      commandText[commandLength]='\0';
      if (commandLength==4 && commandText[0]=='s' && commandText[1]=='t' &&
          commandText[2]=='o' && commandText[3]=='p') {
        commandLength=0;stopFeet();
      }
    } else commandLength=0;
  }
}

void setup() {
  pinMode(LED_BUILTIN,OUTPUT);
  for (uint8_t pin=6;pin<=9;++pin) { pinMode(pin,OUTPUT);digitalWrite(pin,LOW); }
  Serial.begin(115200);
  delay(1500);
  Serial.println("PAIR34_SMALL_GAIT_V4 - small repeated motion, servos 3 (D8) + 4 (D9)");
  Serial.println("c: centre/check first | 4: run BOTH | stop / x: release");
  Serial.println("Keep feet lifted initially. One pair alone does not establish forward walking.");
}

void loop() {
  readCommands();
  if (!running) return;
  unsigned long now=millis();
  if (now-lastUpdate<UPDATE_MS) return;
  lastUpdate=now;
  unsigned long elapsed=now-startedAt;
  uint16_t i=(elapsed/SAMPLE_MS)%GAIT_SAMPLE_COUNT;
  uint16_t j=(i+1)%GAIT_SAMPLE_COUNT;
  float f=(elapsed%SAMPLE_MS)/(float)SAMPLE_MS;
  for (uint8_t k=0;k<2;++k) {
    const int16_t *table=k==0?LEFT_ANKLE_CDEG:RIGHT_ANKLE_CDEG;
    float offset=((1-f)*table[i]+f*table[j])*.01f*GAIT_GAIN;
    offset=constrain(offset,-MAX_OFFSET_DEG,MAX_OFFSET_DEG);
    int pulse=NEUTRAL_US[k]+(int)lroundf(offset*US_PER_DEGREE*MOUNT_DIRECTION[k]);
    lastPulseUs[k]=constrain(pulse,NEUTRAL_US[k]-120,NEUTRAL_US[k]+120);
    feet[k].writeMicroseconds(lastPulseUs[k]);
  }
  unsigned long cycle=elapsed/(GAIT_SAMPLE_COUNT*SAMPLE_MS);
  if (cycle!=lastCycle) {
    lastCycle=cycle;
    Serial.print("Cycle ");Serial.print(cycle);
    Serial.print(" | S3=");Serial.print(lastPulseUs[0]);
    Serial.print(" us | S4=");Serial.print(lastPulseUs[1]);
    Serial.println(" us | repeating; stop / x to release");
  }
}
