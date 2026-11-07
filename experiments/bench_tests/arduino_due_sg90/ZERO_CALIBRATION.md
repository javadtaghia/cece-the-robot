# Calibrate physical zero before changing the walking gait

The supplied video was inspected at full-frame and 0.3 s intervals. The body
is held inverted, both feet are unloaded, and repeated ankle roll and leg yaw
are visible. It does not establish a defective encoder, correct joint signs,
calibrated angles, loaded balance or ground walking. The walking code commands
hip yaw intentionally; with the body held fixed, the legs visibly twist.

The user clarified that the white horns were physically repositioned. This
changes mechanical indexing / neutral, not the direction of shaft rotation
for an increasing pulse. In particular, rotating a hip servo case around its
output axis does not by itself reverse that axis. Check each positive joint
direction before keeping or removing the previous right-side inversions.

The ordinary three-wire SG90 does not report shaft angle to the Due. Arduino
Servo `readMicroseconds()` returns stored command timing, not an encoder
measurement. The current walking sketch already treats its `NEUTRAL_US` as
zero, but all four values were assumed to be 1500 us. That may not correspond
to straight legs and flat feet after fitting the horns.

## Standalone diagnostic — not uploaded automatically

`DueZeroCalibration/DueZeroCalibration.ino` is one file, for the Due Programming
Port at 115200 baud. It performs no automatic gait or startup movement.
The confirmed pins remain 1=D6 left hip, 2=D7 right hip, 3=D8 left foot,
4=D9 right foot. It applies no motor-direction signs, so raw positive-pulse
motion can be observed unambiguously. The existing walking firmware and its
direction values have not been changed by this diagnostic.

1. Support the robot upright with feet unloaded. Select `1`; this only selects
   motor 1 and leaves outputs off. Send `c` to hold its configured zero.
2. Check the leg's neutral orientation relative to the body. If grossly wrong,
   mark the servo shaft's centred position, remove servo power and re-index
   the horn mechanically without turning the shaft. Do not force the gears
   or use a hard stop as a homing reference.
3. For fine alignment, `+` and `-` adjust the commanded pulse by 5 us. Fine
   adjustment is limited to 1300–1700 us, rather than a broad travel sweep.
4. When visibly aligned, send `z` to accept the current **commanded pulse** as
   that joint's logical zero. It does not measure the physical shaft angle.
5. Send `t` to make a small +50 us excursion and return after one second.
   Observe which way the joint moves using a consistent upright robot frame.
6. Repeat for motors `2`, `3`, `4`, then send `p` to print the four zeros.
   `x` or `stop` releases signals at any time; it does not disconnect servo power.

RAM calibration resets when power is removed. Copy the printed `NEUTRAL_US`
array into the walking sketch, or provide it for incorporation and re-upload.
That makes the firmware return to the same calibrated reference at each start;
it cannot make an unknown arbitrary shaft position at power-up become zero.

If the selected joint moves erratically while the printed target remains
constant, inspect supply voltage under load, connections, binding, loose
horn/spline and servo feedback/gear faults. The video alone does not identify
which of those is responsible. If it is stable at a held target but moves
incorrectly during gait, inspect neutral offsets, joint mapping, direction
signs and command timing first.
