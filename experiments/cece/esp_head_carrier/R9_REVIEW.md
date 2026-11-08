# Cece carrier R9 review

Supersedes the prepared R8 print. R8 was not sent after the cutter error; the user subsequently confirmed the fault cleared and the plate empty, then requested these geometry changes. Prior revisions are retained.

- Cradle moves 7 mm toward the head centre (-X from the R8 position), and 2 mm upward. Wall contact locations remain fixed.
- USB orientation reversed: USB leads into the far end (-X); the antenna end (+X) stays open for insertion.
- Dedicated far-end USB portal: 8.5 mm front-to-back x 10 mm high. A 15 x 7 x 8 mm cable-plug envelope is checked, but is not measured from the actual cable.
- Both wall supports are whole, unperforated plates, 20 mm tall and 2 mm thick, replacing the prior 0.8 mm sections. Outer contact span remains 81.1 mm for the nominal 80.8 mm head interior.
- Crossbar depth increases from 4 to 6 mm and riser width from 1.5 to 2.2 mm. The thin flexible section is confined to the camera-pressure flap.
- Upper cradle rail is trimmed to Z=52.1 mm to clear the current head roof after the lift. Camera flap attaches there and bears on the modeled rear housing. No lens contact.

## Validation and limits

One valid solid, closed STL. Both side plates are explicitly checked as complete solids without removed material. No unintended overlap with the modeled head or ultrasonic sensor; wall contact pads intentionally interfere by 0.15 mm per side. Sampled USB-first insertion travel has no fixed-carrier collision. Hold the flap clear during loading and install the loaded carrier into the head.

Camera location is inferred from the requested fit correction and placed at the existing aperture for review. It is not independent evidence of physical alignment. The module is 21.3 x 18 x 4.5 mm; lens offset relative to its centre is provisionally -3 mm in X and -4 mm in Z. Component layout, cable dimensions, clear edge lands, ribbon route, flap preload and stiffness need a physical check. Do not force the stiffer wall plates into the head.

Open Cece_Head_ESP_Assembly_R9.FCStd for review; Cece_ESP_Side_Carrier_R9_PREVIEW.stl is the single printed carrier. R9 has not been sliced or sent to print.
