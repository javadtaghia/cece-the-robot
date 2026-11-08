# Cece carrier R10

Changes from the printed R9, following the marked physical-part photo:

- A is front-to-back depth, as confirmed by the user. Rail depth increases from 10.4 to 12.4 mm. The usable board channel also increases from 5.1 to 7.1 mm, extending toward the camera; the rear datum stays fixed. The vertical rail spacing remains 18.6 mm.
- B is the raised central backing ridge over the main crossbar. Its upper surface is trimmed flush to the main frame at Z=50.7 mm. The camera-flap root ends ahead of this relief so it does not add a raised strip back into that area.
- Board, USB, lens and wall support positions retain R9 locations. Solid side supports and the USB-first insertion direction are retained. The USB opening extends in depth with the channel.

## Checks

The generated carrier is one valid solid and the exported STL is closed. The relieved B region contains no remaining raised material. The sampled insertion sweep clears the modeled fixed carrier. Head and ultrasonic intersection checks pass except for the existing intentional wall contact pads; the camera pad retains its existing provisional preload. These are geometry checks, not measured physical-fit or stiffness proof.

The deeper channel provides more clearance and less restraint in that direction. Check the actual board retention, camera alignment, cable access and flap contact before use. No changes to the measured electronics envelope were made to force a clearance result.

## Files

- Cece_Head_ESP_Assembly_R10.FCStd
- Cece_ESP_Side_Carrier_R10_PREVIEW.stl
- build_cece_mount_R10.py
- cece_mount_R10_checks.json

R9 is preserved. R10 has not been sliced or sent to the printer.
