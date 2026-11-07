"""Generate native KiCad 8 module-wiring schematic for battery operation.

Pin names identify printed module terminals, not their physical left/right order.
Power and signal pins use electrical types; exported nets are checked separately.
"""
from pathlib import Path
import json
import uuid

ROOT = Path(__file__).resolve().parent
NAME = "Cece_USB_Bench_Wiring"
def uid(): return str(uuid.uuid4())
def q(s): return json.dumps(str(s))
def n(x): return f"{x:.4f}".rstrip('0').rstrip('.') if x else '0'
def fx(size=1.0, justify=None):
    return f'(effects (font (size {n(size)} {n(size)}))'+(f' (justify {justify})' if justify else '')+')'

root_id = uid()
symbols = {}
placed = []
wires = []
labels = []
graphics = []
points = {}

def define(name, width, height, pins, graphic=None):
    """pins: (terminal/name, electrical type, local x, local y, angle)."""
    prefix='C' if name=='BulkCap' else 'U'
    s=[f'(symbol {q(name)} (pin_numbers hide) (pin_names (offset 1.016)) (in_bom yes) (on_board yes)',
       f'(property "Reference" {q(prefix)} (at 0 0 0) {fx()})',
       f'(property "Value" {q(name)} (at 0 0 0) {fx()})',
       f'(symbol {q(name+"_0_1")}']
    if graphic:
        s.extend(graphic)
    else:
        s.append(f'(rectangle (start {n(-width/2)} {n(height/2)}) (end {n(width/2)} {n(-height/2)}) (stroke (width 0.254) (type default)) (fill (type background)))')
    s.extend([')',f'(symbol {q(name+"_1_1")}'])
    for terminal,typ,x,y,angle in pins:
        length=5.08 if name=='BulkCap' else 7.62
        s.append(f'(pin {typ} line (at {n(x)} {n(y)} {angle}) (length {n(length)}) (name {q(terminal)} {fx(.95)}) (number {q(terminal)} {fx(.8)}))')
    s.append('))')
    symbols[name]={'text':'\n'.join(s),'pins':pins,'width':width,'height':height}

def place(name,ref,value,x,y):
    definition=symbols[name];sid=uid()
    top=y-definition['height']/2
    text=[f'(symbol (lib_id {q("CeceModules:"+name)}) (at {n(x)} {n(y)} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid {q(sid)})',
          f'(property "Reference" {q(ref)} (at {n(x)} {n(top-2.54)} 0) {fx(1.1)})',
          f'(property "Value" {q(value)} (at {n(x)} {n(y)} 0) {fx(1.15)})',
          f'(property "Footprint" "" (at {n(x)} {n(y)} 0) (effects (font (size 1 1)) hide))']
    for terminal,_,px,py,_ in definition['pins']:
        points[(ref,terminal)]=(round(x+px,4),round(y-py,4))
        text.append(f'(pin {q(terminal)} (uuid {q(uid())}))')
    text.append(f'(instances (project {q(NAME)} (path {q("/"+root_id)} (reference {q(ref)}) (unit 1)))) )')
    placed.append('\n'.join(text))

def wire(*path):
    for a,b in zip(path,path[1:]):
        assert a != b
        wires.append(f'(wire (pts (xy {n(a[0])} {n(a[1])}) (xy {n(b[0])} {n(b[1])})) (stroke (width 0) (type default)) (uuid {q(uid())}))')
def label(name,point):
    labels.append(f'(label {q(name)} (at {n(point[0])} {n(point[1])} 0) {fx(.95,"left bottom")} (uuid {q(uid())}))')
def text(value,x,y,size=1.2):
    graphics.append(f'(text {q(value)} (at {n(x)} {n(y)} 0) {fx(size,"left top")} (uuid {q(uid())}))')
def junction(x,y):
    graphics.append(f'(junction (at {n(x)} {n(y)}) (diameter 0) (color 0 0 0 0) (uuid {q(uid())}))')
def nc(ref,pin):
    x,y=points[(ref,pin)]
    graphics.append(f'(no_connect (at {n(x)} {n(y)}) (uuid {q(uid())}))')

