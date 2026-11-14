# Cece the Robot

Cece is an experimental four-servo robot project. This repository brings
together the mechanical designs, electronics, firmware, emulation and
simulation previously developed across the working folders and an older
hardware repository. It is an independent repository, not a GitHub fork.

## Download Cece

Open the [`codex/cece2` branch](https://github.com/javadtaghia/cece-the-robot/tree/codex/cece2) and choose **Code → Download ZIP**. Extract the whole folder so KiCad can find its symbol library and Arduino can find the sketch headers. This branch includes the current ESP carrier and wiring sheet, the Cece prototype plate, and the separate Cece 2 walking study. To get an updatable copy instead:

```sh
git clone --branch codex/cece2 https://github.com/javadtaghia/cece-the-robot.git
cd cece-the-robot
```

## Bill of materials and Australian prices

The [Cece bill of materials](BILL_OF_MATERIALS.md) lists the quantities, part numbers, original supplier links, order prices and current Australian retail prices for the prototype. The confirmed merchandise from MLAB, Rapid Robotics Australia, Supercheap Hobbies, Little Bird Electronics and Core Electronics totaled **A$225.42 before freight**. The same basket was listed at **A$225.42 on 11 November 2026**. The guide separately lists PLA, ankle hardware, a programming jumper and two choices for the one required 2S balance charger.

## Open the design and print files

| What you want | File and instructions |
| --- | --- |
| Edit the shell | Open the [Cece assembly in FreeCAD](experiments/cece/no_led_mouth/Cece_No_LED_Mouth_Assembly.FCStd). Select `Rounded_Head_Study` for the current head. |
| Inspect the installed camera and controller | Open the [R16 carrier and head assembly](experiments/cece/esp_head_carrier/Cece_Head_ESP_Assembly_R16.FCStd) in FreeCAD. The [R16 fit notes](experiments/cece/esp_head_carrier/R16_REVIEW.md) explain which clearances were modeled. |
| Get the individual STLs | The [15 STLs for the prototype plate](archive/workspace/Cece_Prototype_Plate/) include the body, head, rear cover, arms, legs, feet, washers, heart frame, antenna and charger pieces. This folder preserves the earlier plate; for the current design use the [current head STL](experiments/cece/no_led_mouth/Cece_Head_No_LED_Mouth_TEST_ONLY.stl). |
| Open the whole print plate | Open the [H2S PLA plate](experiments/cece/print_preparation/Cece_PROTOTYPE_NOT_VERIFIED_PLA_H2S.3mf) **as a project** in Bambu Studio to retain the layout and support settings. See the [plate notes](experiments/cece/print_preparation/README.md). |
| Reprint the reinforced ESP support | Use the [R16 carrier STL](experiments/cece/esp_head_carrier/Cece_ESP_Side_Carrier_R16_PREVIEW.stl) for the mesh alone, or the [R16 Bambu Studio project](experiments/cece/esp_head_carrier/Cece_ESP_Support_R16_Reinforced_PLA_TEST_FIT.3mf) for its four-wall PLA settings and supports. |
| Read or edit the wiring | Open the [KiCad 8 project](experiments/cece/electronics/kicad_s3_bench/Cece_USB_Bench_Wiring.kicad_pro), then the [combined schematic](experiments/cece/electronics/kicad_s3_bench/Cece_USB_Bench_Wiring.kicad_sch). You can also [view the drawing without KiCad](experiments/cece/electronics/kicad_s3_bench/preview/Cece_USB_Bench_Wiring.svg). It shows the S3, power supply, driver, four servos, ultrasonic sensor and OLED. See the [OLED pin map](experiments/cece/electronics/kicad_s3_bench/OLED_WIRING.txt) and [battery, USB and charging notes](experiments/cece/electronics/kicad_s3_bench/POWER_AND_CHARGING.txt) when wiring the modules. |

## Program the board or run a simulation

| Goal | Where to start |
| --- | --- |
| Program the physical **XIAO ESP32-S3 Sense** | Start with the [USB hello-world test](experiments/bench_tests/esp32_s3_usb/RUN_USB_TEST.txt). For live camera and mic, individual servo controls and continuous forward walking with a Stop button, open [S3MediaServo.ino](experiments/bench_tests/esp32_s3_media_servo/S3MediaServo/S3MediaServo.ino) in Arduino IDE with its adjacent headers. The [bench guide](experiments/bench_tests/esp32_s3_media_servo/WIRING_AND_TEST.txt) gives the board settings and test sequence. The [hardware test record](experiments/bench_tests/esp32_s3_media_servo/hardware_verification.json) confirms camera and mic capture; it does not confirm servo motion. |
| Emulate the ESP and OLED | Open the [CeceBench folder](experiments/cece/firmware/CeceBench/) in VS Code and follow its [build and Wokwi instructions](experiments/cece/firmware/CeceBench/README.md). This firmware targets the emulated **ESP32-C3**; use the S3 sketch above for the physical Sense board. |
| Move Cece in a room | Follow the [Windows / ROS 2 / Gazebo setup and launch guide](experiments/cece/START_HERE.md). Gazebo simulates the robot and room; the PC bridge drives the joints. |
| Compare walking experiments | Start with the [Bullet gait study](experiments/cece/bullet_gait/README.md). The [Cece 2 speed study](experiments/cece2/README.md) has its own [FreeCAD assembly](experiments/cece2/Cece2_Assembly.FCStd), run instructions and simulation results. It does not release replacement leg STLs. |

## Calibrate each servo before walking

**14 November 2026 walking milestone** (`walking-looks-ok-1411`). The builder reported that Cece's walking looked OK and that the printed [servo angle card](experiments/bench_tests/esp32_s3_media_servo/servo_angle_card.svg) worked well for checking the joints. Print the card at 100% and use it again after changing a servo or refitting a horn.

**Calibration for this Cece** (tag `walking-looks-ok-1411-board-calibration`). On 14 November 2026 at 19:57 Sydney time, the physical ESP reported `CENTER_US 1600 1500 1500 1800` over USB and detected the servo driver at address `0x44`. These are the neutral pulses the firmware uses on a fresh board. The table gives the manual command targets in microseconds. The right hip's three targets were also read back over USB. The other offset targets are calculated from the firmware.

| Driver socket | Installed joint | −10° button | Center | +10° button |
| --- | --- | ---: | ---: | ---: |
| 1 | Left foot | 1500 | 1600 | 1700 |
| 2 | Right foot | 1400 | 1500 | 1600 |
| 3 | Left hip | 1400 | 1500 | 1600 |
| 4 | Right hip | 1750 | 1800 | 1850 |

To verify a replacement ESP after uploading the S3 sketch, open Serial Monitor at **115200** and send lowercase **`s`**. Compare its `CENTER_US` line to the four values above. This reads the settings without moving the legs. An ESP with saved trims uses those values first. To restore a joint on that board, use the calibration controls in step 4 to save the corresponding **Center** pulse, then check again with `s`.

1. Support the body with both feet clear. Open the ESP's phone control page (the `PHONE_URL` shown on serial, or `http://192.168.4.1/` on Cece's own Wi-Fi). Press **Stop movement**, check the 5 V servo supply, then tick the servo confirmation box.
2. Under **Individual servo**, work through the driver sockets one at a time: **1 left foot, 2 right foot, 3 left hip, 4 right hip**, from Cece's perspective. Press **Center** first. Place the card's cross at the pivot. Keep the zero line aligned with the *intended* neutral: a level sole viewed from behind, or a forward-facing foot viewed from above for a hip. Keep the card and body still throughout the check.
3. Press **Center → +10° → Center → −10° → Center**. Let each move settle and read the angle while the servo is holding. Record which side of zero it reaches and how far. The buttons request approximate positions. A centered joint should return to the same neutral and move to opposite sides with roughly even travel. The right hip intentionally has a smaller commanded span.
4. If Center is off and both readings favour one side, open **Calibrate selected joint → Hold saved zero**. Tap **+10 µs** or **−10 µs** one step at a time in the direction that brings the joint toward neutral. These buttons adjust pulse width in microseconds. Wait a second for the last adjustment to settle, then press **Save zero** within the 12-second hold. Confirm the saved message and repeat step 3. If Center is correct but one direction still binds or barely moves, stop and check the linkage. At the trim limit, disconnect servo power before repositioning the horn.
5. Repeat for all four sockets. With Cece supported, restart the controller and recheck each **Center** to confirm the saved settings. Then place Cece on a level surface and try **Start walking forward** with **Stop movement** within reach.

