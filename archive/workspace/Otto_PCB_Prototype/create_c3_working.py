"""Add provisional nets and two partial supply buses to the placement study.

This is an unfinished engineering draft: no fabrication outputs are allowed.
"""
from pathlib import Path
import pcbnew as p

root = Path(__file__).resolve().parent
libs = Path(r'C:\KiCad\8.0\share\kicad\footprints')
footprints = {}
for lib, name in [('Buzzer_Beeper','Buzzer_TDK_PS1240P02BT_D12.2mm_H6.5mm'),
                  ('Connector_PinHeader_2.54mm','PinHeader_1x02_P2.54mm_Vertical'),
                  ('Resistor_SMD','R_0603_1608Metric')]:
    footprints[(lib,name)] = [p.FootprintLoad(str(libs / (lib + '.pretty')), name)
                              for _ in range(5 if lib == 'Resistor_SMD' else 1)]
b = p.LoadBoard(str(root / 'Otto_C3_PLACEMENT_ONLY.kicad_pcb'))
kept = []
def add(lib, name, ref, value, x, y):
    fp = footprints[(lib,name)].pop()
    if not fp:
        raise RuntimeError((lib, name))
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(p.VECTOR2I(p.FromMM(x), p.FromMM(y)))
    b.Add(fp)
    kept.append(fp)
    return fp
for fp in list(b.GetFootprints()):
    revised_positions = {'U2':(45,10), 'J5':(45,31), 'U3':(40,50),
                         'C2':(30,41), 'R1':(39,34), 'R2':(35,34), 'C1':(39,38)}
    if fp.GetReference() in revised_positions:
        x,y = revised_positions[fp.GetReference()]
        fp.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)))
    if fp.GetReference() == 'J6':
        fp.SetPosition(p.VECTOR2I(p.FromMM(58), p.FromMM(53)))
    if fp.GetReference() == 'J1':
        fp.SetPosition(p.VECTOR2I(p.FromMM(26), p.FromMM(52)))
    if fp.GetReference() == 'BZ1':
        b.Remove(fp)
        kept.append(fp)
add('Buzzer_Beeper','Buzzer_TDK_PS1240P02BT_D12.2mm_H6.5mm','BZ1','PS1240 passive piezo',54,40)
add('Connector_PinHeader_2.54mm','PinHeader_1x02_P2.54mm_Vertical','JP1','REMOVE BEFORE USB',8,18)
for ref, x in [('R3',6),('R4',10),('R5',14),('R6',18)]:
    add('Resistor_SMD','R_0603_1608Metric',ref,'100k',x,35)
add('Resistor_SMD','R_0603_1608Metric','R7','220R',47,43)
netnames = ['GND', '5V_SERVO', 'BAT_PLUS', 'ESP_5V', 'GPIO0', 'GPIO1',
            'GPIO3', 'GPIO4', 'GPIO5', 'GPIO6', 'GPIO7', 'SERVO_LL',
            'SERVO_LR', 'SERVO_FL', 'SERVO_FR', 'ECHO_5V','PIEZO_SIGNAL']
nets = {}
for name in netnames:
    old = b.FindNet(name)
    if old:
        nets[name] = old
    else:
        nets[name] = p.NETINFO_ITEM(b, name)
        b.Add(nets[name])

# USB is assumed to face the low-Y side of both socket rows. Confirm against
# the exact board and orientation before connecting or manufacturing.
mapping = {
    'J1': {'1':'GND','2':'5V_SERVO','3':'SERVO_LL'},
    'J2': {'1':'GND','2':'5V_SERVO','3':'SERVO_LR'},
    'J3': {'1':'GND','2':'5V_SERVO','3':'SERVO_FL'},
    'J4': {'1':'GND','2':'5V_SERVO','3':'SERVO_FR'},
    'J5': {'1':'5V_SERVO','2':'GPIO5','3':'ECHO_5V','4':'GND'},
    'J6': {'1':'BAT_PLUS','2':'GND'},
    'J7': {'1':'GPIO5','2':'GPIO6','3':'GPIO7'},
    'J8': {'1':'ESP_5V','2':'GND','4':'GPIO4','5':'GPIO3','7':'GPIO1','8':'GPIO0'},
    'U2': {'2':'BAT_PLUS','3':'GND','4':'GND','5':'5V_SERVO'},
    'U3': {'1':'GND','2':'GPIO0','3':'SERVO_LL', '4':'GND',
           '5':'GPIO1','6':'SERVO_LR','7':'GND','8':'SERVO_FL',
           '9':'GPIO3','10':'GND','11':'SERVO_FR','12':'GPIO4',
           '13':'GND','14':'5V_SERVO'},
    'R1': {'1':'ECHO_5V','2':'GPIO6'},
    'R2': {'1':'GPIO6','2':'GND'},
    'R3': {'1':'GPIO0','2':'GND'},
    'R4': {'1':'GPIO1','2':'GND'},
    'R5': {'1':'GPIO3','2':'GND'},
    'R6': {'1':'GPIO4','2':'GND'},
    'R7': {'1':'GPIO7','2':'PIEZO_SIGNAL'},
    'BZ1': {'1':'PIEZO_SIGNAL','2':'GND'},
    'JP1': {'1':'5V_SERVO','2':'ESP_5V'},
    'C1': {'1':'5V_SERVO','2':'GND'},
    'C2': {'1':'5V_SERVO','2':'GND'},
}
for fp in b.GetFootprints():
    if fp.GetReference() == 'R1': fp.SetValue('10k 1%')
    if fp.GetReference() == 'R2': fp.SetValue('15k 1%')
    if fp.GetReference() == 'U3': fp.SetValue('SN74AHCT125D')
    for pad in fp.Pads():
        name = mapping.get(fp.GetReference(), {}).get(pad.GetNumber())
        if name:
            pad.SetNet(nets[name])

# Two local bus segments between the four servo headers only. They do not
# connect the full power network and are not proof of adequate current rating.
for net, y in [('GND',52), ('5V_SERVO',54.54)]:
    for a, c in [(11,16),(16,21),(21,26)]:
        tr = p.PCB_TRACK(b)
        tr.SetStart(p.VECTOR2I(p.FromMM(a),p.FromMM(y)))
        tr.SetEnd(p.VECTOR2I(p.FromMM(c),p.FromMM(y)))
        tr.SetLayer(p.B_Cu)
        tr.SetWidth(p.FromMM(1.0))
        tr.SetNet(nets[net])
        b.Add(tr)
p.SaveBoard(str(root/'Otto_C3_WORKING_UNFINISHED.kicad_pcb'), b)
(root/'Otto_C3_WORKING_UNFINISHED.kicad_pro').write_text('{}\n', encoding='utf-8')
