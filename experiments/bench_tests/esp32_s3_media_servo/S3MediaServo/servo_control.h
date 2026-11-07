#pragma once
#include <Wire.h>

// Core Electronics CE09181: socket labels 1..4 map to chip channels 3..0.
constexpr uint8_t SERVO_ADDRESS=0x44;
constexpr uint8_t SERVO_CHANNELS[4]={3,2,1,0};
constexpr uint8_t SERVO_PRESCALE=121;
constexpr float SERVO_PWM_HZ=25000000.0f/(4096.0f*(SERVO_PRESCALE+1));
volatile bool servoControllerReady=false;
volatile uint8_t servoActiveSocket=0;
QueueHandle_t servoCommands=nullptr;
String servoControlToken;
struct ServoCommand { uint8_t action; uint8_t socket; }; // 0 stop, 1 test, 2 rescan
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
  servoCommands=xQueueCreate(1,sizeof(ServoCommand));
  Wire.begin(5,6,100000);Wire.setTimeOut(25);
  servoControllerReady=servoCommands && configureServoController();
  Serial.printf("SERVO_DRIVER address=0x44 found=%s outputs=%s\n",servoControllerReady?"YES":"NO",servoControllerReady?"OFF":"NOT_CONFIRMED");
}
void serviceServoControl() {
  ServoCommand command;
  if(servoCommands && xQueueReceive(servoCommands,&command,0)==pdPASS) {
    if(command.action==0) {
      if(servoControllerReady && !servoDisableOutputs()) {
        servoControllerReady=false;Serial.println("SERVO_STOP_I2C_ERROR: disconnect servo power");
      }
      servoActiveSocket=0;Serial.println("SERVO_STOP signals disabled");
    } else if(command.action==2) {
      servoControllerReady=configureServoController();
      Serial.printf("SERVO_RESCAN found=%s outputs=%s\n",servoControllerReady?"YES":"NO",servoControllerReady?"OFF":"NOT_CONFIRMED");
    } else if(command.action==1 && command.socket>=1 && command.socket<=4 && !servoActiveSocket) {
      if(!servoControllerReady) servoControllerReady=configureServoController();
      if(servoControllerReady) {
        servoActiveSocket=command.socket;servoStarted=millis();servoLastUpdate=0;
        Serial.printf("SERVO_TEST socket=%u pulse_range_us=1400..1600\n",command.socket);
      } else Serial.println("SERVO_TEST_ERROR: no controller at 0x44");
    }
  }
  if(!servoActiveSocket || millis()-servoLastUpdate<20) return;
  servoLastUpdate=millis();uint32_t t=millis()-servoStarted;
  if(t>=1900) {
    if(!servoDisableOutputs()) {servoControllerReady=false;Serial.println("SERVO_STOP_I2C_ERROR: disconnect servo power");}
    Serial.println("SERVO_TEST_DONE signals disabled");return;
  }
  int pulse=1500;
  if(t>=400 && t<700) pulse=1500-int((t-400)*100/300);
  else if(t>=700 && t<1300) pulse=1400+int((t-700)*200/600);
  else if(t>=1300 && t<1600) pulse=1600-int((t-1300)*100/300);
  uint16_t counts=uint16_t(pulse*SERVO_PWM_HZ*4096.0f/1000000.0f+0.5f);
  if(!servoOutput(SERVO_CHANNELS[servoActiveSocket-1],counts,false)) {
    servoActiveSocket=0;servoControllerReady=false;
    servoDisableOutputs();Serial.println("SERVO_I2C_ERROR: disconnect servo power");
  }
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
  if(action=="stop") command.action=0;
  else if(action=="scan") command.action=2;
  else if(action=="test") {
    String socket=formField(data,"socket");
    if(formField(data,"confirmed")!="1" || socket.length()!=1 || socket[0]<'1' || socket[0]>'4')
      return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Confirm measured 5V and unloaded servos first.");
    if(servoActiveSocket) return unavailable(req,"Test running. Press Stop or wait two seconds.");
    command.action=1;command.socket=socket[0]-'0';
  } else return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Unknown servo command.");
  if(!servoCommands || xQueueOverwrite(servoCommands,&command)!=pdPASS)
    return httpd_resp_send_err(req,HTTPD_500_INTERNAL_SERVER_ERROR,"Servo queue unavailable.");
  httpd_resp_set_type(req,"application/json");
  return httpd_resp_send(req,"{\"accepted\":true}",HTTPD_RESP_USE_STRLEN);
}
