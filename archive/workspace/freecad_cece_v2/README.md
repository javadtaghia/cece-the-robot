# CeCe — OLED belly, LED eyes and actuator layout

Open `CeCe_Actuator_Study.FCStd` in FreeCAD 1.1. The front of the robot is
negative Y; dimensions are in millimetres. Its approximate height is 176 mm.
This is a design study; the earlier `freecad_cece` files are preserved.

The belly has a 23 × 12 mm OLED viewing opening; the two head openings fit
nominal 5 mm LED bodies. The speaker is provisionally located in the head,
with a grille in the rear cover. The head also retains a microphone port.
The OLED glass and LED eyes in the model are visual representations.

## Moving parts

Expand **Actuator Layout** in the model tree. Gold cylinders show rotation
axes and grey solids show the available spaces assumed for five geared motors:

| Actuator | Proposed motion | Envelope shown |
|---|---|---|
| Left and right leg | Hip rotation about the horizontal X axis | 18 × 12 × 10 mm each |
| Left and right arm | Shoulder rotation about the horizontal X axis | 18 × 12 × 10 mm each |
| Head | Yaw about the vertical Z axis | 10 × 12 × 24 mm |

These are generic placeholder shapes, not verified dimensions or specific
parts. Individual leg drive gives a way to move each leg, but it does **not**
provide a demonstrated weight shift or prove the robot can walk. A suitable
motor type, gearing, torque, feedback, mounts, shafts, couplings, shaft
retainers and mechanical stops are still required. The shown motor bodies do
not yet have a supporting chassis, and the head needs a flexible wire loop to
allow rotation. Arms also need couplings and retention. The rear cover and
electronics mounting have not been validated around the drives.

The two AA cells, motor drivers, voltage regulator, speaker, microphone and
display are only dimensional placeholders. Five motors plus audio and the
ESP32 may exceed the available battery current; select actual components and
test starting current and supply voltage before completing the electrical
design. The ESP32 must not drive motors or the speaker directly, and each LED
needs a suitable current-limiting circuit. A motor driver per required channel
and a regulated logic supply must be selected; no wiring or firmware is yet
provided. The component allowances do not include connector, wire, screw or
switch clearances.

## Files and printing

`cece_preview.png` is the assembled appearance. `cece_actuator_cutaway.png`
shows the motor positions through transparent shells. Expand **Component
Allowances** and use Space to show hidden components. **PLA Parts** contains
the individual prototype solids; STLs are saved in `stl/` in assembled
coordinates. They must be oriented and arranged in the slicer. The macro
`../build_cece_actuators.FCMacro` regenerates the study. It uses solid features,
not fully constrained sketches.

The nominal shell wall is 1.6 mm. For a fit test with a 0.4 mm nozzle, try
0.2 mm layers and four walls. Place the face of each shell on the bed, open
side upwards; place covers and feet flat. Inspect the slicer for supports.
Test LED, foot tongue and M2 screw fits on small samples. Do not treat these
STLs as a finished walking robot; the mechanism and mounts need engineering
and physical testing before printing a final set.

`geometry_checks.json` checks each exported PLA shape for validity and one
connected solid. It does not check clearances throughout motion, gait,
strength, fit to purchased parts, wiring, or power.

## First static balance estimate

`static_balance_estimate.json` is a standing-only calculation using actual
CAD solid volumes and hypothetical component weights. With solid PLA at
1.24 g/cm³, 52 g for two AAs and holder, and guessed weights for all other
parts, it estimates 222 g total and centre of mass at (0.32, -0.79, 68.4) mm.
This is within the combined support area of both stationary feet on a level
floor. Actual printed infill and selected parts will change the result.

The COM projection is between the feet. To reach either individual foot's
inside edge it would need to shift about 10 mm sideways; that is the edge,
with zero stability margin. The present design does not have a specified
weight-shift mechanism. Standing balance does not establish that it can step,
recover from disturbances, or walk. See `../check_cece_static_balance.py`
for all assumed masses and the reproducible calculation.
