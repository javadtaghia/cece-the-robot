# ESP32-C3 SuperMini Otto carrier — placement study

Status: unfinished. Do not manufacture or power this board. No complete
schematic, manufacturing files, or verified power circuit exist. The original
placement study has unconnected pads. The later routing study has preliminary
net assignments and experimental tracks, but still has an unconnected servo
signal and design-rule warnings. The autorouter used default trace widths;
the servo power paths have not been sized or verified for motor current.
Pads without a net do not count as unconnected in DRC. Silkscreen labels
inherited from the old Nano study are placeholders, not a wiring guide.

Latest partial work: `Otto_C3_ROUTING_STUDY_UNFINISHED.kicad_pcb`; inspect
`c3_routing_drc.txt` for its actual check results. This is not a fabrication
design. `C3_CIRCUIT_DRAFT.md` records the proposed electrical connections.

The study uses two 8-position 2.54 mm-pitch sockets spaced 15.24 mm apart,
based on the common 16-pin ESP32-C3 SuperMini form factor. Individual vendors
can use different physical or electrical pinouts: verify the actual board
against its seller's documentation and by inspection before finalising.

Reference pinout, USB at top: one row from top to bottom 5, 6, 7, 8, 9, 10,
20, 21; opposite row 5V, GND, 3V3, 4, 3, 2, 1, 0. Confirm the actual unit.
Do not assign final MCU nets until the footprint orientation is verified.

Provisional system design: four buffered servo signal outputs; dedicated 5 V
servo power; HC-SR04 echo reduced to 3.3 V and trigger buffered or verified;
passive piezo; battery connector; power regulation, switch and power isolation.
Avoid GPIO2, GPIO8 and GPIO9 for signals that disturb ESP32 boot strapping.
Preserve native USB GPIO18 and GPIO19. The buffer, divider, capacitor, power
module, battery and sensor footprints in the study are placeholders only.
The PCB dimensions and sensor/socket locations are not fitted to the robot.

Before fabrication: choose exact electrical parts and battery; finish and
check the schematic, power path, voltage domains, USB interaction, protection,
RF antenna clearance, pin mapping, mechanical fit, current capacity and
routing; perform ERC/DRC and prototype power and motion tests. Only then
export Gerbers, drill files, assembly BOM and placement files.

References:
https://dl.artronshop.co.th/ESP32-C3%20SuperMini%20datasheet.pdf
https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html
https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf
