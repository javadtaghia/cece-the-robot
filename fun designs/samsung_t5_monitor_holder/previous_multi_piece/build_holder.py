"""Generate a provisional Samsung T5 holder and two side hooks with FreeCAD.

Dimensions are millimetres. The monitor thickness and safe bezel overlap MUST
be measured and passed on the command line before printing monitor hooks.
"""
import argparse
import json
from pathlib import Path
import sys
import FreeCAD as App
import Part
import MeshPart

HERE = Path(__file__).resolve().parent
V = App.Vector

def box(x, y, z, dx, dy, dz):
    return Part.makeBox(dx, dy, dz, V(x, y, z))

def fuse(parts):
    shape = parts[0]
    for part in parts[1:]:
        shape = shape.fuse(part)
    return shape.removeSplitter()

def write_stl(shape, path):
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.08,
                                  AngularDeflection=0.35, Relative=False)
    mesh.write(str(path))

def build(thickness, bezel, gap):
    if not 2 <= thickness <= 70:
        raise ValueError('Monitor thickness must be between 2 and 70 mm')
    if not 1 <= bezel <= 8:
        raise ValueError('Front overlap must be between 1 and 8 mm')
    if not 0.3 <= gap <= 3:
        raise ValueError('Padding clearance must be between 0.3 and 3 mm')

    # Samsung T5: x=57.3, y=74, z=10.5. Side walls and front rails
    # leave room for printing tolerance; the USB end and loading end are open.
    width, length = 63.5, 80.0
    back, wall = 2.4, 2.5
    cavity_top = back + 11.5
    ear_y = (15.0, 53.0)
    parts = [box(0, 0, 0, width, length, back),
             box(0, 0, back, wall, length, 13.5),
             box(width-wall, 0, back, wall, length, 13.5),
             box(wall, 0, back, width-2*wall, wall, 13.5),
             box(wall, 0, cavity_top, 3.0, length, 2.0),
             box(width-wall-3.0, 0, cavity_top, 3.0, length, 2.0)]
    for y in ear_y:
        parts.append(box(-15, y, 0, 15, 14, back))
    tray = fuse(parts)
    for x in (11.5, 37.0):
        for y in (12.0, 46.0):
            tray = tray.cut(box(x, y, -0.2, 15, 22, back+0.4))
    for y in ear_y:
        tray = tray.cut(Part.makeCylinder(1.7, back+0.4, V(-9, y+7, -0.2)))
    tray = tray.removeSplitter()

    # Hook rear flange mates to an outside ear using an M3 bolt and nut.
    # Monitor is approximated from z=-thickness to z=0, with left edge x=0.
    front_z = -(thickness + gap)
    hook_parts = [box(-15, 0, back, 15, 14, 3),
                  box(-3.8, 0, front_z-2.4, 3.0, 14, back+3-front_z+2.4),
                  box(-3.8, 0, front_z-2.4, 3.8+bezel, 14, 2.4)]
    hook = fuse(hook_parts)
    hook = hook.cut(Part.makeCylinder(1.7, 3.4, V(-9, 7, back-0.2))).removeSplitter()
    # Positive stop: the upper hook has a horizontal ledge resting on the top
    # edge. The user must place that hook at the screen's top-left corner.
    # It supports weight on the edge rather than squeezing the display faces.
    upper_hook = hook.fuse(box(-3.8, 14, -thickness, 21.8, 3, thickness)).removeSplitter()
    # Simplified SSD/monitor envelopes for checking; not exported as print parts.
    drive = box(3.1, 3.1, back, 57.3, 74, 10.5)
    # Top of the rectangular reference lid is flush with upper hook y=14.
    screen_top = ear_y[1] + 14
    screen = box(0, screen_top - 140, -thickness, 250, 140, thickness)
    drive_overlap = tray.common(drive).Volume
    hook_monitor_overlap = hook.copy()
    hook_monitor_overlap.translate(V(0, ear_y[0], 0))
    hook_monitor_overlap = hook_monitor_overlap.common(screen).Volume
    upper_monitor_overlap = upper_hook.copy()
    upper_monitor_overlap.translate(V(0, ear_y[1], 0))
    upper_monitor_overlap = upper_monitor_overlap.common(screen).Volume
    if hook_monitor_overlap > 1e-5 or upper_monitor_overlap > 1e-5:
        raise RuntimeError('Hook intersects the rectangular monitor envelope')
    dropped_upper = upper_hook.copy()
    dropped_upper.translate(V(0, ear_y[1] - 0.5, 0))
    stop_overlap = dropped_upper.common(screen).Volume
    if stop_overlap < 1e-5:
        raise RuntimeError('Upper ledge did not stop the modeled downward motion')
    if drive_overlap > 1e-5:
        raise RuntimeError('SSD envelope collides with holder: %.5f mm3' % drive_overlap)
    for name, shape in (('holder', tray), ('lower hook', hook), ('upper hook', upper_hook)):
        if not shape.isValid() or len(shape.Solids) != 1:
            raise RuntimeError(name + ' is not a valid single solid')

    doc = App.newDocument('Samsung_T5_Monitor_Holder')
    def feature(name, shape, color):
        obj = doc.addObject('PartDesign::Feature', name)
        obj.Shape = shape
        if obj.ViewObject: obj.ViewObject.ShapeColor = color
        return obj
    feature('Holder_print_one', tray, (0.2, 0.45, 0.72))
    first = hook.copy(); first.translate(V(0, ear_y[0], 0))
    second = upper_hook.copy(); second.translate(V(0, ear_y[1], 0))
    feature('Hook_lower_print_one', first, (0.9, 0.55, 0.12))
    feature('Hook_upper_print_one', second, (0.9, 0.55, 0.12))
    feature('SSD_envelope_reference_only', drive, (0.75, 0.75, 0.75))
    feature('Monitor_envelope_reference_only', screen, (0.18, 0.18, 0.18))
    doc.recompute()
    doc.saveAs(str(HERE / 'Samsung_T5_Holder_Assembly_PROVISIONAL.FCStd'))
    write_stl(tray, HERE / 'T5_holder_print_1_PROVISIONAL.stl')
    # Hooks lie on their sides for printing; inspect supports under top ledge.
    def print_orient(shape, name):
        printable = shape.copy()
        printable.rotate(V(0, 0, 0), V(1, 0, 0), 90)
        printable.translate(V(0, 0, -printable.BoundBox.ZMin))
        write_stl(printable, HERE / name)
        return [printable.BoundBox.XLength, printable.BoundBox.YLength, printable.BoundBox.ZLength]
    lower_bbox = print_orient(hook, 'Lower_side_hook_print_1_PROVISIONAL.stl')
    upper_bbox = print_orient(upper_hook, 'Upper_corner_support_print_1_PROVISIONAL.stl')
    result = {'monitor_thickness_mm': thickness, 'front_bezel_overlap_mm': bezel,
              'padding_clearance_mm': gap, 'hook_opening_mm': thickness + gap,
              'ssd_envelope_mm': [57.3, 74, 10.5],
              'ssd_intersection_volume_mm3': drive_overlap,
              'lower_hook_monitor_proxy_intersection_mm3': hook_monitor_overlap,
              'upper_hook_monitor_proxy_intersection_mm3': upper_monitor_overlap,
              'downward_0p5mm_interference_mm3': stop_overlap,
              'top_support_width_over_lid_mm': 18.0,
              'top_support_depth_over_lid_mm': thickness,
              'top_support_contact_face_mm2': 18.0 * thickness,
              'holder_volume_mm3': tray.Volume, 'lower_hook_volume_mm3': hook.Volume,
              'upper_hook_volume_mm3': upper_hook.Volume,
              'holder_bbox_mm': [tray.BoundBox.XLength, tray.BoundBox.YLength, tray.BoundBox.ZLength],
              'lower_hook_print_bbox_mm': lower_bbox, 'upper_hook_print_bbox_mm': upper_bbox,
              'note': 'Top-edge ledge provides a positive stop in the idealized geometry; actual lid edge, loading, strength and safety are not verified.'}
    (HERE / 'geometry_report.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    App.closeDocument(doc.Name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--monitor-thickness', type=float, required=True)
    parser.add_argument('--bezel-overlap', type=float, default=3.0)
    parser.add_argument('--padding-clearance', type=float, default=0.8)
    args = parser.parse_args()
    build(args.monitor_thickness, args.bezel_overlap, args.padding_clearance)
