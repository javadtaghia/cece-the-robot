// Arduino Due (Programming Port), 115200 baud.
// Confirmed physical mapping: 1 D6 LH, 2 D7 RH, 3 D8 LA, 4 D9 RA.
// Right-side motors 2 and 4 reverse the model direction, as requested.
// Separate regulated 5 V servo supply; common ground; direct 3.3 V signals.
// Candidate open-loop forward gait: physical walking/calibration unverified.
#include <Servo.h>
#include <math.h>
#include <stdint.h>
// BEGIN GENERATED FOUR SERVO GAIT
const uint16_t STARTUP_FRAMES = 28;
const uint16_t CYCLE_FRAMES = 56;
const int16_t STARTUP_CDEG[][4] = {
  {0, 0, 0, 0},
  {0, 0, 66, 177},
  {0, 0, 238, 635},
  {0, 0, 472, 1275},
  {0, 0, 728, 1996},
  {0, 0, 962, 2687},
  {0, 0, 1134, 3217},
  {0, 0, 1200, 3425},
  {0, 0, 1200, 2848},
  {0, 0, 1200, 1777},
  {0, 0, 1200, 1200},
  {42, 42, 1200, 1200},
  {156, 156, 1200, 1200},
  {324, 324, 1200, 1200},
  {528, 528, 1200, 1200},
  {750, 750, 1200, 1200},
  {972, 972, 1200, 1200},
  {1176, 1176, 1200, 1200},
  {1344, 1344, 1200, 1200},
  {1458, 1458, 1200, 1200},
  {1500, 1500, 1200, 1200},
  {1500, 1500, 1200, 1777},
  {1500, 1500, 1200, 2848},
  {1500, 1500, 1200, 3425},
  {1500, 1500, 1075, 3035},
  {1500, 1500, 778, 2139},
  {1500, 1500, 422, 1137},
  {1500, 1500, 125, 333},
};
const int16_t CYCLE_CDEG[][4] = {
  {1500, 1500, 0, 0},
  {1500, 1500, -177, -66},
  {1500, 1500, -635, -238},
  {1500, 1500, -1275, -472},
  {1500, 1500, -1996, -728},
  {1500, 1500, -2687, -962},
  {1500, 1500, -3217, -1134},
  {1500, 1500, -3425, -1200},
  {1500, 1500, -2848, -1200},
  {1500, 1500, -1777, -1200},
  {1500, 1500, -1200, -1200},
  {1416, 1416, -1200, -1200},
  {1188, 1188, -1200, -1200},
  {852, 852, -1200, -1200},
  {444, 444, -1200, -1200},
  {0, 0, -1200, -1200},
  {-444, -444, -1200, -1200},
  {-852, -852, -1200, -1200},
  {-1188, -1188, -1200, -1200},
  {-1416, -1416, -1200, -1200},
  {-1500, -1500, -1200, -1200},
  {-1500, -1500, -1777, -1200},
  {-1500, -1500, -2848, -1200},
  {-1500, -1500, -3425, -1200},
  {-1500, -1500, -3035, -1075},
  {-1500, -1500, -2139, -778},
  {-1500, -1500, -1137, -422},
  {-1500, -1500, -333, -125},
  {-1500, -1500, 0, 0},
  {-1500, -1500, 66, 177},
  {-1500, -1500, 238, 635},
  {-1500, -1500, 472, 1275},
  {-1500, -1500, 728, 1996},
  {-1500, -1500, 962, 2687},
  {-1500, -1500, 1134, 3217},
  {-1500, -1500, 1200, 3425},
  {-1500, -1500, 1200, 2848},
  {-1500, -1500, 1200, 1777},
  {-1500, -1500, 1200, 1200},
  {-1416, -1416, 1200, 1200},
  {-1188, -1188, 1200, 1200},
  {-852, -852, 1200, 1200},
  {-444, -444, 1200, 1200},
  {0, 0, 1200, 1200},
  {444, 444, 1200, 1200},
  {852, 852, 1200, 1200},
  {1188, 1188, 1200, 1200},
  {1416, 1416, 1200, 1200},
  {1500, 1500, 1200, 1200},
  {1500, 1500, 1200, 1777},
  {1500, 1500, 1200, 2848},
  {1500, 1500, 1200, 3425},
  {1500, 1500, 1075, 3035},
  {1500, 1500, 778, 2139},
  {1500, 1500, 422, 1137},
  {1500, 1500, 125, 333},
};
// END GENERATED FOUR SERVO GAIT

const uint8_t MOTOR_PINS[4]={6,7,8,9};
const int MOTOR_DIRECTION[4]={1,-1,1,-1};
const int NEUTRAL_US[4]={1500,1500,1500,1500}; // Calibrate each actual joint.
const float US_PER_DEGREE[4]={10,10,10,10};   // Initial conversion, not measured.
const int MIN_US=1100;
const int MAX_US=1900;
const unsigned long SOURCE_FRAME_MS=20;
const uint8_t TIME_SCALE=2;  // First hardware test: half the simulation speed.
const unsigned long REAL_FRAME_MS=SOURCE_FRAME_MS*TIME_SCALE;
const unsigned long OUTPUT_MS=20;
const unsigned long SETTLE_MS=1000;
Servo motors[4];
bool running=false;
unsigned long startedAt=0,lastUpdate=0,lastCycle=0;
int lastPulseUs[4]={1500,1500,1500,1500};
char commandText[16];
uint8_t commandLength=0;

