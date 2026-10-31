# Otto C3 PCB — engineering review, not a production release

## Current digital checks

The newer `Otto_C3_ENGINEERING_DRAFT.kicad_pcb` has all currently assigned
nets connected and reports zero KiCad DRC violations in `engineering_drc.txt`.
The numbered-pin schematic draft `Otto_C3_SCHEMATIC_DRAFT.kicad_sch` exports
a netlist whose assigned pads match the board, as recorded in
`net_comparison.txt`. The schematic's symbols have passive pin types, so its
zero ERC count only checks connectivity and formatting; it is **not** a
meaningful power-source, logic-level, or component electrical rules check.
No-connect pads are deliberately excluded and DRC cannot detect missing nets.

## Problems that prevent ordering this board

1. **Regulator module envelope:** The earlier placement would have put a
   top-mounted Pololu module past the board edge. In this updated study its
   socket was moved to allocate room for the 22.9 x 22.9 mm module. U2 is
   still only a socket footprint, so DRC cannot detect module-body collision;
   check the exact orientation, envelope, connector heights and neighbouring
   components with an accurate 3D model before fabrication.
2. **Power capacity:** the revised autorouter attempted 1.0 mm widths for
   battery, 5 V and ground, but some local tracks taper to 0.75 or 0.6 mm,
   and power via drills have been enlarged to 0.5–0.6 mm in the newer trial.
   Neither these routes nor the connector/header ratings have been validated for
   simultaneous servo startup and stall currents. Redesign the high-current
   paths, including return paths, plated through-hole and via current, using
   selected copper weight and measured loads.
3. **Supply isolation:** JP1 provides manual isolation only. Some SuperMini
   boards can backfeed USB; connecting USB with the jumper installed can be
   unsafe. An automatic verified isolation design or a tested, clearly
   documented manual power selection must be completed for plug-and-play use.
4. **Electrical review:** select and validate the precise ESP32-C3 board,
   buffer startup/disabled behavior, piezo circuit, sensor trigger voltage,
   resistor tolerances, bulk capacitor, battery protection and connectors.
   Verify the regulator and servo connector footprints and physical polarity.
5. **Housing/RF:** the Otto body STL has a 69 x 69 x 39 mm outer bounding box;
   the current board is 66 x 58 mm. Outer dimensions do not establish clearance
   around walls, servos, batteries, connector heights or the antenna. Perform
   a 3D clearance check and prototype fit, and keep metal/copper away from the
   ESP32 antenna according to the chosen module's documentation.

After correcting these issues, rerun schematic ERC using proper device pin
types, schematic-to-board comparison, PCB DRC with manufacturer rules, Gerber
and drill inspection, and then build and bench-test a prototype. No Gerbers,
drill files or production BOM are released from this draft.
