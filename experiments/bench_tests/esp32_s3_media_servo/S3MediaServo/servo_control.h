#pragma once
#include <Wire.h>
#include "walk_profile.h"

// Core Electronics CE09181: socket labels 1..4 map to chip channels 3..0.
constexpr uint8_t SERVO_ADDRESS=0x44;
constexpr uint8_t SERVO_CHANNELS[4]={3,2,1,0};
constexpr uint8_t SERVO_PRESCALE=121;
constexpr float SERVO_PWM_HZ=25000000.0f/(4096.0f*(SERVO_PRESCALE+1));
volatile bool servoControllerReady=false;
volatile uint8_t servoActiveSocket=0;
QueueHandle_t servoCommands=nullptr;
String servoControlToken;
enum ServoAction { Stop, Test, Scan, Walk, Heartbeat, Position };
struct ServoCommand { ServoAction action; uint8_t socket; int offset; uint32_t owner, sent; };
volatile bool servoWalking = false;
bool servoTaskReady = false;
void motorTask(void *);
uint32_t servoStarted=0, servoLastUpdate=0;

bool servoRegister(uint8_t reg,uint8_t value) {
  Wire.beginTransmission(SERVO_ADDRESS);Wire.write(reg);Wire.write(value);
  return Wire.endTransmission()==0;
}
bool servoOutput(uint8_t channel,uint16_t counts,bool off) {
  Wire.beginTransmission(SERVO_ADDRESS);Wire.write(0x06+4*channel);
  Wire.write(0);Wire.write(0);Wire.write(counts&0xff);Wire.write(off?0x10:((counts>>8)&0x0f));
  return Wire.endTransmission()==0;
}
bool servoDisableOutputs() {
  bool ok=true;
  // Set the per-channel FULL_OFF bits. No centering pulse is sent at startup.
  for(uint8_t channel=0;channel<16;channel++) ok=servoOutput(channel,0,true)&&ok;
  servoActiveSocket=0;
  return ok;
}
bool configureServoController() {
  Wire.beginTransmission(SERVO_ADDRESS);
  if(Wire.endTransmission()!=0) return false;
  // Auto increment and sleep while programming the PWM clock.
  if(!servoRegister(0x00,0x30)) return false;
  if(!servoDisableOutputs()) return false;
  if(!servoRegister(0xFE,SERVO_PRESCALE) || !servoRegister(0x01,0x04)) return false;
  if(!servoRegister(0x00,0x20)) return false;
  delay(5);
  return servoRegister(0x00,0xA0);
}
void setupServoControl() {
  uint8_t bytes[16];esp_fill_random(bytes,sizeof(bytes));char token[33];
  for(size_t i=0;i<16;i++) snprintf(token+i*2,3,"%02x",bytes[i]);
  servoControlToken=token;
  servoCommands=xQueueCreate(8,sizeof(ServoCommand));
  Wire.begin(5,6,100000);Wire.setTimeOut(25);
  servoControllerReady=servoCommands && configureServoController();
  servoTaskReady = servoCommands && xTaskCreate(motorTask,"cece-motion",4096,nullptr,2,nullptr)==pdPASS;
  servoControllerReady = servoControllerReady && servoTaskReady;
  Serial.printf("SERVO_DRIVER address=0x44 found=%s outputs=%s\n",servoControllerReady?"YES":"NO",servoControllerReady?"OFF":"NOT_CONFIRMED");
}
// Motion state and I2C writes belong to the motor task. The HTTP task queues requests.
constexpr uint32_t WALK_TIMEOUT_MS = 3000;
constexpr int CENTER_US[4] = {1500, 1500, 1500, 1500};
// Model-positive rotation relative to the raw manual control on this assembly.
constexpr int WALK_SIGN[4] = {1, 1, -1, -1};
int lastPulseUs[4] = {CENTER_US[0], CENTER_US[1], CENTER_US[2], CENTER_US[3]};
int startPulseUs[4];
int easePulse(int from, int to, uint32_t elapsed, uint32_t duration) {
  if (elapsed >= duration) return to;
  float x = elapsed / float(duration);
  return from + lroundf((to - from) * x * x * (3.0f - 2.0f * x));
}
const int16_t *walkFrame(uint32_t frame) {
  if (frame < STARTUP_FRAMES) return STARTUP_CDEG[frame];
  return CYCLE_CDEG[(frame - STARTUP_FRAMES) % CYCLE_FRAMES];
}
// Gait columns are left hip, right hip, left foot, right foot.
// Physical sockets 1..4 are left foot, right foot, left hip, right hip.
constexpr uint8_t GAIT_COLUMN_BY_SOCKET[4] = {2, 3, 0, 1};
int walkPulse(uint8_t socketIndex, uint32_t elapsed) {
  // Hold center for one second, then follow the phased weight transfer and hip swing.
  if (elapsed < 1000) return easePulse(startPulseUs[socketIndex], CENTER_US[socketIndex], elapsed, 800);
  uint32_t t = elapsed - 1000;
  const uint8_t column = GAIT_COLUMN_BY_SOCKET[socketIndex];
  int a = walkFrame(t / FRAME_MS)[column], b = walkFrame(t / FRAME_MS + 1)[column];
  int offsetUs = lroundf((a + (b - a) * ((t % FRAME_MS) / float(FRAME_MS))) / 10.0f);
  return constrain(CENTER_US[socketIndex] + WALK_SIGN[socketIndex] * offsetUs, 1100, 1900);
}
uint32_t lastHeartbeat = 0, walkOwner = 0;
int manualOffset = 0;
bool testing = false;

