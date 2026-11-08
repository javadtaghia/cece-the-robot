# Cece only — persistent user requirement

The word `otto` is forbidden, case-insensitively, in assistant replies and all
new user-facing filenames, labels, model names, documentation and printed text.
Do not repeat the forbidden word to acknowledge this rule. Use Cece.

## Authoritative design

- Cece has lowercase `cece` on the back of the body and a heart around the LCD.
- Use `experiments/cece/no_led_mouth/Cece_No_LED_Mouth_Assembly.FCStd` for the
  current assembly and its `Rounded_Head_Study` solid for the current head.
- The current head STL is
  `experiments/cece/no_led_mouth/Cece_Head_No_LED_Mouth_TEST_ONLY.stl`.
- Verify the selected source against these files before building mounts.
- Never substitute a legacy reference head, including files in old `parts`
  directories, even when its filename contains Cece.
- No web addresses or third-party branding may be introduced into print parts.
- Preserve earlier Cece versions; make revisions under explicit new names.

## Legacy material

Legacy reference geometry is not current design. Do not load it into current
assemblies or print projects. Preserve legally required third-party license
and attribution records; do not falsify those or break source dependencies
merely to remove a historical identifier. User-facing outputs remain Cece only.

## Fit claims

Latest user correction (8 November 2026): ESP module length 21.3 mm retained,
width 17-18 mm (use 18 mm for clearance) and thickness 4.5 mm. This replaces
the earlier 12.8 mm width and assumed 1.6 mm thickness. Overall USB length
23.2 mm was previously measured. Earlier 23.6 mm stack depth needs reconciling
with the updated module; lens offset, component layout, bare PCB thickness
and exact installed sensor placement are not yet measured.
Label assumptions clearly; do not claim physical fit or camera visibility
solely from a bounding-box model or zero-volume intersection test.

## Current ESP carrier direction

R9 uses USB-first insertion: USB at the far/leading end (-X), antenna at
the open entry end (+X). Both wall plates must be solid, matching sections
without loading windows; R9 uses 2 mm thickness and a 6 mm deep crossbar.
Keep the camera-pressure flap separate in purpose from the stiff wall supports.
The requested 7 mm centreward and 2 mm upward correction is implemented
relative to R8. Camera offsets remain inferred; do not describe the proxy
alignment as measured physical fit.

## Latest carrier revision

R10 follows the marked physical-part photo: A means front-to-back depth,
not vertical rail spacing. Rail depth is 12.4 mm (+2), usable channel depth
is 7.1 mm (+2), and the 18.6 mm vertical opening is unchanged. B is relieved
flush to the main crossbar at Z=50.7; keep the camera flap root ahead of
that relief. R9 and earlier revisions remain preserved.

R11 adds an open 22.3 x 7.1 mm slot through the marked upper cap over the
board channel for pin access. Keep this opening clear of the flap root.
Actual pin geometry remains unmeasured; do not claim physical pin clearance.
