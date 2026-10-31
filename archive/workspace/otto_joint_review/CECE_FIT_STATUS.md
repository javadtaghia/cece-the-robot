# Cece foot and SG90 fit — preliminary

The target is the Rapid Robotics SG90 RR-MOT-SG90, listed overall as 23 x 12.2 x 29 mm. The seller lists horns and accessories, but does not specify detailed horn, shaft or case geometry. Source: https://rapidroboticsaustralia.com.au/products/sg90-micro-servo

## Printed leg/foot interference
The actual Cece cleaned foot meshes and corresponding leg STL meshes were checked for volume intersection every five degrees from -45 to +45 around an estimated Y axis at x=+/-25.5, z=-71.5 mm. Both sides reported zero intersection at sampled angles. Exact contact, positive clearance, hardware, all intermediate angles, shaft alignment, assembled loads and real fit are not checked. Run `python otto_joint_review/cece_clean_foot_sweep.py`; outputs in `cece_clean_foot_sweep.json`.

## Conservative rectangular-envelope test
In one candidate placement, a 12.7 x 23.5 x 29.5 mm box intersects neither the right leg nor foot; 13.2 x 24 x 30 mm intersects the leg by 108.56 mm3. Box dimensions are the nominal retail dimensions plus 0.5 mm and 1 mm on each axis respectively. The box is a coarse screen only: its pose does not establish shaft alignment and ignores mounting ears, horn, screws, wires, and shape changes. This does not demonstrate a fit or that 1 mm extra represents real tolerance.

## Hardware and decision
Each of the four servo joints requires a compatible horn and retaining hardware. The original Otto guide shows ankle horns fixed to the feet using small screws. These are purchased hardware, not demonstrated printable adapters. The approximate turret and horn model generated interference but has unverified geometry and placement; do not infer either definite design failure or success. No new adapter is release-ready. Finalize exact horn/shaft/fastener geometry and all positions, repeat geometric clearance and assembly analysis, then physically test the already printed parts at low power.
