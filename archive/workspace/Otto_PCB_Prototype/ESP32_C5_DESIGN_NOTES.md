# Otto ESP32-C5 carrier: design direction

Status: concept only. The previous Nano PCB is superseded. No manufacturing
files exist for this ESP32 design yet.

`Otto_C5_PLACEMENT_ONLY.kicad_pcb` is a preliminary mechanical study with the
Nano removed. Its controller rectangle is just a drawing, not a footprint.
All pads are unconnected, and the buzzer, regulator and sensor footprints are
placeholders. Do not order this board. No schematic, validated power circuit,
level shifters, routing, or fabrication/assembly outputs have been completed.
Pin labels inherited from the earlier Nano study are not C5 wiring guidance.

## Intended architecture

- ESP32-C5 development board: exact manufacturer, board dimensions, pinout,
  power-input and antenna geometry must be confirmed from its documentation.
- Four SG90 positional servos, each on its own labelled 3-pin GND / regulated
  5 V / signal connector. Consider keyed servo-compatible headers and
  assembly aids for production; check mating connector compatibility.
- Provide a suitable 5 V servo supply and a stable 3.3 V controller supply.
  Do not use the ESP board's small 3.3 V regulator to power the servos.
- Common ground, adequate bulk and local decoupling, and a current-capable
  power path. Size the regulator, conductors and protection using measured
  simultaneous motor startup and stall currents and selected batteries.
- Use a 3.3 V-to-5 V signal buffer with defined startup behavior for the four
  servo control signals unless the chosen servo's input thresholds demonstrate
  adequate 3.3 V operation across voltage and temperature.
- If using a 5 V HC-SR04, reduce its ECHO output to a safe ESP32-C5 level and
  confirm that its trigger input accepts 3.3 V, or buffer that input too.
  A direct onboard sensor connector needs a mechanical test fit in the head;
  otherwise use a short keyed four-wire harness.
- Onboard passive piezo and an appropriate driver if needed, keyed battery
  connector, power switch, protection, and USB/power-source isolation.
- Keep copper, components, battery and servo leads clear of the antenna per
  the exact module manufacturer's requirements.

## Before layout and purchase of production PCBs

Confirm the exact ESP32-C5 board URL or part number. Super Mini is not a
standardized footprint. Verify available GPIOs and avoid unsuitable boot,
flash, USB and other reserved pins; define mapping only after confirming the
board. Verify programming support and adapt the original Arduino Nano Otto
firmware. Select the battery and connectors; design a complete schematic,
check mechanical fit, ERC/DRC, power-source interactions, and test a prototype
before releasing fabrication, assembly BOM and pick-and-place files.

References:
https://documentation.espressif.com/esp32-c5_datasheet_en.html
https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c5/schematic-checklist.html
https://github.com/Open-Hardware-Leaders/OttoDIY
