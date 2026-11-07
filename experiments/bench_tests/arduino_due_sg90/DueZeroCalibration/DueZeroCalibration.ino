// One-joint-at-a-time zero / direction diagnostic. Arduino Due Programming Port.
// Confirmed pins: 1 D6 LH, 2 D7 RH, 3 D8 LA, 4 D9 RA.
// Does NOT read servo position and does NOT execute a walking gait.
// Direct 3.3 V signals, separate regulated 5 V servo supply, common ground.
#include <Servo.h>
const uint8_t PINS[4]={6,7,8,9};
int zeroUs[4]={1500,1500,1500,1500}; // RAM only; print and copy into walking code.
Servo servos[4];
int selected=-1;
int targetUs=1500;
bool enabled=false;
bool testActive=false;
uint8_t stopWordLength=0;
unsigned long testStarted=0,lastReport=0;

void releaseSignals() {
  for(uint8_t k=0;k<4;++k) {
    if(servos[k].attached()) servos[k].detach();
    pinMode(PINS[k],OUTPUT);digitalWrite(PINS[k],LOW);
  }
  enabled=false;testActive=false;
  digitalWrite(LED_BUILTIN,LOW);
}

void printZeros() {
  Serial.print("const int NEUTRAL_US[4]={");
  for(uint8_t k=0;k<4;++k) {if(k) Serial.print(',');Serial.print(zeroUs[k]);}
  Serial.println("}; // motor order: LH,RH,LA,RA");
  Serial.println("These are commanded pulse zeros, not encoder readings. RAM values reset at power-off.");
}

void printTarget() {
  Serial.print("Motor ");Serial.print(selected+1);
  Serial.print(" target=");Serial.print(targetUs);
  Serial.print(" us; configured zero=");Serial.print(zeroUs[selected]);
  Serial.println(" us. Actual shaft angle is NOT measured.");
}

void holdTarget(int us) {
  // Fine alignment only; a large error needs mechanical horn re-indexing.
  targetUs=constrain(us,1300,1700);
  if(!servos[selected].attached()) servos[selected].attach(PINS[selected],1000,2000);
  servos[selected].writeMicroseconds(targetUs);
  enabled=true;digitalWrite(LED_BUILTIN,HIGH);printTarget();
}

void menu() {
  Serial.println("CECE_ZERO_CAL_V1 - 115200 baud, no motion at boot");
  Serial.println("1..4 SELECT ONLY | c HOLD selected zero | +/- adjust target by 5 us");
  Serial.println("z ACCEPT selected target as zero (RAM) | p PRINT zeros");
  Serial.println("t TEST selected +50 us then return to zero | x / stop RELEASE all | ? HELP");
  Serial.println("Support the mechanism; neutral is physical straight alignment, not a hard stop.");
}

void setup() {
  pinMode(LED_BUILTIN,OUTPUT);releaseSignals();
  Serial.begin(115200);delay(1500);menu();
}

void loop() {
  while(Serial.available()) {
    char c=Serial.read();
    if(c>='A' && c<='Z') c+='a'-'A';
    if(c=='x') {
      stopWordLength=0;releaseSignals();Serial.println("Signals OFF. Servo supply remains powered.");continue;
    }
    if(stopWordLength) {
      const char stopWord[]="stop";
      if(c==stopWord[stopWordLength]) {
        if(++stopWordLength==4) {
          stopWordLength=0;releaseSignals();Serial.println("Signals OFF. Servo supply remains powered.");
        }
      } else stopWordLength=(c=='s')?1:0;
      continue; // Never interpret the 't' inside "stop" as a direction test.
    }
    if(c=='s') {stopWordLength=1;continue;}
    if(c>='1' && c<='4') {
      releaseSignals();selected=c-'1';targetUs=zeroUs[selected];
      Serial.print("Selected motor ");Serial.print(selected+1);
      Serial.println(". Outputs OFF; send c to hold its configured zero.");
    } else if(c=='x') {
      releaseSignals();Serial.println("Signals OFF. Servo supply remains powered.");
    } else if(c=='?') menu();
    else if(c=='p') printZeros();
    else if(c=='c' || c=='+' || c=='-' || c=='z' || c=='t') {
      if(selected<0) {Serial.println("Select motor 1..4 first.");continue;}
      if(c=='c') {testActive=false;holdTarget(zeroUs[selected]);}
      else if(!enabled) {Serial.println("Outputs off. Send c before adjustments.");}
      else if(c=='+') {testActive=false;holdTarget(targetUs+5);}
      else if(c=='-') {testActive=false;holdTarget(targetUs-5);}
      else if(c=='z') {
        if(testActive) {Serial.println("Wait for direction test to finish before accepting zero.");continue;}
        zeroUs[selected]=targetUs;Serial.println("Stored commanded target as logical zero in RAM.");printZeros();
      } else if(c=='t') {
        if(zeroUs[selected]+50>1700) {Serial.println("No test: +50 us exceeds fine-adjustment limit.");continue;}
        holdTarget(zeroUs[selected]+50);testStarted=millis();testActive=true;
        Serial.println("Observe physical +50 us direction; returns in one second. No software sign applied.");
      }
    }
  }
  if(testActive && millis()-testStarted>=1000) {
    testActive=false;holdTarget(zeroUs[selected]);Serial.println("Direction test finished; holding zero.");
  }
  if(enabled && millis()-lastReport>=3000) {
    lastReport=millis();printTarget();
  }
}
