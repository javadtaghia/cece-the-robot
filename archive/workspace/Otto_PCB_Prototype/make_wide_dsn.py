from pathlib import Path
root=Path(__file__).resolve().parent
data=(root/'otto_c3_working.dsn').read_text()
before='(class kicad_default "" 5V_SERVO BAT_PLUS ECHO_5V ESP_5V GND GPIO0 GPIO1'
after='(class kicad_default "" ECHO_5V ESP_5V GPIO0 GPIO1'
if before not in data:
    raise ValueError('Unexpected input routing classes')
data=data.replace(before,after,1)
pos=data.index('    (class kicad_default')
wide='    (class POWER_WIDE "" 5V_SERVO BAT_PLUS GND\n      (circuit (use_via Via[0-1]_600:300_um))\n      (rule (width 1000) (clearance 200))\n    )\n'
data=data[:pos]+wide+data[pos:]
(root/'otto_c3_wide_trial.dsn').write_text(data)
