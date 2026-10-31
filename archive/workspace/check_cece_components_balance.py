"""First-order static balance screen of the v2 model; FreeCAD Python."""
import FreeCAD as App, os, json

root = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(root, 'freecad_cece_components')
doc = App.openDocument(os.path.join(out, 'CeCe_Component_Study.FCStd'))
items = []
for obj in doc.getObject('PLA_Parts').Group + [doc.getObject('Heart_badge')]:
    v = obj.Shape.Volume
    c = obj.Shape.Solids[0].CenterOfMass
    items.append((obj.Name, v * 0.00124, c.x, c.y, c.z))

# These are explicitly hypothetical masses, not selected hardware specs.
assumptions = [
    ('AA_holder_allowance',52),   # two cells 48 g plus holder 4 g
    ('SuperMini_allowance',5), ('Driver_allowance',1),
    ('Driver_2_allowance',1), ('Driver_3_allowance',1),
    ('Power_boost_allowance',6), ('PWM_controller_allowance',5.5),
    ('Regulator_allowance',1), ('Speaker_allowance',6),
    ('Amplifier_allowance',3), ('OLED_board_allowance',5),
    ('Microphone_allowance',0.4),
    ('Left_leg_gearmotor',9.5), ('Right_leg_gearmotor',9.5),
    ('Left_arm_gearmotor',9.5), ('Right_arm_gearmotor',9.5), ('Head_gearmotor',9.5),
    ('LED_eye_L8',0.5), ('LED_eye_8',0.5),
]
for name,mass in assumptions:
    c = doc.getObject(name).Shape.Solids[0].CenterOfMass
    items.append((name,mass,c.x,c.y,c.z))
# Allow 8 g for undetailed wiring and screws at a guessed position.
items.append(('wire_and_fastener_allowance',8,0,0,78))
mass = sum(p[1] for p in items)
com = [sum(p[1]*p[i] for p in items)/mass for i in (2,3,4)]
# Flat-foot contact regions: x in [-46,-18] / [18,46], y in [-29,15],
# with corner radii. At the calculated y the inner x edges are straight.
if not -25 < com[1] < 11:
    raise ValueError('Foot corner geometry needs explicit projection check')
result = {
 'scope':'static standing only, both feet flat, level floor, guessed component masses',
 'total_mass_g':round(mass,2),
 'center_of_mass_mm':[round(x,2) for x in com],
 'both_feet_support_hull_x_mm':[-46,46],
 'left_foot_support_x_mm':[-46,-18], 'right_foot_support_x_mm':[18,46],
 'minimum_com_shift_toward_left_foot_mm':round(com[0]+18,2),
 'minimum_com_shift_toward_right_foot_mm':round(18-com[0],2),
 'mass_assumptions':'PLA at 1.24 g/cm3, fully solid volumes; guessed hardware masses, including 52 g cells plus holder and 8 g wiring/fasteners',
 'limitation':'Boundary is zero margin; does not include stability reserve, motor torque, friction, motion, moving contact, cable routing, tolerances or actual weights.',
 'items':[{'name':p[0],'mass_g':round(p[1],3),'center_mm':[round(v,2) for v in p[2:]]} for p in items]
}
with open(os.path.join(out,'static_balance_estimate.json'),'w') as f:json.dump(result,f,indent=2)
print(json.dumps({k:v for k,v in result.items() if k!='items'},indent=2))

