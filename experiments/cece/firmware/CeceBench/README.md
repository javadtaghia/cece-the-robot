# Cece ESP32-C3 simulator and bench firmware

This project builds real Arduino ESP32-C3 firmware. It is currently a component diagnostic, not a complete walking or voice controller. No physical board, wiring, power system or motion has been verified.

## Checked so far

- Wokwi runs the compiled C3 firmware and shows a modeled HC-SR04 range reading of about 25 cm. An I2C scan detects the modeled PCA9685 servo driver at 0x44. This is functional simulation, not electrical or mechanical certification.
- An SSD1327 custom-chip model displays the firmware's status screen in Wokwi; the simulated ESP32 I2C scan detects it at 0x3D. The model covers the command subset used by this firmware, not the complete display controller, and the physical display remains untested.
- The simulated ESP32 connected to Wokwi Wi-Fi and sent text requests through its private gateway to the PC bridge, receiving responses from Ollama and from OpenAI via AtBots ChatGPT sign-in. It has also retrieved live Sydney weather through the updated bridge. The separate API-key provider has only mocked tests.
- Wokwi does not emulate the ESP32-C3 I2S peripheral. The firmware contains hardware I2S `mic` and `beep` diagnostics, but the microphone, amplifier and speaker have not been emulated or tested on hardware. The experimental robot microphone Wi-Fi path is unverified; camera, robot-side speech playback and a validated walking controller remain outstanding. The camera interface and model are not selected.

An experimental laptop conversational voice application is in `pc_bridge/laptop_voice.py`.
It uses Vosk or faster-whisper for local speech recognition and Windows speech synthesis for
laptop audio. Recognized text goes through Wokwi serial into the running ESP32
firmware, which sends the request over Wi-Fi to the PC bridge and displays the
reply on its modeled OLED. It does not emulate the ESP32's I2S microphone or
amplifier. A generated speech sample and a live laptop-microphone utterance
were transcribed successfully after selecting the built-in WDM-KS microphone.
The voice window has an input-device selector and input-level indication.

The prototype needs `vosk`, `sounddevice`, `pyserial`, Windows
System.Speech, and a locally downloaded Vosk model. Optionally install
`faster-whisper` and provide `--whisper-model PATH_TO_CTRANSLATE2_MODEL`
for the stronger local recognizer. Launch it from the same
Python environment as AtBots with `python pc_bridge/laptop_voice.py --model
PATH_TO_VOSK_MODEL --device DEVICE_INDEX`. Start conversation listens for each
utterance and ends it after a pause; Stop conversation stops between turns.
Recognition is local and the microphone is not monitored while Cece speaks,
so interruption and full-duplex streaming are not yet supported.

Run the Gazebo world with its four joint controllers as described in
`../../ros2_sim/README.md`, then start the bridge with `--port 8768
--provider atbots --sim-motion`. This explicit flag permits the bridge to
invoke the experimental Gazebo gait when asked to move. It never commands
real motors. The Gazebo controller is called by the PC, not via observed
PCA9685 PWM signals. Wokwi's RFC2217 port 4000 must be reachable by the
laptop voice application, and the simulated ESP32 must first connect to
`Wokwi-GUEST` through the serial command documented below. The RFC2217
service is not authenticated; restrict access to trusted environments.

## Wiring

Pin assignments are provisional, not a build-ready schematic. See `../../electronics/WIRING_DRAFT.md`. SDA GPIO0 and SCL GPIO1 connect to the SSD1327 (default 0x3D) and PiicoDev PCA9685 (0x44); HC-SR04 TRIG GPIO7 and ECHO GPIO10 require a verified 3.3 V-safe echo interface. PiicoDev sockets 1, 2, 3, 4 map to PCA channels 3, 2, 1, 0. Servo power is separate from logic with common ground; assess power, polarity and current on the actual system. Never connect a 5 V echo directly to an ESP32 pin.

The firmware sends no servo commands at boot, but a separately powered PCA9685 can retain earlier outputs. Remove servo power before checking connections; start with a restrained individual servo and conservative limits. `release` requests all four signals off, but cannot establish physical safety.

## Run

Install the ESP32 Arduino core and Adafruit SSD1327/GFX libraries, then run `arduino-cli compile --fqbn esp32:esp32:esp32c3 --output-dir build .`. Open this folder in VS Code with the Wokwi extension, then run `Wokwi: Start Simulator`. The generated binary and ELF under `build/` are not committed.

At 115200 baud the bench serial commands include `scan`, `status`, `wifi Wokwi-GUEST -`, `servo 1 90`, `release`, `mic`, `beep` and `ask <http://PC-IP:8765/ask> <message>`. I2S commands are physical-device diagnostics and are not modeled by Wokwi.

