"""One-piece T5 sleeve with side guides and a positive top-edge stop.

All dimensions are millimetres. This remains a physical-fit prototype.
"""
import argparse
import json
from pathlib import Path
import FreeCAD as App
import Part
import MeshPart

HERE = Path(__file__).resolve().parent
V = App.Vector

def box(x, y, z, dx, dy, dz):
    return Part.makeBox(dx, dy, dz, V(x, y, z))

def build(thickness, opening, bezel_overlap, top_opening, top_overlap):
    if not 2 <= thickness < opening <= thickness + 4:
        raise ValueError('Opening must be larger than lid thickness by at most 4 mm')
    if not 1 <= bezel_overlap <= 5 or not 1 <= top_overlap <= 5:
        raise ValueError('Front overlaps must be 1–5 mm')
    if not thickness < top_opening <= thickness + 6:
        raise ValueError('Top opening must be larger than lid thickness by at most 6 mm')
    width, length, back, wall = 63.5, 80.0, 2.4, 2.5
    cavity_top = back + 11.5
    front_z = -opening
    hook_positions = (15.0, 53.0)
    # Thin back rails and ribs replace the solid back panel. The open top
    # leaves the SSD USB-C end unobstructed. Small overlaps make robust solids.
    parts = [
        box(0, 0, 0, wall, length, back),
        box(width-wall, 0, 0, wall, length, back),
        box(wall-0.2, 0, cavity_top-0.2, 3.2, length, 2.2),
        box(width-wall-3, 0, cavity_top-0.2, 3.2, length, 2.2),
    ]
    for y in (0, 25, 51, 76):
        parts.append(box(wall-0.2, y, 0, width-2*wall+0.4, 4, back))
    for y in (0, 22, 45, 74):
        for x in (0, width-wall):
            parts.append(box(x, y, back-0.2, wall, 6, 11.9))
    # Two short bottom stops retain the SSD without a solid bottom wall.
    for x in (wall-0.2, width-wall-8):
        parts.append(box(x, 0, back-0.2, 8.2, 2.5, 11.9))
    for y in hook_positions:
        # Rear bridge overlaps the side rail and joins the complete skeleton.
        parts.append(box(-3.8, y, 0, 4.0, 14.2, back))
        parts.append(box(-3.8, y, front_z-2.4, 3.1, 14, back-front_z+2.4))
        parts.append(box(-3.8, y, front_z-2.4, 3.8+bezel_overlap, 14, 2.4))
    # Two top hooks wrap over the edge and return over the black top border.
    # Separate top parameters permit a loose fit and adjustable overlap.
    screen_top = hook_positions[1] + 14
    top_front_z = -top_opening
    top_left = box(-3.8, screen_top, top_front_z-2.4, 21.8, 3, top_opening+2.6)
    top_right = box(width-13.5, screen_top, top_front_z-2.4, 13.5, 3, top_opening+2.6)
    left_return = box(-3.8, screen_top-top_overlap, top_front_z-2.4,
                      21.8, top_overlap+0.2, 2.4)
    right_return = box(width-13.5, screen_top-top_overlap, top_front_z-2.4,
                       13.5, top_overlap+0.2, 2.4)
    parts.extend((top_left, top_right, left_return, right_return))
    # Overlap the left side bridge outside the lid for a manifold union.
    parts.append(box(-3.8, screen_top-0.2, -thickness, 3.0, 0.4, thickness))
    holder = parts[0]
    for part in parts[1:]:
        holder = holder.fuse(part)
    holder = holder.removeSplitter()
    if not holder.isValid() or len(holder.Solids) != 1:
        raise RuntimeError('One-piece holder must be a valid single solid')

    ssd = box(3.1, 3.1, back, 57.3, 74, 10.5)
    lid = box(0, screen_top-140, -thickness, 250, 140, thickness)
    ssd_collision = holder.common(ssd).Volume
    lid_collision = holder.common(lid).Volume
    dropped = holder.copy()
    dropped.translate(V(0, -0.5, 0))
    stop_interference = dropped.common(lid).Volume
    top_stops = []
    for pad in (top_left, top_right):
        probe = pad.copy()
        probe.translate(V(0, -0.5, 0))
        top_stops.append(probe.common(lid).Volume)
    if ssd_collision > 1e-5 or lid_collision > 1e-5 or min(top_stops) < 1e-5:
        raise RuntimeError('SSD, lid or either top stop geometry check failed')

    doc = App.newDocument('Samsung_T5_One_Piece_Holder')
    for name, shape in [('Holder_one_piece_PRINT', holder),
                        ('SSD_reference_do_not_print', ssd),
                        ('Lid_reference_do_not_print', lid)]:
        obj = doc.addObject('PartDesign::Feature', name)
        obj.Shape = shape
    doc.recompute()
    doc.saveAs(str(HERE / 'Samsung_T5_One_Piece_Prototype.FCStd'))
    # Orient on its long side. Some overhangs remain: inspect slicer support.
    printable = holder.copy()
    printable.rotate(V(0, 0, 0), V(0, 1, 0), -90)
    printable.translate(V(0, 0, -printable.BoundBox.ZMin))
    mesh = MeshPart.meshFromShape(Shape=printable, LinearDeflection=0.08,
                                  AngularDeflection=0.35, Relative=False)
    if not mesh.isSolid() or mesh.hasNonManifolds() or mesh.countComponents() != 1:
        raise RuntimeError('STL mesh must be watertight, manifold and connected')
    mesh.write(str(HERE / 'T5_One_Piece_Holder_PROTOTYPE.stl'))
    result = {
        'measured_lid_thickness_mm': thickness,
        'user_measured_black_bezel_width_mm': 7,
        'side_hook_opening_mm': opening,
        'nominal_total_clearance_mm': opening-thickness,
        'nominal_front_hook_overlap_mm': bezel_overlap,
        'nominal_margin_to_active_screen_mm': 7-bezel_overlap,
        'ssd_intersection_volume_mm3': ssd_collision,
        'lid_proxy_intersection_volume_mm3': lid_collision,
        'side_hook_count': len(hook_positions), 'top_hook_count': len(top_stops),
        'top_hook_opening_mm': top_opening, 'top_bezel_width_reported_mm': 7,
        'top_front_hook_overlap_mm': top_overlap,
        'downward_0p5mm_interference_mm3': stop_interference,
        'top_hook_interference_each_mm3': top_stops,
        'solid_count': len(holder.Solids), 'mesh_watertight': mesh.isSolid(),
        'mesh_components': mesh.countComponents(), 'volume_mm3': holder.Volume,
        'solid_pla_mass_estimate_g_at_1p24': holder.Volume * 0.00124,
        'print_bbox_mm': [printable.BoundBox.XLength, printable.BoundBox.YLength,
                          printable.BoundBox.ZLength],
        'status': 'Single CAD solid with two side and two top hooks; physical fit, supports, strength and retention are unverified.'
    }
    (HERE / 'one_piece_geometry_report.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    App.closeDocument(doc.Name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--lid', type=float, default=4)
    parser.add_argument('--opening', type=float, default=6)
    parser.add_argument('--overlap', type=float, default=3)
    parser.add_argument('--top-opening', type=float, default=6)
    parser.add_argument('--top-overlap', type=float, default=5)
    args = parser.parse_args()
    build(args.lid, args.opening, args.overlap, args.top_opening, args.top_overlap)
