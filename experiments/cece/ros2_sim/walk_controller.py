"""Experimental four-joint Gazebo gait. Does not command physical hardware."""
import argparse
import math
import json
from pathlib import Path
import sys
import time

from gz.transport13 import Node
from gz.msgs10.double_pb2 import Double

NAMES = ("left_hip", "left_ankle", "right_hip", "right_ankle")
STOP_FILE = Path(__file__).resolve().parent / "generated" / ".cece_stop"
POSES = json.loads((Path(__file__).resolve().parent.parent / "hip_drive_study" /
                    "edge_transfer_results.json").read_text())["poses"]
EDGE = sorted((abs(row["body_roll_deg"]), abs(row["selected"]["swing_ankle_deg"]))
              for row in POSES if row["stance"] == "left" and row["selected"])

def edge_angle(roll):
    for (x0, y0), (x1, y1) in zip(EDGE, EDGE[1:]):
        if roll <= x1:
            fraction = (roll - x0) / (x1 - x0)
            return min(28.0, y0 + fraction * (y1 - y0))
    return min(28.0, EDGE[-1][1])

def targets(half, phase, t, direction="forward"):
    # Slow, bounded test gait adapted from the existing Bullet experiment.
    ease = t * t * (3 - 2 * t)
    left_stance = half % 2 == 0
    start = 0 if half == 0 else (-10 if left_stance else 10)
    end = 10 if left_stance else -10
    sign = 1 if left_stance else -1
    contact = edge_angle(12)
    if phase == 0:
        roll = 12 * ease
        a, b, hip = roll, edge_angle(roll), start
    elif phase == 1:
        a, b, hip = 12, contact + (12 - contact) * ease, start
    elif phase == 2:
        a, b, hip = 12, 12, start + (end - start) * ease
    elif phase == 3:
        a, b, hip = 12, 12 + (contact - 12) * ease, end
    else:
        roll = 12 * (1 - ease)
        a, b, hip = roll, edge_angle(roll), end
    if direction == "backward":
        left_hip, right_hip = -hip, -hip
    elif direction in ("left", "right"):
        turn_sign = -1 if direction == "left" else 1
        if phase == 0 and half == 0:
            stance_hip, swing_hip = -10 * ease, 10 * ease
        elif phase < 2:
            stance_hip, swing_hip = -10, 10
        elif phase == 2:
            stance_hip, swing_hip = -10 + 20 * ease, 10 - 20 * ease
        else:
            stance_hip, swing_hip = 10, -10
        if left_stance:
            left_hip, right_hip = turn_sign * stance_hip, turn_sign * swing_hip
        else:
            left_hip, right_hip = turn_sign * swing_hip, turn_sign * stance_hip
    else:
        left_hip, right_hip = hip, hip
    if left_stance:
        return [left_hip, sign * a, right_hip, sign * b]
    return [left_hip, sign * b, right_hip, sign * a]

def main(steps=None, phase_seconds=0.8, direction="forward"):
    if steps is None:
        parser = argparse.ArgumentParser()
        parser.add_argument("--steps", type=int, default=0, help="0 runs until stopped")
        parser.add_argument("--phase-seconds", type=float, default=0.8, help="Seconds per gait phase; experimental")
        parser.add_argument("--direction", choices=("forward", "backward", "left", "right"), default="forward")
        args = parser.parse_args()
        steps, phase_seconds, direction = args.steps, args.phase_seconds, args.direction
    if not 0.3 <= phase_seconds <= 2.0:
        raise ValueError("Phase duration must be between 0.3 and 2 seconds")
    if steps < 0:
        raise ValueError("Step count must be nonnegative")
    node = Node()
    pubs = [node.advertise("/cece/" + name, Double) for name in NAMES]
    time.sleep(1.5)  # Allow transport discovery.
    missing = [name for name, pub in zip(NAMES, pubs) if not pub.has_connections()]
    if missing:
        raise RuntimeError("Gazebo joint controllers not connected: " + ", ".join(missing))
    def send(angles):
        for pub, angle in zip(pubs, angles):
            msg = Double()
            msg.data = math.radians(angle)
            pub.publish(msg)
    half = 0
    try:
        while (steps == 0 or half < steps) and not STOP_FILE.exists():
            for phase in range(5):
                start = time.monotonic()
                while not STOP_FILE.exists():
                    t = min(1.0, (time.monotonic() - start) / phase_seconds)
                    send(targets(half, phase, t, direction))
                    if t >= 1:
                        break
                    time.sleep(.05)
                if STOP_FILE.exists():
                    break
            half += 1
    finally:
        send([0, 0, 0, 0])
        STOP_FILE.unlink(missing_ok=True)
    print("Gait targets sent to Gazebo. Motion and balance require observation.")

if __name__ == "__main__":
    main()
