"""Cece carrier R11, preserving the previous revision. Dimensions in mm."""
from pathlib import Path
import json
import FreeCAD as A
import Part, MeshPart
V=A.Vector
H=Path(__file__).resolve().parent
src=A.openDocument(str(H.parent/'no_led_mouth'/'Cece_No_LED_Mouth_Assembly.FCStd'))

doc=A.newDocument('Cece_Head_ESP_Assembly_R11')
def add(n,s,label=None):
 o=doc.addObject('PartDesign::Feature',n);o.Shape=s;o.Label=label or n.replace('_',' ');return o
def box(dx,dy,dz,x,y,z):return Part.makeBox(dx,dy,dz,V(x-dx/2,y-dy/2,z-dz/2))
skip={'Camera_Stack_Clearance_Provisional','Camera_Lens_Corridor_Provisional','ESP32_C3_Board_Envelope'}
for o in src.Objects:
 if o.Name not in skip and hasattr(o,'Shape') and not o.Shape.isNull():add(o.Name,o.Shape.copy(),o.Label)
head=doc.getObject('Rounded_Head_Study').Shape
# Revision R11: 18.6 mm vertical opening, 4 mm backing, open USB end.
# Local Y becomes assembly Z; local Z becomes rearward depth.
OPENING = 18.6
BASE = 4.0
WALL = 1.4
LENGTH = 25.2
WIDTH = OPENING + 2*WALL
DEPTH_INCREASE_R11 = 2.0
RAIL_DEPTH = 12.4  # R9 10.4 + requested 2 mm toward camera
SLIDE_DEPTH = 7.1  # R9 5.1 + 2 mm usable front-to-back clearance
SLIDE_Y = -18.2  # preserve rear datum; move front boundary 2 mm
MODULE_THICKNESS = 4.5
SLIDE_CLEARANCE = .3

def localbox(dx,dy,dz,x,y,z):
 return Part.makeBox(dx,dy,dz,V(x,y,z))
pieces=[localbox(LENGTH,WALL,BASE,0,y,0) for y in (0,WIDTH-WALL)]
# Far-end backing rail is later opened for USB; antenna-entry end has no vertical rail.
pieces.append(localbox(WALL,WIDTH,BASE,0,0,0))
for y in (0,WIDTH-WALL):
 pieces.append(localbox(22.7,WALL,RAIL_DEPTH,0,y,0))
pieces.append(localbox(WALL,WIDTH,RAIL_DEPTH,0,0,0))
cradle=pieces[0]
for piece in pieces[1:]:cradle=cradle.fuse(piece)
cradle=cradle.removeSplitter()
pose=A.Placement(V(-12.6,-12.2,29.3),A.Rotation(V(1,0,0),90))
cradle.Placement=pose.multiply(cradle.Placement)
# Module-edge channels. Insert USB-first through the open antenna end BEFORE
# placing the loaded carrier in the head; the lens cannot slide across the
# head front while already projecting through its circular aperture.
# Before the R11 lift, module envelope spans z=31.0..49.0 and y=-19.45..-14.95.
for z0,z1 in ((29.3,31.5),(48.5,50.7)):
 guide=box(22.7,9.1,z1-z0,-1.25,SLIDE_Y,(z0+z1)/2)
 cradle=cradle.fuse(guide)
for z0,z1 in ((30.7,31.8),(48.2,49.3)):
 groove=box(23.0,SLIDE_DEPTH,z1-z0,-1.1,SLIDE_Y,(z0+z1)/2)
 cradle=cradle.cut(groove)
cradle=cradle.removeSplitter()
# R11: cradle centre X=3, up 2 mm; wall grips stay located in the head.
cradle.translate(V(3,0,2))
# Lower the upper rail surface slightly to clear the unchanged head roof.
cradle=cradle.cut(box(100,100,20,0,-20,62.1))
# Restore the narrow open crossbar. Only the side grips become 20 mm tall.
BRIDGE_HEIGHT = 2.4
BRIDGE_Z = 49.5  # top surface flush with frame top at z=50.7
GRIP_HEIGHT = 20.0
GRIP_TOP = 46.1  # retain side grip fit below rounded head shoulders
GRIP_Z = GRIP_TOP - GRIP_HEIGHT/2
carrier=cradle.fuse(box(74.0,6.0,BRIDGE_HEIGHT,0,-13.2,BRIDGE_Z))
for sign in (-1,1):
 carrier=carrier.fuse(box(4.1,6.0,2.4,sign*38.05,-13.2,44.9))
 carrier=carrier.fuse(box(2.2,6.0,7.0,sign*36.25,-13.2,47.2))
pads=[]
for sign in (-1,1):
 carrier=carrier.fuse(box(2.0,12,GRIP_HEIGHT,sign*39.1,-19.4,GRIP_Z))
 pad=box(.45,2,GRIP_HEIGHT,sign*40.325,-24.4,GRIP_Z)
 pads.append(pad)
 carrier=carrier.fuse(pad)