define('Battery',25.4,30.48,[('+','power_out',20.32,5.08,180),('-','power_out',20.32,-10.16,180)])
define('PushbuttonSwitch',40.64,35.56,[('VIN','power_in',-27.94,5.08,0),('VOUT','power_out',27.94,5.08,180),('GND','power_in',0,-25.4,90),('ON','input',-10.16,25.4,270),('OFF','input',0,25.4,270),('CTRL','tri_state',10.16,25.4,270)])
define('UBEC',35.56,30.48,[('IN+','power_in',-25.4,5.08,0),('IN-','power_in',-25.4,-10.16,0),('OUT+','power_out',25.4,5.08,180),('OUT-','passive',25.4,-10.16,180)])
# Cable terminals are passive; USB supply is used only with JP1 removed.
define('PC_USB',25.4,25.4,[('USB 5V','passive',20.32,10.16,180),('USB GND','passive',20.32,-10.16,180)])
# Functional power-flow types describe JP1 fitted; programming requires removal.
define('RunLink',5.08,10.16,[('IN','power_in',-10.16,0,0),('OUT','power_out',10.16,0,180)])
define('Schottky',20.32,10.16,[('A','power_in',-17.78,0,0),('K','power_out',17.78,0,180)])
define('XIAO_Sense',50.8,71.12,[('USB VBUS','power_in',-33.02,15.24,0),('USB GND','passive',-33.02,-5.08,0),('5V HEADER','power_in',-33.02,-20.32,0),('BAT+','power_in',-33.02,-27.94,0),('3V3','power_out',33.02,20.32,180),('D4 / GPIO5','bidirectional',33.02,10.16,180),('D5 / GPIO6','bidirectional',33.02,0,180),('GND','power_in',33.02,-10.16,180)])
driver_pins=[('5V MOTOR','power_in',-38.1,43.18,0),('GND MOTOR','power_in',-38.1,27.94,0),('3V3 LOGIC','power_in',-38.1,-10.16,0),('SDA','bidirectional',-38.1,-20.32,0),('SCL','input',-38.1,-30.48,0),('GND LOGIC','power_in',-38.1,-40.64,0)]
for socket,cy in enumerate([60.96,86.36,111.76,137.16],1):
    for terminal,dy,typ in [('SIG',-5.08,'output'),('5V',0,'passive'),('GND',5.08,'passive')]:
        driver_pins.append((f'{socket} {terminal}',typ,38.1,101.6-(cy+dy),180))
define('PiicoDev_CE09181',60.96,111.76,driver_pins)
define('SG90',35.56,20.32,[('SIGNAL','input',-25.4,5.08,0),('RED 5V','power_in',-25.4,0,0),('BROWN GND','power_in',-25.4,-5.08,0)])
define('BulkCap',7.62,5.08,[('+','passive',0,7.62,270),('-','passive',0,-7.62,90)],graphic=[
    '(polyline (pts (xy -3.81 2.54) (xy 3.81 2.54)) (stroke (width 0.508) (type default)) (fill (type none)))',
    '(polyline (pts (xy -3.81 -2.54) (xy 3.81 -2.54)) (stroke (width 0.508) (type default)) (fill (type none)))',
    f'(text "+" (at -5.08 3.81 0) {fx(1.27)})'])

place('Battery','BT1','Dualsky 2S / 550mAh',27.94,63.5)
place('PushbuttonSwitch','U2','Mini PB Reverse / LV',101.6,63.5)
place('UBEC','U3','Hobbywing UBEC / 5.0V',172.72,63.5)
place('BulkCap','C1','1000uF / 25V',215.9,66.04)
place('PiicoDev_CE09181','U4','PiicoDev CE09181',271.78,101.6)
place('PC_USB','J1','USB: PROGRAM ONLY',40.64,167.64)
place('XIAO_Sense','U1','XIAO ESP32-S3 Sense',109.22,172.72)
place('RunLink','JP1','RUN',22.86,200.66)
place('Schottky','D1','1N5819',53.34,200.66)
for i,name in enumerate(['SG90 LEFT HIP','SG90 RIGHT HIP','SG90 LEFT FOOT','SG90 RIGHT FOOT'],1):
    place('SG90',f'M{i}',name,365.76,[60.96,86.36,111.76,137.16][i-1])

# Battery -> electronic switch -> UBEC. Negative is not switched.
wire(points['BT1','+'],points['U2','VIN'])
label('BATTERY_PLUS',(60.96,58.42))
wire(points['U2','VOUT'],points['U3','IN+'])
label('SWITCHED_BAT_PLUS',(132.08,58.42))
wire(points['BT1','-'],(55.88,73.66),(55.88,93.98),(101.6,93.98),(137.16,93.98),(137.16,73.66),points['U3','IN-'])
wire(points['U2','GND'],(101.6,93.98));junction(101.6,93.98)
label('GND',(55.88,93.98))
for pin in ['ON','OFF','CTRL']: nc('U2',pin)

# Servo supply with local bulk capacitor.
wire(points['U3','OUT+'],points['C1','+'],points['U4','5V MOTOR'])
wire(points['U3','OUT-'],points['C1','-'],points['U4','GND MOTOR'])
junction(*points['C1','+']);junction(*points['C1','-'])
label('5V_SERVO',(203.2,58.42));label('GND',(223.52,73.66))

# Battery operation powers the ESP via UBEC, removable run link and diode.
# USB is a mutually exclusive programming mode; remove JP1 before USB.
wire(points['J1','USB 5V'],points['U1','USB VBUS']);label('ESP_5V',(63.5,157.48))
wire(points['J1','USB GND'],points['U1','USB GND']);label('GND',(63.5,177.8))
label('5V_SERVO',points['JP1','IN'])
wire(points['JP1','OUT'],points['D1','A'])
wire(points['D1','K'],(73.66,200.66),(73.66,193.04),points['U1','5V HEADER'])
label('ESP_5V',(73.66,193.04))
nc('U1','BAT+')
for src,dst,x,net in [('3V3','3V3 LOGIC',198.12,'3V3_LOGIC'),('D4 / GPIO5','SDA',208.28,'I2C_SDA'),('D5 / GPIO6','SCL',218.44,'I2C_SCL'),('GND','GND LOGIC',228.6,'GND')]:
    a=points['U1',src];b=points['U4',dst]
    wire(a,(x,a[1]),(x,b[1]),b)
    label(net,(152.4,a[1]))

