/* Cece ESP32-C3 bench firmware. REAL HARDWARE TARGET; prototype, not a walking controller.
 * SSD1327 128x128, HC-SR04, PiicoDev PCA9685 4-channel servo driver.
 * Wiring remains provisional. Servos do not move until an explicit serial command.
 * Disable/remove servo power until mechanical fit and direction have been checked.
 */
#include <Wire.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include <ESP_I2S.h>
#include <mbedtls/base64.h>
#include <math.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1327.h>

constexpr uint8_t SDA_PIN = 0, SCL_PIN = 1, TRIG_PIN = 7, ECHO_PIN = 10;
constexpr uint8_t SERVO_ADDR = 0x44;
Adafruit_SSD1327 display(128, 128, &Wire, -1, 400000);
bool screen_ok = false, servo_ok = false, driver_configured = false;
unsigned long previous = 0, last_echo_at = 0;
unsigned long last_echo_us = 0;
I2SClass audio;
bool audio_ready = false;
String line;
String last_reply;
WebServer remote_server(80);
String remote_token;
bool remote_started = false;
bool startAudio();

void receiveRemoteMessage() {
  if (remote_token.length() < 16 || remote_server.header("X-Cece-Token") != remote_token) {
    remote_server.send(403, "text/plain", "Forbidden");
    return;
  }
  if (!remote_server.hasArg("plain")) {
    remote_server.send(400, "text/plain", "Missing message");
    return;
  }
  String message = remote_server.arg("plain");
  message.trim();
  if (!message.length() || message.length() > 120) {
    remote_server.send(400, "text/plain", "Message must contain 1-120 bytes");
    return;
  }
  last_reply = message;
  remote_server.send(200, "text/plain", "Message accepted; OLED output not verified");
}

void receiveRemoteMic() {
  if (remote_token.length() < 16 || remote_server.header("X-Cece-Token") != remote_token) {
    remote_server.send(403, "text/plain", "Forbidden"); return;
  }
  if (!startAudio()) { remote_server.send(503, "text/plain", "I2S unavailable"); return; }
  // 256 ms of 16 kHz, signed 16-bit mono PCM from the left I2S slot.
  // INMP441 wiring, slot selection, bit alignment and actual level need bench tests.
  const size_t samples = 4096;
  int16_t *pcm = static_cast<int16_t*>(malloc(samples * sizeof(int16_t)));
  if (!pcm) { remote_server.send(503, "text/plain", "Audio buffer unavailable"); return; }
  int32_t frames[256];
  size_t written = 0;
  while (written < samples) {
    size_t got = audio.readBytes(reinterpret_cast<char*>(frames), sizeof(frames));
    if (!got || got % 8) break;
    for (size_t i = 0; i + 1 < got / sizeof(int32_t) && written < samples; i += 2) {
      pcm[written++] = static_cast<int16_t>(frames[i] >> 16);
    }
  }
  if (written != samples) {
    free(pcm); remote_server.send(503, "text/plain", "I2S capture incomplete"); return;
  }
  remote_server.setContentLength(samples * sizeof(int16_t));
  remote_server.send(200, "application/octet-stream", "");
  remote_server.sendContent(reinterpret_cast<const char*>(pcm), samples * sizeof(int16_t));
  free(pcm);
}

void receiveRemoteStatus() {
  if (remote_token.length() < 16 || remote_server.header("X-Cece-Token") != remote_token) {
    remote_server.send(403, "text/plain", "Forbidden"); return;
  }
  bool valid = last_echo_us > 0 && millis() - last_echo_at < 2000;
  String result = "{\"range_cm\":";
  result += valid ? String(last_echo_us / 58.0f, 1) : "null";
  result += ",\"oled_detected\":"; result += screen_ok ? "true" : "false";
  result += ",\"servo_driver_detected\":"; result += servo_ok ? "true" : "false";
  result += "}";
  remote_server.send(200, "application/json", result);
}

