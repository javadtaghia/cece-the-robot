"""Generate a legible, reviewable KiCad circuit draft from explicit pin connections.

The symbols are generic representation blocks; electrical pin types and ERC
still need engineering review. This draft is not a manufacturing release.
"""
from pathlib import Path
import uuid

root = Path(__file__).resolve().parent
uid = lambda: str(uuid.uuid4())
project_id = uid()
components = [
 ('J7','ESP32-C3 left socket','Connector_PinSocket_2.54mm:PinSocket_1x08_P2.54mm_Vertical',
  ['GPIO5','GPIO6','GPIO7',None,None,None,None,None]),
 ('J8','ESP32-C3 right socket','Connector_PinSocket_2.54mm:PinSocket_1x08_P2.54mm_Vertical',
  ['ESP_5V','GND',None,'GPIO4','GPIO3',None,'GPIO1','GPIO0']),
 ('U2','Pololu S13V30F5','Connector_PinSocket_2.54mm:PinSocket_1x05_P2.54mm_Vertical',
  [None,'BAT_PLUS','GND','GND','5V_SERVO']),
 ('J6','Battery JST XH','Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical', ['BAT_PLUS','GND']),
 ('JP1','REMOVE BEFORE USB','Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',['5V_SERVO','ESP_5V']),
 ('U3','SN74AHCT125D','Package_SO:SOIC-14_3.9x8.7mm_P1.27mm',
  ['GND','GPIO0','SERVO_LL','GND','GPIO1','SERVO_LR','GND','SERVO_FL','GPIO3','GND','SERVO_FR','GPIO4','GND','5V_SERVO']),
 ('J1','Left leg','Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical',['GND','5V_SERVO','SERVO_LL']),
 ('J2','Right leg','Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical',['GND','5V_SERVO','SERVO_LR']),
 ('J3','Left foot','Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical',['GND','5V_SERVO','SERVO_FL']),
 ('J4','Right foot','Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical',['GND','5V_SERVO','SERVO_FR']),
 ('J5','HC-SR04','Connector_PinSocket_2.54mm:PinSocket_1x04_P2.54mm_Vertical',['5V_SERVO','GPIO5','ECHO_5V','GND']),
 ('R1','10k 1%','Resistor_SMD:R_0603_1608Metric',['ECHO_5V','GPIO6']),
 ('R2','15k 1%','Resistor_SMD:R_0603_1608Metric',['GPIO6','GND']),
 ('R3','100k','Resistor_SMD:R_0603_1608Metric',['GPIO0','GND']),
 ('R4','100k','Resistor_SMD:R_0603_1608Metric',['GPIO1','GND']),
 ('R5','100k','Resistor_SMD:R_0603_1608Metric',['GPIO3','GND']),
 ('R6','100k','Resistor_SMD:R_0603_1608Metric',['GPIO4','GND']),
 ('R7','220R','Resistor_SMD:R_0603_1608Metric',['GPIO7','PIEZO_SIGNAL']),
 ('BZ1','PS1240 piezo','Buzzer_Beeper:Buzzer_TDK_PS1240P02BT_D12.2mm_H6.5mm',['PIEZO_SIGNAL','GND']),
 ('C1','100nF','Capacitor_SMD:C_0603_1608Metric',['5V_SERVO','GND']),
 ('C2','bulk capacitor TBD','Capacitor_THT:CP_Radial_D8.0mm_P3.50mm',['5V_SERVO','GND']),
]

def symbol(n):
    # All pins are passive: this makes the pin connections reviewable, but ERC
    # is not a substitute for checking the actual device's electrical types.
    top=(n-1)*1.27
    s=[f'(symbol "Block{n}" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)',
       '(property "Reference" "U" (at 0 0 0) (effects (font (size 1 1))))',
       '(property "Value" "Block" (at 0 0 0) (effects (font (size 1 1))))',
       f'(symbol "Block{n}_0_1" (rectangle (start -1.27 {top+1.27}) (end 8.89 {-top-1.27}) (stroke (width 0.254) (type default)) (fill (type background))))',
       f'(symbol "Block{n}_1_1"']
    for i in range(n):
        y=top-i*2.54
        s.append(f'(pin passive line (at -5.08 {y} 0) (length 3.81) (name "{i+1}" (effects (font (size 0.8 0.8)))) (number "{i+1}" (effects (font (size 0.8 0.8)))))')
    return ' '.join(s)+'))'

lines=[f'(kicad_sch (version 20231120) (generator "eeschema") (uuid "{project_id}") (paper "A3")', '(lib_symbols']
library=['(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")']
for n in sorted({len(c[3]) for c in components}):
    library.append(symbol(n))
    lines.append(symbol(n).replace(f'(symbol "Block{n}"',f'(symbol "Otto:Block{n}"',1))
library.append(')')
(root/'Otto.kicad_sym').write_text('\n'.join(library),encoding='utf8')
(root/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "Otto") (type "KiCad") (uri "${KIPRJMOD}/Otto.kicad_sym") (options "") (descr "Draft connection blocks")))\n',encoding='utf8')
lines.append(')')
positions = [(45,45),(105,45),(165,45),(225,35),(225,51),(285,45),
             (45,100),(105,100),(165,100),(225,100),(285,100),
             (45,135),(105,135),(165,135),(225,135),(285,135),
             (45,165),(105,165),(165,165),(225,165),(285,165)]
for (ref,val,foot,pins),(x,y) in zip(components, positions):
    x=round(x/1.27)*1.27; y=round(y/1.27)*1.27
    symid=uid(); n=len(pins); top=(n-1)*1.27
    lines.append(f'(symbol (lib_id "Otto:Block{n}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{symid}")')
    lines.append(f'(property "Reference" "{ref}" (at {x+3} {y-top-4} 0) (effects (font (size 1 1))))')
    lines.append(f'(property "Value" "{val}" (at {x+3} {y+top+4} 0) (effects (font (size 1 1))))')
    lines.append(f'(property "Footprint" "{foot}" (at {x} {y} 0) (effects (font (size 1 1)) (hide yes)))')
    lines.append(f'(instances (project "Otto_C3_SCHEMATIC_DRAFT" (path "/{project_id}" (reference "{ref}") (unit 1)))) )')
    for i,net in enumerate(pins):
        yy=y-top+i*2.54
        if net:
            lines.append(f'(label "{net}" (at {x-5.08} {yy} 0) (effects (font (size 0.8 0.8)) (justify right bottom)) (uuid "{uid()}"))')
        else:
            lines.append(f'(no_connect (at {x-5.08} {yy}) (uuid "{uid()}"))')
lines.append(f'(text "UNFINISHED: electrical pin types, power safety, fit and routing require review" (at 70 15 0) (effects (font (size 1.5 1.5))) (uuid "{uid()}"))')
lines.append(')')
(root/'Otto_C3_SCHEMATIC_DRAFT.kicad_sch').write_text('\n'.join(lines),encoding='utf8')
