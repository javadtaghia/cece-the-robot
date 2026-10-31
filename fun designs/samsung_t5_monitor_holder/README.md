# Samsung T5 holder — 13-inch MacBook Air M2 (provisional)

**Do not print or clip the hooks to the laptop yet.** The screen-lid thickness,
usable bezel width, edge curvature, and padding thickness have not been measured.
The checked-in hook is a *placeholder* based on a 5.0 mm lid and a 2.0 mm
front overlap. Those numbers are assumptions, not measurements or a claim of
safe fit. Apple lists 11.3 mm for the **whole closed laptop**, not its lid.

The T5 is specified by Samsung as 74 × 57.3 × 10.5 mm. The design places its
74 mm dimension vertically, with the USB-C end at the open top. It uses an
open, ventilated sleeve and two side hooks, each fastened to a side ear.

## Files

- `Samsung_T5_Holder_Assembly_PROVISIONAL.FCStd`: editable FreeCAD assembly,
  including **approximate reference envelopes**, not a model of the actual Mac.
- `T5_holder_print_1_PROVISIONAL.stl`: one T5 sleeve.
- `Monitor_hook_print_2_PROVISIONAL.stl`: print two after the laptop measurements
  are confirmed and the design is regenerated and checked.
- `build_holder.py`: FreeCAD Python source; `geometry_report.json` records the
  assumptions and checks for the current export.

## What must be checked before printing the hooks

1. Measure the thickness of just the open display at the intended contact
   points and the width of the black, non-active border. The bezel overlap must
   stay inside that border, with a margin for printer and placement error.
2. Check the rounded/tapered edges, rubber seal, screen glass, cable path, lid
   opening, balance and the position of the hooks on the real laptop. Do not let
   a clip or padding press on the display pixels or glass.
3. **Side clips have not been proven to resist sliding under the SSD and cable
   weight.** Friction depends on the measured fit and padding; the current model
   does not establish load capacity, hinge loads, or long-term PLA creep. A
   supporting feature or a different mounting method may be needed.
4. Remove the holder before closing the laptop. Do not rely on it until the
   real fit and retention have been tested without the SSD installed.

The side ears have 3.4 mm holes for two M3 bolts and nuts (not included).
If the interface survives the fit and load review, short M3 bolts, nuts and
soft protective pads are expected. Print the sleeve flat on its large back;
the hook STL is oriented on its side. Choose supports after inspecting a slicer
preview; the horizontal screw holes may need attention. No print profile or
physical fit has been validated. Cable-plug size and clearance are unverified.

## Regenerate after measuring

From this folder on this Windows PC, with FreeCAD 1.1 installed:

```powershell
& 'C:\Program Files\FreeCAD 1.1\bin\python.exe' .\build_holder.py --monitor-thickness MEASURED_LID_MM --bezel-overlap SAFE_OVERLAP_MM --padding-clearance PADDING_AND_SLACK_MM
```

The CAD check verifies that a rectangular T5 envelope does not intersect the
sleeve and that the exported shapes are valid solids. It does not verify the
monitor, snap fit, friction, USB plug, print strength, or physical assembly.

Sources: [Samsung T5 specifications](https://www.samsung.com/uk/memory-storage/portable-ssd/portable-ssd-t5-1tb-black-mu-pa1t0b-eu/), [Apple MacBook Air M2 technical specifications](https://support.apple.com/en-gb/111867).
