"""Create an unrouted C5 placement study; no MCU footprint is assumed."""
import pcbnew as p
from pathlib import Path

root = Path(__file__).resolve().parent
board = p.LoadBoard(str(root / 'Otto_carrier_DRAFT.kicad_pcb'))
for fp in list(board.GetFootprints()):
    if fp.GetReference() == 'A1':
        board.Remove(fp)
    else:
        for pad in fp.Pads():
            pad.SetNetCode(0)

# A drawing-only placeholder, deliberately not a manufactured footprint.
for a, b in [((25, 12), (43, 12)), ((43, 12), (43, 37)),
             ((43, 37), (25, 37)), ((25, 37), (25, 12))]:
    line = p.PCB_SHAPE()
    line.SetShape(p.SHAPE_T_SEGMENT)
    line.SetStart(p.VECTOR2I(p.FromMM(a[0]), p.FromMM(a[1])))
    line.SetEnd(p.VECTOR2I(p.FromMM(b[0]), p.FromMM(b[1])))
    line.SetLayer(p.Dwgs_User)
    line.SetWidth(p.FromMM(0.15))
    board.Add(line)
note = p.PCB_TEXT(board)
note.SetText('ESP32-C5 BOARD TBD')
note.SetPosition(p.VECTOR2I(p.FromMM(34), p.FromMM(24)))
note.SetTextSize(p.VECTOR2I(p.FromMM(1), p.FromMM(1)))
note.SetLayer(p.Dwgs_User)
board.Add(note)
p.SaveBoard(str(root / 'Otto_C5_PLACEMENT_ONLY.kicad_pcb'), board)
(root / 'Otto_C5_PLACEMENT_ONLY.kicad_pro').write_text('{}\n', encoding='utf-8')
