"""Static interference audit for the provisional v2 design, in FreeCAD Python."""
import FreeCAD as App, json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'freecad_cece_components')
doc = App.openDocument(os.path.join(OUT, 'CeCe_Component_Study.FCStd'))
motors = [o for o in doc.getObject('Actuator_Layout').Group if 'gearmotor' in o.Name]
ref_names = ['AA_holder_allowance','SuperMini_allowance','Driver_allowance',
             'Driver_2_allowance','Driver_3_allowance','Power_boost_allowance','PWM_controller_allowance',
             'Regulator_allowance','Speaker_allowance','Amplifier_allowance',
             'OLED_board_allowance','Microphone_allowance']
refs = [doc.getObject(x) for x in ref_names]
shells = [doc.getObject(x) for x in ['Torso_shell','Torso_rear_cover',
          'Neck_channel','Neck_rear_strip','Head_shell','Head_rear_cover']]
results = []
for category, pairs in [
    ('motor_motor',[(a,b) for i,a in enumerate(motors) for b in motors[i+1:]]),
    ('motor_electronics',[(a,b) for a in motors for b in refs]),
    ('motor_shell',[(a,b) for a in motors for b in shells]),
    ('electronics_shell',[(a,b) for a in refs for b in shells]),
    ('electronics_electronics',[(a,b) for i,a in enumerate(refs) for b in refs[i+1:]])]:
    for a,b in pairs:
        v = a.Shape.common(b.Shape).Volume
        if v > 0.01:results.append({'category':category,'a':a.Name,'b':b.Name,'overlap_mm3':round(v,2)})
report = {'method':'Static BRep volume intersection only, in assembled position',
          'caveats':'Contact, tolerances, wiring, supports, movement, shaft engagement and component fit are not checked.',
          'overlaps':results}
with open(os.path.join(OUT,'static_interference.json'),'w') as f:json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))

