"""Cece head and full assembly with side-spanning ESP carrier. No legacy head input."""
from pathlib import Path
import json
import FreeCAD as A
import Part, MeshPart
V=A.Vector
H=Path(__file__).resolve().parent
src=A.openDocument(str(H.parent/'no_led_mouth'/'Cece_No_LED_Mouth_Assembly.FCStd'))
ref=A.openDocument(str(H/'Cece_ESP_Board_Cradle_TEST_FIT.FCStd'))
doc=A.newDocument('Cece_Head_ESP_Assembly')
def add(n,s,label=None):
 o=doc.addObject('PartDesign::Feature',n);o.Shape=s;o.Label=label or n.replace('_',' ');return o
def box(dx,dy,dz,x,y,z):return Part.makeBox(dx,dy,dz,V(x-dx/2,y-dy/2,z-dz/2))
skip={'Camera_Stack_Clearance_Provisional','Camera_Lens_Corridor_Provisional','ESP32_C3_Board_Envelope'}
for o in src.Objects:
 if o.Name not in skip and hasattr(o,'Shape') and not o.Shape.isNull():add(o.Name,o.Shape.copy(),o.Label)
head=doc.getObject('Rounded_Head_Study').Shape
cradle=ref.getObject('Cradle_TEST_FIT').Shape.copy()
pose=A.Placement(V(-12.6,-12.2,29.9),A.Rotation(V(1,0,0),90))
cradle.Placement=pose.multiply(cradle.Placement)
carrier=cradle.fuse(box(80.2,1.2,2.4,0,-12.8,44.9))
pads=[]
for sign in (-1,1):
 carrier=carrier.fuse(box(.8,12,2.4,sign*39.7,-19.4,44.9))
 pad=box(.45,2,2.4,sign*40.325,-24.4,44.9);pads.append(pad);carrier=carrier.fuse(pad)
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
doc.recompute();doc.saveAs(str(H/'Cece_Head_ESP_Assembly.FCStd'))
print_shape=carrier.copy();print_shape.Placement=pose.inverse().multiply(print_shape.Placement)
mesh=MeshPart.meshFromShape(Shape=print_shape,LinearDeflection=.08,AngularDeflection=.25,Relative=False)
assert mesh.isSolid();mesh.write(str(H/'Cece_ESP_Side_Carrier_CANDIDATE.stl'))
report={'source':'../no_led_mouth/Cece_No_LED_Mouth_Assembly.FCStd',
 'status':'CECE ONLY; modeled sensor clearance passes, physical fit unverified',
 'camera_centre_xyz_mm':[0,-40,38], 'nominal_head_inner_span_mm':80.8,'carrier_contact_span_mm':81.1,
 'solid_PLA_estimate_g':round(carrier.Volume*.00124,2),'valid_single_solid':True,'closed_mesh':True,
 'overlaps_mm3':checks,'sensor_clearances_mm':gaps,
 'limits':['PCB outline and stack bounds measured; lens offset, USB geometry and housing are provisional.',
           'Ultrasonic placement from current Cece CAD; installed placement not measured.',
           'Nominal 0.15 mm contact per side; actual insertion force, fatigue and grip untested.',
           'PCB positive retention, cables, antenna and insertion path remain unverified.',
           'Current assembly head selected by project rule; printed head must match this source.']}
(H/'cece_mount_checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
A.closeDocument(doc.Name);A.closeDocument(src.Name);A.closeDocument(ref.Name)
