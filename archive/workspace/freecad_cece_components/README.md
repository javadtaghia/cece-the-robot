# CeCe compact component study

This model combines the requested 2-AA battery, ESP32-C3 Super Mini, belly OLED,
LED eyes, microphone, speaker and five separately driven body movements. It is
a **component packaging and feasibility study, not a completed robot**. Open
`CeCe_Component_Study.FCStd` in FreeCAD 1.1. Z is up, negative Y is forward.
The body is 76 × 48 × 62 mm; total height is about 176 mm. Feet span 92 mm.
It has not been proven to be the smallest possible robot.

## Candidate parts and placement

These are engineering candidates, not an instruction to buy yet:

| Count | Candidate | Size or defining property | Model location |
|---|---|---|---|
| 5 | [Pololu 1094, 298:1 LP gearmotor](https://www.pololu.com/product/1094) | Conservative 26 × 12 × 10 mm plus 9 mm shaft; 9.5 g | Two hip, two shoulder, one vertical neck |
| 1 | [Adafruit 4440, 0.91-inch I2C OLED](https://www.adafruit.com/product/4440) | 35 × 20 × 4 mm board; ~25 × 7 mm display | Torso front |
| 1 | ESP32-C3 Super Mini | ~22.5 × 18 mm, board variant to confirm | Upper torso |
| 1 | [Adafruit 3421 I2S microphone](https://www.adafruit.com/product/3421) | 16.7 × 12.7 × 1.8 mm board | Head front, next to face port |
| 1 | [Adafruit 1890 speaker](https://www.adafruit.com/product/1890) | 28 mm diameter × 4.5 mm; 8 Ω, 0.25 W rated | Head rear, facing grille |
| 1 | [Adafruit 3006 MAX98357A I2S amplifier](https://www.adafruit.com/product/3006) | 19.4 × 17.8 × 3 mm published, confirm connector height | Head |
| 3 | [Pololu 2135 DRV8835 dual motor driver](https://www.pololu.com/product/2135) | 17.8 × 10.2 mm per carrier | Lower torso |
| 1 | [Adafruit 815 PCA9685 PWM board](https://www.adafruit.com/product/815) | 62.5 × 25.4 × 3 mm without headers | Rear torso; must verify solder and wire clearances |
| 1 | [Adafruit 2030 PowerBoost 1000 Basic](https://www.adafruit.com/product/2030) | 29 × 23 × 2 mm without connectors | Torso |
| 1 | [Pololu 2830 3.3 V step-down](https://www.pololu.com/product/2830) | 12.7 × 17.8 × ~3.6 mm without headers | Torso |
| 2 | 5 mm through-hole LEDs with individual resistors | Exact LED and resistor values not chosen | Head front |
| 2 | AA cells in series | 58 × 34 × 18 mm holder envelope is an assumption | Low torso |

Grey objects in **Actuator Layout** show motor bodies; gold shows axis and
shaft/extension placeholders. Toggle the hidden objects in **Component
Allowances** to inspect component envelopes. The motor is a 6 V nominal part:
the proposed 5.2 V boost rail is below its specification point. The published
45 rpm, 0.36 A stall current and 2.0 kg·cm extrapolated stall torque are at
6 V, not verified at 5.2 V. The 3 mm output is D-shaped; round holes in this
model do not couple it. No encoder, stops, shaft bearings or motor mount are
designed. Output torque must not be treated as a safe continuous operating
torque. The exact model's rear motor terminals and mounting screws need more
space than a simple 26 mm block.

## Power and control concept (not yet a circuit design)

Two series AAs -> switch -> 5.2 V boost -> separate motor-driver supply and
3.3 V buck -> ESP32, PWM board, OLED, microphone and audio electronics. Five
DC motor channels need ten direction/enable signals; a PCA9685 can provide
these via I2C after its logic level, PWM frequency and startup behaviour are
verified. It cannot read joint positions; add sensors or another safe way to
limit motion before operating motors. Two separate LED circuits need current
limiting. ESP32-C3 standard I2S supports paired TX/RX sharing clock and word
select, subject to matching audio formats and GPIO planning. Amplifier outputs
are bridge driven; neither speaker terminal is ground. The selected speaker's
0.25 W rating must be respected by an actual power/volume limit.

Do not connect USB and the external supply together until power-path isolation
for the actual Super Mini board has been designed. Never connect motors or the
speaker directly to ESP32 GPIO. Servo-like position control is not available
from these unencoded DC motors without feedback and firmware.

The boost converter's rated output does not establish what the AA cells can
supply. As an illustration, 1 A at 5.2 V from a 2 V battery pack at an assumed
85% efficiency would require about 3.1 A from the cells before wiring losses.
Real loaded cell voltage, battery contacts, converter startup, ripple, audio
bursts, motor startup and simultaneous stalls must be measured. Staggering
motor starts reduces demand but does not by itself establish safe operation.

## Balance and next work

The `static_balance_estimate.json` uses solid PLA density plus hypothetical
hardware masses and estimates ~237 g. With both feet flat it places the
projected centre of mass between them. Reaching either single-foot support
edge requires roughly 18 mm of lateral COM shift, with zero margin. The
current two hip rotations do not supply a demonstrated weight shift. Wider
motor placement has worsened this requirement compared with the previous
model. **It is not a demonstrated walking mechanism.** Earlier walking
simulations concern different geometry, and some fell.

Before a real build: choose a compact weight-shift/gait mechanism and test it
with a free-base physics model; calculate and measure torque and power using
actual loads; add shaft couplings, supports, brackets, a battery holder, wiring
channels and a flex loop for head rotation; resolve RF antenna clearance,
button, switch and USB access; and check all moving clearances. A package
envelope can pass collision checks while connectors and leads do not fit.
The size and mass may need revision. The STL parts are fit-study artifacts,
not a final fabrication set.

`static_interference.json` checks static volume overlap among the listed
motor, board and shell envelopes. It does not check wires, connections,
mounts, axes, sweeps or stability. All board dimensions are bare-board
envelopes and need clearances for solder, connectors and fasteners.
