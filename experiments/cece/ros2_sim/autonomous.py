"""Experimental Gazebo-only obstacle avoidance using range data and camera health.

This cannot drive physical motors. The Gazebo range is a lidar approximation;
the camera is monitored for availability, not interpreted for obstacles.
"""
import math
import threading
import time
from pathlib import Path
from gz.transport13 import Node
from gz.msgs10.laserscan_pb2 import LaserScan
from gz.msgs10.image_pb2 import Image
import walk_controller

AUTO_STOP = Path(__file__).resolve().parent / "generated" / ".cece_auto_stop"
CLEARANCE_M = 0.5
STALE_S = 3.0

class SensorState:
    def __init__(self):
        self.lock = threading.Lock()
        self.ranges = None
        self.range_time = 0.0
        self.camera_time = 0.0
        self.forward = False
        self.moving = False

    def scan(self, msg):
        values = [x for x in msg.ranges if not math.isnan(x) and x >= msg.range_min]
        with self.lock:
            self.ranges = min(values) if values else None
            self.range_time = time.monotonic()
            blocked = self.ranges is None or self.ranges < CLEARANCE_M
            if self.forward and blocked:
                walk_controller.STOP_FILE.touch()

    def image(self, msg):
        if msg.width and msg.height and len(msg.data) >= msg.width * msg.height:
            with self.lock:
                self.camera_time = time.monotonic()

    def reading(self):
        with self.lock:
            now = time.monotonic()
            valid = now - self.range_time < STALE_S and now - self.camera_time < STALE_S
            return self.ranges if valid else None

    def watchdog(self):
        while not AUTO_STOP.exists():
            time.sleep(0.2)
            with self.lock:
                now = time.monotonic()
                if self.moving and (now - self.range_time >= STALE_S or now - self.camera_time >= STALE_S):
                    walk_controller.STOP_FILE.touch()

def main():
    state = SensorState()
    node = Node()
    node.subscribe(LaserScan, "/cece/range_scan", state.scan)
    node.subscribe(Image, "/cece/camera/image", state.image)
    threading.Thread(target=state.watchdog, daemon=True).start()
    blocked_turns = 0
    print("Waiting for camera and range sensor", flush=True)
    try:
        while not AUTO_STOP.exists():
            distance = state.reading()
            if distance is None:
                time.sleep(0.2)
                continue
            if distance < CLEARANCE_M:
                blocked_turns += 1
                if blocked_turns > 8:
                    print("No clear route found; stopping", flush=True)
                    break
                print(f"Obstacle {distance:.2f}m: turn left", flush=True)
                direction = "left"
                steps = 2
            else:
                blocked_turns = 0
                print(f"Clear {distance:.2f}m: forward", flush=True)
                direction = "forward"
                steps = 1
            with state.lock:
                state.forward = direction == "forward"
                state.moving = True
            # Recheck after marking forward, to close the callback/start race.
            if state.forward and (state.reading() is None or state.reading() < CLEARANCE_M):
                with state.lock:
                    state.forward = False
                    state.moving = False
                continue
            walk_controller.main(steps=steps, phase_seconds=0.4, direction=direction)
            with state.lock:
                state.forward = False
                state.moving = False
            time.sleep(0.1)
    finally:
        AUTO_STOP.unlink(missing_ok=True)
        print("Autonomous simulation stopped", flush=True)

if __name__ == "__main__":
    main()
