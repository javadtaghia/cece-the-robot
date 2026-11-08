# Cece carrier R13: route around the board

R13 removes the straight central rail completely. A U-shaped route connects the remaining frame ends, with arms outside the module ends and a rear span behind its pin-access area. This replaces the repeated ledge-trimming approach in R11 and R12.

- Removed central straight span: 22.3 mm long.
- Rear span: centre Y=-6.5 mm, 4 mm deep, 2.4 mm high.
- Clear space from the modeled rear board face to the rear span: 6.45 mm.
- Arms: centres X=-10.15 and +16.15 mm, 4 mm wide; outside the 21.3 mm board length.
- Nearest new route to the reserved prototype-board component envelope: nominal 0.5 mm. An earlier trial offset intersected this allowance and was rejected before export.
- Board, camera, USB, flap contact point and head-wall supports retain their existing positions. R12 is preserved.

## Validation

The former central straight-rail volume is empty. The board-to-new-span access zone is empty. The new route has zero overlap with every solid or allowance in the source assembly, including the prototype-board component allowance. Existing head, USB, ultrasonic and sampled insertion checks pass. Carrier is one valid solid; STL is closed.

These are CAD checks. Exact pin and connector geometry remains unmeasured, and U-frame stiffness and flap force have not been physically tested. The 6.45 mm gap is to the board envelope, not an asserted margin around actual pins.

Files: Cece_Head_ESP_Assembly_R13.FCStd and Cece_ESP_Side_Carrier_R13_PREVIEW.stl. R13 has not been sliced or printed.
