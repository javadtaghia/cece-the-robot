"""Generate an intentionally unrouted KiCad 8 placement and connectivity draft."""
import pcbnew as p
from pathlib import Path

root = Path(__file__).resolve().parent
libs = Path(r'C:\KiCad\8.0\share\kicad\footprints')
board = p.BOARD()
nets = {}
for name in ['GND', '5V', 'D2_LEG_L', 'D3_LEG_R', 'D4_FOOT_L', 'D5_FOOT_R', 'D8_TRIG', 'D9_ECHO', 'D13_BUZZ', 'BAT_POS']:
    n = p.NETINFO_ITEM(board, name)
    board.Add(n)
    nets[name] = n

def place(lib, name, ref, value, x, y, mapping):
    fp = p.FootprintLoad(str(libs / (lib + '.pretty')), name)
    if fp is None:
        raise RuntimeError((lib, name))
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(p.VECTOR2I(p.FromMM(x), p.FromMM(y)))
    board.Add(fp)
    for pad in fp.Pads():
        net = mapping.get(pad.GetNumber())
        if net:
            pad.SetNet(nets[net])
    return fp

place('Module', 'Arduino_Nano', 'A1', 'Nano ATmega328P V3', 23, 10,
      {'4':'GND','29':'GND','27':'5V','5':'D2_LEG_L','6':'D3_LEG_R',
       '7':'D4_FOOT_L','8':'D5_FOOT_R','11':'D8_TRIG','12':'D9_ECHO','16':'D13_BUZZ'})
header3 = 'PinHeader_1x03_P2.54mm_Vertical'
for ref, label, x, sig in [('J1','LEFT LEG',6,'D2_LEG_L'),('J2','RIGHT LEG',11,'D3_LEG_R'),
                            ('J3','LEFT FOOT',16,'D4_FOOT_L'),('J4','RIGHT FOOT',21,'D5_FOOT_R')]:
    place('Connector_PinHeader_2.54mm', header3, ref, label, x, 52,
          {'1':'GND','2':'5V','3':sig})
place('Connector_PinSocket_2.54mm','PinSocket_1x04_P2.54mm_Vertical','J5','HC-SR04 VCC TRIG ECHO GND',54,10,
      {'1':'5V','2':'D8_TRIG','3':'D9_ECHO','4':'GND'})
place('Connector_JST','JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical','J6','BATTERY POLARITY TBD',54,38,{})
place('Connector_PinSocket_2.54mm','PinSocket_1x05_P2.54mm_Vertical','U2','POLOLU 4082 PINOUT TBD',61,10,{})
place('Buzzer_Beeper','Buzzer_12x9.5RM7.6','BZ1','PASSIVE PIEZO FOOTPRINT TBD',54,28,{})
for a,b in [((2,2),(68,2)),((68,2),(68,60)),((68,60),(2,60)),((2,60),(2,2))]:
    shape=p.PCB_SHAPE(); shape.SetShape(p.SHAPE_T_SEGMENT); shape.SetStart(p.VECTOR2I(p.FromMM(a[0]),p.FromMM(a[1]))); shape.SetEnd(p.VECTOR2I(p.FromMM(b[0]),p.FromMM(b[1]))); shape.SetLayer(p.Edge_Cuts); shape.SetWidth(p.FromMM(0.05)); board.Add(shape)
p.SaveBoard(str(root/'Otto_carrier_DRAFT.kicad_pcb'),board)
(root/'Otto_carrier_DRAFT.kicad_pro').write_text('{}\n', encoding='utf-8')
