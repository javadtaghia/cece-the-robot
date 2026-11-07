# Arduino Due + four SG90 bench test

This is a standalone temporary test. It does not replace Cece's ESP32 firmware
or run the robot's walking gait. The Due sends 3.3 V control signals directly
to the servos, as requested. Servo power remains a separate regulated 5.0 V.
The SG90 seller does not publish its signal-high threshold; this test checks
whether these specific units respond to 3.3 V control signals.

## Zero and direction calibration

If horn alignment or hip movement looks wrong, first see `ZERO_CALIBRATION.md`.
The standalone single-file `DueZeroCalibration/DueZeroCalibration.ino` was
compiled for the Programming Port, but was not uploaded automatically. It
checks one joint at a time and does not replace the gait or assume horn
re-indexing reverses a motor. The video-review frames remain local and are
excluded from Git.

## Four-servo forward-gait candidate — V6

`DueCeceFourServoWalk/DueCeceFourServoWalk.ino` is the current single-file
four-motor candidate. The user confirmed this mapping:

| Motor | Due pin | Joint | Model direction multiplier |
| --- | --- | --- | --- |
| 1 | D6 | Left body / hip | +1 |
| 2 | D7 | Right body / hip | -1 |
| 3 | D8 | Left foot / ankle | +1 |
| 4 | D9 | Right foot / ankle | -1 |

At 115200 baud, send `4` or `w` to repeat the four-servo forward reference
until `stop` or `x`. `c` optionally holds all four at their configured neutral;
`?` prints the version and help. The startup banner is `CECE4_WALK_V6`.
It does not move automatically at boot and does not require `c` before start.

The tables contain Cece 2's full nominal amplitudes: hips ±15 degrees and
ankles up to approximately 34.25 degrees for edge transfer / foot clearance.
The first hardware check is **half the reference speed** (`TIME_SCALE=2`),
with 50 Hz target updates. It settles at configured neutral for one second,
performs the reference's startup half-step, then repeats the steady cycle.
The startup and repeating tables are separate to avoid incorrectly jumping
the hips from -15 degrees to zero at a table wrap.

`generate_four_servo_walk.py` exports the tables in hardware motor order,
checks the right-side signs, confirms pulse bounds without clipping and
compares ten cycles against the source. `four_servo_walk_check.json` records
the source hash and errors. Node quantization is under 0.005 degrees; linear
interpolation between source nodes can differ from the continuous reference
by up to about 1.24 degrees. These are target comparisons, not measured joints.

The initial `NEUTRAL_US` values are all 1500 and the conversion is initially
10 us/degree. Neither has been physically calibrated. Support the assembled
robot, check that neutral gives correctly aligned legs and feet, and verify
the physical directions and clearance before a ground trial. A mounting
orientation description and a reversed software sign do not prove actual
joint direction. This is open-loop firmware without balance feedback.

This version was compiled for **arduino:sam:arduino_due_x_dbg**, uploaded to
the detected Due **Programming Port COM10**, and its version/help and stop
responses were verified. No movement command or physical walking trial was
performed automatically. See `due_four_walk_v6_upload_check.json`.

## 1. Test the Due first — no servos connected

1. Connect a USB data cable to the Due's **Programming Port**, nearest the DC
   barrel jack. The connector on a standard Due is Micro-USB.
2. Open Arduino IDE. In Boards Manager, install **Arduino SAM Boards
   (32-bits ARM Cortex-M3)** if missing. This core is already installed on this PC.
3. Select **Arduino Due (Programming Port)** and its COM port.
4. Open `DueHello/DueHello.ino`, then click Upload.
5. Open Serial Monitor at **115200 baud**. The built-in LED should blink and
   the monitor should repeatedly print `Hello from the Due - LED ON`.

No USB CDC setting is needed for this Programming Port test.

## 2. Wire the servos with power off

See `Due_Four_SG90_Wiring.png`. No additional logic chip or servo-driver board
is used. Each SG90 already contains a controller and motor driver.

| Connection | Wire |
| --- | --- |
| Due D6 -> servo 1 signal | Orange |
| Due D7 -> servo 2 signal | Orange |
| Due D8 -> servo 3 signal | Orange |
| Due D9 -> servo 4 signal | Orange |
| Regulated +5.0 V -> all four servo power wires | Red |
| Supply negative -> all four servo ground wires | Brown |
| Due GND -> the same supply negative/ground junction | Common ground |

Power the Due through USB. Use the existing Hobbywing UBEC at its **5 V**
setting for servo power. Verify its output with a multimeter first. Do not
connect the servo red wires to Due 3V3 or 5V, or directly to the 2S battery.
Do not join the external +5 V positive rail to the Due's USB-derived +5 V rail.
Only the ground and four signal connections cross between the two systems.
Route the servo supply/return through a suitable power distribution junction
and wires, rather than through Due pins or thin signal jumpers.

## 3. Upload the four-servo test

1. Leave servo power off while uploading.
2. Install **Servo by Michael Margolis, Arduino** using Library Manager if
   necessary. Version 1.3.0 was installed locally for compiling this test.
3. Upload `DueFourServoTest/DueFourServoTest.ino` to the Due Programming Port.
4. Keep the servos out of the robot and unload their horns. The first command
   requests centre, which can move suddenly if a shaft starts elsewhere.
5. With the Due powered by USB and the signal/ground connections checked,
   turn on the separate 5 V servo supply.
6. Open Serial Monitor at **115200 baud**. Type one character and press Send.