For the optional bridge use `python pc_bridge/server.py`; it listens on localhost by default and selects AtBots' ChatGPT provider with model `gpt-6-luna`. Install AtBots in the Python environment used for the bridge, then use its `atbots auth login chatgpt` flow and separately grant plan usage. Account eligibility and model access must be tested; neither is implied by sign-in. AtBots manages its own credentials in the OS credential store. Do not copy tokens or keys into the project.

On this Windows PC, AtBots commit `b244c96b531032291ea87c9e6746cdfda23ea226` required the local patch in `pc_bridge/patches/atbots-windows-keyring.patch`: the credential store rejected a large single entry. The patch stores chunks in the native keychain and updates a manifest after writing them. Synthetic round-trip/deletion and 41 AtBots authentication tests passed; sign-in and a live model call then succeeded. It has not been reviewed or incorporated upstream. The patch contains no credentials.

Alternatively, `--provider openai` uses the Responses API and requires `OPENAI_API_KEY` privately in the bridge process environment; its API billing is separate from chat. `--provider ollama` selects the local model. Weather requests use Open-Meteo for Sydney by default. Override all three of `--city`, `--latitude` and `--longitude` for a different fixed location. Without `--sim-motion`, a request to move returns a message that walking is not yet available. With it, the bridge requests the experimental Gazebo gait; neither mode drives physical servos.

To accept requests from a real ESP32 on a trusted LAN, explicitly choose the PC's LAN address with `--listen <PC-LAN-IP>`. Prototype HTTP is unauthenticated and unencrypted; do not expose it on the public internet or untrusted networks.

For Wokwi VS Code's private gateway, after connecting with `wifi Wokwi-GUEST -`, the local text path is `ask http://host.wokwi.internal:8765/ask Say hello briefly`. Start the bridge first; when using the Ollama provider, its server must also be running. Weather was tested via the same path on port 8766.

The PCA9685 Wokwi model is from https://github.com/bonnyr/wokwi-pca9685-custom-chip (MIT; license included). The SSD1327 model implements only a subset of the controller. References: https://learn.adafruit.com/adafruit-grayscale-1-5-128x128-oled-display ; https://github.com/CoreElectronics/CE-PiicoDev-PyPI/blob/main/src/PiicoDev_Servo.py ; https://docs.wokwi.com/guides/esp32 .

## Experimental laptop-to-robot Wi-Fi messages

This path is implemented but **not yet tested with the purchased ESP32, OLED,
microphone or speaker**. It sends text to the firmware's display buffer. It
includes experimental robot-microphone capture and speaker playback paths,
but does not command physical servos. The camera and autonomous Gazebo behavior also remain separate.

1. Connect the ESP32 to your Wi-Fi using the serial `wifi <ssid> <password>`
   command; `status` reports the IP address. Never paste your password into a
   repository, issue, or chat.
2. In the serial monitor, issue `remote <your-random-token>` with a unique
   random 16–64 character token without spaces. For example, generate one
   privately on your PC with `python -c "import secrets; print(secrets.token_hex(16))"`.
   Do not share it or include it in chat. The token
   stays in RAM and must be configured again after reset. `remote off` disables
   the message endpoint.
3. On the laptop, open the Cece voice app. In the real-robot Wi-Fi section,
   enter `http://` followed by the ESP32 IP address, enter the same token,
   type a message and press **Send**. An acceptance response means the firmware
   accepted the message; it does not prove the display is wired or working.
4. With those fields filled before clicking **Start conversation**, the laptop
   transcribes its microphone locally, sends the recognized text to the robot
   display, asks the laptop bridge for a reply, sends the reply to the display,
   and plays speech on the **laptop speaker**. With the experimental robot
   speaker option checked it also sends the generated PCM to the robot, though
   timing, audio quality and playback on the hardware have not been verified.
   The laptop polls the robot ultrasonic reading; no echo is shown as unavailable.
   Select **Use robot microphone**
   to request 16 kHz mono I2S audio chunks over Wi-Fi instead of using the
   laptop microphone. This path is untested on hardware; the microphone I2S
   slot, wiring, gain and bit alignment must be checked on the actual device. Start the PC bridge as described
   in Start Here. With the robot address left blank, the existing Wokwi path is
   used.

The prototype uses HTTP and sends the token and text **without encryption**.
Use only a trusted private network; do not expose the endpoint to the internet
or use it on public Wi-Fi. The firmware requires a token but has not had a
security audit. Use the robot's USB serial setup only after its power and GPIO
wiring have been independently verified.
