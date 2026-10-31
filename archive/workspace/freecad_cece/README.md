# CeCe PLA robot — FreeCAD housing prototype

This design follows the supplied green robot reference: rectangular torso,
narrow neck, box head, antenna, heart badge and two broad feet. It is a
**housing and fit prototype, not a completed or proven walking robot**.

Open `CeCe_PLA_Prototype.FCStd` in FreeCAD 1.1. The model uses millimetres,
Z up, and negative Y forward. Overall height is 176 mm; torso is 76 × 48 ×
62 mm. Head is 44 × 32 × 36 mm. Nominal shell wall is 1.6 mm.

The document contains named editable solid features, rather than fully
constrained parametric sketches. To change dimensions and rebuild, edit and run
`../build_cece_freecad.FCMacro`. Exported STLs retain assembly coordinates;
orient, arrange and drop each part to the bed in the slicer.

## What is included

- Hollow torso and head with separate rear covers and M2 screw holes.
- 23 × 12 mm OLED viewing opening, speaker grille and microphone sound port.
- Hollow neck cable channel and separate cover strip.
- Two leg blanks with 3.2 mm crosswise pivot holes and mating foot tongues.
- Wide 28 × 44 mm feet, decorative arms, antenna and heart.
- Hidden reference envelopes for batteries, controller, motor and audio modules.

Expand **Component Allowances** and toggle visibility with Space in FreeCAD
to inspect purchased-part spaces. OLED glass and cyan eyes are display previews;
they are not PLA parts. A 6 × 4 × 10 mm microphone envelope is provisional,
not a selected module specification.

## PLA print starting point

Assuming a 0.4 mm nozzle: begin with 0.2 mm layers and four wall lines.
Orient the open backs of torso and head upward, so their front faces are on
the bed. Orient rear covers flat. Put the flat bottoms of the feet on the bed.
Inspect sliced layers around the internal screw bosses; supports may be needed.
The antenna needs separate orientation/supports. Ream pivot bores as needed.
These are starting settings; printer tolerances have not been measured.

The foot socket is 0.6 mm larger overall than the leg tongue. Test one foot/leg
fit before printing the rest. M2 rear-panel clearance holes are 2.4 mm;
pilot holes are 1.6 mm. Validate screw fit on a scrap coupon before using them.
Use a short screw chosen after measuring the assembled stack; avoid bottoming
out. Neck, badge and antenna are intended to be bonded after fit checks.

## Work remaining before a walking build

1. Confirm the board is ESP32-C3 Super Mini and measure every actual module,
   battery holder, connectors, wires and motor shaft.
2. Select a motor and driver based on measured voltage, torque and starting
   current. Two AA cells require a properly selected regulated logic supply.
3. Engineer the crank, foot-orientation guides, weight transfer, bearings,
   shaft retention, motor mount and arm attachments. The present leg holes
   are placeholders; no working transmission is supplied.
4. Add electronics retention, OLED mounting, USB/switch access and wire routing.
5. Validate an unsupported gait with actual payload, then fabricate and test
   the bare mechanism before adding the shell. Earlier folder simulations
   concern other geometries and do not validate this model.

`geometry_checks.json` reports BRep validity and connected-solid counts for
exported parts. These checks establish geometry integrity only; they do not
prove printability, balance, walking, strength, or electrical compatibility.