const int16_t* gaitRow(unsigned long frame) {
  if(frame<STARTUP_FRAMES) return STARTUP_CDEG[frame];
  return CYCLE_CDEG[(frame-STARTUP_FRAMES)%CYCLE_FRAMES];
}

void printHelp() {
  Serial.println("CECE4_WALK_V6 - four-servo forward reference");
  Serial.println("1=D6 LEFT HIP | 2=D7 RIGHT HIP | 3=D8 LEFT FOOT | 4=D9 RIGHT FOOT");
  Serial.println("Right motors 2 and 4 reversed. Initial neutral=1500 us each.");
  Serial.println("4 or w = START ALL FOUR | stop or x = signals OFF | c = hold neutral | ? = help");
  Serial.println("Starts stopped. Support the robot; verify neutral, signs and clearance before a ground test.");
}

void stopAll() {
  running=false;
  for(uint8_t k=0;k<4;++k) {
    if(motors[k].attached()) motors[k].detach();
    pinMode(MOTOR_PINS[k],OUTPUT);digitalWrite(MOTOR_PINS[k],LOW);
  }
  digitalWrite(LED_BUILTIN,LOW);
  Serial.println("STOP V6: all four signals off; servo supply remains powered.");
}

void attachNeutral() {
  for(uint8_t k=0;k<4;++k) {
    if(!motors[k].attached()) motors[k].attach(MOTOR_PINS[k],MIN_US,MAX_US);
    motors[k].writeMicroseconds(NEUTRAL_US[k]);
    lastPulseUs[k]=NEUTRAL_US[k];
  }
}

void centreAll() {
  running=false;attachNeutral();digitalWrite(LED_BUILTIN,LOW);
  Serial.println("Holding ALL FOUR at configured neutral. Check straight body/legs and flat feet.");
}

void startWalk() {
  if(running) {Serial.println("Already running. stop / x stops all four.");return;}
  attachNeutral();
  startedAt=millis();lastUpdate=startedAt;lastCycle=0;
  running=true;digitalWrite(LED_BUILTIN,HIGH);
  Serial.println("RUN CECE4_WALK_V6: settle 1 s, then repeat four-servo gait until stop / x.");
}

void readCommands() {
  while(Serial.available()) {
    char c=Serial.read();
    if(c>='A' && c<='Z') c+='a'-'A';
    if(c=='4' || c=='w') {commandLength=0;startWalk();}
    else if(c=='x') {commandLength=0;stopAll();}
    else if(c=='?') {commandLength=0;printHelp();}
    else if(c=='c' && commandLength==0) {centreAll();}
    else if(c>='a' && c<='z') {
      if(commandLength<sizeof(commandText)-1) commandText[commandLength++]=c;
      else commandLength=0;
      commandText[commandLength]='\0';
      if(commandLength==4 && commandText[0]=='s' && commandText[1]=='t' &&
          commandText[2]=='o' && commandText[3]=='p') {commandLength=0;stopAll();}
    } else commandLength=0;
  }
}

void setup() {
  pinMode(LED_BUILTIN,OUTPUT);digitalWrite(LED_BUILTIN,LOW);
  for(uint8_t k=0;k<4;++k) {pinMode(MOTOR_PINS[k],OUTPUT);digitalWrite(MOTOR_PINS[k],LOW);}
  Serial.begin(115200);delay(1500);printHelp();
}

void loop() {
  readCommands();
  if(!running) return;
  unsigned long now=millis();
  if(now-lastUpdate<OUTPUT_MS) return;
  lastUpdate=now;
  unsigned long elapsed=now-startedAt;
  if(elapsed<SETTLE_MS) return;
  elapsed-=SETTLE_MS;
  unsigned long frame=elapsed/REAL_FRAME_MS;
  float mix=(elapsed%REAL_FRAME_MS)/(float)REAL_FRAME_MS;
  const int16_t *a=gaitRow(frame),*b=gaitRow(frame+1);
  for(uint8_t k=0;k<4;++k) {
    float offset=((1-mix)*a[k]+mix*b[k])*.01f;
    int pulse=NEUTRAL_US[k]+(int)lroundf(offset*US_PER_DEGREE[k]*MOTOR_DIRECTION[k]);
    lastPulseUs[k]=constrain(pulse,MIN_US,MAX_US);
    motors[k].writeMicroseconds(lastPulseUs[k]);
  }
  unsigned long cycle=frame<STARTUP_FRAMES?0:1+(frame-STARTUP_FRAMES)/CYCLE_FRAMES;
  if(cycle!=lastCycle) {
    lastCycle=cycle;Serial.print("V6 gait cycle ");Serial.print(cycle);
    for(uint8_t k=0;k<4;++k) {Serial.print(" | S");Serial.print(k+1);Serial.print("=");Serial.print(lastPulseUs[k]);}
    Serial.println(" us | stop / x to release");
  }
}
