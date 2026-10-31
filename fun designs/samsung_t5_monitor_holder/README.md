# Samsung T5 one-piece MacBook holder — prototype

This design is **one print**: an open skeleton sleeve, two right-angle side
hooks and a top-edge ledge. No screws or separate clips are needed. The T5
slides in from the top; its USB-C end stays at the open end of the sleeve.
Position the upper hook at the **top-left corner** of the laptop display.

## Current files

- `T5_One_Piece_Holder_PROTOTYPE.stl`: the single print file.
- `Samsung_T5_One_Piece_Prototype.FCStd`: FreeCAD assembly. It contains one
  printable solid plus separate SSD and lid **reference-only** envelopes.
- `build_one_piece.py` and `one_piece_geometry_report.json`: generator and
  recorded geometry checks. Earlier multi-piece studies are in
  `previous_multi_piece/`; they are not used by this design.

## Fit and retention

The user measured the lid as 4 mm thick and the black border as 7 mm wide. The
side hook opening is 6 mm, giving 2 mm of total clearance. The front hook
extends 3 mm over the border, leaving a nominal 4 mm to the picture boundary.
Actual placement, printing tolerances, rounded lid edges and padding can change
those clearances.

The top ledge rests on the upper edge and provides a positive stop against
sliding down; the design does not rely on the loose side hooks squeezing the
screen. The ledge will still put the weight of the SSD, holder and cable on
the lid edge. No design carrying weight there can guarantee zero pressure.
The side hooks can also disengage if the holder rotates or is pulled away;
real-world retention and safe loading are unverified. Remove the holder before
closing the laptop.

The SSD envelope fits without a modeled collision; the part is one valid CAD
solid and the STL is a single closed manifold. Against a simplified rectangular
lid, a 0.5 mm downward movement makes the top ledge intersect the lid reference,
showing a stop in this idealized geometry. These checks do **not** establish a
safe real-laptop fit, screen protection, adequate strength or USB cable fit.
Inspect and test the unloaded part without forcing it before considering use
with the SSD. The top-left corner shape and cable strain remain to be checked.

## Printing

The export is oriented on its long side (about 24.3 × 80.0 × 67.3 mm). Inspect
the slicer preview; the side hooks, frame and top ledge can need supports in
that orientation. No support profile or physical print has been verified.
The solid CAD volume is about 7.70 cm³, or **9.6 g if fully solid PLA at
1.24 g/cm³**. Actual filament will differ and support material is additional.
The rails are deliberately light, so layer orientation and strength matter.

Source dimensions: [Samsung T5 specifications](https://www.samsung.com/uk/memory-storage/portable-ssd/portable-ssd-t5-1tb-black-mu-pa1t0b-eu/).

## Regenerate

On this Windows PC with FreeCAD 1.1, run from this directory:

```powershell
& 'C:\Program Files\FreeCAD 1.1\bin\python.exe' .\build_one_piece.py --lid 4 --opening 6 --overlap 3
```

The generation script exports the print STL and FreeCAD geometry. On a newly
generated FreeCAD file, toggle the printable part and references visible if
FreeCAD initially hides them; reference objects must not be sent to the printer.
