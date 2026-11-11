# Superseded opposite-end trial: do not print R14

R15 corrected the shoulder position; R16 is the current reinforced carrier. R14 interpreted screen-right as positive X; the supplied view shows the requested end at negative X.

# Cece carrier R14: move right shoulder sideways

User confirmed the highlighted frame should move sideways, taking its right-hand shoulder beyond the board end.

- Right shoulder moves +3 mm X: centre 16.15 to 19.15 mm.
- Inner face moves 14.15 to 17.15 mm, giving 3.5 mm nominal clearance from the board end at X=13.65 mm (previously 0.5 mm).
- U connecting span extends 3 mm to meet it; the former shoulder footprint is removed.
- Left shoulder, rear-span depth position, board, USB and camera retain their R13 positions.

## Validation

Boolean comparison against R13 confirms removed material only at X=14.15..17.15 and added material only at X=18.15..21.15. Board, USB socket, camera housing and lens shapes and coordinates are unchanged. The added right-end clearance volume is unobstructed.

The carrier remains one valid solid with a closed STL. Existing modeled head, source component allowances, ultrasonic, USB and sampled insertion checks pass. Real header-pin and connector dimensions remain unmeasured; this is a geometric correction, not proof of physical pin fit or stiffness.

Open Cece_Head_ESP_Assembly_R14.FCStd. Print geometry: Cece_ESP_Side_Carrier_R14_PREVIEW.stl. R13 is preserved. R14 has not been sliced or sent to print.
