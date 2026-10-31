"""KiCad 8 ESP32-C3 carrier placement study; not a fabrication design."""
import pcbnew as p
from pathlib import Path

root = Path(__file__).resolve().parent
libs = Path(r'C:\KiCad\8.0\share\kicad\footprints')
b = p.LoadBoard(str(root / 'Otto_carrier_DRAFT.kicad_pcb'))
for fp in list(b.GetFootprints()):
    if fp.GetReference() == 'A1':
        b.Remove(fp)
    else:
        for pad in fp.Pads():
            pad.SetNetCode(0)

def add(lib, name, ref, value, x, y):
    fp = p.FootprintLoad(str(libs / (lib + '.pretty')), name)
    if not fp:
        raise RuntimeError((lib, name))
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(p.VECTOR2I(p.FromMM(x), p.FromMM(y)))
    b.Add(fp)

# Common 16-hole SuperMini layout, 15.24 mm between rows, 2.54 mm pitch.
# Pinouts vary: no electrical nets are assigned until the purchased board is checked.
for ref,x in [('J7',23),('J8',38.24)]:
    add('Connector_PinSocket_2.54mm','PinSocket_1x08_P2.54mm_Vertical',ref,
        'ESP32-C3 SOCKET PINOUT VERIFY',x,12)
add('Package_SO','SOIC-14_3.9x8.7mm_P1.27mm','U3','74AHCT125 BUFFER TBD',48,45)
add('Resistor_SMD','R_0603_1608Metric','R1','ECHO DIVIDER TOP TBD',42,36)
add('Resistor_SMD','R_0603_1608Metric','R2','ECHO DIVIDER BOTTOM TBD',46,36)
add('Capacitor_SMD','C_0603_1608Metric','C1','100nF TBD',50,36)
add('Capacitor_THT','CP_Radial_D8.0mm_P3.50mm','C2','BULK CAPACITOR TBD',30,42)

note = p.PCB_TEXT(b)
note.SetText('DRAFT - UNROUTED - DO NOT ORDER')
note.SetPosition(p.VECTOR2I(p.FromMM(35),p.FromMM(5)))
note.SetTextSize(p.VECTOR2I(p.FromMM(1),p.FromMM(1)))
note.SetLayer(p.Dwgs_User)
b.Add(note)
p.SaveBoard(str(root/'Otto_C3_PLACEMENT_ONLY.kicad_pcb'),b)
(root/'Otto_C3_PLACEMENT_ONLY.kicad_pro').write_text('{}\n',encoding='utf-8')
