"""Check exported KiCad nets, including the single-page ultrasonic circuit."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parent
xml = ET.parse(root / 'Cece_USB_Bench_Wiring.net.xml').getroot()
nets = {n.attrib['name']: {(p.attrib['ref'], p.attrib['pin']) for p in n.findall('node')}
        for n in xml.findall('./nets/net')}
checks = []

def check(name, nodes, exact=False):
    actual = nets[name]
    expected = set(nodes)
    assert (actual == expected if exact else expected <= actual), (name, actual, expected)
    checks.append(name)

check('/BATTERY_PLUS', [('BT1','+'), ('U2','VIN')], True)
check('/SWITCHED_BAT_PLUS', [('U2','VOUT'), ('U3','IN+')], True)
check('/ESP_5V', [('D1','K'), ('J1','USB_5V'), ('U1','5V_HEADER'), ('U1','USB_VBUS')], True)
check('Net-(D1-PadA)', [('D1','A'), ('JP1','OUT')], True)
check('/3V3_LOGIC', [('U1','3V3'), ('U4','3V3_LOGIC')], True)
check('/I2C_SDA', [('U1','D4_/_GPIO5'), ('U4','SDA')], True)
check('/I2C_SCL', [('U1','D5_/_GPIO6'), ('U4','SCL')], True)
check('/ULTRA_TRIG_3V3', [('U1','D0_/_GPIO1'), ('U5','TRIG')], True)
check('/ULTRA_ECHO_3V3', [('U1','D1_/_GPIO2'), ('R1','1'), ('R2','1')], True)
check('/ECHO_RAW_5V', [('U5','ECHO'), ('R1','2')], True)
check('/5V_SERVO', [('U3','OUT+'), ('JP1','IN'), ('C1','+'), ('C2','1'), ('U4','5V_MOTOR'), ('U5','VCC')])
check('/GND', [('BT1','-'), ('U1','GND'), ('U2','GND'), ('U3','IN-'), ('U3','OUT-'),
               ('U4','GND_LOGIC'), ('U4','GND_MOTOR'), ('C1','-'), ('C2','2'), ('R2','2'), ('U5','GND')])
for i in range(1,5):
    check(f'/SERVO_{i}_PWM', [(f'M{i}','SIGNAL'), ('U4',f'{i}_SIG')], True)
    assert {(f'M{i}','RED_5V'), ('U4',f'{i}_5V')} <= nets['/5V_SERVO']
    assert {(f'M{i}','BROWN_GND'), ('U4',f'{i}_GND')} <= nets['/GND']
check('unconnected-(U1-PadBAT+)', [('U1','BAT+')], True)
values = {c.attrib['ref']: c.findtext('value') for c in xml.findall('./components/comp')}
assert values['R1'] == '2.2k / 1%' and values['R2'] == '3.3k / 1%'
assert values['C2'] == '100nF / 25V'
erc = json.loads((root/'erc.json').read_text())
assert len(erc['sheets']) == 1 and all(not s['violations'] for s in erc['sheets'])
report = dict(passed=True, revision='1.3', checks=checks,
              servo_power_checked=True, echo_divider_volts_at_5V=3.0,
              erc_violations=0, physical_hardware_tested=False,
              charger_pinout_verified=False, ultrasonic_firmware_implemented=False)
(root/'connection_verification.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: power, four servos, I2C, ultrasonic wiring and protected ECHO; ERC zero.')