### Where calibration lives in the S3 firmware

| What to adjust | Exact code in the Arduino sketch folder |
| --- | --- |
| Mechanical zero per socket | [`servo_control.h`, line 15, `CENTER_US`](experiments/bench_tests/esp32_s3_media_servo/S3MediaServo/servo_control.h#L15) defines the defaults in socket order: **1600, 1500, 1500, 1800 µs**. For an assembled robot use **Save zero**. [The save handler](experiments/bench_tests/esp32_s3_media_servo/S3MediaServo/servo_control.h#L157) writes the value to the ESP. [The boot loader for joint settings](experiments/bench_tests/esp32_s3_media_servo/S3MediaServo/servo_control.h#L66) restores saved trims over the defaults and applies the older left-foot trim migration. To back up an individual robot's effective values, record the four `centers` from its `/status` page. |
| Travel around a correct zero | [`servo_control.h`, line 22, `jointPulse()`](experiments/bench_tests/esp32_s3_media_servo/S3MediaServo/servo_control.h#L22) applies the travel scale to manual moves and walking. Socket 4 uses half scale. At its default 1800 µs center, **+10°** requests **1850 µs** and **−10°** requests **1750 µs**. The card shows the actual mechanical travel. |
| A joint moves in the wrong direction during walking | [`servo_control.h`, line 91, `WALK_SIGN`](experiments/bench_tests/esp32_s3_media_servo/S3MediaServo/servo_control.h#L91) sets walking direction per socket. The manual buttons use raw pulse direction. Change a walking sign only after checking neutral and confirming the joint moves freely both ways. |

## Find your way around

| What you need | Where to look |
| --- | --- |
| Main Cece studies and project history | [experiments/cece](experiments/cece/README.md) |
| Current 3D body, leg, actuator and full-robot studies | [hip and leg studies](experiments/cece/hip_drive_study/), [head and body](experiments/cece/no_led_mouth/), [heart](experiments/cece/heart_v4/) |
| FreeCAD assemblies and electronics fit analysis | [packaging study](experiments/cece/packaging_study/README.md), [full-electronics studies](experiments/cece/hip_drive_study/) |
| ROS 2, Gazebo room, gait and measurements | [ROS / Gazebo study](experiments/cece/ros2_sim/README.md) |
| Fun designs and accessories | [Fun designs](fun%20designs/README.md) |
| Third-party sources and license notes | [Notices](THIRD_PARTY_NOTICES.md) |

The CAD, circuit and gait are **prototypes**. The current Gazebo controller
has not demonstrated reliable foot lift and landing, and its commands are
generated on the PC rather than derived from the simulated ESP32's servo
outputs. The 14 November physical walking observation is recorded above.
Repeatability, walking speed and charging still need hardware measurements.
The existing PCB studies are drafts.

## Repository and local dependencies

This repository contains the project files and research results, not installed
software, credentials, AI model downloads or local build outputs. The setup
guide explains the dependencies. On the existing Windows installation the
checkout is `workspace/cece_the_robot_repo` and the separately installed tools
remain under `workspace/tools`. Some older analysis scripts use a separately
installed `workspace/cece_mesh_deps`; see the [Bullet reproduction notes](experiments/cece/bullet_gait/README.md).

Cece is the only active design. Legacy reference-robot files have been removed
from the working folders. Use AGENTS.md for the authoritative Cece geometry.
Current studies retain their individual validation limits; a draft filename
does not establish physical fit or a final print release.
