# Cece 2 — four-servo speed study

Branch: `codex/cece2`. `main` remains Cece. This directory adds a separate
candidate controller and measured simulation results; the original Cece CAD,
firmware and controllers are preserved. No replacement STL is released here.

The target is **10 times the previous simulated walking speed**, not ten times
the animation playback rate. The original 10-step Bullet result was 84.88 mm
in 40 s (2.122 mm/s), giving an initial target of 21.22 mm/s. This study also
repeats the old gait for 40 steps at the same command rate as the candidate.
These are model measurements, not measurements of an assembled robot.

## Selected configuration

Keep the existing four positional SG90 servos: one **hip yaw** (vertical axis)
and one **ankle roll** (fore/aft axis) per leg. Preserve the existing leg and
foot interfaces while testing the faster control profile. The simulations
do not yet justify buying different motors or printing longer legs.

| Setting | Previous gait | Cece 2 candidate |
| --- | --- | --- |
| Hip swing | ±10° | ±15° |
| Body roll target | 12° | 12° |
| Weight transfer | 800 ms | 140 ms |
| Lift | 800 ms | 60 ms |
| Hip swing | 800 ms | 200 ms |
| Land | 800 ms | 60 ms |
| Return to centre | 800 ms | 100 ms |
| Alternating half-step | 4.00 s | 0.56 s nominal |
| Target updates | 50 Hz in comparison runs | 50 Hz |

Angles are offsets in the model's joint coordinates, not absolute angles to
write to a physical servo. Actual horn neutral angles, handedness, mechanical
limits and PWM endpoints must be calibrated separately.

The five phases retain smooth cubic interpolation. The larger stride and
different phase times provide the speed increase. Simply dividing all old
durations by ten failed: it moved at 21.5 mm/s but completed **zero** detected
lift-and-land events. That result is retained in `speed_sweep.json`.

## Evidence and acceptance

`selected_validation.json` contains the final 40-step comparisons and
sensitivity results. The screening rule is: 40/40 lift-and-land events,
no fall, positive forward travel, no detected stance-foot flight, and at most
2 mm of stance-foot origin movement during swing/landing. The latter is a
screening threshold, not a hardware specification. Integrated tangential
contact movement is additionally reported and is **not zero**; passing this
screen does not establish a slip-free gait.

All raw reports, including rejected trials, are preserved in
`raw_simulation_results.zip`. Generated `results/` files remain local and are
ignored by Git to keep the review readable. The report and geometry-check
tools read from the archive when a raw report has not been regenerated.

`finalist_refinement.json` includes same-length baseline runs. At 240 Hz the
candidate measured 22.632 mm/s versus 2.197 mm/s for the old gait; at 480 Hz it
measured 22.356 versus 2.178 mm/s. Both completed 40/40 lift-and-land events
with no fall. Maximum stance-foot origin movement was 1.79 and 1.97 mm.
That is about **10.3×** in these nominal model comparisons.

The old PyBullet position gain was specified per physics step, so its response
changed when the solver step changed. The final model uses
`gain = 1 - 0.88 ** (240 / physics_hz)` to preserve the reference position-error
response time. It equals the old 0.12 gain at 240 Hz. This is an explicit
controller-model assumption, not a measured SG90 tuning parameter or a change
to the electronics. Both old and candidate gait comparisons use this rule.
Raw fixed-gain failures are retained alongside the corrected-model runs.

`cad_trajectory_clearance_results.json` checks ten pairs of actual body, leg
and foot STL solids at 120 Hz over ten candidate half-steps. Check its trace
hash against `results/bullet_geometry_selected_final_results.json`. This is a
discrete mesh test: horns, fasteners, wiring and the rest of the head contents
are not included. The physics engine itself still uses simplified colliders
and disables self-collision.

