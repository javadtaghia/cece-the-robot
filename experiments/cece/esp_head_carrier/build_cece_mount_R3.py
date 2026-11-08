"""Cece carrier R3, preserving the previous revision. Dimensions in mm."""
from pathlib import Path
import json
import FreeCAD as A
import Part, MeshPart
V=A.Vector
H=Path(__file__).resolve().parent
src=A.openDocument(str(H.parent/'no_led_mouth'/'Cece_No_LED_Mouth_Assembly.FCStd'))

doc=A.newDocument('Cece_Head_ESP_Assembly_R3')
def add(n,s,label=None):
 o=doc.addObject('PartDesign::Feature',n);o.Shape=s;o.Label=label or n.replace('_',' ');return o
def box(dx,dy,dz,x,y,z):return Part.makeBox(dx,dy,dz,V(x-dx/2,y-dy/2,z-dz/2))
skip={'Camera_Stack_Clearance_Provisional','Camera_Lens_Corridor_Provisional','ESP32_C3_Board_Envelope'}
for o in src.Objects:
 if o.Name not in skip and hasattr(o,'Shape') and not o.Shape.isNull():add(o.Name,o.Shape.copy(),o.Label)
head=doc.getObject('Rounded_Head_Study').Shape
# Revision R3: 18 mm vertical opening, 4 mm backing, open USB end.
# Local Y becomes assembly Z; local Z becomes rearward depth.
OPENING = 18.0
BASE = 4.0
WALL = 1.4
LENGTH = 25.2
WIDTH = OPENING + 2*WALL
BOARD_STANDOFF = 4.2  # preserve the original board proxy position

def localbox(dx,dy,dz,x,y,z):
 return Part.makeBox(dx,dy,dz,V(x,y,z))
pieces=[localbox(LENGTH,WALL,BASE,0,y,0) for y in (0,WIDTH-WALL)]
# Only the far-end backing rail: the USB-end vertical rail is removed.
pieces.append(localbox(WALL,WIDTH,BASE,0,0,0))
for y in (0,WIDTH-WALL):
 pieces.append(localbox(22.7,WALL,5.4,0,y,0))
for y in (WALL,WIDTH-WALL-.8):
 pieces.append(localbox(21.3,.8,1.0,WALL,y,BOARD_STANDOFF-1))
pieces.append(localbox(WALL,WIDTH,5.4,0,0,0))
cradle=pieces[0]
for piece in pieces[1:]:cradle=cradle.fuse(piece)
cradle=cradle.removeSplitter()
pose=A.Placement(V(-12.6,-12.2,29.9),A.Rotation(V(1,0,0),90))
cradle.Placement=pose.multiply(cradle.Placement)
# Restore the narrow open crossbar. Only the side grips become 20 mm tall.
BRIDGE_HEIGHT = 2.4
BRIDGE_Z = 44.9
GRIP_HEIGHT = 20.0
GRIP_TOP = BRIDGE_Z + BRIDGE_HEIGHT/2
GRIP_Z = GRIP_TOP - GRIP_HEIGHT/2
carrier=cradle.fuse(box(80.2,4.0,BRIDGE_HEIGHT,0,-14.2,BRIDGE_Z))
pads=[]
for sign in (-1,1):
 carrier=carrier.fuse(box(.8,12,GRIP_HEIGHT,sign*39.7,-19.4,GRIP_Z))
 pad=box(.45,2,GRIP_HEIGHT,sign*40.325,-24.4,GRIP_Z)
 pads.append(pad)
 carrier=carrier.fuse(pad)
carrier=carrier.removeSplitter()
add('ESP_Side_Bridge',carrier,'Cece ESP carrier - reaches both inner side walls')
components={
 'ESP_PCB':box(21.3,1.6,12.8,0,-17.2,38),
 'ESP_USB_Socket':box(3.8,4,8,10.55,-18.5,38),
 'ESP_Camera_Housing':box(12,5,12,0,-33,38),
 'ESP_Camera_Lens':Part.makeCylinder(3.8,7.5,V(0,-40,38),V(0,1,0)),
 'ESP_Stack_Envelope':box(21.3,23.6,12.8,0,-28.2,38)}