| Command | Action |
| --- | --- |
| `1`, `2`, `3`, `4` | Test that servo only |
| `a` | Test all four sequentially |
| `t` | Move all four together; use after individual tests pass |
| `x` | Stop pulses to all four, including during an active test |
| `?` | Print the menu again |

The test waits for a command; it sends no servo pulses at startup. It requests
1500 us centre, then gradually moves to 1400 us, 1600 us and back to centre,
with pauses. This is a small pulse range, not a full 0–180° sweep, and is not
a calibrated angle range for your units. At completion, pulses are detached.
`x` disables control signals; it does not disconnect the servo's power.

Start with one servo connected and command `1`. Then test each remaining servo
and cable. Only then connect all four and use `a`, followed by `t`. Stop and
remove servo power if a motor stalls, growls continuously or gets hot. A
nonresponding servo is not automatically defective: check the 5 V rail under
load, connector polarity, common ground, PWM signal and whether its signal
input recognises 3.3 V.

## Optional: one nominal 90-degree step per command

Upload `DueServo90Step/DueServo90Step.ino` instead of the small-sweep sketch.
The wiring stays the same. Send `c` once to centre the servos, then send
`1` to step servo 1, or `2`/`3`/`4` for the other servos. Wait for `Ready`
before sending the next command. Each servo follows commanded positions
`90 -> 180 -> 90 -> 0 -> 90 ...`, reversing at the ends because SG90 is a
positional servo. `x` stops signals; send `c` again before resuming.

These are **nominal commanded angles**, using an initial 1000–2000 us pulse
mapping. The seller does not specify angle-versus-pulse calibration. Measure
the actual horn movement before claiming 90-degree physical travel. Stop if
a unit reaches its physical stop or keeps growling; do not widen the pulse
range blindly to chase an angle. The first centring movement can be sudden.

## Current single-file test V5: servos 3 and 4 together

Open and upload `DuePair34TestV5/DuePair34TestV5.ino` (single file, embedded
gait tables). The version banner is `DUE_PAIR34_V5_DIRECT_START`. This version
removes the mandatory centre command: **4 starts both servos directly**, after
an 800 ms neutral settling interval. `c` remains optional. `?` prints help,
and `stop` / `x` disables pulses. The earlier V4 file is retained separately.

On this PC the Due was detected on **COM10, Programming Port**. The correct
Arduino CLI target is **arduino:sam:arduino_due_x_dbg**; the shorter
`arduino_due_x` identifies the Native USB Port profile in core 1.6.12.

Use D8 for bench servo 3 (assumed left ankle), D9 for bench servo 4 (assumed
right ankle), direct 3.3 V signals, separate regulated 5 V servo power and
common ground. Check the actual physical joint mapping. At 115200 baud, send
`4` to repeat both feet until `stop` or `x`; no `c` prerequisite is needed.
The help can be checked at any time by sending `?`.

The other two servo signals remain inactive. This pair alone is not a full
forward-walking gait: both hips are still needed for the complete mechanism.

The source is Cece 2's left-ankle and right-ankle reference (joint indices 1
and 3), reduced to **35% amplitude** and slowed to **2x the reference time**.
The 50 Hz output interpolates the embedded samples, with a **2.24 s cycle**.
This is a deliberate reduced-range diagnostic, not the exact full-amplitude
simulation result. The nominal offsets are approximately:

- Left ankle: **-12 to +4.2 degrees**, initially **1380-1542 us**.
- Right ankle: **-4.2 to +12 degrees**, initially **1458-1620 us**.

Pulses have an additional hard cap of ±120 us around each configured neutral.
`generate_pair34_gait.py` regenerates the paired tables and checks repeated
motion, pulse bounds and reference interpolation over five cycles.
`pair34_gait_check.json` records the checks. The pulse/angle conversion of
10 us/degree is an initial assumption, not a calibration of the purchased
servos. Check `NEUTRAL_US`, `MOUNT_DIRECTION` and `US_PER_DEGREE` against the
assembled joints with the feet unloaded. Changing these cannot fix a loose
horn, binding joint, insufficient supply or a board reset.

The sketch prints a cycle counter while running. If the counter continues
but a servo remains at one end, stop and inspect neutral, direction,
mechanical coupling, signal and supply. If the startup banner repeats by
itself, the board is resetting. `x` only disables pulses; disconnect the
external supply to remove servo power.

Earlier versions remain in `DueServo4SingleAnkleGait`, `DueServo4SmallSweep`
and `DueServo4WideSweep`. The earlier single-ankle exporter now targets its
archive folder so it cannot overwrite the current paired-foot sketch.

## Build from the command line

From the repository root, with Arduino CLI available:

```text
arduino-cli compile --fqbn arduino:sam:arduino_due_x_dbg experiments/bench_tests/arduino_due_sg90/DueHello
arduino-cli compile --fqbn arduino:sam:arduino_due_x_dbg experiments/bench_tests/arduino_due_sg90/DueFourServoTest
```

Compilation verifies that the sketches build for the Due, not that the
physical wiring or servos have passed. No board has been flashed automatically.

References: [Arduino Due](https://store.arduino.cc/products/arduino-due),
[Arduino Servo library](https://github.com/arduino-libraries/Servo/blob/master/docs/api.md),
[Arduino servo power troubleshooting](https://support.arduino.cc/hc/en-us/articles/360017053760-Troubleshoot-servo-motors),
[purchased SG90 specifications](https://rapidroboticsaustralia.com.au/products/sg90-micro-servo).