void receiveRemoteSpeaker() {
  if (remote_token.length() < 16 || remote_server.header("X-Cece-Token") != remote_token) {
    remote_server.send(403, "text/plain", "Forbidden"); return;
  }
  if (!remote_server.hasArg("plain")) { remote_server.send(400, "text/plain", "Missing audio"); return; }
  String encoded = remote_server.arg("plain");
  if (!encoded.length() || encoded.length() > 5500) { remote_server.send(400, "text/plain", "Invalid audio size"); return; }
  uint8_t *pcm = static_cast<uint8_t*>(malloc(4096)); size_t decoded = 0;
  if (!pcm) { remote_server.send(503, "text/plain", "Audio buffer unavailable"); return; }
  if (mbedtls_base64_decode(pcm, 4096, &decoded,
      reinterpret_cast<const unsigned char*>(encoded.c_str()), encoded.length()) != 0 || decoded == 0 || decoded % 2) {
    free(pcm); remote_server.send(400, "text/plain", "Invalid audio encoding"); return;
  }
  if (!startAudio()) { free(pcm); remote_server.send(503, "text/plain", "I2S unavailable"); return; }
  int32_t frames[256];
  for (size_t offset = 0; offset < decoded; ) {
    size_t n = 0;
    while (offset + 1 < decoded && n < 128) {
      int16_t sample = static_cast<int16_t>(uint16_t(pcm[offset]) | (uint16_t(pcm[offset + 1]) << 8));
      int32_t expanded = static_cast<int32_t>(sample) * 65536;
      frames[2*n] = expanded; frames[2*n+1] = expanded;
      offset += 2; n++;
    }
    if (audio.write(frames, n * 2 * sizeof(int32_t)) != n * 2 * sizeof(int32_t)) {
      free(pcm); remote_server.send(503, "text/plain", "I2S playback incomplete"); return;
    }
  }
  free(pcm);
  remote_server.send(200, "text/plain", "Audio submitted to I2S; output not verified");
}

void startRemote() {
  if (!remote_started) {
    const char *headers[] = {"X-Cece-Token"};
    remote_server.collectHeaders(headers, 1);
    remote_server.on("/message", HTTP_POST, receiveRemoteMessage);
    remote_server.on("/microphone", HTTP_GET, receiveRemoteMic);
    remote_server.on("/status", HTTP_GET, receiveRemoteStatus);
    remote_server.on("/speaker", HTTP_POST, receiveRemoteSpeaker);
    remote_server.begin();
    remote_started = true;
  }
}