The modeled robot is 339.159 g. The original estimated hardware masses,
inertias, contact polygons and PLA solids are retained; no mass was silently
removed to obtain the speed. The [purchased servo listing](https://rapidroboticsaustralia.com.au/products/sg90-micro-servo)
specifies 0.12 s/60° **without load**, 1.8 kg·cm holding torque at 4.8 V, and
4.8–5 V operation. The simulation uses an assumed 0.08 N·m cap and a hypothetical
linear torque/speed envelope, not a measured continuous rating. Real backlash,
rail sag, bearing friction, temperature, floor friction and print tolerance
remain outside the model.

**Status: speed target reached in the nominal Bullet model; hardware, Gazebo,
firmware deployment and a robust physical walking release are not approved by
these results.** Inspect the sensitivity failures rather than assuming the
nominal result applies to every payload or floor.

| Sensitivity case | Speed | Lift/land | Outcome |
| --- | ---: | ---: | --- |
| Nominal, 240 Hz physics | 22.632 mm/s | 40/40 | Passes screen and 10× target |
| Nominal, 480 Hz physics | 22.356 mm/s | 40/40 | Passes screen and 10× target |
| Lower assumed floor friction | 20.116 mm/s | 40/40 | Walk screen passes; speed is below 10× |
| Additional assumed 60 g | 22.893 mm/s | 40/40 | Model screen passes; not a physical payload rating |
| 0.06 N·m motor cap | 22.931 mm/s | 39/40 | Reject: missed lift/landing |
| 0.04 N·m motor cap | 23.202 mm/s | 0/40 | Reject: displacement without walking |
| Assumed no-load speed 350°/s | 22.528 mm/s | 40/40 | Reject: 2.33 mm stance-origin movement |

The candidate can have roughly 14° of peak target-tracking error in this
servo approximation. The speed result is not evidence of accurate joint
tracking or adequate margin for a weaker delivered servo.

## Why retain this leg configuration first?

| Configuration with four servos | Benefit | Unresolved cost |
| --- | --- | --- |
| Hip yaw + ankle roll per leg | Reuses current electronics and joints; screened above | Small stride, lateral sway and floor-dependent contact |
| Hip pitch + ankle roll per leg, with passive parallel links | Can produce a direct fore/aft stride while keeping foot pitch controlled | Requires new hip mounts, link pivots and a verified linkage; not simulated or released here |
| Hip pitch + knee pitch per leg | Direct sagittal leg motion | Uses all four motors without an active lateral weight-transfer joint; needs another balancing mechanism |

Longer legs alone increase load moment and centre-of-mass height. Under the
assumed 0.08 N·m cap, 339.159 g gives only about 24 mm of static horizontal
load lever before that cap is used (`torque / weight`), with less margin during
acceleration. A new linkage should only replace this candidate if measured
servo limits, actual fit or physical walking require it.

## Run the live Bullet simulation on this PC

From the repository root in PowerShell:

```powershell
& '.\experiments\cece2\run_cece2.ps1' -Steps 40
```

It opens a live physics window and runs at real-time pace, then closes when
the requested run finishes. It does not control or flash an ESP32.
For a portable Python environment with PyBullet, NumPy, SciPy, trimesh,
manifold3d and Pillow installed:

```text
python experiments/cece2/simulate.py --gui --name gui_cece2 --steps 40 --hip-deg 15 --roll-deg 12 --phase-seconds 1 --phase-weights .14,.06,.20,.06,.10 --command-hz 50 --normalized-controller
```

## Reproduce the checks

Use the same Python environment as the existing `cece/bullet_gait` study:

```text
python experiments/cece2/test_gait.py
python experiments/cece2/validate_selected.py
python experiments/cece2/simulate.py --name geometry_selected_final --steps 10 --hip-deg 15 --phase-seconds 1 --phase-weights .14,.06,.20,.06,.10 --command-hz 50 --normalized-controller --geometry-trace --trace-hz 120
python experiments/cece2/check_cad_trajectory.py --name geometry_selected_final
python experiments/cece2/export_targets.py
```

`profile.json` and `cece2_forward_50hz_offsets.csv` describe the candidate.
The CSV is for inspection or subsequent firmware integration, not a ready
servo calibration. `create_simulator.py` regenerates this isolated simulator
from the unchanged original and adds the explicitly recorded options. Final
reports record source/asset hashes. Intermediate sweep reports are exploratory
and may refer to earlier revisions of the study script; use the selected
validation for the current implementation.

## Gazebo trial

### Separate Cece 2 viewing scene

`Cece2_Assembly.FCStd` is a coloured FreeCAD inspection assembly of the retained
mechanism, with the Cece 2 profile recorded in its model tree.
`show_cece2.FCMacro` recreates that view without overwriting Cece's CAD.

In Ubuntu/WSL, launch a separate Gazebo scene from the repository root:

```bash
bash experiments/cece2/run_view.sh
```

Then, in another Ubuntu/WSL terminal at the repository root:

```bash
bash experiments/cece2/walk_view.sh 40
```

This uses the isolated `cece2_view` transport partition, model `cece2` and
world `cece2_room`. Its ankle stops allow the 34.248° edge-transfer target
(the old scene clipped it at 30°), and its velocity limit is set to the
assumed 500°/s no-load upper bound. Motor effort stays at 0.08 N·m. These
are scene assumptions; Gazebo's PID and simple box colliders differ from the
Bullet study. `gazebo_view_check.json` records all four joints moving during
the live view. The observed position moved sideways as well as forward;
straight-line walking and the 10× result are **not** established in Gazebo.

`Cece2_FreeCAD_Front.png` and `Cece2_Gazebo_View.png` are captures of these
views, not fabricated concept images. The Gazebo service utilities focus the
camera and capture the actual rendered view.

### Using the existing Cece world instead

Start and reset the existing world using `../cece/START_HERE.md`, then stop the
old gait controller. In the Ubuntu/WSL terminal, using the same `GZ_PARTITION`
as Gazebo:

```bash
source /opt/ros/jazzy/setup.bash
python3 experiments/cece2/run_gazebo.py --steps 10
```

This publishes the candidate's targets on the existing four `/cece/` joint
topics. It honours the existing stop marker and returns toward neutral on
exit. It is an optional controller; the old controller and interface are
unchanged. Gazebo's existing contact model differs from Bullet, so this
command is **not** a claim that the same speed or foot lift has been measured
there. The fast profile currently covers forward walking only. Reverse,
turning and autonomous transitions require their own checks.

Before changing the real firmware, verify the delivered servo horns and joints,
measure the complete robot's mass and 5 V supply under simultaneous motion,
then test restrained low-speed steps while recording foot clearance, slippage
and current. The original Cece joint-retention issues remain relevant; faster
commands do not repair unverified mechanical attachments.
