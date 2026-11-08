"""Cece carrier R8, preserving the previous revision. Dimensions in mm."""
from pathlib import Path
import json
import FreeCAD as A
import Part, MeshPart
V=A.Vector
H=Path(__file__).resolve().parent
src=A.openDocument(str(H.parent/'no_led_mouth'/'Cece_No_LED_Mouth_Assembly.FCStd'))

doc=A.newDocument('Cece_Head_ESP_Assembly_R8')
def add(n,s,label=None):
 o=doc.addObject('PartDesign::Feature',n);o.Shape=s;o.Label=label or n.replace('_',' ');return o
def box(dx,dy,dz,x,y,z):return Part.makeBox(dx,dy,dz,V(x-dx/2,y-dy/2,z-dz/2))
skip={'Camera_Stack_Clearance_Provisional','Camera_Lens_Corridor_Provisional','ESP32_C3_Board_Envelope'}
for o in src.Objects:
 if o.Name not in skip and hasattr(o,'Shape') and not o.Shape.isNull():add(o.Name,o.Shape.copy(),o.Label)
head=doc.getObject('Rounded_Head_Study').Shape
# Revision R8: 18.6 mm vertical opening, 4 mm backing, open USB end.
# Local Y becomes assembly Z; local Z becomes rearward depth.
OPENING = 18.6
BASE = 4.0
WALL = 1.4
LENGTH = 25.2
WIDTH = OPENING + 2*WALL
RAIL_DEPTH = 10.4  # prior 5.4 mm plus requested 5 mm
MODULE_THICKNESS = 4.5
SLIDE_CLEARANCE = .3

def localbox(dx,dy,dz,x,y,z):
 return Part.makeBox(dx,dy,dz,V(x,y,z))
pieces=[localbox(LENGTH,WALL,BASE,0,y,0) for y in (0,WIDTH-WALL)]
# Only the far-end backing rail: the USB-end vertical rail is removed.
pieces.append(localbox(WALL,WIDTH,BASE,0,0,0))
for y in (0,WIDTH-WALL):
 pieces.append(localbox(22.7,WALL,RAIL_DEPTH,0,y,0))
pieces.append(localbox(WALL,WIDTH,RAIL_DEPTH,0,0,0))
cradle=pieces[0]
for piece in pieces[1:]:cradle=cradle.fuse(piece)
cradle=cradle.removeSplitter()
pose=A.Placement(V(-12.6,-12.2,29.3),A.Rotation(V(1,0,0),90))
cradle.Placement=pose.multiply(cradle.Placement)
# PCB-edge channels. Insert sideways through the open USB end BEFORE
# placing the loaded carrier in the head; the lens cannot slide across the
# head front while already projecting through its circular aperture.
# Updated module envelope spans z=31.0..49.0 and y=-19.45..-14.95.
for z0,z1 in ((29.3,31.5),(48.5,50.7)):
 guide=box(22.7,7.1,z1-z0,-1.25,-17.2,(z0+z1)/2)
 cradle=cradle.fuse(guide)
for z0,z1 in ((30.7,31.8),(48.2,49.3)):
 groove=box(23.0,5.1,z1-z0,-1.1,-17.2,(z0+z1)/2)
 cradle=cradle.cut(groove)
cradle=cradle.removeSplitter()
# Move the entire cradle toward the USB end; wall grips stay located in the head.
cradle.translate(V(10,0,0))
# Restore the narrow open crossbar. Only the side grips become 20 mm tall.
BRIDGE_HEIGHT = 2.4
BRIDGE_Z = 49.5  # top surface flush with frame top at z=50.7
GRIP_HEIGHT = 20.0
GRIP_TOP = 46.1  # retain side grip fit below rounded head shoulders
GRIP_Z = GRIP_TOP - GRIP_HEIGHT/2
carrier=cradle.fuse(box(74.0,4.0,BRIDGE_HEIGHT,0,-14.2,BRIDGE_Z))
for sign in (-1,1):
 carrier=carrier.fuse(box(4.1,4.0,2.4,sign*38.05,-14.2,44.9))
 carrier=carrier.fuse(box(1.5,4.0,7.0,sign*36.25,-14.2,47.2))
pads=[]
for sign in (-1,1):
 carrier=carrier.fuse(box(.8,12,GRIP_HEIGHT,sign*39.7,-19.4,GRIP_Z))
 pad=box(.45,2,GRIP_HEIGHT,sign*40.325,-24.4,GRIP_Z)
 pads.append(pad)
 carrier=carrier.fuse(pad)
# Clearance tunnel for sideways loading of the shifted module, outside the head.
# This also notches the rear portion of the right grip; its front contact pad remains.
carrier=carrier.cut(box(46.0,5.1,18.6,22.05,-17.2,40))
carrier=carrier.cut(box(28.0,4.6,8.6,32.5,-18.5,40))
carrier=carrier.removeSplitter()
fixed_carrier=carrier.copy()
# Upper anchored cantilever. Free end bears on the camera housing, never lens.
# Nominal 0.20 mm elastic displacement is provisional, not a verified force.
FLAP_PRELOAD=.20
flap=box(6.0,18.4,1.4,0,-21.4,50.0)
flap=flap.fuse(box(6.0,.8,10.6,0,-29.8,44.0))
flap=flap.fuse(box(6.0,1.4,2.0,0,-29.5,48.4))
push_pad=box(5.0,.8,3.0,0,-30.3,40.5)
flap=flap.fuse(push_pad).removeSplitter()
carrier=carrier.fuse(flap).removeSplitter()
add('ESP_Side_Bridge',carrier,'Cece shifted ESP carrier with upper camera flap')
add('Flap_Contact_Zone',push_pad,'Camera housing contact pad - 0.20 mm provisional preload')
components={
 'ESP_PCB':box(21.3,4.5,18.0,10,-17.2,40),
 'ESP_USB_Socket':box(3.8,4,8,20.55,-18.5,40),
 'ESP_Camera_Housing':box(12,5,12,0,-33,38),
 'ESP_Camera_Lens':Part.makeCylinder(3.8,7.5,V(0,-40,38),V(0,1,0)),
 'ESP_Stack_Envelope':box(32.65,25.05,18.0,4.675,-27.475,40)}
