# Cece ESP carrier R7 review

Updated to the user correction: module 21.3 mm long, 18 mm wide and 4.5 mm thick. Width uses the larger end of the given 17-18 mm range. The green solid represents the complete module envelope, not bare PCB laminate.

- Frame opening: 18.6 mm; channel: 5.1 mm, nominal 0.3 mm clearance each side.
- Long support top stays aligned with frame top at Z=50.7 mm.
- Rail depth remains 10.4 mm, including the requested 5 mm increase.
- Side grips remain 20 mm tall; USB end remains open for sliding insertion.
- Single printed carrier, no separate insert. Prior revisions preserved.

CAD checks: valid single solid, closed STL, no modeled sensor interference, no unintended head intersection. Side contact pads intentionally have 0.15 mm interference per side. Sampled loading travel is 23.5 mm in 0.5 mm increments, checked outside the head. Load the board before installing the carrier in the head.

The carrier has 4.8 mm modeled clearance to the ultrasonic PCB. Solid PLA volume corresponds to about 2.50 g; this is not a sliced weight estimate.

Camera placement remains provisional. Module centre is now Z=40 mm while lens centre remains Z=38 mm at the existing aperture. That 2 mm offset requires checking on the actual assembly; it is not verified by the revised width/thickness measurements. The resulting combined depth envelope is 25.05 mm, which must also be reconciled with the previous 23.6 mm measurement. Rail contact with component-free board edges, retention and physical insertion require checking.

R7 was subsequently sliced and sent on 8 November 2026 at the user request: green PLA, 0.20 mm layers, two walls, 10% infill, critical tree supports only. Estimated 2.43 g and 14m30s. Printer accepted the job and began homing; physical completion was not verified. R8 supersedes it after the physical-fit correction. Open Cece_Head_ESP_Assembly_R7.FCStd for review; Cece_ESP_Side_Carrier_R7_PREVIEW.stl contains only the carrier.