bool present(uint8_t address) { Wire.beginTransmission(address); return Wire.endTransmission() == 0; }
bool regWrite(uint8_t reg, uint8_t value) {
  Wire.beginTransmission(SERVO_ADDR); Wire.write(reg); Wire.write(value); return Wire.endTransmission() == 0;
}
bool setPwm(uint8_t channel, uint16_t off, bool disabled = false) {
  Wire.beginTransmission(SERVO_ADDR); Wire.write(0x06 + 4 * channel);
  Wire.write(0); Wire.write(0); Wire.write(off & 0xff); Wire.write(disabled ? 0x10 : ((off >> 8) & 0x0f));
  return Wire.endTransmission() == 0;
}
bool setupDriver() {
  if (!present(SERVO_ADDR)) return false;
  // Reset and configure ~50Hz; autoincrement allows four-byte channel writes.
  if (!regWrite(0x00, 0x30) || !regWrite(0xfe, 121)) return false;
  for (uint8_t channel = 0; channel < 4; ++channel) if (!setPwm(channel, 0, true)) return false;
  if (!regWrite(0x00, 0x20)) return false;
  delay(2);
  return true;
}
void releaseAll() {
  if (!driver_configured) return;
  bool ok = true;
  for (uint8_t ch = 0; ch < 4; ++ch) ok &= setPwm(ch, 0, true);
  Serial.println(ok ? "Servo signals disabled" : "I2C ERROR: servo disable not confirmed");
}
void scanBus() {
  Serial.println("I2C scan:");
  for (uint8_t addr = 1; addr < 127; ++addr) if (present(addr)) Serial.printf("  0x%02X\n", addr);
}
bool startAudio() {
  if (audio_ready) return true;
  // Shared clocks: BCLK GPIO3, WS GPIO4, amplifier DIN GPIO6, microphone SD GPIO5.
  audio.setPins(3, 4, 6, 5);
  audio_ready = audio.begin(I2S_MODE_STD, 16000, I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_STEREO);
  if (!audio_ready) Serial.println("ERROR: I2S failed to start");
  return audio_ready;
}
void audioBeep() {
  if (!startAudio()) return;
  int32_t frame[128];
  for (int block=0; block<125; ++block) {
    for (int i=0; i<64; ++i) {
      // Conservative digital level: 1/32 full scale, copied into both slots.
      float phase = 2.0f * PI * 440.0f * (block*64+i) / 16000.0f;
      int32_t sample = int32_t(sinf(phase) * 67108864.0f);
      frame[2*i]=sample; frame[2*i+1]=sample;
    }
    if (audio.write(frame, sizeof(frame)) != sizeof(frame)) { Serial.println("ERROR: I2S transmit incomplete"); return; }
  }
  Serial.println("Audio test tone sent; speaker connection not verified");
}
void micSample() {
  if (!startAudio()) return;
  int32_t frame[256];
  size_t got = audio.readBytes(reinterpret_cast<char*>(frame), sizeof(frame));
  int64_t left = 0, right = 0;
  for (size_t i=0; i+1<got/sizeof(int32_t); i+=2) {
    int64_t l=frame[i], r=frame[i+1]; if (l<0) l=-l; if (r<0) r=-r;
    if (l>left) left=l; if (r>right) right=r;
  }
  Serial.printf("I2S mic sample bytes=%u peak_L=%lld peak_R=%lld (raw; not speech recognition)\n", unsigned(got), (long long)left, (long long)right);
}
void command(String cmd) {
  cmd.trim();
  if (cmd.startsWith("remote ")) {
    String token = cmd.substring(7); token.trim();
    if (token == "off") { remote_token = ""; Serial.println("Remote messages disabled"); return; }
    if (token.length() < 16 || token.length() > 64 || token.indexOf(' ') >= 0) {
      Serial.println("ERROR: token must be 16-64 characters without spaces"); return;
    }
    remote_token = token;
    startRemote();
    Serial.println("Remote messages enabled; token is held in RAM only"); return;
  }
  if (cmd.startsWith("wifi ")) {
    String rest = cmd.substring(5); int space = rest.indexOf(' ');
    if (space < 1) { Serial.println("Usage: wifi <ssid> <password-or-dash>"); return; }
    String ssid = rest.substring(0, space), password = rest.substring(space + 1);
    if (password == "-") password = "";
    WiFi.persistent(false); WiFi.mode(WIFI_STA); WiFi.begin(ssid.c_str(), password.c_str());
    Serial.println("WiFi connection started; use status to check."); return;
  }
  if (cmd.startsWith("ask ")) {
    String rest = cmd.substring(4); int space = rest.indexOf(' ');
    if (space < 1 || WiFi.status() != WL_CONNECTED) { Serial.println("Usage: connect WiFi, then ask <http://PC:8765/ask> <message>"); return; }
    String url = rest.substring(0, space), question = rest.substring(space + 1);
    if (!url.startsWith("http://") || question.length() == 0 || question.length() > 200) { Serial.println("ERROR: invalid URL or message"); return; }
    HTTPClient http; http.setTimeout(60000);
    if (!http.begin(url)) { Serial.println("ERROR: could not open bridge URL"); return; }
    http.addHeader("Content-Type", "text/plain; charset=utf-8");
    int code = http.POST(question);
    if (code == HTTP_CODE_OK) { last_reply = http.getString(); last_reply = last_reply.substring(0, 120); Serial.print("LLM: "); Serial.println(last_reply); }
    else Serial.printf("Bridge request failed: %d\n", code);
    http.end(); return;
  }
  if (cmd == "status") {
    if (WiFi.status() == WL_CONNECTED) { Serial.print("WiFi connected IP: "); Serial.println(WiFi.localIP()); }
    else Serial.println("WiFi not connected");
    return;
  }
  if (cmd == "beep") { audioBeep(); return; }
  if (cmd == "mic") { micSample(); return; }
  if (cmd == "scan") { scanBus(); return; }
  if (cmd == "release") { releaseAll(); return; }
  int label, degrees; char extra;
  if (sscanf(cmd.c_str(), "servo %d %d %c", &label, &degrees, &extra) == 2 && label >= 1 && label <= 4 && degrees >= 60 && degrees <= 120) {
    if (!driver_configured) { driver_configured = setupDriver(); servo_ok = driver_configured; }
    if (!driver_configured) { Serial.println("ERROR: PiicoDev driver not found/configured at 0x44"); return; }
    // Core Electronics maps socket labels 1,2,3,4 to PCA9685 channels 3,2,1,0.
    const uint8_t pca_channel = 4 - label;
    const uint16_t pulse_us = 1500 + (degrees - 90) * 10;
    const uint16_t counts = (uint32_t(pulse_us) * 4096 + 10000) / 20000;
    Serial.println(setPwm(pca_channel, counts) ? "Servo signal set; verify actual motion" : "ERROR: I2C write failed");
    return;
  }
  Serial.println("Commands: beep | mic | scan | wifi <ssid> <password-or-dash> | remote <token-or-off> | status | ask <url> <text> | servo <socket 1-4> <60-120 degrees> | release");
}
void setup() {
  Serial.begin(115200); Wire.begin(SDA_PIN, SCL_PIN); Wire.setClock(400000);
  pinMode(TRIG_PIN, OUTPUT); pinMode(ECHO_PIN, INPUT); digitalWrite(TRIG_PIN, LOW);
  servo_ok = present(SERVO_ADDR);
  uint8_t oled = present(0x3d) ? 0x3d : (present(0x3c) ? 0x3c : 0);
  if (oled) screen_ok = display.begin(oled);
  Serial.println("Cece bench: SSD1327, ultrasonic, PiicoDev. Firmware does not send servo commands at boot; driver may retain prior outputs.");
  Serial.println("Commands: beep | mic | scan | wifi <ssid> <password-or-dash> | remote <token-or-off> | status | ask <url> <text> | servo <socket 1-4> <60-120 degrees> | release");
}
void loop() {
  if (remote_started) remote_server.handleClient();
  while (Serial.available()) {
    char c = char(Serial.read());
    if (c == '\n' || c == '\r') { if (line.length()) { command(line); line = ""; } }
    else if (line.length() < 96) line += c;
  }
  if (millis() - previous < 500) return;
  previous = millis();
  digitalWrite(TRIG_PIN, LOW); delayMicroseconds(2); digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10); digitalWrite(TRIG_PIN, LOW);
  unsigned long us = pulseIn(ECHO_PIN, HIGH, 30000);
  last_echo_us = us; last_echo_at = millis();
  Serial.printf("distance: %s %.1f cm; driver: %s\n", us ? "" : "no echo", us / 58.0f, servo_ok ? "found" : "not found");
  if (screen_ok) {
    display.clearDisplay(); display.setTextSize(1); display.setTextColor(SSD1327_WHITE); display.setCursor(0, 0);
    display.println("cece bench"); display.println(); display.print("Range: ");
    if (us) { display.print(us / 58.0f, 1); display.println(" cm"); } else display.println("no echo");
    display.print("Servo driver: "); display.println(servo_ok ? "found" : "missing"); if (last_reply.length()) { display.println(); display.println(last_reply); } display.display();
  }
}
