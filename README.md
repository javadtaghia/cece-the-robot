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
| Program the physical **XIAO ESP32-S3 Sense** | Start with the [USB hello-world test](experiments/bench_tests/esp32_s3_usb/RUN_USB_TEST.txt). For camera, mic, Wi-Fi and servo-driver commands, open [S3MediaServo.ino](experiments/bench_tests/esp32_s3_media_servo/S3MediaServo/S3MediaServo.ino) in Arduino IDE with its adjacent headers. The [bench guide](experiments/bench_tests/esp32_s3_media_servo/WIRING_AND_TEST.txt) gives the board settings and test sequence. The [hardware test record](experiments/bench_tests/esp32_s3_media_servo/hardware_verification.json) confirms camera and mic capture; it does not confirm servo motion. |
| Emulate the ESP and OLED | Open the [CeceBench folder](experiments/cece/firmware/CeceBench/) in VS Code and follow its [build and Wokwi instructions](experiments/cece/firmware/CeceBench/README.md). This firmware targets the emulated **ESP32-C3**; use the S3 sketch above for the physical Sense board. |
| Move Cece in a room | Follow the [Windows / ROS 2 / Gazebo setup and launch guide](experiments/cece/START_HERE.md). Gazebo simulates the robot and room; the PC bridge drives the joints. |
| Compare walking experiments | Start with the [Bullet gait study](experiments/cece/bullet_gait/README.md). The [Cece 2 speed study](experiments/cece2/README.md) has its own [FreeCAD assembly](experiments/cece2/Cece2_Assembly.FCStd), run instructions and simulation results. It does not release replacement leg STLs. |

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
outputs. Physical fit, electronics, charging, motor power and walking have
not been validated. The existing PCB studies are drafts, not manufacturing
release files.

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