void stopMotion() {
  if (!servoDisableOutputs()) {
    servoControllerReady = false;
    Serial.println("SERVO_STOP_I2C_ERROR: disconnect servo power");
  }
  servoWalking = false;
  walkOwner = 0;
  servoActiveSocket = 0;
}
bool writePulse(uint8_t socketIndex, int us) {
  uint16_t ticks = lroundf(us * SERVO_PWM_HZ * 4096.0f / 1000000.0f);
  if (servoOutput(SERVO_CHANNELS[socketIndex], ticks, false)) {
    lastPulseUs[socketIndex] = us;
    return true;
  }
  stopMotion();
  servoControllerReady = false;
  return false;
}
void serviceServoControl() {
  uint32_t now = millis();
  if (servoWalking && now - lastHeartbeat >= WALK_TIMEOUT_MS) stopMotion();
  ServoCommand c;
  while (xQueueReceive(servoCommands, &c, 0) == pdPASS) {
    now = millis();
    if (c.action == Stop) { stopMotion(); continue; }
    if (c.action == Heartbeat) {
      if (servoWalking && c.owner == walkOwner) lastHeartbeat = now;
      continue;
    }
    if (servoWalking || servoActiveSocket) continue;
    if (c.action == Scan) { servoControllerReady = configureServoController(); continue; }
    if (!servoControllerReady || now - c.sent >= WALK_TIMEOUT_MS) continue;
    servoStarted = now;
    for (uint8_t j = 0; j < 4; ++j) startPulseUs[j] = lastPulseUs[j];
    servoLastUpdate = now - 20;
    if (c.action == Walk) {
      walkOwner = c.owner;
      lastHeartbeat = now;
      servoWalking = true;
    } else {
      servoActiveSocket = c.socket;
      manualOffset = c.offset;
      testing = c.action == Test;
    }
  }
  if (now - servoLastUpdate < 20) return;
  servoLastUpdate = now;
  uint32_t elapsed = now - servoStarted;
  if (servoWalking) {
    for (uint8_t j = 0; j < 4; ++j)
      if (!writePulse(j, walkPulse(j, elapsed))) break;
  } else if (servoActiveSocket) {
    if (elapsed >= 1900) { stopMotion(); return; }
    int offset = manualOffset;
    if (testing) {
      offset = 0;
      if (elapsed >= 400 && elapsed < 700) offset = -int((elapsed - 400) / 3);
      else if (elapsed >= 700 && elapsed < 1300) offset = -100 + int((elapsed - 700) / 3);
      else if (elapsed >= 1300 && elapsed < 1600) offset = 100 - int((elapsed - 1300) / 3);
    }
    uint8_t j = servoActiveSocket - 1;
    int target = CENTER_US[j] + offset;
    if (!testing) target = easePulse(startPulseUs[j], target, elapsed, 800);
    else if (elapsed < 400) target = easePulse(startPulseUs[j], CENTER_US[j], elapsed, 400);
    writePulse(j, target);
  }
}
void motorTask(void *) {
  for (;;) {
    serviceServoControl();
    vTaskDelay(pdMS_TO_TICKS(10));
  }
}
bool queueStop() {
  if (!servoTaskReady) return false;
  ServoCommand stop = {Stop};
  xQueueReset(servoCommands);
  return xQueueSendToFront(servoCommands, &stop, 0) == pdPASS;
}