# The named power wires are common inside the driver. No extra motor adapters.
for i in range(1,5):
    for driver_pin,servo_pin,net in [('SIG','SIGNAL',f'SERVO_{i}_PWM'),('5V','RED 5V','5V_SERVO'),('GND','BROWN GND','GND')]:
        a=points['U4',f'{i} {driver_pin}'];b=points[f'M{i}',servo_pin]
        wire(a,b);label(net,(312.42,a[1]))

text('CECE - BATTERY POWER + USB PROGRAMMING',20.32,15.24,2.54)
text('Normal run: battery powers ESP + four SG90s | USB for programming only | Camera / mic / Wi-Fi retained',20.32,22.86,1.35)
text('1. BATTERY / SWITCH / REGULATOR',20.32,30.48,1.6)
text('2. CONTROLLER / SERVO SOCKETS',241.3,30.48,1.6)
text('Leave these three\ncontrol pins unwired.',76.2,27.94,.95)
text('Set and measure\n5.0V BEFORE connecting.',157.48,86.36,1.1)
text('C1 + to 5V; striped\nnegative side to GND.',195.58,99.06,1.05)
text('3. ESP POWER + FOUR LOGIC WIRES',20.32,119.38,1.6)
text('Camera / mic on Sense add-on.\nUSB VBUS and 5V header are\ninternally common (ESP_5V).',86.36,185.42,1.05)
text('JP1: fitted to RUN; REMOVE before USB.\nD1 banded end -> ESP 5V header.',15.24,208.28,1.05)
text('Both address switches OFF\nI2C address 0x44\nSockets 1/2 = hips; 3/4 = feet\nChip channels = 3/2/1/0',246.38,162.56,1.15)
text('POWER / PROGRAMMING MODES\nRUN: no computer USB; JP1 fitted; switch ON.\nBattery -> switch -> UBEC 5V -> servos AND ESP.\nESP branch: JP1 -> D1 -> ESP 5V header.\nPROGRAM: switch OFF; REMOVE JP1; then plug USB.\nAfter programming: unplug USB, then refit JP1.\nD1 alone does NOT prevent PC backfeed; remove JP1.\nNever connect 2S pack directly to ESP 5V or BAT+.\nAll GND labels share ground. Use proper power wire.',20.32,220.98,1.15)
text('BATTERY HAS TWO SEPARATE CONNECTORS\nMain 2-wire lead: RED = pack +; BLACK = pack -.\nMain lead supplies the switch / UBEC as drawn above.\n3-wire BLACK / BLUE / RED plug = 2S balance lead.\nBalance functions: pack -, cell midpoint, pack +.\nWire-to-pin order is NOT verified: do not wire by colour.\nMidpoint is NOT ground; never join it to GND.',157.48,220.98,1.15)
text('CHARGER CONNECTION - PENDING IDENTIFICATION\nUnplug MAIN lead from robot before charging.\nUse a charger explicitly rated for 2S LiPo (8.4V full).\nBalance plug -> charger 2S balance socket, after pin check.\nSome chargers ALSO need main red/black charge leads;\nothers charge through the balance plug alone.\nExact connections require charger model + plug photos.\nDo NOT use an unverified Adafruit 1S USB-C charger.\nESP USB and UBEC do not charge this pack.',294.64,185.42,1.1)
text('MODULE DRAWING\nFollow printed terminal labels, not block positions.\nModule wiring only; no physical footprint mapping.\nSwitch is ON/OFF, not safety isolation.',294.64,243.84,1.05)

external='(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")\n'+ '\n'.join(d['text'] for d in symbols.values())+'\n)\n'
(ROOT/'CeceModules.kicad_sym').write_text(external,encoding='utf-8')
(ROOT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "CeceModules") (type "KiCad") (uri "${KIPRJMOD}/CeceModules.kicad_sym") (options "") (descr "Cece module wiring symbols")))\n')
cached='\n'.join(d['text'].replace('(symbol '+q(name),'(symbol '+q('CeceModules:'+name),1) for name,d in symbols.items())
sheet=[f'(kicad_sch (version 20231120) (generator "eeschema") (uuid {q(root_id)}) (paper "A3")',
       '(title_block (title "Cece - Battery operation / USB programming") (date "2026-11-07") (rev "1.1") (company "Cece the robot") (comment 1 "Remove JP1 before USB. Charger wiring pending model confirmation."))',
       '(lib_symbols\n'+cached+'\n)',*placed,*wires,*labels,*graphics,')']
(ROOT/(NAME+'.kicad_sch')).write_text('\n'.join(sheet)+'\n',encoding='utf-8')
(ROOT/(NAME+'.kicad_pro')).write_text(json.dumps({'meta':{'filename':NAME+'.kicad_pro','version':1},'schematic':{},'text_variables':{}},indent=2)+'\n')
print(ROOT/(NAME+'.kicad_sch'))