for n,s in components.items():add(n,s,n.replace('_',' ')+' - internal layout provisional')
# Check the modeled stacked assembly along the rail axis, outside the head.
slide_results=[]
for step in range(48):
 dx=step*.5
 for n,shape in components.items():
  if n=='ESP_Stack_Envelope':continue
  shifted=shape.copy();shifted.translate(V(dx,0,0))
  v=fixed_carrier.common(shifted).Volume
  if v>.001:slide_results.append({'part':n,'offset_mm':dx,'overlap_mm3':round(v,4)})
assert not slide_results,slide_results[:5]

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
for n in ['ESP_PCB','ESP_USB_Socket','ESP_Camera_Lens']:
 checks['carrier_vs_'+n]=round(overlap(carrier,components[n]),4)
 assert checks['carrier_vs_'+n]<.001,(n,checks['carrier_vs_'+n])
checks['intentional_flap_preload_vs_camera_housing']=round(overlap(carrier,components['ESP_Camera_Housing']),4)
checks['fixed_carrier_vs_camera_housing']=round(overlap(fixed_carrier,components['ESP_Camera_Housing']),4)
assert checks['fixed_carrier_vs_camera_housing']<.001
assert abs(checks['intentional_flap_preload_vs_camera_housing']-3.0)<.01
assert carrier.isValid() and len(carrier.Solids)==1
doc.recompute();doc.saveAs(str(H/'Cece_Head_ESP_Assembly_R8.FCStd'))
print_shape=carrier.copy();print_shape.Placement=pose.inverse().multiply(print_shape.Placement)
mesh=MeshPart.meshFromShape(Shape=print_shape,LinearDeflection=.08,AngularDeflection=.25,Relative=False)
assert mesh.isSolid();mesh.write(str(H/'Cece_ESP_Side_Carrier_R8_PREVIEW.stl'))
report={'source':'../no_led_mouth/Cece_No_LED_Mouth_Assembly.FCStd',
 'status':'PREVIEW: 10 mm cradle shift and camera flap; physical force and clear edge lands need checking',
 'cradle_shift_xyz_mm':[10,0,0],'camera_offset_from_module_centre_xyz_mm':[-10,-22.8,-2], 'camera_centre_xyz_mm':[0,-40,38], 'nominal_head_inner_span_mm':80.8,'carrier_contact_span_mm':81.1,
 'requested_dimensions_mm':{'opening':OPENING,'backing':BASE,'crossbar_height':BRIDGE_HEIGHT,'crossbar_depth':4.0,'side_grip_height':GRIP_HEIGHT,'rail_depth':RAIL_DEPTH,'depth_increase':5.0,'module_thickness':MODULE_THICKNESS,'module_width':18.0,'module_length':21.3,'slide_gap':5.1,'slide_clearance_per_face':SLIDE_CLEARANCE},'removed':'USB-end vertical backing rail','revision':'Cradle and module shift 10 mm toward USB end; upper anchored flap presses camera housing; right grip loading tunnel added' ,
 'slide_check':{'axis':'X from USB end','travel_mm':23.5,'step_mm':.5,'modeled_component_overlaps':slide_results,'loading':'Load ESP outside the head, holding camera flap back, then install loaded carrier. Sweep checks fixed carrier only; compliant flap is excluded and reported separately.'},
 'flap':{'leaf_width_mm':6.0,'leaf_thickness_mm':0.8,'leaf_length_mm':10.6,'nominal_preload_mm':FLAP_PRELOAD,'contact':'rear of camera housing, away from lens','force_verified':False},
 'solid_PLA_estimate_g':round(carrier.Volume*.00124,2),'valid_single_solid':True,'closed_mesh':True,
 'overlaps_mm3':checks,'sensor_clearances_mm':gaps,
 'limits':['User corrected module width to 17-18 mm (18 used) and thickness to 4.5 mm; 21.3 mm length retained. The requested 10 mm cradle shift gives a modeled 10 mm camera-to-module-centre offset away from USB; this is not an independently measured lens offset; exact USB and vertical lens offsets remain provisional. Camera stays at aperture z=38 while module centre is z=40; the 2 mm vertical offset is unverified. Combined front-to-back proxy extent is now 25.05 mm, not the old 23.6 mm estimate.',
           'Ultrasonic placement from current Cece CAD; installed placement not measured.',
           'Nominal 0.15 mm head contact per side; right grip has a loading window. Actual head grip, flap force, fatigue and preload untested; do not press the lens or ribbon cable.',
           '4.5 mm is treated as the module envelope, not bare PCB laminate. Usable edge lands, rail retention, cable routing and loaded-carrier insertion into head require physical checks.',
           'Current assembly head selected by project rule; printed head must match this source.']}
(H/'cece_mount_R8_checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
A.closeDocument(doc.Name);A.closeDocument(src.Name)