# USB-first insertion from the antenna end (+X). The board exits the
# cradle after 23.5 mm travel, before reaching the solid wall support.
carrier=carrier.cut(box(45.4,SLIDE_DEPTH,18.6,14.75,SLIDE_Y,42))
carrier=carrier.cut(box(28.0,6.6,8.6,4.2,-19.5,42))
# Dedicated USB cable portal at the leading/far end (-X).
# 8.5 mm front-to-back by 10 mm vertically; plug body remains provisional.
carrier=carrier.cut(box(12,10.5,10,-9.6,-19.5,42))
# B: shave the central raised backing ridge flush with the main frame.
# Main frame top is Z=50.7; its front face is Y=-16.2.
# Preserve the front retaining lip and the camera flap, away from this band.
B_FLUSH_Z = BRIDGE_Z + BRIDGE_HEIGHT/2
b_relief=box(25.4,6.0,10,3.0,-13.2,B_FLUSH_Z+5)
carrier=carrier.cut(b_relief).removeSplitter()
fixed_carrier=carrier.copy()
# Flap anchored to the upper frame, above the corrected module envelope.
# Camera target stays at the existing hole; inferred offsets are provisional.
FLAP_PRELOAD=.20
flap=box(6.0,14.4,.8,0,-23.4,51.7)  # root stays ahead of the flush B band
flap=flap.fuse(box(6.0,.8,12.6,0,-29.8,45.0))
flap=flap.fuse(box(6.0,1.4,2.0,0,-29.5,50.0))
push_pad=box(5.0,.8,3.0,0,-30.3,40.5)
flap=flap.fuse(push_pad).removeSplitter()
carrier=carrier.fuse(flap).removeSplitter()
# R11: open the marked roof over the board channel for its pins.
# Cut through the cap and flap root above the channel, preserving the
# continuous main frame behind it and the front lip supporting the flap.
PIN_SLOT_LENGTH = 22.3  # board length 21.3 plus 0.5 mm at each end
PIN_SLOT_DEPTH = SLIDE_DEPTH
PIN_SLOT_Z_MIN = 50.7
pin_slot=box(PIN_SLOT_LENGTH,PIN_SLOT_DEPTH,12.0,3,SLIDE_Y,PIN_SLOT_Z_MIN+6)
carrier=carrier.cut(pin_slot).removeSplitter()
fixed_carrier=fixed_carrier.cut(pin_slot).removeSplitter()
add('Pin_Access_Clearance',pin_slot,'Pin access opening - 22.3 x 7.1 mm; pin dimensions unmeasured')
add('ESP_Side_Bridge',carrier,'Cece R11 carrier - open pin access above board')
add('Flap_Contact_Zone',push_pad,'Camera housing contact pad - 0.20 mm provisional preload')
components={
 'ESP_PCB':box(21.3,4.5,18.0,3,-17.2,42),
 'ESP_USB_Socket':box(3.8,4,8,-7.55,-18.5,42),
 'ESP_Camera_Housing':box(12,5,12,0,-33,38),
 'ESP_Camera_Lens':Part.makeCylinder(3.8,7.5,V(0,-40,38),V(0,1,0)),
 'USB_Plug_Clearance_Provisional':box(15,7,8,-16.95,-18.5,42),
 'ESP_Stack_Envelope':box(24.0,25.05,19.0,2.0,-27.475,41.5)}
for n,s in components.items():add(n,s,n.replace('_',' ')+' - internal layout provisional')
# Check the modeled stacked assembly along the rail axis, outside the head.
slide_results=[]
for step in range(48):
 dx=step*.5
 for n,shape in components.items():
  if n in ('ESP_Stack_Envelope','USB_Plug_Clearance_Provisional'):continue
  shifted=shape.copy();shifted.translate(V(dx,0,0))
  v=fixed_carrier.common(shifted).Volume
  if v>.001:slide_results.append({'part':n,'offset_mm':dx,'overlap_mm3':round(v,4)})
assert not slide_results,slide_results[:5]

def overlap(a,b):return 0.0 if not a.BoundBox.intersect(b.BoundBox) else a.common(b).Volume
checks={};gaps={}
checks['pin_slot_remaining_material_mm3']=round(carrier.common(pin_slot).Volume,6)
assert checks['pin_slot_remaining_material_mm3']<.001
checks['B_raised_material_above_frame_mm3']=round(carrier.common(b_relief).Volume,6)
assert checks['B_raised_material_above_frame_mm3']<.001
assert abs(RAIL_DEPTH-10.4-2.0)<1e-6
assert abs(SLIDE_DEPTH-5.1-2.0)<1e-6
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
for n in ['ESP_PCB','ESP_USB_Socket','ESP_Camera_Lens','USB_Plug_Clearance_Provisional']:
 checks['carrier_vs_'+n]=round(overlap(carrier,components[n]),4)
 assert checks['carrier_vs_'+n]<.001,(n,checks['carrier_vs_'+n])
