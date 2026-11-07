// XIAO ESP32-S3 Sense: camera + PDM microphone -> phone over local Wi-Fi.
// Arduino ESP32 3.3.12. USB CDC enabled, OPI PSRAM, 8 MB flash.
// Uses only the included Sense camera/microphone board; no servos or amplifier.
#include <Arduino.h>
#include <WiFi.h>
#include <Preferences.h>
#include <ESP_I2S.h>
#include "esp_camera.h"
#include "esp_http_server.h"
#include "esp_random.h"
#include "web_page.h"

constexpr char VERSION[] = "CECE_S3_PHONE_MEDIA_V1";
constexpr uint32_t SAMPLE_RATE = 16000;
I2SClass microphone(I2S_NUM_0);
bool cameraReady = false, micReady = false;
uint16_t sensorId = 0;
uint32_t lastWifiAttempt = 0, lastAnnouncement = 0;
bool announced = false;
String apName, apPassword;
SemaphoreHandle_t cameraLock, micLock;
struct NetworkSettings { char ssid[33]; char password[64]; };
QueueHandle_t networkQueue;
httpd_handle_t webServer = nullptr, videoServer = nullptr, audioServer = nullptr;

void printStatus() {
  Serial.printf("STATUS %s camera=%s sensor=0x%04x microphone=%s psram_bytes=%u wifi=%s\n",
    VERSION, cameraReady ? "OK" : "FAIL", sensorId, micReady ? "OK" : "FAIL",
    ESP.getPsramSize(), WiFi.status() == WL_CONNECTED ? "CONNECTED" : "NOT_CONNECTED");
  if (WiFi.status() == WL_CONNECTED) Serial.printf("PHONE_URL http://%s/\n", WiFi.localIP().toString().c_str());
}

void setupCamera() {
  if (!psramFound()) { Serial.println("CAMERA: enable OPI PSRAM in Tools before uploading."); return; }
  camera_config_t c = {};
  c.ledc_channel = LEDC_CHANNEL_0; c.ledc_timer = LEDC_TIMER_0;
  c.pin_d0 = 15; c.pin_d1 = 17; c.pin_d2 = 18; c.pin_d3 = 16;
  c.pin_d4 = 14; c.pin_d5 = 12; c.pin_d6 = 11; c.pin_d7 = 48;
  c.pin_xclk = 10; c.pin_pclk = 13; c.pin_vsync = 38; c.pin_href = 47;
  c.pin_sccb_sda = 40; c.pin_sccb_scl = 39;
  c.pin_pwdn = -1; c.pin_reset = -1; c.xclk_freq_hz = 20000000;
  c.pixel_format = PIXFORMAT_JPEG; c.frame_size = FRAMESIZE_QVGA;
  c.jpeg_quality = 12; c.fb_count = 2;
  c.fb_location = CAMERA_FB_IN_PSRAM; c.grab_mode = CAMERA_GRAB_LATEST;
  esp_err_t error = esp_camera_init(&c);
  if (error != ESP_OK) { Serial.printf("CAMERA_INIT_ERROR 0x%x\n", error); return; }
  sensor_t *sensor = esp_camera_sensor_get();
  if (sensor) {
    sensorId = sensor->id.PID;
    if (sensorId == OV3660_PID) { sensor->set_vflip(sensor, 1); sensor->set_brightness(sensor, 1); sensor->set_saturation(sensor, -2); }
  }
  // Confirm actual JPEG bytes, not just successful sensor register access.
  camera_fb_t *frame = esp_camera_fb_get();
  cameraReady = frame && frame->len > 4 && frame->buf[0] == 0xff && frame->buf[1] == 0xd8;
  if (frame) {
    Serial.printf("CAMERA_FRAME width=%u height=%u bytes=%u valid_jpeg=%s\n", frame->width, frame->height, frame->len, cameraReady ? "YES" : "NO");
    esp_camera_fb_return(frame);
  }
}

void setupMicrophone() {
  microphone.setPinsPdmRx(42, 41);
  microphone.setTimeout(200);
  micReady = microphone.begin(I2S_MODE_PDM_RX, SAMPLE_RATE, I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_MONO);
  if (!micReady) Serial.printf("MIC_INIT_ERROR %d\n", microphone.lastError());
}

