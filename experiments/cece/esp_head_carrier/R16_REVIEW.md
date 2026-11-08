# Cece carrier R16: reinforced USB-end upright

R16 addresses the upright and frame roots marked in the user's breakage photo. R15 is preserved.

- Added a 4 x 4 mm external buttress, 19.4 mm tall, joining the upper U-shaped shoulder to the lower cradle.
- Added a joining web alongside the existing thin upright. It stops below the pin-access opening.
- Broadened the lower root and added triangular braces at the upper and lower connections.
- Added 405.81 cubic millimetres of material, approximately 0.50 g of solid PLA. Actual sliced weight includes supports and depends on settings.
- Board, camera, USB socket, head and ultrasonic positions remain unchanged. No material was removed from R15.

## Verification

The builder checks one valid solid, a closed STL, the preserved board-access zones, modeled USB socket and plug clearance, head and ultrasonic intersections, and a 23.5 mm insertion/extraction sweep in 0.5 mm steps. All pass. The added reinforcement also has no intersection with the source assembly parts or clearance allowances.

These are geometric checks, not a measured breaking-load test. Actual pin geometry remains unmeasured; the camera flap retains its intended provisional contact. No strength multiplier is claimed.

## Files and printing

- `Cece_Head_ESP_Assembly_R16.FCStd`: assembly with the electronics proxies.
- `Cece_ESP_Side_Carrier_R16_PREVIEW.stl`: carrier only.
- `build_cece_mount_R16.py`: reproducible geometry and checks.
- `cece_mount_R16_checks.json` and `R16_change_check.json`: validation results.

For the next print use PLA, 0.20 mm layers, 4 walls and 15% infill, with essential supports. The prior 2-wall lightweight print profile has not been reused for R16. Clip support branches before peeling them away from the narrow cradle and camera flap. R16 has not been sliced or sent to the printer.
