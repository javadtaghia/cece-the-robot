"""Compare explicit schematic netlist against physical pad assignments."""
from pathlib import Path
import xml.etree.ElementTree as ET
import pcbnew as p

root=Path(__file__).resolve().parent
xml=ET.parse(root/'Otto_C3_SCHEMATIC_DRAFT.xml').getroot()
b=p.LoadBoard(str(root/'Otto_C3_ENGINEERING_DRAFT.kicad_pcb'))
expected={}
for net in xml.findall('./nets/net'):
    name=net.get('name')
    if name.startswith('unconnected-'):
        continue
    for node in net.findall('node'):
        expected[(node.get('ref'),node.get('pin'))]=name.removeprefix('/')
actual={}
for fp in b.GetFootprints():
    for pad in fp.Pads():
        if pad.GetNetname(): actual[(fp.GetReference(),pad.GetNumber())]=pad.GetNetname()
problems=[]
for key in sorted(expected.keys() | actual.keys()):
    if expected.get(key)!=actual.get(key): problems.append((key,expected.get(key),actual.get(key)))
out='Schematic vs PCB net comparison\n'+('PASS: all assigned pads match.\n' if not problems else '\n'.join(map(str,problems))+'\n')
(root/'net_comparison.txt').write_text(out)
print(out)