void commonHeaders(httpd_req_t *req) {
  httpd_resp_set_hdr(req, "Cache-Control", "no-store");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
}
esp_err_t rootHandler(httpd_req_t *req) {
  commonHeaders(req); httpd_resp_set_type(req, "text/html; charset=utf-8");
  return httpd_resp_send(req, PHONE_PAGE, HTTPD_RESP_USE_STRLEN);
}
esp_err_t statusHandler(httpd_req_t *req) {
  char data[300]; const bool connected = WiFi.status() == WL_CONNECTED;
  snprintf(data, sizeof(data), "{\"camera\":%s,\"microphone\":%s,\"sensor\":\"0x%04x\",\"psram\":%u,\"connected\":%s,\"ip\":\"%s\",\"rssi\":%d}",
    cameraReady ? "true" : "false", micReady ? "true" : "false", sensorId,
    ESP.getPsramSize(), connected ? "true" : "false", connected ? WiFi.localIP().toString().c_str() : "", connected ? WiFi.RSSI() : 0);
  commonHeaders(req); httpd_resp_set_type(req, "application/json");
  return httpd_resp_send(req, data, HTTPD_RESP_USE_STRLEN);
}
int hexDigit(char c) { if(c >= '0' && c <= '9') return c-'0'; if(c >= 'A' && c <= 'F') return c-'A'+10; if(c >= 'a' && c <= 'f') return c-'a'+10; return -1; }
String decodeForm(const String &in) {
  String out;
  for (size_t i=0;i<in.length();i++) {
    if(in[i]=='+') out+=' ';
    else if(in[i]=='%' && i+2<in.length() && hexDigit(in[i+1])>=0 && hexDigit(in[i+2])>=0) {
      char c=(hexDigit(in[i+1])<<4)|hexDigit(in[i+2]); if(!c) return String(); out+=c; i+=2;
    } else out+=in[i];
  }
  return out;
}
String formField(const String &body, const char *key) {
  const String prefix = String(key)+"=";
  int start=0;
  while(start < (int)body.length()) {
    int end=body.indexOf('&',start); if(end<0) end=body.length();
    const String field=body.substring(start,end);
    if(field.startsWith(prefix)) return decodeForm(field.substring(prefix.length()));
    start=end+1;
  }
  return String();
}
esp_err_t wifiHandler(httpd_req_t *req) {
  // Reject network reconfiguration submitted by a different website.
  char origin[100]={}, host[80]={};
  if(httpd_req_get_hdr_value_len(req,"Origin")) {
    if(httpd_req_get_hdr_value_str(req,"Origin",origin,sizeof(origin))!=ESP_OK ||
       httpd_req_get_hdr_value_str(req,"Host",host,sizeof(host))!=ESP_OK ||
       String(origin)!=String("http://")+host) {
      httpd_resp_set_status(req,"403 Forbidden");
      return httpd_resp_send(req,"Open Wi-Fi setup directly on Cece.",HTTPD_RESP_USE_STRLEN);
    }
  }
  if(req->content_len <= 0 || req->content_len > 512) return httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "Invalid Wi-Fi form length.");
  char body[513]; size_t used=0;
  while(used < req->content_len) {
    int n=httpd_req_recv(req,body+used,req->content_len-used);
    if(n<=0) return httpd_resp_send_err(req, HTTPD_408_REQ_TIMEOUT, "Form timed out.");
    used+=n;
  }
  body[used]=0;
  String ssid=formField(body,"ssid"), password=formField(body,"password");
  if(ssid.length()==0 || ssid.length()>32 || password.length()>63 || (password.length()>0 && password.length()<8))
    return httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"Use a Wi-Fi name of 1-32 bytes and a password of 8-63 characters, or leave the password empty for an open network.");
  NetworkSettings settings={}; ssid.toCharArray(settings.ssid,sizeof(settings.ssid)); password.toCharArray(settings.password,sizeof(settings.password));
  if(xQueueOverwrite(networkQueue,&settings)!=pdPASS) return httpd_resp_send_err(req,HTTPD_500_INTERNAL_SERVER_ERROR,"Unable to save network settings.");
  memset(&settings,0,sizeof(settings)); memset(body,0,sizeof(body));
  return rootHandler(req);
}
esp_err_t unavailable(httpd_req_t *req, const char *message) {
  httpd_resp_set_status(req, "503 Service Unavailable");
  return httpd_resp_send(req, message, HTTPD_RESP_USE_STRLEN);
}
esp_err_t videoHandler(httpd_req_t *req) {
  if(!cameraReady) return unavailable(req,"Camera not detected. Check the Sense camera board.");
  if(xSemaphoreTake(cameraLock,0)!=pdTRUE) return unavailable(req,"Camera is in use.");
  commonHeaders(req); httpd_resp_set_type(req,"multipart/x-mixed-replace;boundary=ceceframe");
  esp_err_t result=ESP_OK;
  while(result==ESP_OK) {
    camera_fb_t *frame=esp_camera_fb_get(); if(!frame) {result=ESP_FAIL;break;}
    char header[128]; int length=snprintf(header,sizeof(header),"\r\n--ceceframe\r\nContent-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n",frame->len);
    result=httpd_resp_send_chunk(req,header,length);
    if(result==ESP_OK) result=httpd_resp_send_chunk(req,(const char *)frame->buf,frame->len);
    esp_camera_fb_return(frame);
    vTaskDelay(pdMS_TO_TICKS(90));
  }
  xSemaphoreGive(cameraLock); return result;
}
esp_err_t audioHandler(httpd_req_t *req) {
  if(!micReady) return unavailable(req,"Microphone not detected.");
  if(xSemaphoreTake(micLock,0)!=pdTRUE) return unavailable(req,"Microphone is in use.");
  commonHeaders(req); httpd_resp_set_type(req,"application/octet-stream");
  httpd_resp_set_hdr(req,"X-Audio-Format","s16le;rate=16000;channels=1");
  int16_t samples[512]; esp_err_t result=ESP_OK;
  // Discard queued DMA samples so a new listener begins near live time.
  for(int i=0;i<4;i++) microphone.readBytes((char *)samples,sizeof(samples));
  while(result==ESP_OK) {
    size_t n=microphone.readBytes((char *)samples,sizeof(samples));
    n &= ~size_t(1);
    if(!n) {result=ESP_FAIL;break;}
    result=httpd_resp_send_chunk(req,(const char *)samples,n);
  }
  xSemaphoreGive(micLock); return result;
}
bool startServer(httpd_handle_t *server, uint16_t port, uint16_t controlPort) {
  httpd_config_t config=HTTPD_DEFAULT_CONFIG();
  config.server_port=port; config.ctrl_port=controlPort; config.stack_size=8192;
  config.max_open_sockets=3; config.lru_purge_enable=true;
  config.send_wait_timeout=2; config.recv_wait_timeout=5;
  esp_err_t error=httpd_start(server,&config);
  if(error!=ESP_OK) Serial.printf("HTTP_SERVER_ERROR port=%u code=0x%x\n",port,error);
  return error==ESP_OK;
}
void route(httpd_handle_t server,const char *uri,httpd_method_t method,esp_err_t (*handler)(httpd_req_t *)) {
  httpd_uri_t entry={}; entry.uri=uri;entry.method=method;entry.handler=handler;
  esp_err_t error=httpd_register_uri_handler(server,&entry);
  if(error!=ESP_OK) Serial.printf("HTTP_ROUTE_ERROR %s 0x%x\n",uri,error);
}
void showSetup() {
  Serial.printf("SETUP_SSID %s\nSETUP_PASSWORD %s\nSETUP_URL http://%s/\n",apName.c_str(),apPassword.c_str(),WiFi.softAPIP().toString().c_str());
}
void setupWifi() {
  WiFi.mode(WIFI_AP_STA); WiFi.setHostname("cece"); WiFi.setSleep(false); WiFi.setAutoReconnect(true);
  Preferences prefs; prefs.begin("cece-media",false);
  apPassword=prefs.getString("ap-password","");
  if(apPassword.length()<8) {
    uint8_t randomBytes[8]; esp_fill_random(randomBytes,sizeof(randomBytes));
    char password[17];for(size_t i=0;i<8;i++) snprintf(password+i*2,3,"%02x",randomBytes[i]);
    apPassword=password; prefs.putString("ap-password",apPassword);
  }
  char name[32];snprintf(name,sizeof(name),"Cece-Setup-%06X",(unsigned)(ESP.getEfuseMac()&0xffffff));apName=name;
  if(!WiFi.softAP(apName.c_str(),apPassword.c_str(),1,false,2)) Serial.println("SETUP_AP_ERROR");
  String ssid=prefs.getString("ssid",""), password=prefs.getString("password",""); prefs.end();
  showSetup();
  if(ssid.length()) {WiFi.begin(ssid.c_str(),password.c_str());lastWifiAttempt=millis();Serial.println("WIFI_CONNECTING saved network");}
}
// USB diagnostics retrieve actual JPEG/PCM bytes without a Wi-Fi connection.
void serialDiagnostic(char command) {
  if(command=='i') {printStatus();showSetup();}
  else if(command=='c') {
    if(!cameraReady || xSemaphoreTake(cameraLock,0)!=pdTRUE) {Serial.println("JPEG_ERROR camera unavailable or streaming");return;}
    camera_fb_t *frame=esp_camera_fb_get();
    if(frame) {Serial.printf("JPEG %u\n",frame->len);Serial.write(frame->buf,frame->len);Serial.println("\nJPEG_END");esp_camera_fb_return(frame);}
    else Serial.println("JPEG_ERROR no frame");
    xSemaphoreGive(cameraLock);
  } else if(command=='a') {
    if(!micReady || xSemaphoreTake(micLock,0)!=pdTRUE) {Serial.println("PCM_ERROR microphone unavailable or streaming");return;}
    constexpr size_t target=SAMPLE_RATE*2;size_t sent=0;int16_t samples[512];
    for(int i=0;i<4;i++) microphone.readBytes((char *)samples,sizeof(samples));
    Serial.printf("PCM %u\n",target);
    while(sent<target) {size_t wanted=min(sizeof(samples),target-sent);size_t n=microphone.readBytes((char *)samples,wanted);if(!n)break;Serial.write((uint8_t *)samples,n);sent+=n;}
    Serial.println("\nPCM_END");xSemaphoreGive(micLock);
  }
}
void setup() {
  Serial.begin(115200); const uint32_t begin=millis();while(!Serial && millis()-begin<2500) delay(10);
  Serial.printf("\nBOOT %s\n",VERSION);
  cameraLock=xSemaphoreCreateMutex();micLock=xSemaphoreCreateMutex();networkQueue=xQueueCreate(1,sizeof(NetworkSettings));
  if(!cameraLock || !micLock || !networkQueue) {Serial.println("FATAL no memory for locks/queue");while(true)delay(1000);}
  setupCamera();setupMicrophone();setupWifi();
  if(startServer(&webServer,80,32768)) {route(webServer,"/",HTTP_GET,rootHandler);route(webServer,"/status",HTTP_GET,statusHandler);route(webServer,"/wifi",HTTP_POST,wifiHandler);}
  if(startServer(&videoServer,81,32769)) route(videoServer,"/video",HTTP_GET,videoHandler);
  if(startServer(&audioServer,82,32770)) route(audioServer,"/audio",HTTP_GET,audioHandler);
  printStatus();Serial.println("USB commands: i=status/setup details, c=JPEG, a=one second microphone PCM");
}
void loop() {
  NetworkSettings settings;
  if(xQueueReceive(networkQueue,&settings,0)==pdPASS) {
    Preferences prefs;prefs.begin("cece-media",false);prefs.putString("ssid",settings.ssid);prefs.putString("password",settings.password);prefs.end();
    WiFi.disconnect();WiFi.begin(settings.ssid,settings.password);memset(&settings,0,sizeof(settings));
    lastWifiAttempt=millis();announced=false;Serial.println("WIFI_CONNECTING updated network");
  }
  if(WiFi.status()==WL_CONNECTED) {
    if(!announced) {printStatus();announced=true;}
  } else {
    announced=false;
    if(lastWifiAttempt && millis()-lastWifiAttempt>25000 && millis()-lastAnnouncement>15000) {
      Serial.println("WIFI_WAITING: check 2.4 GHz network name/password. Setup Wi-Fi remains available.");lastAnnouncement=millis();
    }
  }
  while(Serial.available()) serialDiagnostic(Serial.read());
  delay(10);
}
