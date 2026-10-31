# Samsung T5 one-piece MacBook holder — prototype

This design is **one print**: an open skeleton sleeve, two right-angle side
hooks and two top hooks that wrap over the front edge. No screws or separate clips are needed. The T5
slides in from the top; its USB-C end stays at the open end of the sleeve.
Position the upper hook at the **top-left corner** of the laptop display.

## Current files

- `T5_One_Piece_Holder_PROTOTYPE.stl`: the single print file.
- `T5_One_Piece_Holder_PROTOTYPE.3mf`: Bambu Studio project, H2S 0.4 mm nozzle,
  0.20 mm layer height, eSUN PLA+, automatic tree support for critical regions.
- `Samsung_T5_One_Piece_Prototype.FCStd`: FreeCAD assembly. It contains one
  printable solid plus separate SSD and lid **reference-only** envelopes.
- `build_one_piece.py` and `one_piece_geometry_report.json`: generator and
  recorded geometry checks. Earlier multi-piece studies are in
  `previous_multi_piece/`; they are not used by this design.

## Fit and retention

The user measured the lid as 4 mm thick and reported 7 mm black borders at
the left and top. All four hook openings are 6 mm, giving 2 mm total clearance.
The side hooks extend 3 mm over the left bezel; the top hooks extend 5 mm over
the top bezel at the user’s request. That leaves only a nominal **2 mm margin**
to the top picture boundary. Placement, printing tolerances, rounded lid edges
and padding can change that; inspect the actual fit before placing it on the
screen.

The two top hooks rest on the upper edge and return over the front; they
provide positive stops against sliding down. The design does not rely on the
loose side hooks squeezing the screen. The hooks will still put the weight of the SSD, holder and cable on
the lid edge. No design carrying weight there can guarantee zero pressure.
The loose hooks may still disengage if the holder rotates or is pulled away;
real-world retention and safe loading are unverified. Remove the holder before
closing the laptop.

The SSD envelope fits without a modeled collision; the part is one valid CAD
solid and the STL is a single closed manifold. Against a simplified rectangular
lid, a 0.5 mm downward movement makes each of the two top hooks intersect the lid reference,
showing two stops in this idealized geometry. These checks do **not** establish a
safe real-laptop fit, screen protection, adequate strength or USB cable fit.
Inspect and test the unloaded part without forcing it before considering use
with the SSD. The top-left corner shape and cable strain remain to be checked.

## Printing

The export is oriented on its long side (about 24.3 × 80.0 × 67.3 mm). Bambu
Studio sliced it as one object using the saved H2S PLA+ profile and automatic
tree support for critical regions. Its estimate was **9.39 g model + 5.81 g
support = 15.20 g total**, about **1 hour 7 minutes**. This is an estimate,
not a physical print result; inspect the preview and supports before printing.

The rails are deliberately light, so layer orientation and strength matter.
No print, real-laptop fit, or loaded support has been tested.

Source dimensions: [Samsung T5 specifications](https://www.samsung.com/uk/memory-storage/portable-ssd/portable-ssd-t5-1tb-black-mu-pa1t0b-eu/).

## Regenerate

On this Windows PC with FreeCAD 1.1, run from this directory:

```powershell
& 'C:\Program Files\FreeCAD 1.1\bin\python.exe' .\build_one_piece.py --lid 4 --opening 6 --overlap 3 --top-opening 6 --top-overlap 5
```

The generation script exports the print STL and FreeCAD geometry. On a newly
generated FreeCAD file, toggle the printable part and references visible if
FreeCAD initially hides them; reference objects must not be sent to the printer.