for n,s in components.items():add(n,s,n.replace('_',' ')+' - internal layout provisional')
def overlap(a,b):return 0.0 if not a.BoundBox.intersect(b.BoundBox) else a.common(b).Volume
checks={};gaps={}
for n,s in {'ESP_Side_Bridge':carrier,**components}.items():
 for sensor in ['HC_SR04_PCB','HC_SR04_Left_Can','HC_SR04_Right_Can']:
  u=doc.getObject(sensor).Shape;k=n+'_vs_'+sensor
  checks[k]=round(overlap(s,u),4);gaps[k]=round(s.distToShape(u)[0],3)
  assert checks[k]<.001,(k,checks[k])
 # The complete cuboid includes empty space near the aperture: check actual proxies instead.
 if n!='ESP_Stack_Envelope':
  checks[n+'_vs_head']=round(overlap(s,head),4)
hard=carrier
for pad in pads:hard=hard.cut(pad)
checks['carrier_excluding_contact_pads_vs_head']=round(overlap(hard,head),4)
assert checks['carrier_excluding_contact_pads_vs_head']<.001,checks
for n in components:
 if n!='ESP_Stack_Envelope':assert checks[n+'_vs_head']<.001,(n,checks[n+'_vs_head'])
# Existing camera opening is centred at x=0,z=38, radius 4 mm.
sight=Part.makeCylinder(.4,24,V(0,-40.2,38),V(0,1,0))
checks['camera_centre_ray_vs_ultrasonic_PCB']=round(overlap(sight,doc.getObject('HC_SR04_PCB').Shape),4)
assert checks['camera_centre_ray_vs_ultrasonic_PCB']==0
assert carrier.isValid() and len(carrier.Solids)==1
doc.recompute();doc.saveAs(str(H/'Cece_Head_ESP_Assembly_R3.FCStd'))
print_shape=carrier.copy();print_shape.Placement=pose.inverse().multiply(print_shape.Placement)
mesh=MeshPart.meshFromShape(Shape=print_shape,LinearDeflection=.08,AngularDeflection=.25,Relative=False)
assert mesh.isSolid();mesh.write(str(H/'Cece_ESP_Side_Carrier_R3_TEST_FIT.stl'))
report={'source':'../no_led_mouth/Cece_No_LED_Mouth_Assembly.FCStd',
 'status':'CECE ONLY; modeled sensor clearance passes, physical fit unverified',
 'camera_centre_xyz_mm':[0,-40,38], 'nominal_head_inner_span_mm':80.8,'carrier_contact_span_mm':81.1,
 'requested_dimensions_mm':{'opening':OPENING,'backing':BASE,'crossbar_height':BRIDGE_HEIGHT,'crossbar_depth':4.0,'side_grip_height':GRIP_HEIGHT},'removed':'USB-end vertical backing rail','revision':'Open crossbar restored; 20 mm side grips extend downward, not across the electronics',
 'solid_PLA_estimate_g':round(carrier.Volume*.00124,2),'valid_single_solid':True,'closed_mesh':True,
 'overlaps_mm3':checks,'sensor_clearances_mm':gaps,
 'limits':['PCB outline and stack bounds measured; lens offset, USB geometry and housing are provisional.',
           'Ultrasonic placement from current Cece CAD; installed placement not measured.',
           'Nominal 0.15 mm contact per side; actual insertion force, fatigue and grip untested.',
           'PCB positive retention, cables, antenna and insertion path remain unverified.',
           'Current assembly head selected by project rule; printed head must match this source.']}
(H/'cece_mount_R3_checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
A.closeDocument(doc.Name);A.closeDocument(src.Name)