checks['intentional_flap_preload_vs_camera_housing']=round(overlap(carrier,components['ESP_Camera_Housing']),4)
checks['fixed_carrier_vs_camera_housing']=round(overlap(fixed_carrier,components['ESP_Camera_Housing']),4)
assert checks['fixed_carrier_vs_camera_housing']<.001
assert abs(checks['intentional_flap_preload_vs_camera_housing']-3.0)<.01
for sign in (-1,1):
 plate=box(2,12,20,sign*39.1,-19.4,GRIP_Z)
 assert plate.cut(carrier).Volume<.001
assert carrier.isValid() and len(carrier.Solids)==1
doc.recompute();doc.saveAs(str(H/'Cece_Head_ESP_Assembly_R11.FCStd'))
print_shape=carrier.copy();print_shape.Placement=pose.inverse().multiply(print_shape.Placement)
mesh=MeshPart.meshFromShape(Shape=print_shape,LinearDeflection=.08,AngularDeflection=.25,Relative=False)
assert mesh.isSolid();mesh.write(str(H/'Cece_ESP_Side_Carrier_R11_PREVIEW.stl'))
report={'source':'../no_led_mouth/Cece_No_LED_Mouth_Assembly.FCStd',
 'status':'R11 PREVIEW: through-slot over board for pin access; real pin position and projection not measured',
 'cradle_shift_from_R8_xyz_mm':[-7,0,2],'cradle_position_shift_from_base_xyz_mm':[3,0,2],'camera_offset_from_module_centre_xyz_mm':[-3,-22.8,-4], 'camera_centre_xyz_mm':[0,-40,38], 'nominal_head_inner_span_mm':80.8,'carrier_contact_span_mm':81.1,
 'requested_dimensions_mm':{'opening':OPENING,'backing':BASE,'crossbar_height':BRIDGE_HEIGHT,'crossbar_depth':6.0,'wall_support_thickness':2.0,'usb_portal_depth':10.5,'usb_portal_height':10.0,'side_grip_height':GRIP_HEIGHT,'rail_depth':RAIL_DEPTH,'depth_increase_from_R9':2.0,'module_thickness':MODULE_THICKNESS,'module_width':18.0,'module_length':21.3,'slide_gap':SLIDE_DEPTH,'slide_rear_clearance':0.3,'slide_front_clearance':2.3,'B_flush_height':B_FLUSH_Z},'pin_access':{'length_mm':PIN_SLOT_LENGTH,'depth_mm':PIN_SLOT_DEPTH,'slot_base_z_mm':PIN_SLOT_Z_MIN,'type':'through roof above board channel','actual_pin_dimensions_verified':False},'removed':'Cap and flap-root material above the board channel inside the pin access slot','revision':'R11 opens a 22.3 x 7.1 mm through-slot over the board channel. Keeps R10 depth, main crossbar, solid wall supports, component locations and camera flap contact position.' ,
 'slide_check':{'axis':'+X extraction / -X insertion; USB leads from open antenna end','travel_mm':23.5,'step_mm':.5,'modeled_component_overlaps':slide_results,'loading':'Load ESP outside the head, holding camera flap back, then install loaded carrier. Sweep checks fixed carrier only; compliant flap is excluded and reported separately.'},
 'flap':{'leaf_width_mm':6.0,'leaf_thickness_mm':0.8,'leaf_length_mm':12.6,'nominal_preload_mm':FLAP_PRELOAD,'contact':'rear of camera housing, away from lens','force_verified':False},
 'solid_PLA_estimate_g':round(carrier.Volume*.00124,2),'valid_single_solid':True,'closed_mesh':True,
 'overlaps_mm3':checks,'sensor_clearances_mm':gaps,
 'limits':['Pin access slot follows the marked roof region. Actual header positions, projection direction, protrusion and connector bodies are not measured or modeled; physical pin and head clearance is not proven. Upper board retention is reduced by opening this cap.','Module is 21.3 x 18 x 4.5 mm. USB-first orientation follows the user photo and description. Cradle shift -7 X/+2 Z follows requested correction; camera proxy is placed at the unchanged aperture for review, not as proof of alignment. Resulting lens offset (-3 X/-4 Z from module centre) is inferred, not measured. USB and camera geometry and ribbon route remain provisional. USB plug check uses an unmeasured 15 x 7 x 8 mm plug body envelope; compare with actual cable.',
           'Ultrasonic placement from current Cece CAD; installed placement not measured.',
           'Both wall plates are solid 2 mm sections, replacing 0.8 mm sections; crossbar depth 6 mm. Nominal 0.15 mm head contact per side remains. Stiffer supports may need fit adjustment; do not force them into the head. Flap force and fatigue remain untested.',
           '4.5 mm is treated as the module envelope, not bare PCB laminate. Usable edge lands, rail retention, cable routing and loaded-carrier insertion into head require physical checks.',
           'Current assembly head selected by project rule; printed head must match this source.']}
(H/'cece_mount_R11_checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
A.closeDocument(doc.Name);A.closeDocument(src.Name)
