"""Board-size test cradle; head interface deliberately awaits physical head data.

Run with FreeCAD's bundled Python. All dimensions in mm.
This is an open cradle, not a proven retained head mount.
"""
from pathlib import Path
import json
import FreeCAD as App
import Part, MeshPart

OUT = Path(__file__).resolve().parent
V = App.Vector
PCB_LENGTH = 21.3
PCB_WIDTH = 12.8
LENGTH_WITH_USB = 23.2
STACK_HEIGHT = 23.6
CLEARANCE_PER_SIDE = 0.3
WALL = 1.4
BASE = 1.2
EDGE_SUPPORT = 0.5
UNDERSIDE_ALLOWANCE = 3.0  # Unmeasured: test before resting real PCB on supports.

inside_w = PCB_WIDTH + 2 * CLEARANCE_PER_SIDE
outside_w = inside_w + 2 * WALL
length = LENGTH_WITH_USB + 2 * CLEARANCE_PER_SIDE + WALL
board_z = BASE + UNDERSIDE_ALLOWANCE

def box(dx, dy, dz, x, y, z):
    return Part.makeBox(dx, dy, dz, V(x, y, z))

# Skeleton base: perimeter rails and two short crossbars, no solid floor.
parts = [box(length, WALL, BASE, 0, y, 0)
         for y in (0, outside_w - WALL)]
parts += [box(WALL, outside_w, BASE, x, 0, 0)
          for x in (0, length - WALL)]

# Upright fences with broad entry relief; USB end remains open.
for y in (0, outside_w - WALL):
    parts.append(box(PCB_LENGTH + WALL, WALL, board_z + 1.2, 0, y, 0))

# Two narrow PCB-edge shelves. No pressure clips touch unknown components.
support_width = CLEARANCE_PER_SIDE + EDGE_SUPPORT
for y in (WALL, outside_w - WALL - support_width):
    parts.append(box(PCB_LENGTH, support_width, 1.0,
                     WALL, y, board_z - 1.0))

# Closed far end provides a repeatable insertion stop; USB end has no wall.
parts.append(box(WALL, outside_w, board_z + 1.2, 0, 0, 0))
shape = parts[0]
for p in parts[1:]:
    shape = shape.fuse(p)
shape = shape.removeSplitter()

doc = App.newDocument('Cece_ESP_Board_Cradle_TEST_FIT')
obj = doc.addObject('PartDesign::Feature', 'Cradle_TEST_FIT')
obj.Label = 'Open board cradle - TEST FIT ONLY - no head retention'
obj.Shape = shape
for key, val in [('PCBLength', PCB_LENGTH), ('PCBWidth', PCB_WIDTH),
                 ('LengthWithUSB', LENGTH_WITH_USB), ('StackHeight', STACK_HEIGHT),
                 ('SideClearance', CLEARANCE_PER_SIDE),
                 ('UnverifiedUndersideSpace', UNDERSIDE_ALLOWANCE)]:
    obj.addProperty('App::PropertyLength', key, 'Dimensions')
    setattr(obj, key, val)
obj.addProperty('App::PropertyString', 'Status', 'Verification')
obj.Status = 'TEST FIT ONLY: head, PCB edge lands and underside clearance not verified'

# Reference envelope is saved separately in the assembly, never exported to STL.
proxy = doc.addObject('PartDesign::Feature', 'Board_Size_Reference_NOT_PRINTED')
proxy.Shape = box(PCB_LENGTH, PCB_WIDTH, STACK_HEIGHT,
                  WALL + CLEARANCE_PER_SIDE, WALL + CLEARANCE_PER_SIDE, board_z)
proxy.Label = 'Measured bounding box only - lens offset unknown - NOT PRINTED'
if App.GuiUp:
    obj.ViewObject.ShapeColor = (0.2, 0.65, 0.85)
    proxy.ViewObject.Transparency = 80
    proxy.ViewObject.Visibility = False
doc.recompute()
doc.saveAs(str(OUT / 'Cece_ESP_Board_Cradle_TEST_FIT.FCStd'))
mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.08,
                              AngularDeflection=0.25, Relative=False)
mesh.write(str(OUT / 'Cece_ESP_Board_Cradle_TEST_FIT.stl'))

report = {
    'status': 'SIZE TEST ONLY; NOT A FITTED OR RETAINED HEAD MOUNT',
    'user_measurements_mm': {'pcb_length': PCB_LENGTH, 'pcb_width': PCB_WIDTH,
                             'overall_length_with_USB': LENGTH_WITH_USB,
                             'total_stack_thickness': STACK_HEIGHT},
    'cradle_overall_mm': [round(shape.BoundBox.XLength, 3),
                          round(shape.BoundBox.YLength, 3),
                          round(shape.BoundBox.ZLength, 3)],
    'valid_solid': shape.isValid(), 'solid_count': len(shape.Solids),
    'closed_mesh': mesh.isSolid(),
    'volume_mm3': round(shape.Volume, 2),
    'solid_PLA_estimate_g_at_1_24': round(shape.Volume * 0.00124, 2),
    'print': {'orientation': 'flat perimeter base on build plate',
              'material': 'PLA', 'layer_mm': 0.2, 'walls': 2,
              'infill_percent': 10, 'supports': 'none expected; verify in slicer'},
    'not_verified': ['actual PCB underside and edge component clearance',
                     'PCB material thickness and camera lens offset',
                     'Otto head variant, inner dimensions, camera opening',
                     'ultrasonic board location and cable space',
                     'retention; this open size gauge has no clips or head tabs'],
}
assert report['valid_solid'] and report['solid_count'] == 1 and report['closed_mesh']
(OUT / 'test_cradle_checks.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
App.closeDocument(doc.Name)
