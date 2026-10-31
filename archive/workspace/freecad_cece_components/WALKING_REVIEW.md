# Walking review — current component study

The existing FreeCAD assembly is not a proven walking robot. The two leg
gearmotors are shown as rotating at horizontal, left-to-right axes. They have
no D-shaft couplers, bearings, motor mounts, load-bearing chassis or feedback.
Even if those were made, they only swing the legs front/back: no mechanism
has been specified to shift weight sideways and hold it over one foot. The
feet and legs also move as one rigid piece. There is no checked gait or
controlled foot-lifting sequence, and no clearance checks over joint motion.

## First-order balance check

The component study's `static_balance_estimate.json` assumes 236.63 g total
including a 52 g two-AA holder. On flat ground with the model at rest, the
centre of mass projects between feet; the inside edge of each foot is
approximately 18 mm from the midline. The projection must move by roughly
18 mm simply to reach a one-foot support boundary, with zero margin. Dynamic
walking may use momentum, but that has not been shown or controlled here.

Merely moving the battery sideways is not a realistic solution in this exact
body: in an ideal translation without shifting any other mass, moving 52 g
would require about 18*236.63/52 = 82 mm of travel from the middle to move
the total COM 18 mm. The assumed 58 mm-wide holder inside a 72.8 mm-wide
cavity has only about 7.4 mm of ideal side travel from the centre, even
before guides, wires and other items. That movement would shift the total COM
roughly 1.6 mm. The hardware placement needs a different approach.

## Candidate mechanism for further development

Investigate a compact **two-axis hip**: one motor rocks the torso sideways
over the supporting foot, while a second motor drives a mechanically linked,
alternating leg swing. A rigid chassis and moving joints are required. Arms
and head may retain separate small motors. This is an engineering proposal,
not a mechanism that exists in the current CAD and not a proven gait.

A first quasi-static geometric target is a lateral COM displacement of
18 mm plus a margin. Using an idealised 70.7 mm COM height and a rotation
about a ground-level centre, reaching 21 mm takes approximately 17 degrees
of roll. This is an order-of-magnitude geometric target only; the actual
contact edge, rolling pivot, support foot rotation, kinematics and floor
friction change the result. More detailed geometry may need more or less.

Next work requires an explicit linkage or geared hip design, real shaft
couplings and supports; a free-base model that uses the new geometry, actual
mass distribution, floor contact and motor limits; and repeated trials with
varying friction, mass and perturbations. A positive result must include
repeatable alternating steps and net forward movement without external
support, followed by a real-world prototype. The old chick and crank
simulations are separate candidates and cannot validate this assembly.

Source calculation: `../check_cece_components_balance.py` and
`static_balance_estimate.json`. All masses and placements are provisional.