esp_err_t servoHandler(httpd_req_t *req) {
  char token[40]={};
  if(httpd_req_get_hdr_value_str(req,"X-Cece-Control",token,sizeof(token))!=ESP_OK || servoControlToken!=token) {
    httpd_resp_set_status(req,"403 Forbidden");
    return httpd_resp_send(req,"Refresh Cece's page before using motor controls.",HTTPD_RESP_USE_STRLEN);
  }
  if(req->content_len<=0 || req->content_len>96) return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Invalid servo command.");
  char body[97]={};size_t used=0;
  while(used<req->content_len) {
    int n=httpd_req_recv(req,body+used,req->content_len-used);
    if(n<=0) return httpd_resp_send_err(req,HTTPD_408_REQ_TIMEOUT,"Command timed out.");used+=n;
  }
  String data(body);String action=formField(data,"action");ServoCommand command={};
  command.sent = millis();
  if (action == "stop") {
    if (!queueStop()) return unavailable(req,"Motion task unavailable.");
  } else {
    if (!servoTaskReady) return unavailable(req,"Motion task unavailable.");
    if (action == "heartbeat" || action == "walk") {
      String owner = formField(data,"owner");
      if (owner.length() != 8 || owner == "00000000" || strspn(owner.c_str(),"0123456789abcdef") != 8)
        return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Invalid walk session.");
      command.owner = strtoul(owner.c_str(), nullptr, 16);
    }
    if (action == "heartbeat") command.action = Heartbeat;
    else {
      if (servoWalking || servoActiveSocket) return unavailable(req,"Motion active. Press Stop first.");
      if (action == "scan") command.action = Scan;
      else {
        if (!servoControllerReady) return unavailable(req,"Servo driver unavailable. Check wiring and rescan.");
        if (formField(data,"confirmed") != "1")
          return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Confirm servo supply and clearance first.");
        if (action == "walk") command.action = Walk;
        else if (action == "test" || action == "position") {
          String socket = formField(data,"socket");
          if (socket.length()!=1 || socket[0]<'1' || socket[0]>'4')
            return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Choose socket 1 to 4.");
          command.socket = socket[0]-'0';
          command.action = action == "test" ? Test : Position;
          if (command.action == Position) {
            String offset = formField(data,"offset");
            if (offset!="0" && offset!="-100" && offset!="100")
              return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Invalid manual pulse offset.");
            command.offset = offset.toInt();
          }
        } else return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Unknown action.");
      }
    }
    if (xQueueSend(servoCommands,&command,0)!=pdPASS) return unavailable(req,"Motion queue busy.");
  }
  httpd_resp_set_type(req,"application/json");
  return httpd_resp_send(req,"{\"accepted\":true}",HTTPD_RESP_USE_STRLEN);
}
