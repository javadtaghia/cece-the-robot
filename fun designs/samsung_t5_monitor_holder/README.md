# Samsung T5 holder — 13-inch MacBook Air M2, prototype

A ventilated sleeve holds the Samsung T5 behind the screen, with its USB-C end
at the open top. The upper clip has a **top-edge ledge**: hang it on the
MacBook's top-left corner so the ledge carries the holder's weight. The lower
clip locates the holder along the left side. The design does not depend on the
side clips gripping the screen to resist downward sliding.

## Dimensions and safety

- User-measured display lid thickness: **4 mm**.
- User-measured left black border: **7 mm**.
- Side hook opening: **6 mm**, leaving 2 mm total clearance around the lid.
- Nominal front-hook overlap: **3 mm**, leaving 4 mm to the reported picture
  boundary before measurement, printer and placement errors.
- The top ledge extends 18 mm along the top edge and spans the nominal 4 mm
  lid depth. Position the **upper clip at the very top-left corner**; the
  sleeve extends about 13 mm above the lid in this arrangement.

A loose side gap avoids an intentional squeeze on the front and back, but the
weight **must still bear on the lid's top edge**. The real corner curvature,
protective padding, local load, cable pull, print strength and lid/hinge load
have not been tested. The design does not establish that attaching it is safe
for the laptop. Use a thin soft protective pad on the top contact if suitable;
check that padding does not force the front hook against the glass. Remove the
holder before closing the laptop.

The geometric reference lid is a rectangular approximation, not the MacBook's
actual CAD. The CAD check found no overlap in the nominal pose and found a
36 mm³ collision if the upper hook is moved 0.5 mm downward, indicating a
positive stop in that simplified model. It is not a strength, friction,
printer-tolerance or real-laptop fit test.

## Print files

- `T5_holder_print_1_PROVISIONAL.stl`: one SSD sleeve.
- `Lower_side_hook_print_1_PROVISIONAL.stl`: one lower side-positioning hook.
- `Upper_corner_support_print_1_PROVISIONAL.stl`: one upper hook with top ledge.
- `Samsung_T5_Holder_Assembly_PROVISIONAL.FCStd`: FreeCAD assembly, including
  simplified lid and SSD references. `build_holder.py` regenerates the parts;
  `geometry_report.json` records the nominal checks.

The hooks attach to the sleeve with two M3 bolts and nuts, not included. Inspect
the slicer preview: the upper ledge is cantilevered in the supplied print
orientation and will likely need support beneath it; the small horizontal bolt
holes may also need attention. Print the sleeve flat on its back. No printer
profile, physical fit or loaded part has been validated. Do not trust the SSD
to this prototype until the contact, retention and strength have been checked;
test initial fit without the SSD and without forcing any part.

The SSD geometry uses Samsung's published **74 × 57.3 × 10.5 mm** dimensions;
USB plug size and clearance remain unverified. [Samsung specifications](https://www.samsung.com/uk/memory-storage/portable-ssd/portable-ssd-t5-1tb-black-mu-pa1t0b-eu/).

## Regenerate for different measurements

From this folder on this PC, with FreeCAD 1.1 installed:

```powershell
& 'C:\Program Files\FreeCAD 1.1\bin\python.exe' .\build_holder.py --monitor-thickness 4 --bezel-overlap 3 --padding-clearance 2
```

`padding-clearance` is the **total extra jaw space**, so 4 + 2 = 6 mm. Values
must be rechecked against the actual edge and any padding before use.
