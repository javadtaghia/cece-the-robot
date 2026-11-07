# Cece the Robot

Cece is an experimental four-servo robot project. This repository brings
together the mechanical designs, electronics, firmware, emulation and
simulation previously developed across the working folders and an older
hardware repository. It is an independent repository, not a GitHub fork.

**Start here:** [Run the Windows / ROS 2 / Gazebo / Wokwi prototype](experiments/cece/START_HERE.md).

## Find your way around

| What you need | Where to look |
| --- | --- |
| Main Cece studies and project history | [experiments/cece](experiments/cece/README.md) |
| Current 3D body, leg, actuator and full-robot studies | [hip and leg studies](experiments/cece/hip_drive_study/), [head and body](experiments/cece/no_led_mouth/), [heart](experiments/cece/heart_v4/) |
| FreeCAD assemblies and electronics fit analysis | [packaging study](experiments/cece/packaging_study/README.md), [full-electronics studies](experiments/cece/hip_drive_study/) |
| Printable prototype plate | [print preparation](experiments/cece/print_preparation/README.md) |
| ESP32-C3 firmware, modeled OLED and Wokwi circuit | [CeceBench](experiments/cece/firmware/CeceBench/README.md) |
| ROS 2, Gazebo room, gait and measurements | [ROS / Gazebo study](experiments/cece/ros2_sim/README.md) |
| Bullet walking experiments, assumptions and recordings | [Bullet gait study](experiments/cece/bullet_gait/README.md) |
| Electronics and wiring | [battery-powered ESP wiring](experiments/cece/electronics/kicad_s3_bench/Cece_USB_Bench_Wiring.kicad_sch), [wiring draft](experiments/cece/electronics/WIRING_DRAFT.md) |
| Current ESP head carrier and full Cece assembly | [Cece head mounting study](experiments/cece/esp_head_carrier/Cece_Head_ESP_Assembly.FCStd) |
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
