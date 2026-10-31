# Otto carrier board — preliminary placement only

**Superseded:** This draft uses an Arduino Nano. The project now targets an
ESP32-C5 Super Mini; do not use this Nano draft for fabrication or wiring.
See `ESP32_C5_DESIGN_NOTES.md`. The exact C5 board and pinout remain to be
confirmed before creating a new controller footprint.

This is an **unrouted, incomplete draft**, not a PCB to manufacture. Open
`Otto_carrier_DRAFT.kicad_pro` in KiCad 8 and then open the PCB editor. White
ratsnest lines show intended connections. No schematic or Gerbers exist yet.

The goal is a low-wiring carrier: socketed classic ATmega328P Nano V3, four
2.54 mm servo headers, HC-SR04 socket, board-mounted 5 V power module, battery
connector and onboard passive piezo. The physical outline and connector
locations are placeholders, not verified to fit the printed Otto body.

## Intended connections

Servo header pin order is 1 GND, 2 regulated 5 V, 3 signal. J1 D2 left leg,
J2 D3 right leg, J3 D4 left foot and J4 D5 right foot. J5 is intended as a
1x4 female socket for a standard HC-SR04, with pin 1 VCC, pin 2 TRIG (D8),
pin 3 ECHO (D9), pin 4 GND. Verify the physical sensor's labels and mounting
orientation before plugging it in. Servo housings are unkeyed: verify polarity.

The battery and regulator positions are deliberately **unassigned**. Confirm
the actual regulator's pin order, physical orientation, connector polarity,
current handling, battery chemistry, switch, reverse protection, bulk
capacitance and USB/external-5V isolation before wiring them. The piezo is
also unassigned: select an exact component and design its driver. Never put
battery voltage directly into a Nano or servo 5 V rail. Test power and USB
behavior before attaching motors.

## Work required before ordering boards

1. Select the exact controller, regulator, buzzer, battery/connector and header
   components; lock manufacturer part numbers and assembly orientation.
2. Make a complete schematic, connect and protect the power path, assign all
   footprints, and run electrical rules checks. Add required decoupling and
   a suitable power switch and battery/USB isolation.
3. Measure the actual Otto shell and components; revise the 66 x 58 mm draft
   outline and provide mounting holes, USB access and connector clearances.
4. Route the board with power-current widths and clearances, then run KiCad
   DRC, inspect 3D and make a prototype. Verify voltage, current, polarity,
   servo operation and brownouts before committing to production.
5. Generate Gerber, drill, BOM and component placement files only after the
   prototype is reviewed and tested. This draft is not ready for those files.

`create_layout.py` reproduces the draft using KiCad 8's bundled Python and
standard footprints. It is a starting point, not a verified circuit.
