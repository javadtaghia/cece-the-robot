# Cece carrier R12: remove marked ledge

The user identified the remaining frame ledge beside the board in R11. R12 extends the clearance cut down to Z=48.0 mm, below the crossbar underside, and 2 mm farther behind the board. The previous roof-only cut did not remove this ledge.

- Opening: 22.3 mm along the board and 9.1 mm front-to-back.
- Rear rail begins at Y=-12.65 mm; board rear face remains Y=-14.95 mm, giving 2.3 mm nominal clearance in this region.
- A continuous rail 2.45 mm deep and 2.4 mm high remains behind the opening to keep the part connected. Its stiffness has not been physically tested.
- Electronics, camera flap contact, depth increase and solid wall supports retain their previous positions. R11 is preserved.

## Checks

Single valid solid; closed STL. No material remains in the opening or the explicitly checked 2 mm rearward board-edge clearance zone. The remaining rail is continuous in CAD. Existing sampled insertion and modeled head/ultrasonic checks pass, with only the documented intentional contact pads and camera preload.

The green shape is an envelope, not a detailed model of the purchased board. Actual pin directions, length and connector dimensions remain unmeasured; do not treat the clearance check as verified hardware fit.

Open Cece_Head_ESP_Assembly_R12.FCStd. The printable part is Cece_ESP_Side_Carrier_R12_PREVIEW.stl. R12 has not been sliced or printed.
